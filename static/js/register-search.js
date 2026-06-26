document.addEventListener('DOMContentLoaded', function() {
    const partInput = document.getElementById('part-name');
    const partList = document.getElementById('part-list');
    const processSelect = document.getElementById('process-name');
    const lotInput = document.getElementById('lot-no');
    const regForm = document.getElementById('searchForm');
    const loadingOverlay = document.getElementById('loading-overlay');

    let partData = {}; // JSON 데이터를 저장할 변수

    function showLoading() { if (loadingOverlay) loadingOverlay.style.display = 'flex'; }
    function hideLoading() { if (loadingOverlay) loadingOverlay.style.display = 'none'; }

    // 1. 페이지 로드 시 JSON 데이터 가져오기 (Flask 엔드포인트 필요)
    fetch('/get_part_json') // JSON을 반환하는 Flask 라우트를 생성해야 합니다.
        .then(res => res.json())
        .then(data => { partData = data; });

    // 2. 규격 입력 시 자동 완성 및 공정 업데이트
    partInput.addEventListener('input', function() {
        const val = this.value.trim();
        partList.innerHTML = ''; // 리스트 초기화

        if (val.length >= 3) {
            // 키(규격명) 검색 및 목록 표시
            const matches = Object.keys(partData).filter(key => key.includes(val));
            matches.forEach(match => {
                const option = document.createElement('option');
                option.value = match;
                partList.appendChild(option);
            });

            // 만약 입력값이 등록된 규격과 정확히 일치하면 공정 목록 갱신
            if (partData[val]) {
                updateProcessOptions(val);
            }
        }
    });

    // 3. 공정 드롭다운 동적 생성 함수
    function updateProcessOptions(selectedPart) {
        const processes = Object.keys(partData[selectedPart]);
        processSelect.innerHTML = '<option value="" disabled selected>공정 선택</option>';
        
        processes.forEach(proc => {
            const option = document.createElement('option');
            option.value = proc;
            option.textContent = proc;
            processSelect.appendChild(option);
        });
    }

    if (lotInput) {
        lotInput.addEventListener('input', function() {
            let lotNum = this.value.trim().toUpperCase();
            let isValid = (lotNum.startsWith("KK20") && lotNum.length === 13) || 
                        (lotNum.startsWith("20") && lotNum.length === 11);

            if (lotNum === "") {
                this.style.borderColor = "#ddd"; 
                this.style.boxShadow = "none";
            } else if (isValid) {
                this.style.borderColor = "#05A0E2";
                this.style.boxShadow = "0 0 5px rgba(5, 160, 226, 0.2)";
            } else {
                this.style.borderColor = "#dc3545";
                this.style.boxShadow = "0 0 5px rgba(220, 53, 69, 0.2)";
            }
        });
    }

    if (regForm) {
        regForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            // 1. 유효성 검사
            const lotVal = lotInput.value.trim().toUpperCase();
            const isValid = (lotVal.startsWith("KK20") && lotVal.length === 13) || 
                            (lotVal.startsWith("20") && lotVal.length === 11);
            
            if (!isValid) {
                alert("LOT 번호 형식이 올바르지 않습니다.");
                return;
            }

            if (lotVal.startsWith("20")) {
                lotInput.value = "KK" + lotVal;
            } else {
                lotInput.value = lotVal;
                }

            // 중복 체크 통신 시작 전 로딩 오버레이 활성화
            showLoading();

            // 2. 서버에 중복 여부 확인 (비동기 Fetch)
            const formData = new FormData(regForm);
            formData.append('check_only', 'true');

            try {
                const response = await fetch(regForm.action, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                // 3. 중복 존재 시 질문
                if (result.is_duplicate) {
                    hideLoading(); 
                    if (!confirm("DB에 동일한 LOT/공정의 데이터가 이미 존재합니다.\n기존 데이터를 삭제 후 덮어쓸까요?")) {
                        hideLoading(); 
                        return;
                    }
                    showLoading();
                }
            } catch (error) {
                console.error("중복 체크 실패:", error);
                hideLoading(); // 에러 발생 시에도 화면이 굳지 않도록 오버레이 제거
                alert("중복 체크 중 오류가 발생했습니다.");
                return;
            }

            // 4. 데이터 정상 제출 처리
            setTimeout(function() {
                regForm.submit();
            }, 1000);
        });
    }

    window.addEventListener('pageshow', function(event) {
        if (event.persisted || (window.performance && window.performance.navigation.type === 2)) {
            hideLoading();
        }
    });
});