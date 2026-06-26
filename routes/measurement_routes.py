import json
import os
import pandas as pd
import pymysql
from flask import (
    Blueprint, flash, jsonify, make_response, redirect,
    render_template, request, session, url_for
    )
from scripts.data_extractor.modules.collector import get_lot_data_dict

meas_bp = Blueprint('meas', __name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1q2w3e',
    'database': 'part_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
    }

def get_db_connection():
    return pymysql.connect(**db_config)

def is_measurement_exist(lot_no, process) -> bool:
    db = None
    duplicate_flag = False

    try:
        db = get_db_connection()
        cursor = db.cursor()
        sql = "SELECT COUNT(*) AS cnt FROM measurement WHERE lot_no = %s AND process = %s"
        cursor.execute(sql, (lot_no, process))
        result = cursor.fetchone()
        if result and result.get('cnt', 0) > 0:
            duplicate_flag = True
        else:
            duplicate_flag = False

    except Exception as e:
        print(f"DB duplication Check Error: {e}")
        return False 
    finally:
        if db: db.close()

    return duplicate_flag

@meas_bp.route('/measurement/register')
def index_register():
    return redirect(url_for('meas.extract_data'))

@meas_bp.route('/measurement/register/search', methods=['GET', 'POST'])
def extract_data():
    if request.method == 'GET':
        return render_template('measurement/register-search.html')
    
    lot_no = request.form.get('lot_no')
    process = request.form.get('process')
    part_name = request.form.get('part_name')

    check_only = request.form.get('check_only') == 'true'
    duplicate_flag = is_measurement_exist(lot_no, process)
    
    if check_only:
        return jsonify({"is_duplicate": duplicate_flag})

    # call data_extractor here.
    result = get_lot_data_dict(lot_no, process, part_name, include_ng=True)
    
    if result.get("status") == "error":
        flash(result.get("message"))
        return redirect(url_for('meas.extract_data'))
    
    session.pop('temp_meas_data', None)
    result['is_duplicate'] = duplicate_flag
    session['temp_meas_data'] = result
    return redirect(url_for('meas.show_extracted_data'))

@meas_bp.route('/get_part_json')
def get_part_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    json_path = os.path.join(
        root_dir, 'scripts', 'data_extractor', 'resources', 'index_part_data.json'
        )
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "파일을 찾을 수 없습니다."}), 404
    
@meas_bp.route('/measurement/register/data_viewer')
def show_extracted_data():
    data = session.get('temp_meas_data')
    if not data:
        flash("전송된 데이터가 없거나 세션이 만료되었습니다.")
        return redirect(url_for('meas.extract_data'))
    
    # 템플릿 결과를 담은 응답 객체 생성
    response = make_response(
        render_template('measurement/register-data_viewer.html', data=data)
        )
    
    # 캐시를 방지하는 헤더들을 응답 객체에 추가
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # 완성된 응답 객체 리턴
    return response

