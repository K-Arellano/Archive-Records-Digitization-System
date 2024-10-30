function populateList(index, surname, fname, midname, sfxname, student_wer, student_cer, tbody) {
    index = parseInt(index);
    var row = tbody.insertRow(-1) // Insert a new row at the end of the table

    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    var cell5 = row.insertCell(4);
    var cell6 = row.insertCell(5);
    var cell7 = row.insertCell(6);
    var cell8 = row.insertCell(7);

    cell1.innerHTML = `<div class="text-center p-2 fs-def"><input type="checkbox" class="checkbox form-check-input m-auto" id="${index}"></div>`;
    cell2.innerHTML = `<input type="text" class="form-control w-full text-truncate fs-medium" id="student_surname" name="student_surname" value="${surname}" placeholder = "${surname}" onkeyup = "checkAccuracyData()"> `; // Last Name
    cell3.innerHTML = `<input type="text" class="form-control w-full text-truncate fs-medium" id="student_firstname" name="student_firstname" value="${fname}" placeholder = "${fname}" onkeyup = "checkAccuracyData()"> `; // First Name
    cell4.innerHTML = `<input type="text" class="form-control text-truncate text-center fs-medium" id="student_middlename" name="student_middlename" maxlength="1" value="${midname}" placeholder = "${midname}" onkeyup = "checkAccuracyData()"> `; // MI
    cell5.innerHTML = `<input type="text" class="form-control text-truncate text-center fs-medium" id="student_suffixname" name="student_suffixname" maxlength="4" value="${sfxname}" placeholder = "${sfxname}" onkeyup = "checkAccuracyData()"> `; // Suffix
    cell6.innerHTML = `<input type="text" class="form-control text-truncate text-center fs-medium" id="student_wer" name="student_wer" value="${student_wer}" placeholder = "${student_wer}" disabled> `; // wer
    cell7.innerHTML = `<input type="text" class="form-control text-truncate text-center fs-medium" id="student_cer" name="student_cer" value="${student_cer}" placeholder = "${student_cer}" disabled> `; // cer

    cell8.innerHTML = `<button class="text-center border-0 bg-transparent w-full updateERRperDelete fs-medium no-border-button" id="deleteButton${index}"
     data-bs-placement="left" data-bs-trigger="hover" data-bs-html="true"
                                            title="Remove this row"
                                            ><span class="fa-solid fa-square-minus"></span></button>`; // Button

    (function (row) {
        cell8.querySelector(`#deleteButton${index}`).addEventListener('click', function () {
            row.style.transition = 'opacity 250ms ease-out';
            row.style.opacity = '0';

            setTimeout(function () {
                setTimeout(function () {
                    row.remove();
                    checkAccuracyData();
                }, 100);
            }, 250);
        });
    })(row);
}

function addRows(count) {
    var table = document.getElementById('studentList');
    var tbody = table.getElementsByTagName('tbody')[0]; // Get the tbody element
    var startingIndex = 0;

    // Check if tbody has existing rows
    if (tbody.rows.length !== 0) {
        // Get the last row in the tbody
        var lastRow = tbody.rows[tbody.rows.length - 1];
        // Find the id of the last checkbox
        var checkbox = lastRow.querySelector('input[type="checkbox"]');
        var lastCheckboxId = parseInt(checkbox.id);

        startingIndex = lastCheckboxId + 1;
    }

    for (var i = 0; i < count; i++) {
        populateList(startingIndex + i, "", "", "", "", "100.00%", "100.00%", tbody);
    }
}

function checkForEmptyTable() {
    var tbodyIsEmpty = document.querySelector('tbody').childElementCount === 0;
    if (tbodyIsEmpty) {
        addRows(20);
    }
}

function clearEmptyRows() {
    var table = document.getElementById('studentList');
    var tbody = table.getElementsByTagName('tbody')[0];
    var rows = tbody.getElementsByTagName('tr');

    for (var i = rows.length - 1; i >= 0; i--) {
        var row = rows[i];
        let surnameInput = row.querySelector('input[name="student_surname"]');
        let firstnameInput = row.querySelector('input[name="student_firstname"]');

        // Check if both surname and firstname are empty
        if (surnameInput.value.trim() === "" && firstnameInput.value.trim() === "") {
            row.remove();
        }
    }
}

function noSelectedData(event, message, buttonFunction) {
    let messageErrorTools = document.getElementById('errorContainerTools');
    messageErrorTools.innerHTML = ''; // Clear any existing content

    messageErrorTools.innerHTML = `
        <div class="modal-body">
            <div class="">
                <h5 class="fw-bold mb-3"> Oops! No rows selected </h5>
                <p class=""> Please choose one or more rows to ${event}. ${message} </p>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" data-bs-dismiss="modal" class="button fs-medium fw-medium px-4 me-3">Close</button>
            <button onclick="${buttonFunction}" class="button btn-orange fs-medium fw-medium px-4" data-bs-dismiss="modal">
                Confirm
            </button>
        </div>
    `;

    $('#selection_uploadTools').modal('show'); // Show the modal
}

