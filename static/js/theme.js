// 主题切换功能
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeMobileMenu();
    initializePageLoadAnimations();
    initializeHoverEffects();
    initializeSmoothScrolling();
    initializeCardClicks();
    initializeRippleEffects();
    initializeFilterClear();
    initializeBackButton();
});

function initializeTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    // 从localStorage获取保存的主题
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // 绑定主题切换事件
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);

        // 添加切换动画效果
        themeToggle.style.transform = 'scale(0.9)';
        setTimeout(() => {
            themeToggle.style.transform = '';
        }, 150);
    });
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#theme-toggle i');
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}

// 返回上一页的通用函数，若没有历史则跳转到默认页面
function goBack() {
    const backButton = document.getElementById('back-button');
    const defaultUrl = backButton ? backButton.dataset.defaultUrl : '/';

    // 尝试使用 history.back()
    if (window.history.length > 1) {
        const prevPath = window.location.pathname;
        window.history.back();
        // 如果在短时间内没有变化，则跳转到默认页面
        setTimeout(() => {
            if (window.location.pathname === prevPath) {
                window.location.href = defaultUrl;
            }
        }, 300);
    } else {
        window.location.href = defaultUrl;
    }
}

function initializeMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileMenuToggle && navMenu) {
    mobileMenuToggle.addEventListener('click', function() {
        navMenu.classList.toggle('mobile-menu-open');
        mobileMenuToggle.classList.toggle('active');
    });

    // 点击其他地方关闭移动菜单
    document.addEventListener('click', function(e) {
        if (!mobileMenuToggle.contains(e.target) && !navMenu.contains(e.target)) {
            navMenu.classList.remove('mobile-menu-open');
            mobileMenuToggle.classList.remove('active');
        }
    });
}
}

// 滚动触发动画
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // 观察所有需要动画的元素
    const animatedElements = document.querySelectorAll('.fade-in-section');
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// 页面加载动画
function initializePageLoadAnimations() {
    // 为需要渐入动画的元素添加类
    const sections = document.querySelectorAll('.featured-section, .features-section');
    sections.forEach((section, index) => {
        section.classList.add('fade-in-section');
        section.style.transitionDelay = `${index * 0.2}s`;
    });

    // 延迟触发可见性检查
    setTimeout(() => {
        initializeScrollAnimations();
    }, 100);
}

// 增强的悬停效果
function initializeHoverEffects() {
    // 为电影卡片添加更丰富的悬停效果
    const filmCards = document.querySelectorAll('.film-card');
    filmCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.zIndex = '10';
        });

        card.addEventListener('mouseleave', function() {
            this.style.zIndex = '1';
        });
    });
}

// 平滑滚动
function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// 使电影卡和特性卡整体可点击（支持键盘与无障碍）
function initializeCardClicks() {
    function makeClickable(selector, attrName = 'data-href') {
        document.querySelectorAll(selector + '[' + attrName + ']').forEach(card => {
            const href = card.getAttribute(attrName);
            if (!href) return;
            card.style.cursor = 'pointer';

            // 可聚焦与语义化
            if (!card.hasAttribute('tabindex')) card.setAttribute('tabindex', '0');
            if (!card.hasAttribute('role')) card.setAttribute('role', 'link');

            // 鼠标点击：若不是点击到内部交互元素则导航
            card.addEventListener('click', function(e) {
                if (e.target.closest('a') || e.target.closest('button') || e.target.closest('input')) return;
                window.location.href = href;
            });

            // 键盘激活
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    window.location.href = href;
                }
            });
        });
    }

    makeClickable('.film-card', 'data-href');
    makeClickable('.feature-card', 'data-href');
}

// 点击波纹效果与按压反馈
function initializeRippleEffects() {
    function createRipple(e, element) {
        const rect = element.getBoundingClientRect();
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        const size = Math.max(rect.width, rect.height) * 0.5;
        ripple.style.width = ripple.style.height = size + 'px';
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        element.appendChild(ripple);
        setTimeout(() => ripple.remove(), 700);
    }

    function attach(selector) {
        document.querySelectorAll(selector).forEach(el => {
            el.addEventListener('pointerdown', function(e) {
                // ignore if clicking inner controls
                if (e.target.closest('a') || e.target.closest('button') || e.target.closest('input')) return;
                el.classList.add('pressed');
                createRipple(e, el);
            });
            el.addEventListener('pointerup', function() {
                el.classList.remove('pressed');
            });
            el.addEventListener('pointerleave', function() {
                el.classList.remove('pressed');
            });
        });
    }

    attach('.film-card');
    attach('.feature-card');
    attach('.btn');
}

// 返回按钮初始化与回退逻辑
function initializeBackButton() {
    const backBtn = document.getElementById('back-button');
    if (!backBtn) return;

    // 判断是否能回退：优先使用 history.length，其次使用 document.referrer 判断是否来自本站
    const canHistoryBack = window.history && window.history.length > 1;
    const referrer = document.referrer || '';
    const sameSiteReferrer = referrer.includes(window.location.hostname);

    if (canHistoryBack || sameSiteReferrer) {
        backBtn.style.display = 'inline-flex';
    } else {
        backBtn.style.display = 'none';
    }

    backBtn.addEventListener('click', function() {
        // 尝试后退历史
        if (window.history && window.history.length > 1) {
            window.history.back();
            // 如果后退无效，在短延时后跳转到首页作为兜底
            setTimeout(() => {
                if (document.hidden || document.readyState === 'complete') {
                    window.location.href = window.SITE_HOME || '/';
                }
            }, 300);
            return;
        }

        // fallback：直接跳转到站点首页
        window.location.href = window.SITE_HOME || '/';
    });
}

// 清除筛选按钮行为（若存在）
function initializeFilterClear() {
    const clearBtn = document.querySelector('.clear-filters');
    if (!clearBtn) return;
    clearBtn.addEventListener('click', function(e) {
        e.preventDefault();
        // 重定向到电影列表（无查询参数）
        window.location.href = window.SITE_HOME ? window.SITE_HOME.replace('/', '/films') : '/films';
    });
}

// 在 DOMContentLoaded 后也初始化清除筛选（如果页面存在筛选表单）
// 用户菜单下拉功能
document.addEventListener('DOMContentLoaded', function() {
    const userMenuTrigger = document.querySelector('.user-menu-trigger');
    const userMenuDropdown = document.querySelector('.user-menu-dropdown');

    if (userMenuTrigger && userMenuDropdown) {
        userMenuTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            userMenuDropdown.classList.toggle('show');
        });

        // 点击其他地方关闭下拉菜单
        document.addEventListener('click', function() {
            userMenuDropdown.classList.remove('show');
        });
    }
});
