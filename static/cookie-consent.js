(function() {
    'use strict';
    
    const CookieConsent = {
        COOKIE_NAME: 'hassan_kamran_cookie_consent',
        COOKIE_DURATION: 365,
        
        init: function() {
            const consent = this.getConsentStatus();
            
            if (consent === null) {
                this.showConsentBanner();
            } else {
                this.applyConsent(consent);
            }
        },
        
        getConsentStatus: function() {
            const cookie = document.cookie
                .split('; ')
                .find(row => row.startsWith(this.COOKIE_NAME + '='));
            
            if (cookie) {
                const value = cookie.split('=')[1];
                return value === 'true';
            }
            
            return null;
        },
        
        setConsentStatus: function(consent) {
            const date = new Date();
            date.setTime(date.getTime() + (this.COOKIE_DURATION * 24 * 60 * 60 * 1000));
            const expires = 'expires=' + date.toUTCString();
            
            document.cookie = this.COOKIE_NAME + '=' + consent + ';' + expires + ';path=/;SameSite=Lax';
        },
        
        applyConsent: function(granted) {
            if (typeof window.clarity !== 'undefined' && window.clarity.consent) {
                window.clarity.consent(granted);
            }
            
            if (typeof gtag !== 'undefined') {
                gtag('consent', 'update', {
                    'analytics_storage': granted ? 'granted' : 'denied',
                    'ad_storage': granted ? 'granted' : 'denied'
                });
            }
            
            this.setConsentStatus(granted);
        },
        
        showConsentBanner: function() {
            const banner = document.createElement('div');
            banner.id = 'cookie-consent-banner';
            banner.className = 'cookie-consent-banner';
            banner.innerHTML = `
                <div class="cookie-consent-content">
                    <div class="cookie-consent-text">
                        <h3>We value your privacy</h3>
                        <p>We use cookies to enhance your browsing experience, analyze site traffic, and personalize content. By clicking "Accept All", you consent to our use of cookies.</p>
                        <a href="/privacy.html" class="cookie-consent-link">Privacy Policy</a>
                    </div>
                    <div class="cookie-consent-actions">
                        <button class="cookie-consent-btn cookie-consent-btn-secondary" id="cookie-consent-reject">
                            Reject All
                        </button>
                        <button class="cookie-consent-btn cookie-consent-btn-primary" id="cookie-consent-accept">
                            Accept All
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(banner);
            
            setTimeout(() => {
                banner.classList.add('cookie-consent-banner-visible');
            }, 100);
            
            document.getElementById('cookie-consent-accept').addEventListener('click', () => {
                this.handleConsent(true);
                this.hideBanner();
            });
            
            document.getElementById('cookie-consent-reject').addEventListener('click', () => {
                this.handleConsent(false);
                this.hideBanner();
            });
        },
        
        handleConsent: function(granted) {
            this.applyConsent(granted);
            
            if (granted) {
                if (!window.clarity && window.clarityInitFunction) {
                    window.clarityInitFunction();
                }
            }
        },
        
        hideBanner: function() {
            const banner = document.getElementById('cookie-consent-banner');
            if (banner) {
                banner.classList.remove('cookie-consent-banner-visible');
                setTimeout(() => {
                    banner.remove();
                }, 300);
            }
        }
    };
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => CookieConsent.init());
    } else {
        CookieConsent.init();
    }
})();