function removeRows(removeAll) {
    if (removeAll) {
        document.querySelectorAll('tbody tr').forEach(row => row.remove()); // Remove all rows
        showToast('Success!', 'All rows removed successfully.', 'fc-green fa-solid fa-circle-check', 'border-success');
    } else {
        const checkboxes = document.querySelectorAll('tbody .checkbox:checked');

        checkboxes.forEach(checkbox => {
            checkbox.closest('tr').remove();
        });
        showToast('Success!', 'Removed selected rows successfully.', 'fc-green fa-solid fa-circle-check', 'border-success');
    }
    checkForEmptyTable()
    new bootstrap.Toast(document.querySelector('#add_userToast')).show();
}

function clearTextRows(clearAll) {
    if (clearAll) {
        document.querySelectorAll('tbody input[type="text"]').forEach(input => {
            input.value = ''; // Clear all input fields
        });
        showToast('Success!', 'All input fields cleared successfully.', 'fc-green fa-solid fa-circle-check', 'border-success');
    } else {
        const checkboxes = document.querySelectorAll('tbody .checkbox:checked');

        checkboxes.forEach(checkbox => {
            const inputFields = checkbox.closest('tr').querySelectorAll('input[type="text"]');
            inputFields.forEach(input => {
                input.value = ''; // Clear individual row input fields
            });
        });
        showToast('Success!', 'Cleared selected rows input fields successfully.', 'fc-green fa-solid fa-circle-check', 'border-success');
    }

    document.querySelectorAll('.checkbox').forEach(checkbox => {
        checkbox.checked = false; // Clear all input fields
    });

    new bootstrap.Toast(document.querySelector('#add_userToast')).show();
}

function handleRemoveOrClear(event) {
    var checkboxes = document.querySelectorAll('tbody .checkbox:checked');
    var selectAll = document.querySelector('#select-all');

    if (checkboxes.length === 0) {
        if (event.target.id === 'removeButton') {
            $('#deleteSelctedList_confirmation').modal('hide');
            noSelectedData('remove', '  Remove all rows instead?', 'removeRows(true)');
        } else if (event.target.id === 'clearButton') {
            $('#clearSelctedList_confirmation').modal('hide');
            noSelectedData('clear', '  Clear all rows instead?', 'clearTextRows(true)');
        }
    } else {
        if (event.target.id === 'removeButton') {
            removeRows(false);
        } else if (event.target.id === 'clearButton') {
            clearTextRows(false);
        }
    }

    selectAll.checked = false;
    checkForEmptyTable();
}

// Event listener for the "Select All" checkbox
document.querySelector('#select-all').addEventListener('change', function () {
    var checkboxes = document.querySelectorAll('.checkbox');

    // If "Select All" checkbox is checked, check all other checkboxes
    if (this.checked) {
        checkboxes.forEach(function (checkbox) {
            checkbox.checked = true;
        });
    } else {
        // If "Select All" checkbox is unchecked, uncheck all other checkboxes
        checkboxes.forEach(function (checkbox) {
            checkbox.checked = false;
        });
    }
});

// Event listener for individual checkboxes
document.querySelectorAll('tbody .checkbox').forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
        // If any individual checkbox is unchecked, uncheck the "Select All" checkbox
        var selectAllCheckbox = document.querySelector('#select-all');
        if (!this.checked) {
            selectAllCheckbox.checked = false;
        }

        var allCheckboxes = document.querySelectorAll('tbody .checkbox');
        var allChecked = Array.from(allCheckboxes).every(function (checkbox) {
            return checkbox.checked;
        });

        document.querySelector('#select-all').checked = allChecked;
    });
});

function populateResults(students) {
    var table = document.getElementById('studentList');
    var tbody = table.getElementsByTagName('tbody')[0];
    clearEmptyRows();

    if (students.length > 0) {
        students.forEach(function (student, index) {
            var isDuplicate = false;
            tbody.querySelectorAll('tr').forEach(function (row) {
                var surname = row.querySelector('[name="student_surname"]').value;
                var firstname = row.querySelector('[name="student_firstname"]').value;
                var middlename = row.querySelector('[name="student_middlename"]').value;
                var suffixname = row.querySelector('[name="student_suffixname"]').value;

                if (surname == student.surname &&
                    firstname === student.firstname &&
                    middlename === student.middlename &&
                    suffixname === student.suffix) {
                    isDuplicate = true;
                    return;
                }
            });

            if (!isDuplicate) {
                populateList(index, student.surname.trim(), student.firstname.trim(), student.middlename.trim(), student.suffix.trim(), "0.00%", "0.00%", tbody);
            }
        });
    }
}

function populateErrorRate(errorRates) {
    var table = document.getElementById('studentList');
    var tbody = table.getElementsByTagName('tbody')[0];

    if (errorRates.length > 0) {
        errorRates.forEach(function (errorRate) {
            tbody.querySelectorAll('tr').forEach(function (row) {
                if (errorRate.id === parseInt(row.querySelector('.checkbox').id)) {
                    row.querySelector('[name="student_wer"]').value = errorRate.wer.toFixed(2) + '%';
                    row.querySelector('[name="student_cer"]').value = errorRate.cer.toFixed(2) + '%';
                }
            });
        });
    }
}

addRows(20);

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('populateInputs').onclick = function () {
        addRows(1);
        checkAccuracyData();
    }
    document.querySelector('#removeButton').addEventListener('click', handleRemoveOrClear);
    document.querySelector('#clearButton').addEventListener('click', handleRemoveOrClear);
});