@meas_bp.route('/measurement/register/save', methods=['POST'])
def save_measurement_data():
    selected_sn = request.form.getlist('selected_ids')
    all_data = session.get('temp_meas_data')

    if not all_data or not selected_sn:
        return "전송된 데이터가 없거나 세션이 만료되었습니다.", 400
    info = all_data.get('info', {})

    selected_parts = [
        part for part in all_data.get('parts', [])
        if part.get('serial_num') in selected_sn
    ]

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        insert_data_list = []

        # 공통 정보 매핑
        lot_no = info.get('lot_num')
        process = info.get('process')
        
        # DB 내 중복 데이터 우선 삭제
        is_duplicate = all_data.get('is_duplicate', False)
        if is_duplicate:
            delete_sql = "DELETE FROM measurement WHERE lot_no = %s AND process = %s"
            cursor.execute(delete_sql, (lot_no, process))

        # 공통 정보 매핑
        part_name = info.get('part_name')
        cursor.execute("SELECT id FROM part_list WHERE part_name = %s", (part_name))
        raw_part_id = cursor.fetchone()
        if not raw_part_id:
            raise KeyError("DB.part_list에 없는 규격.")
        part_id = raw_part_id['id']
        
        dim_names = info.get('dim_basic_name', [])
        dim_basics = info.get('dim_basic_float', [])
        tol_uppers = info.get('tol_upper', [])
        tol_lowers = info.get('tol_lower', [])

        # 필터링된 selected_parts만 가지고 데이터 생성 루프 진입
        for part in selected_parts:
            serial_no = part.get('serial_num')
            m_time = part.get('measured_time')
            worked_machine = part.get('worked_cnc')
            # -- 추후 machine 테이블과 연계
            worker = part.get('worker')
            # -- 추후 worker 테이블과 연계

            dims = part.get('dims', [])
            is_passes = part.get('is_pass', [])

            # 각 파트의 치수 항목 수만큼 루프 돌며 데이터 준비
            for idx, dim_val in enumerate(dims):
                d_name = dim_names[idx]
                d_basic = dim_basics[idx] if idx < len(dim_basics) else 0.0
                t_upper = tol_uppers[idx] if idx < len(tol_uppers) else 0.0
                t_lower = tol_lowers[idx] if idx < len(tol_lowers) else 0.0
                is_pass_val = 1 if (idx < len(is_passes) and is_passes[idx]) else 0
                
                # 리스트 내 튜플로 적재
                insert_data_list.append((
                    lot_no, part_id, process, m_time, worked_machine,
                    d_name, dim_val, d_basic, t_upper, t_lower,
                    is_pass_val, serial_no, worker
                ))
                
        # DB Bulk Insert 실행
        if insert_data_list:
            insert_sql = """
                INSERT INTO measurement (
                    lot_no, part_id, process, measured_datetime, worked_machine, 
                    dim_name, dim, dim_basic, tol_upper, tol_lower, 
                    is_pass, serial_no, worker
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_sql, insert_data_list)

        db.commit()
        session.pop('temp_meas_data', None)

        # 성공 페이지 접근 허용 플래그
        session['save_success_allowed'] = True
        return redirect(url_for('meas.save_success'))
        
    except Exception as e:
        if db:
            db.rollback()
        script = f"""
        <script>
            alert("저장 중 오류 발생: {str(e)}");
            window.location.href = "{url_for('meas.extract_data')}";
        </script>
        """
        return make_response(script)
    
    finally:
        if db: db.close()

@meas_bp.route('/measurement/register/save-success')
def save_success():
    if not session.pop('save_success_allowed', None):
        script = """
        <script>
            alert("잘못된 접근입니다.");
            window.location.href = "/measurement/register/search";
        </script>
        """
        return make_response(script)
    
    return render_template('measurement/register-success.html')

@meas_bp.route('/api/get_processes/<lot_no>')
def get_processes(lot_no):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT DISTINCT process 
                FROM measurement 
                WHERE lot_no = %s 
                ORDER BY process ASC
            """
            cursor.execute(sql, (lot_no,))
            rows = cursor.fetchall()
            process_list = [row['process'] for row in rows]
            return {"status": "success", "processes": process_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
    finally:
        conn.close()

@meas_bp.route('/measurement/history/search')
def index_history():
    return render_template('measurement/history-search.html')

@meas_bp.route('/measurement/history/data_viewer', methods=['GET'])
def show_history_data():
    lot_no = request.values.get('lot_no')
    process = request.values.get('process')

    if not lot_no or not process:
        return redirect(url_for('meas.index_history'))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 추후 worker, machine 테이블 join + product_name
            sql = """
                SELECT m.*, p.part_name
                FROM measurement m
                INNER JOIN part_list p ON m.part_id = p.id
                WHERE m.lot_no = %s 
                AND m.process = %s 
                ORDER BY m.measured_datetime ASC,
                CASE WHEN m.dim_name LIKE '%%(%%' THEN 1 ELSE 0 END ASC,
                m.dim_name ASC;
            """
            cursor.execute(sql, (lot_no, process))
            db_results = cursor.fetchall()
            
            # 1. DB 데이터를 데이터프레임으로 변환
            df = pd.DataFrame(db_results)
            df = df.drop(columns=['id', 'part_id'])
            df['worker'] = df['worker'].fillna('-')
            df['dim_with_pass'] = df.apply(lambda x: f"{x['dim']}|{x['is_pass']}", axis=1)

            # 2. 피벗 테이블 생성
            df_pivot = df.pivot_table(
                index=['measured_datetime', 'worked_machine', 'worker'], 
                columns='dim_name', 
                values='dim_with_pass',
                aggfunc='first'
            ).reset_index()

            # -- 컬럼 순서 재정렬 로직 --
            # 1. 고정 컬럼(시간, 장비)과 치수 컬럼 분리
            fixed_cols = ['measured_datetime', 'worked_machine', 'worker']
            dim_cols = [col for col in df_pivot.columns if col not in fixed_cols]

            # 2. 치수 컬럼 정렬 (일반 이름 먼저, '('로 시작하는 것은 뒤로)
            # key 파라미터를 사용하여 '('로 시작하면 우선순위 1, 아니면 0을 부여.
            sorted_dim_cols = sorted(dim_cols, key=lambda x: (1 if x.startswith('(') else 0, x))

            # 3. 전체 컬럼 순서 합치기
            new_column_order = fixed_cols + sorted_dim_cols
            df_pivot = df_pivot[new_column_order]
            # --------------------------------

            df_pivot['measured_datetime'] = df_pivot['measured_datetime'].dt.strftime(
                '%Y-%m-%d %H:%M:%S'
                )
            df_pivot = df_pivot.fillna('-')

            table_data = df_pivot.to_json(
                orient='records', date_format='iso', force_ascii=False
                )

            # 3. 헤더 치수 추출
            exclude_cols = ['dim_name', 'measured_datetime', 'worked_machine', 'worker']
            dim_name_list = [col for col in df_pivot.columns if col not in exclude_cols]
            specs = {}
            for dn in dim_name_list:
                target_row = df[df['dim_name'] == dn].iloc[0]
                specs[dn] = {
                    'basic': float(target_row['dim_basic']),
                    'upper': float(target_row['tol_upper']),
                    'lower': float(target_row['tol_lower'])
                }
            header_data = dim_name_list

    finally:
        conn.close()

    return render_template(
        'measurement/history-data_viewer.html',
        table_data=table_data,
        header_data=header_data,
        specs = specs,
        info={
            'lot_no': lot_no, 'process': process,
            'part_name': df['part_name'].iloc[0]
            }
        )