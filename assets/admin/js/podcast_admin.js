document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('#id_audio_file');
    if (!input) return;

    const maxSize = 30 * 1024 * 1024;
    const allowedExtensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'];

    function removeOldInfo() {
        const oldInfo = input.parentElement.querySelector('.podcast-upload-info');
        if (oldInfo) oldInfo.remove();
    }

    input.setAttribute('accept', 'audio/*,.mp3,.wav,.ogg,.m4a,.flac,.aac');

    input.addEventListener('change', function () {
        removeOldInfo();
        const file = input.files && input.files[0];
        if (!file) return;

        const ext = '.' + file.name.split('.').pop().toLowerCase();
        const sizeMb = file.size / (1024 * 1024);
        const info = document.createElement('div');
        info.className = 'podcast-upload-info';

        const errors = [];
        if (!allowedExtensions.includes(ext)) {
            errors.push('فقط فایل صوتی مجاز است.');
        }
        if (file.size > maxSize) {
            errors.push('حجم فایل نباید بیشتر از ۳۰ مگابایت باشد.');
        }

        info.innerHTML = `
            <span>نام فایل: ${file.name}</span>
            <span>حجم: ${sizeMb.toFixed(2)} MB</span>
            <span>فرمت: ${ext}</span>
            ${errors.length ? `<div class="podcast-upload-error">${errors.join(' ')}</div>` : '<div class="podcast-upload-warning">فایل از نظر اولیه قابل قبول است.</div>'}
        `;
        input.parentElement.appendChild(info);

        if (errors.length) {
            input.value = '';
        }
    });
});
