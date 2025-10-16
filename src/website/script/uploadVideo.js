const form = document.getElementById('uploadForm');
const progressText = document.getElementById('progressText');

form.addEventListener('submit', function(event) {
    event.preventDefault(); // prevent normal form submit

    const fileInput = form.querySelector('input[type="file"]');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('videoFile', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/file/upload', true);

    let startTime = Date.now();

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            const uploadedMB = (e.loaded / (1024 * 1024)).toFixed(2);
            const totalMB = (e.total / (1024 * 1024)).toFixed(2);
            const percent = Math.round((e.loaded / e.total) * 100);

            const elapsedSec = (Date.now() - startTime) / 1000;
            const speed = (e.loaded / (1024 * 1024) / elapsedSec).toFixed(2); // MB/s

            progressText.textContent = `Uploading: ${uploadedMB} MB / ${totalMB} MB (${percent}%) at ${speed} MB/s`;
        }
    };

    xhr.onload = function() {
        if (xhr.status === 200) {
            progressText.textContent = `Upload complete ✅ (${(file.size/(1024*1024)).toFixed(2)} MB)`;
        } else {
            progressText.textContent = 'Upload failed ❌';
        }
    };

    xhr.onerror = function() {
        progressText.textContent = 'Upload error ❌';
    };

    xhr.send(formData);
});
