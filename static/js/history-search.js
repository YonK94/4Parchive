document.addEventListener('DOMContentLoaded', function() {
    const lotInput = document.getElementById('lot-no');
    const processSection = document.getElementById('process-section');
    const processSelect = document.getElementById('process-name');

    let isLoading = false;

    // 1. 유효성 검사 로직을 별도 함수로 분리
    function getLotValidity(lotVal) {
        const isFull = (lotVal.startsWith("KK20") && lotVal.length === 13);
        const isShort = (lotVal.startsWith("20") && lotVal.length === 11);
        return { isFull, isShort, isValid: isFull || isShort };
    }

    if (lotInput) {
        lotInput.addEventListener('input', function() {
            let lotNum = this.value.trim().toUpperCase();
            const { isValid } = getLotValidity(lotNum);

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

    async function loadProcessList() {
        if (isLoading) return;

        let lotNo = lotInput.value.trim().toUpperCase();
        if (!lotNo) {
            processSection.style.display = 'none';
            return;
        }

        // 2. 유효성 검사 및 자동 변환 로직
        const validity = getLotValidity(lotNo);
        
        if (validity.isShort) {
            lotNo = "KK" + lotNo;
            lotInput.value = lotNo; 
        } else if (!validity.isFull) {
            alert('LOT 번호 형식이 올바르지 않습니다.');
            lotInput.value = "";
            lotInput.style.borderColor = "#ddd";
            processSection.style.display = 'none';
            // alert 확인 후 다시 입력창에 포커스
            setTimeout(() => lotInput.focus(), 10); 
            return;
        }

        try {
            isLoading = true;
            
            const response = await fetch(`/api/get_processes/${lotNo}`);
            const data = await response.json();

            if (data.status === 'success' && data.processes.length > 0) {
                processSelect.innerHTML = '<option value="" disabled selected>공정 선택</option>';
                data.processes.forEach(proc => {
                    const option = document.createElement('option');
                    option.value = proc;
                    option.textContent = proc;
                    processSelect.appendChild(option);
                });
                processSection.style.display = 'block';
                lotInput.style.borderColor = "#05A0E2";
            } else {
                alert('해당 LOT로 등록된 데이터가 없습니다.');
                processSection.style.display = 'none';
                lotInput.value = "";
                setTimeout(() => lotInput.focus(), 10);
            }
        } catch (error) {
            console.error('공정 로드 실패:', error);
        } finally {
            isLoading = false;
        }
    }

    lotInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.blur(); // blur 이벤트가 loadProcessList를 실행
        }
    });

    lotInput.addEventListener('blur', loadProcessList);
});