document.addEventListener("DOMContentLoaded", function () {
    // 현재 URL 경로에 따라 header에 active 클래스 부여.
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.header-nav-item');
    
    navItems.forEach(item => {
        const matchRoot = item.getAttribute('data-match-root');
        const href = item.getAttribute('href');
        const comparePath = matchRoot || href;

        if (comparePath) {
            // 1. 메인 페이지('/') 처리: 정확히 일치할 때만 active
            if (comparePath === '/') {
                if (currentPath === '/') item.classList.add('active');
            } 
            // 2. 나머지 경로: 시작 경로가 일치하면 active
            else if (currentPath.startsWith(comparePath)) {
                item.classList.add('active');
            }
        }
    });
});