// static/js/measurement_viewer.js
function initMeasurementTable(tableData, headerData, specs) {
    // 1. Tabulator 컬럼 정의 생성
    const columns = [
        {
            title: "측정일시", 
            field: "measured_datetime", 
            width: 150, 
            hozAlign: "center",
            formatter: function(cell) {
                const val = cell.getValue();
                if (!val || val === "-") return "-";
                return val.substring(2, 16); 
            }
        },
        {
            title: "장비", 
            field: "worked_machine", 
            width: 80, 
            hozAlign: "center",
            formatter: function(cell) {
                const val = cell.getValue();
                if (!val || val === "-") return "-";
                return val.replace("4-", "");
            }
        },
        // {
        //     title: "작업자", 
        //     field: "worker", 
        //     width: 80, 
        //     hozAlign: "center",
        //     formatter: function(cell) {
        //         const val = cell.getValue();
        //         return (val === null || val === undefined || val === "") ? "-" : val;
        //     }
        // },
    ];

    // 2. 동적 헤더 추가
    headerData.forEach(function(dimName) {
        const s = specs[dimName] || { basic: "-", upper: "-", lower: "-" };
        const combinedTitle = `
            <div>
                ${dimName}
                <div class="spec-text" style="font-size: 0.75rem; color: #666; font-weight: normal; margin-top: 2px;">
                    ${s.basic}<br>[${s.lower}/${s.upper}]
                </div>
            </div>
        `;
        
        columns.push({
            title: combinedTitle, // HTML 구조가 들어간 제목
            field: dimName,
            width: 120,
            hozAlign: "center",
            headerHozAlign: "center",
            formatter: function(cell) {
                const rawVal = cell.getValue();
                const cellElement = cell.getElement();
                cellElement.classList.remove("badge-ng");
                cellElement.style.backgroundColor = "";

                if (!rawVal || rawVal === "-") return "-";

                const parts = String(rawVal).split("|");
                const val = parts[0]; 
                const isPass = parts[1];

                if (isPass === "0") {
                    cellElement.classList.add("badge-ng");
                    cellElement.style.backgroundColor = "#ffeaea"; 
                }

                return (val === "NaN" || isNaN(val)) ? "-" : Number(val).toFixed(3);
            }
        });
    });

    // 3. 표 초기화
    return new Tabulator("#data-table", {
        data: tableData,
        columns: columns,
        layout: "fitColumns",
        height: "600px",
        placeholder: "조회된 데이터가 없습니다.",
        nestedFieldSeparator: false,
        movableColumns: true,
        resizableColumnFit: true,
    });
}