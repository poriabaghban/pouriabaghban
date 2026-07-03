/**
 * Skills Progress Bar Animation
 * نوار پیشرفت مهارت‌ها با انیمیشن
 */

document.addEventListener('DOMContentLoaded', function() {
    // انتظار تا IntersectionObserver قابل دسترسی باشد
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    // شروع انیمیشن progress bar
                    const skillsAnimation = entry.target;
                    const progressBars = skillsAnimation.querySelectorAll('.progress-bar');
                    
                    progressBars.forEach(function(progressBar) {
                        const parentDiv = progressBar.closest('.progress');
                        const skillDiv = parentDiv.querySelector('.skill');
                        
                        if (skillDiv) {
                            const valElement = skillDiv.querySelector('.val');
                            if (valElement) {
                                // استخراج درصد از textContent (مثل: "95%")
                                const percentage = parseInt(valElement.textContent);
                                
                                // تنظیم CSS variable برای width
                                progressBar.style.setProperty('--progress-width', percentage + '%');
                                
                                // فعال کردن انیمیشن
                                progressBar.style.animation = 'none';
                                // Trigger reflow
                                void progressBar.offsetWidth;
                                progressBar.style.animation = 'fillProgressBar 1.5s ease-in-out forwards';
                            }
                        }
                    });
                    
                    // از مراقبت صفحه درخواست کنید
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        // مراقبت از تمام عناصر skills-animation
        const skillsAnimationElements = document.querySelectorAll('.skills-animation');
        skillsAnimationElements.forEach(function(el) {
            observer.observe(el);
        });
    } else {
        // اگر IntersectionObserver در دسترس نیست، انیمیشن فوری اجرا شود
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(function(progressBar) {
            const parentDiv = progressBar.closest('.progress');
            const skillDiv = parentDiv.querySelector('.skill');
            
            if (skillDiv) {
                const valElement = skillDiv.querySelector('.val');
                if (valElement) {
                    const percentage = parseInt(valElement.textContent);
                    progressBar.style.width = percentage + '%';
                }
            }
        });
    }
});
