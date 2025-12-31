// Theme and Language switching functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeLanguage();
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

    // Get saved theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Bind theme toggle event
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);

        // Add toggle animation effect
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

// Language switching functionality
function initializeLanguage() {
    const langToggle = document.getElementById('lang-toggle');
    const currentLangSpan = document.getElementById('current-lang');

    if (!langToggle || !currentLangSpan) return;

    // Get saved language from localStorage or default to English
    const savedLang = localStorage.getItem('language') || 'en';
    setLanguage(savedLang);

    // Bind language toggle event
    langToggle.addEventListener('click', function() {
        const currentLang = localStorage.getItem('language') || 'en';
        const newLang = currentLang === 'en' ? 'zh' : 'en';

        setLanguage(newLang);
        localStorage.setItem('language', newLang);

        // Add toggle animation
        langToggle.style.transform = 'scale(0.9)';
        setTimeout(() => {
            langToggle.style.transform = '';
        }, 150);

        // Call backend to set language in session and reload page
        fetch(`/language/${newLang}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (response.ok) {
                // Reload page to apply language changes
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Language switch error:', error);
            // Fallback: still reload
            window.location.reload();
        });
    });
}

function setLanguage(lang) {
    const currentLangSpan = document.getElementById('current-lang');
    if (currentLangSpan) {
        currentLangSpan.textContent = lang.toUpperCase();
    }

    // Set document language
    document.documentElement.lang = lang;

    // You could add more dynamic text updates here
    // For now, we rely on server-side rendering for different languages
}

// General function to go back, redirect to default page if no history
function goBack() {
    const backButton = document.getElementById('back-button');
    const defaultUrl = backButton ? backButton.dataset.defaultUrl : '/';

    // Try using history.back()
    if (window.history.length > 1) {
        const prevPath = window.location.pathname;
        window.history.back();
        // If no change in short time, redirect to default page
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

    // Close mobile menu when clicking elsewhere
    document.addEventListener('click', function(e) {
        if (!mobileMenuToggle.contains(e.target) && !navMenu.contains(e.target)) {
            navMenu.classList.remove('mobile-menu-open');
            mobileMenuToggle.classList.remove('active');
        }
    });
}
}

// Scroll trigger animations
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

    // Observe all elements that need animation
    const animatedElements = document.querySelectorAll('.fade-in-section');
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Page load animations
function initializePageLoadAnimations() {
    // Add class to elements that need fade-in animation
    const sections = document.querySelectorAll('.featured-section, .features-section');
    sections.forEach((section, index) => {
        section.classList.add('fade-in-section');
        section.style.transitionDelay = `${index * 0.2}s`;
    });

    // Delay trigger visibility check
    setTimeout(() => {
        initializeScrollAnimations();
    }, 100);
}

// Enhanced hover effects
function initializeHoverEffects() {
    // Add richer hover effects to movie cards
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

// Smooth scrolling
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

// Make movie cards and feature cards clickable overall (keyboard and accessibility support)
function initializeCardClicks() {
    function makeClickable(selector, attrName = 'data-href') {
        document.querySelectorAll(selector + '[' + attrName + ']').forEach(card => {
            const href = card.getAttribute(attrName);
            if (!href) return;
            card.style.cursor = 'pointer';

            // Focusable and semantic
            if (!card.hasAttribute('tabindex')) card.setAttribute('tabindex', '0');
            if (!card.hasAttribute('role')) card.setAttribute('role', 'link');

            // Mouse click: navigate if not clicking on internal interactive elements
            card.addEventListener('click', function(e) {
                if (e.target.closest('a') || e.target.closest('button') || e.target.closest('input')) return;
                window.location.href = href;
            });

            // Keyboard activation
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

// Click ripple effects and press feedback
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

// Back button initialization and fallback logic
function initializeBackButton() {
    const backBtn = document.getElementById('back-button');
    if (!backBtn) return;

    // Check if can go back: prefer history.length, then use document.referrer to check if from same site
    const canHistoryBack = window.history && window.history.length > 1;
    const referrer = document.referrer || '';
    const sameSiteReferrer = referrer.includes(window.location.hostname);

    if (canHistoryBack || sameSiteReferrer) {
        backBtn.style.display = 'inline-flex';
    } else {
        backBtn.style.display = 'none';
    }

    backBtn.addEventListener('click', function() {
        // Try going back in history
        if (window.history && window.history.length > 1) {
            window.history.back();
            // If back fails, redirect to home page after short delay as fallback
            setTimeout(() => {
                if (document.hidden || document.readyState === 'complete') {
                    window.location.href = window.SITE_HOME || '/';
                }
            }, 300);
            return;
        }

        // Fallback: directly redirect to site home page
        window.location.href = window.SITE_HOME || '/';
    });
}

// Clear filter button behavior (if exists)
function initializeFilterClear() {
    const clearBtn = document.querySelector('.clear-filters');
    if (!clearBtn) return;
    clearBtn.addEventListener('click', function(e) {
        e.preventDefault();
        // Redirect to movie list (without query parameters)
        window.location.href = window.SITE_HOME ? window.SITE_HOME.replace('/', '/films') : '/films';
    });
}

// Also initialize clear filter after DOMContentLoaded (if page has filter form)
// User menu dropdown functionality
document.addEventListener('DOMContentLoaded', function() {
    const userMenuTrigger = document.querySelector('.user-menu-trigger');
    const userMenuDropdown = document.querySelector('.user-menu-dropdown');

    if (userMenuTrigger && userMenuDropdown) {
        userMenuTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            userMenuDropdown.classList.toggle('show');
        });

        // Close dropdown when clicking elsewhere
        document.addEventListener('click', function() {
            userMenuDropdown.classList.remove('show');
        });
    }
});
