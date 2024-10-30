const dropzone = document.getElementById('dropzone');
const documentImageInput = document.getElementById('document_image');
const previewContainer = document.getElementById('previewContainer');
const preview = document.getElementById('preview');
const dragText = document.getElementById('dragText');
const ocr_button = document.getElementById('submitOCR');
const save_button = document.getElementById('continueButton');
let image_saved = false;

dropzone.addEventListener('click', () => {
    if (!image_saved) {
        documentImageInput.click();
    }
});

documentImageInput.addEventListener('change', handleFiles);

dropzone.addEventListener('dragover', (e) => {
    if (!image_saved) {
        e.preventDefault();
        dropzone.classList.add('dragging');
    }
});

dropzone.addEventListener('dragleave', () => {
    if (!image_saved) {
        dropzone.classList.remove('dragging');
    }
});

dropzone.addEventListener('drop', (e) => {
    if (!image_saved) {
        e.preventDefault();
        dropzone.classList.remove('dragging');
        const files = e.dataTransfer.files;
        if (files.length) {
            handleFiles({ target: { files } });
        }
    }
});

function handleFiles(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            previewContainer.classList.remove('d-none');
            save_button.classList.remove('d-none');
            dragText.classList.add('d-none');
        };
        reader.readAsDataURL(file);
    }
}

cancel_image.addEventListener('click', function (event) {
    event.stopPropagation();
    preview.src = '';
    ocr_button.classList.add('d-none');
    save_button.classList.add('d-none');
    previewContainer.classList.add('d-none');
    dragText.classList.remove('d-none');
    documentImageInput.value = '';
    image_saved = false;
});

function saveImage() {
    image_saved = true;
    ocr_button.classList.remove('d-none');
    save_button.classList.add('d-none');
}

continueButton.addEventListener('click', function (event) {
    event.stopPropagation();
    saveImage();
});