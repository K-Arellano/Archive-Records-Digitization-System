let hasUnsavedChanges = false;
let nextUrl = '';

function userchanges(status) {
    hasUnsavedChanges = status;
}

function checkAllInputs() {
    // Select all relevant input fields
    const inputs = document.querySelectorAll('input[type="text"], input[type="number"], input[type="file"]');
    let allEmpty = true;

    // Check each input
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].type === 'file') {
            if (inputs[i].files.length > 0) {
                allEmpty = false;
                break;
            }
        } else {
            if (inputs[i].value.trim() !== '') {
                allEmpty = false;
                break;
            }
        }
    }

    userchanges(!allEmpty);
}

// Add event listeners to input fields
const inputs = document.querySelectorAll('input[type="text"], input[type="number"], input[type="file"]');
inputs.forEach(input => {
    input.addEventListener('input', checkAllInputs);
});

// Capture link clicks
document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', function (event) {
        if (hasUnsavedChanges) {
            event.preventDefault(); // Prevent default action
            nextUrl = this.href; // Save the URL
            const modal = new bootstrap.Modal(document.getElementById('onExitPage'));
            modal.show();
        }
    });
});

// Handle the "Stay" button
document.getElementById('cancel_discard').addEventListener('click', function () {
    hasUnsavedChanges = true; // Keep unsaved changes status
});

// Handle the "Leave" button
document.getElementById('continue_discard').addEventListener('click', function () {
    hasUnsavedChanges = false; // Reset unsaved changes status
    window.location.href = nextUrl; // Navigate to the saved URL
});

// Handle the case when the user tries to close the tab or navigate away
window.addEventListener('beforeunload', function (event) {
    if (hasUnsavedChanges) {
        event.preventDefault();
        event.returnValue = ''; // For modern browsers
    }
});
