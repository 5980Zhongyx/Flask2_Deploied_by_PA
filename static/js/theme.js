// Theme and Language switching functionality
document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle removed — do not initialize theme switching
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

// initializeTheme removed — theme switching UI has been removed per requirement.
function initializeTheme() {
    // no-op
}

// updateThemeIcon no-op since theme toggle removed
function updateThemeIcon(theme) { /* no-op */ }

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
        // Call backend to set language in session; include credentials so session cookie is sent/received.
        fetch(`/language/${newLang}`, {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            // reload regardless; backend sets session cookie
            window.location.reload();
        })
        .catch(error => {
            console.error('Language switch error:', error);
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

// ==========================================
// ACCESSIBILITY ENHANCEMENTS
// ==========================================

// Speech synthesis for screen readers and voice assistance
class AccessibilityManager {
    constructor() {
        this.speechSynthesis = window.speechSynthesis;
        this.isHighContrast = false;
        this.fontSize = 1.0;
        this.isScreenReaderMode = false;
        this.init();
    }

    init() {
        this.createAccessibilityPanel();
        this.setupKeyboardShortcuts();
        this.setupFocusManagement();
        this.loadUserPreferences();
    }

    createAccessibilityPanel() {
        const panel = document.createElement('div');
        panel.id = 'accessibility-panel';
        panel.className = 'accessibility-panel';
        panel.innerHTML = `
            <button class="accessibility-toggle" aria-label="Accessibility options" title="Accessibility options">
                <i class="fas fa-universal-access"></i>
            </button>
            <div class="accessibility-menu" role="dialog" aria-modal="false" aria-labelledby="accessibility-title">
                <div class="accessibility-header">
                    <div id="accessibility-title" role="heading" aria-level="2">Accessibility Options</div>
                    <button class="close-accessibility" aria-label="Close accessibility menu">&times;</button>
                </div>
                <div class="accessibility-options">
                    <button id="speak-page" class="accessibility-btn" aria-label="Read page aloud">
                        <i class="fas fa-volume-up"></i> Read Page
                    </button>
                    <button id="high-contrast" class="accessibility-btn" aria-label="Toggle high contrast mode">
                        <i class="fas fa-adjust"></i> High Contrast
                    </button>
                    <button id="increase-font" class="accessibility-btn" aria-label="Increase font size">
                        <i class="fas fa-plus"></i> Larger Text
                    </button>
                    <button id="decrease-font" class="accessibility-btn" aria-label="Decrease font size">
                        <i class="fas fa-minus"></i> Smaller Text
                    </button>
                    <button id="screen-reader-mode" class="accessibility-btn" aria-label="Toggle screen reader friendly mode">
                        <i class="fas fa-eye"></i> Screen Reader Mode
                    </button>
                    <button id="keyboard-nav" class="accessibility-btn" aria-label="Show keyboard shortcuts">
                        <i class="fas fa-keyboard"></i> Keyboard Shortcuts
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(panel);
        // keep references for event handlers to avoid global queries
        this.panel = panel;
        this.menu = panel.querySelector('.accessibility-menu');
        this.toggleBtn = panel.querySelector('.accessibility-toggle');
        this.closeBtn = panel.querySelector('.close-accessibility');
        this.bindAccessibilityEvents();
    }

    bindAccessibilityEvents() {
        // Toggle panel (scoped to this panel)
        const toggle = this.toggleBtn;
        const menu = this.menu;
        const closeBtn = this.closeBtn;

        if (toggle) {
            toggle.setAttribute('aria-expanded', 'false');
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const showing = menu.classList.toggle('show');
                toggle.setAttribute('aria-expanded', showing ? 'true' : 'false');
                if (showing) toggle.focus();
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                menu.classList.remove('show');
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
                if (toggle) toggle.focus();
            });
        }

        // Close panel on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (this.menu && this.menu.classList.contains('show')) {
                    this.menu.classList.remove('show');
                    if (this.toggleBtn) this.toggleBtn.setAttribute('aria-expanded', 'false');
                    if (this.toggleBtn) this.toggleBtn.focus();
                }
            }
        });

        // Accessibility options
        document.getElementById('speak-page').addEventListener('click', () => this.speakPageContent());
        document.getElementById('high-contrast').addEventListener('click', () => this.toggleHighContrast());
        document.getElementById('increase-font').addEventListener('click', () => this.adjustFontSize(0.1));
        document.getElementById('decrease-font').addEventListener('click', () => this.adjustFontSize(-0.1));
        document.getElementById('screen-reader-mode').addEventListener('click', () => this.toggleScreenReaderMode());
        document.getElementById('keyboard-nav').addEventListener('click', () => this.showKeyboardShortcuts());
    }

    speakPageContent() {
        if (!this.speechSynthesis) {
            this.announceToScreenReader('Speech synthesis not supported in this browser');
            return;
        }

        // Stop any ongoing speech
        this.speechSynthesis.cancel();

        // Get main content to read
        const mainContent = document.querySelector('main') || document.body;
        const textToRead = this.extractReadableText(mainContent);

        if (textToRead.trim()) {
            const utterance = new SpeechSynthesisUtterance(textToRead);
            utterance.lang = document.documentElement.lang || 'en';
            utterance.rate = 0.8; // Slightly slower for clarity
            utterance.pitch = 1;

            utterance.onstart = () => this.announceToScreenReader('Reading page content...');
            utterance.onend = () => this.announceToScreenReader('Finished reading page content');

            this.speechSynthesis.speak(utterance);
        } else {
            this.announceToScreenReader('No readable content found on this page');
        }
    }

    extractReadableText(element) {
        // Extract text from headings, paragraphs, and links
        const selectors = 'h1, h2, h3, h4, h5, h6, p, a, li, td, th, caption, figcaption, label';
        const elements = element.querySelectorAll(selectors);
        let text = '';

        elements.forEach(el => {
            const tagName = el.tagName.toLowerCase();
            let prefix = '';

            // Add semantic prefixes for better context
            if (tagName.startsWith('h')) {
                prefix = `Heading level ${tagName.charAt(1)}: `;
            } else if (tagName === 'a') {
                prefix = 'Link: ';
            } else if (tagName === 'li') {
                prefix = '• ';
            }

            const content = el.textContent.trim();
            if (content && !el.closest('[aria-hidden="true"], .sr-only, [hidden]')) {
                text += prefix + content + '. ';
            }
        });

        return text;
    }

    toggleHighContrast() {
        this.isHighContrast = !this.isHighContrast;
        document.documentElement.classList.toggle('high-contrast', this.isHighContrast);

        const btn = document.getElementById('high-contrast');
        btn.innerHTML = this.isHighContrast ?
            '<i class="fas fa-adjust"></i> Normal Contrast' :
            '<i class="fas fa-adjust"></i> High Contrast';

        this.saveUserPreferences();
        this.announceToScreenReader(this.isHighContrast ? 'High contrast mode enabled' : 'High contrast mode disabled');
    }

    adjustFontSize(delta) {
        this.fontSize = Math.max(0.7, Math.min(2.0, this.fontSize + delta));
        document.documentElement.style.fontSize = `${this.fontSize * 100}%`;
        this.saveUserPreferences();
        this.announceToScreenReader(`Font size adjusted to ${Math.round(this.fontSize * 100)}%`);
    }

    toggleScreenReaderMode() {
        this.isScreenReaderMode = !this.isScreenReaderMode;
        document.documentElement.classList.toggle('screen-reader-mode', this.isScreenReaderMode);

        const btn = document.getElementById('screen-reader-mode');
        btn.innerHTML = this.isScreenReaderMode ?
            '<i class="fas fa-eye-slash"></i> Normal Mode' :
            '<i class="fas fa-eye"></i> Screen Reader Mode';

        this.saveUserPreferences();
        this.announceToScreenReader(this.isScreenReaderMode ? 'Screen reader friendly mode enabled' : 'Screen reader friendly mode disabled');
    }

    showKeyboardShortcuts() {
        const shortcuts = `
Keyboard Shortcuts:
• Alt + H: Go to Home
• Alt + S: Go to Search
• Alt + R: Go to Recommendations
• Alt + P: Go to Profile
• Alt + T: Toggle Theme
• Alt + L: Switch Language
• Alt + A: Open Accessibility Menu
• Escape: Close menus
• Tab: Navigate through elements
• Enter/Space: Activate buttons and links
        `;

        alert(shortcuts);
        this.announceToScreenReader('Keyboard shortcuts displayed');
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only trigger if not in form inputs
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.contentEditable === 'true') {
                return;
            }

            if (e.altKey) {
                switch (e.key.toLowerCase()) {
                    case 'h':
                        e.preventDefault();
                        window.location.href = '/';
                        break;
                    case 's':
                        e.preventDefault();
                        const searchInput = document.querySelector('input[name="search"]');
                        if (searchInput) searchInput.focus();
                        break;
                    case 'r':
                        e.preventDefault();
                        window.location.href = '/recommendations';
                        break;
                    case 'p':
                        e.preventDefault();
                        window.location.href = '/profile';
                        break;
                    case 't':
                        // Theme toggle removed — no action
                        e.preventDefault();
                        break;
                    case 'l':
                        e.preventDefault();
                        this.toggleLanguage();
                        break;
                    case 'a':
                        e.preventDefault();
                        document.querySelector('.accessibility-toggle').click();
                        break;
                }
            }

            // Escape key handling
            if (e.key === 'Escape') {
                // Close any open menus
                document.querySelectorAll('.accessibility-menu.show, .mobile-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }

    setupFocusManagement() {
        // Improve focus visibility
        document.addEventListener('focusin', (e) => {
            if (e.target.matches('button, a, input, select, textarea')) {
                e.target.style.outline = '2px solid #007bff';
                e.target.style.outlineOffset = '2px';
            }
        });

        document.addEventListener('focusout', (e) => {
            if (e.target.matches('button, a, input, select, textarea')) {
                e.target.style.outline = '';
                e.target.style.outlineOffset = '';
            }
        });

        // Skip to main content link - only create if not already present in template
        if (!document.querySelector('.skip-link')) {
            const skipLink = document.createElement('a');
            skipLink.href = '#main-content';
            skipLink.className = 'skip-link sr-only';
            skipLink.textContent = 'Skip to main content';
            document.body.insertBefore(skipLink, document.body.firstChild);

            // Show skip link on focus
            skipLink.addEventListener('focus', () => skipLink.classList.remove('sr-only'));
            skipLink.addEventListener('blur', () => skipLink.classList.add('sr-only'));
        } else {
            // If one or more skip-links exist in the template, dedupe and ensure keyboard focus shows it
            const existingLinks = Array.from(document.querySelectorAll('.skip-link'));
            if (existingLinks.length > 1) {
                // keep the first, remove others
                for (let i = 1; i < existingLinks.length; i++) {
                    const el = existingLinks[i];
                    el.parentNode && el.parentNode.removeChild(el);
                }
            }

            const existing = document.querySelector('.skip-link');
            if (existing) {
                // remove any inline color/background/opacity that may interfere and ensure it's hidden by sr-only
                try {
                    existing.style.removeProperty('color');
                    existing.style.removeProperty('background-color');
                    existing.style.removeProperty('opacity');
                    existing.removeAttribute('style');
                    existing.classList.add('sr-only');
                } catch (e) {
                    // ignore
                }

                existing.addEventListener &&
                    existing.addEventListener('focus', () => existing.classList.remove('sr-only'));
                existing.addEventListener &&
                    existing.addEventListener('blur', () => existing.classList.add('sr-only'));
            }
        }
    }

    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    saveUserPreferences() {
        const preferences = {
            highContrast: this.isHighContrast,
            fontSize: this.fontSize,
            screenReaderMode: this.isScreenReaderMode
        };
        localStorage.setItem('accessibility_preferences', JSON.stringify(preferences));
    }

    loadUserPreferences() {
        try {
            const preferences = JSON.parse(localStorage.getItem('accessibility_preferences') || '{}');

            if (preferences.highContrast) {
                this.isHighContrast = true;
                document.documentElement.classList.add('high-contrast');
            }

            if (preferences.fontSize) {
                this.fontSize = preferences.fontSize;
                document.documentElement.style.fontSize = `${this.fontSize * 100}%`;
            }

            if (preferences.screenReaderMode) {
                this.isScreenReaderMode = true;
                document.documentElement.classList.add('screen-reader-mode');
            }
        } catch (e) {
            console.warn('Failed to load accessibility preferences:', e);
        }
    }

    toggleTheme() {
        // Theme switch removed; keep function as no-op for backwards compatibility
        // Previously toggled data-theme; now intentionally disabled.
        return;
    }

    toggleLanguage() {
        // Trigger language toggle if available
        const langToggle = document.getElementById('lang-toggle');
        if (langToggle) {
            langToggle.click();
        }
    }
}

// Initialize accessibility manager
const accessibilityManager = new AccessibilityManager();
