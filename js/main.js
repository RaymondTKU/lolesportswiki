// 英雄聯盟電競資訊網 - 主要JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
    // 導航欄滾動效果
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // 搜尋功能
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    
    // 搜尋下拉選單
    const searchDropdown = document.createElement('div');
    searchDropdown.className = 'search-dropdown';
    searchInput.parentNode.style.position = 'relative';
    searchInput.parentNode.appendChild(searchDropdown);
    
    const searchSuggestions = [
        'T1', 'Gen.G', 'JDG', 'BLG', 'G2', 'Fnatic', 'Faker', 'Ruler', 'Caps', 'Canyon',
        'LCK', 'LPL', 'LEC', 'World Championship', 'MSI'
    ];
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        if (query.length > 0) {
            const filtered = searchSuggestions.filter(item => 
                item.toLowerCase().includes(query)
            );
            
            if (filtered.length > 0) {
                searchDropdown.innerHTML = filtered.map(item => 
                    `<div class="search-dropdown-item">${item}</div>`
                ).join('');
                searchDropdown.classList.add('active');
            } else {
                searchDropdown.classList.remove('active');
            }
        } else {
            searchDropdown.classList.remove('active');
        }
    });
    
    // 點擊搜尋建議項目
    searchDropdown.addEventListener('click', function(e) {
        if (e.target.classList.contains('search-dropdown-item')) {
            searchInput.value = e.target.textContent;
            searchDropdown.classList.remove('active');
        }
    });
    
    // 點擊外部關閉下拉選單
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
            searchDropdown.classList.remove('active');
        }
    });
    
    // 搜尋按鈕功能
    searchBtn.addEventListener('click', function() {
        const query = searchInput.value.trim();
        if (query) {
            // 這裡可以加入搜尋功能，目前只是示例
            alert(`搜尋: ${query}`);
        }
    });
    
    // Enter鍵搜尋
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });

    // 平滑滾動
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // 滾動視差效果
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translate3d(0, ${yPos}px, 0)`;
        });
    });

    // 載入動畫
    const loadingScreen = document.createElement('div');
    loadingScreen.className = 'loading';
    loadingScreen.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(loadingScreen);
    
    window.addEventListener('load', function() {
        setTimeout(() => {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.remove();
            }, 500);
        }, 1000);
    });

    // 滾動顯示動畫
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // 觀察所有需要動畫的元素
    const animateElements = document.querySelectorAll('.match-card, .player-card, .team-showcase');
    animateElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(50px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });

    // 數字計數動畫
    function animateNumber(element, start, end, duration) {
        let startTime = null;
        
        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const progress = Math.min(timeElapsed / duration, 1);
            
            const current = Math.floor(progress * (end - start) + start);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(animation);
            }
        }
        
        requestAnimationFrame(animation);
    }
    
    // 統計數字動畫
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.target);
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateNumber(counter, 0, target, 2000);
                    observer.unobserve(counter);
                }
            });
        });
        observer.observe(counter);
    });

    // 按鈕懸浮效果
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // 卡片懸浮效果
    const cards = document.querySelectorAll('.match-card, .player-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 10px 30px rgba(200, 155, 60, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });

    // 表單驗證
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function validateForm(formData) {
        const errors = [];
        
        if (!formData.username || formData.username.length < 3) {
            errors.push('用戶名至少需要3個字符');
        }
        
        if (!formData.email || !validateEmail(formData.email)) {
            errors.push('請輸入有效的電子郵件地址');
        }
        
        if (!formData.password || formData.password.length < 6) {
            errors.push('密碼至少需要6個字符');
        }
        
        return errors;
    }
    
    // 收藏功能
    const favoriteButtons = document.querySelectorAll('.btn-favorite');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const isFavorited = this.classList.contains('favorited');
            
            if (isFavorited) {
                this.classList.remove('favorited');
                this.innerHTML = '♡ 收藏';
                this.style.color = 'var(--text-white)';
            } else {
                this.classList.add('favorited');
                this.innerHTML = '♥ 已收藏';
                this.style.color = 'var(--accent-gold)';
            }
        });
    });

    // 回到頂部按鈕
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '↑';
    backToTop.className = 'back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--gradient-gold);
        color: var(--primary-blue);
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 1000;
    `;
    
    document.body.appendChild(backToTop);
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 500) {
            backToTop.style.opacity = '1';
        } else {
            backToTop.style.opacity = '0';
        }
    });
    
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // 自動輪播功能
    const carousel = document.querySelector('.carousel-container');
    if (carousel) {
        let isScrolling = false;
        
        carousel.addEventListener('mouseenter', function() {
            isScrolling = true;
            this.style.animationPlayState = 'paused';
        });
        
        carousel.addEventListener('mouseleave', function() {
            isScrolling = false;
            this.style.animationPlayState = 'running';
        });
    }
});
