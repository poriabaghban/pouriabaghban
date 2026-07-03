/**
 * Skeleton Loading Manager
 * مدیریت نمایش skeleton در زمان لود صفحه
 */

class SkeletonLoader {
    constructor() {
        this.skeletons = [];
        this.isLoading = false;
    }

    /**
     * نمایش skeleton برای یک عنصر
     */
    showSkeleton(elementId, type = 'text', count = 1) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.innerHTML = '';
        
        for (let i = 0; i < count; i++) {
            const skeleton = this.createSkeleton(type);
            element.appendChild(skeleton);
        }
    }

    /**
     * ایجاد یک skeleton element
     */
    createSkeleton(type) {
        const div = document.createElement('div');
        
        switch (type) {
            case 'text':
                div.className = 'skeleton skeleton-text';
                break;
            case 'text-large':
                div.className = 'skeleton skeleton-text large';
                break;
            case 'avatar':
                div.className = 'skeleton skeleton-avatar';
                break;
            case 'image':
                div.className = 'skeleton skeleton-image';
                break;
            case 'button':
                div.className = 'skeleton skeleton-button';
                break;
            case 'card':
                div.innerHTML = `
                    <div class="skeleton skeleton-image sm"></div>
                    <div class="skeleton skeleton-text" style="width: 80%;"></div>
                    <div class="skeleton skeleton-text" style="width: 60%;"></div>
                `;
                break;
            default:
                div.className = 'skeleton skeleton-text';
        }
        
        return div;
    }

    /**
     * نمایش loading bar در بالای صفحه
     */
    showLoadingBar() {
        const bar = document.createElement('div');
        bar.className = 'skeleton-loading-bar';
        bar.id = 'loading-bar';
        document.body.insertBefore(bar, document.body.firstChild);
    }

    /**
     * پنهان کردن loading bar
     */
    hideLoadingBar() {
        const bar = document.getElementById('loading-bar');
        if (bar) {
            bar.style.opacity = '0';
            bar.style.transition = 'opacity 0.3s ease';
            setTimeout(() => bar.remove(), 300);
        }
    }

    /**
     * نمایش overlay loading
     */
    showOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'skeleton-overlay';
        overlay.id = 'skeleton-overlay';
        overlay.innerHTML = `
            <div>
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">در حال بارگذاری...</span>
                </div>
                <p style="margin-top: 1rem; text-align: center;">درحال بارگذاری...</p>
            </div>
        `;
        document.body.appendChild(overlay);
        this.isLoading = true;
    }

    /**
     * پنهان کردن overlay loading
     */
    hideOverlay() {
        const overlay = document.getElementById('skeleton-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.transition = 'opacity 0.3s ease';
            setTimeout(() => overlay.remove(), 300);
        }
        this.isLoading = false;
    }

    /**
     * شبیه سازی بارگذاری
     */
    simulateLoad(duration = 2000) {
        this.showLoadingBar();
        setTimeout(() => {
            this.hideLoadingBar();
        }, duration);
    }
}

// ایجاد instance جهانی
const skeletonLoader = new SkeletonLoader();

/**
 * نمایش skeleton هنگام شروع صفحه (اگر اینترنت کند است)
 */
window.addEventListener('load', () => {
    // صفحه بارگذاری شد
});

/**
 * نمایش skeleton قبل از بارگذاری
 */
document.addEventListener('DOMContentLoaded', () => {
    // اگر صفحه کند لود شد، skeleton نمایش می‌دهد
});

/**
 * برای Fetch requests
 */
function fetchWithSkeleton(url, elementId, skeletonType = 'text') {
    skeletonLoader.showSkeleton(elementId, skeletonType);
    skeletonLoader.showLoadingBar();
    
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            skeletonLoader.hideLoadingBar();
            return data;
        })
        .catch(error => {
            skeletonLoader.hideLoadingBar();
            console.error('Error:', error);
        });
}

/**
 * برای AJAX requests (jQuery)
 */
function ajaxWithSkeleton(options) {
    skeletonLoader.showLoadingBar();
    
    const defaultOptions = {
        complete: function() {
            skeletonLoader.hideLoadingBar();
        }
    };
    
    return $.ajax({...defaultOptions, ...options});
}
