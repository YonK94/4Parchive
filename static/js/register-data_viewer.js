document.addEventListener('DOMContentLoaded', () => {
    const selectAll = document.getElementById('selectAll');
    const form = document.querySelector('form');
    const getItems = () => document.querySelectorAll('input[name="selected_ids"]');

    if (selectAll) {
        // [전체 선택] 클릭 시 -> 개별 체크박스들 전체 제어
        selectAll.addEventListener('change', function() {
            getItems().forEach(cb => {  
                cb.checked = this.checked;
            });
        });

        // [개별 체크박스] 클릭 시 -> '전체 선택' 상태 업데이트 (역동기화)
        getItems().forEach(cb => {
            cb.addEventListener('change', () => {
                const totalCount = getItems().length;
                const checkedCount = document.querySelectorAll('input[name="selected_ids"]:checked').length;
                
                // 전체 개수와 체크된 개수가 같을 때만 '전체 선택' 체크박스를 체크 상태로 변경
                selectAll.checked = (totalCount === checkedCount);
            });
        });
    }

    // 폼 제출(등록 버튼) 제어 및 알림
    if (form) {
        form.addEventListener('submit', function(e) {
            const checkedCount = document.querySelectorAll('input[name="selected_ids"]:checked').length;

            if (checkedCount === 0) {
                alert("선택된 데이터가 없습니다.\n등록할 데이터를 선택해 주세요.");
                e.preventDefault();
                return;
            }

            if (!confirm("정말 등록하겠습니까?")) {
                e.preventDefault();
            }
        });
    }
});