document.getElementById('ocr_manual').addEventListener('click', function () {
    const fileInput = document.getElementById('document_image');
    const selectedFile = fileInput.files[0];

    if (selectedFile) {

        let reader = new FileReader();
        reader.addEventListener("load", function () {
            window.src = reader.result;
            $('#document_image').val();
        }, false);
        reader.readAsDataURL(selectedFile);
    }
});

let cropper;

$('#ManualScanImageModal').on('shown.bs.modal', function () {
    let width = document.getElementById('crop-image-container').offsetWidth - 20;
    let height = width * 1.2; // Set the height to be 50% of the width
    $('#crop-image-container').height(height + 'px');
    cropper = $('#crop-image-container').croppie({
        viewport: {
            width: width,
            height: height // Set the height to be 50% of the width
        },
    });
    $('.cr-slider-wrap').remove();
    $('.modal-body1').height(document.getElementById('crop-image-container').offsetHeight + 5 + 'px');
    cropper.croppie('bind', {
        url: window.src,
    }).then(function () {
        cropper.croppie('setZoom', 0);
    });
});

//destroy the rendered image in the modal croppie 
$('#ManualScanImageModal').on('hidden.bs.modal', function () {
    cropper.croppie('destroy');
});

$(document).on('click', '#crop_customOcr', function (ev) {
    // Getting the cropped image using Croppie and converting it to a Blob
    cropper.croppie('result', {
        type: 'blob',
        format: 'jpeg',
        size: 'original'
    }).then(function (blob) {
        const button = $('#crop_customOcr');
        button.text("Scanning...");
        // Creating a FormData object 
        let formData = new FormData();
        formData.append('document_image', blob, 'cropped_image.jpg');
        // Appending 'iterationsMorph' value to the formData

        $.ajax({
            url: '/scanner',
            type: 'POST',
            data: formData,
            processData: false,  // Tell jQuery not to process the data
            contentType: false,  // Tell jQuery not to set contentType
            headers: { 'X-CSRFToken': '{{ csrf_token() }}' },
            success: function (data) {
                if (data === 'No file uploaded') {
                    showToast('No file uploaded!', 'Please try again.', 'fc-orange fa-solid fa-circle-check', 'border-danger');
                    new bootstrap.Toast(document.querySelector('#add_userToast')).show();
                }
                else {
                    if (data.length > 0) {
                        populateResults(data);
                        showToast('Success!', 'OCR result.', 'fc-green fa-solid fa-circle-check', 'border-success');
                        new bootstrap.Toast(document.querySelector('#add_userToast')).show();
                    } else {
                        let modal = new bootstrap.Modal(document.getElementById('error_ocr'));
                        modal.show();
                    }
                }
            },
            error: function (error) {
                console.error(error);
                let modal = new bootstrap.Modal(document.getElementById('error_ocr'));
                modal.show();
            }
        });
    });
});