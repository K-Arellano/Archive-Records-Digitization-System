let documentDetails = {
    academicYear: '',
    college: '',
    course: '',
    yearLevel: '',
    section: '',
    subjectName: '',
    subjectType: '',
    semester: '',
    pageNum: '',
};

function updateDocumentName(document_filename) {
    let allEmpty = Object.values(documentDetails).every(function (value) {
        return value.trim() === '';
    });

    if (allEmpty) {
        $(document_filename).val("");

    } else {
        let colcourse = documentDetails.college && documentDetails.course
            ? documentDetails.college + '-' + documentDetails.course
            : (documentDetails.college || documentDetails.course);

        let year_level = documentDetails.yearLevel !== "0" && documentDetails.section
            ? documentDetails.yearLevel + documentDetails.section
            : (documentDetails.yearLevel !== "0" && documentDetails.section === "")
                ? documentDetails.yearLevel
                : '';

        let subject = documentDetails.subjectName && documentDetails.subjectType
            ? documentDetails.subjectName + (documentDetails.subjectType === "1"
                ? '_LECT'
                : documentDetails.subjectType === "2"
                    ? '_LAB'
                    : '')
            : '';

        let academic_year = documentDetails.semester !== "0" && documentDetails.academicYear
            ? documentDetails.semester + '_' + documentDetails.academicYear
            : documentDetails.semester !== "0"
                ? documentDetails.semester
                : documentDetails.academicYear || '';


        let combination1 = colcourse && year_level
            ? colcourse + '-' + year_level
            : colcourse && year_level === ""
                ? colcourse
                : colcourse === "" && year_level
                    ? year_level
                    : '';

        let combination2 = academic_year && subject
            ? academic_year + '_' + subject
            : subject === "" && academic_year
                ? academic_year
                : subject && academic_year === ""
                    ? subject
                    : '';

        let doc_name = combination1 !== "" && combination2 !== ""
            ? combination1 + '_' + combination2
            : combination1 || combination2 || '';


        doc_name += combination1 !== "" || combination2 !== "" ?
            '_pg-' + String(documentDetails.pageNum) :
            '';

        $(document_filename).val(doc_name);
    }
}

function updateObject(college, course, year_level, section, subject, unit, semester, starting_year, ending_year, pageNum) {
    documentDetails = {
        college: $(college + ' option:selected').text(),
        course: $(course + ' option:selected').text(),
        yearLevel: $(year_level + ' option:selected').val(),
        section: $(section).val() ? $(section).val().replace(/\s+/g, '') : '',
        subjectName: $(subject).val(),
        subjectType: $(unit + ' option:selected').val(),
        semester: $(semester + ' option:selected').text() ? $(semester + ' option:selected').text().replace(/\s+/g, '') : '',
        academicYear: $(starting_year).val() && $(ending_year).val() ? $(starting_year).val() + '-' + $(ending_year).val() : '',
        pageNum: $(pageNum + ' option:selected').text(),
    };
}

function updateObjectEdit(college, course, year_level, section, subject, unit, semester, starting_year, ending_year, pageNum) {
    documentDetails = {
        college: $(college + ' option:selected').text().match(/\((.*?)\)/)?.[1] || '',
        course: $(course + ' option:selected').text().match(/\((.*?)\)/)?.[1] || '',
        yearLevel: $(year_level + ' option:selected').val(),
        section: $(section).val() ? $(section).val().replace(/\s+/g, '') : '',
        subjectName: $(subject).val(),
        subjectType: $(unit + ' option:selected').val(),
        semester: $(semester + ' option:selected').text() ? $(semester + ' option:selected').text().replace(/\s+/g, '') : '',
        academicYear: $(starting_year).val() && $(ending_year).val() ? $(starting_year).val() + '-' + $(ending_year).val() : '',
        pageNum: $(pageNum + ' option:selected').text(),
    };
}

function updateYearStart(startingYearInput, endingYearInput) {
    const startingYear = parseInt(startingYearInput.value);
    if (!isNaN(startingYear)) {
        endingYearInput.value = (startingYear + 1).toString();
    }
}
function updateYearEnd(startingYearInput, endingYearInput) {
    const endingYear = parseInt(endingYearInput.value);
    if (!isNaN(endingYear)) {
        startingYearInput.value = (endingYear - 1).toString();
    }
}

function enforceMaxLength(inputElement, maxLength) {
    var currentDate = new Date();
    currentYear = currentDate.getFullYear();
    // Check if the current value exceeds the maxLength
    if (inputElement.value.length > maxLength) {
        // If so, slice the value to the maxLength
        inputElement.value = inputElement.value.slice(0, maxLength);
    }

    if ((Number(inputElement.value) < inputElement.min || Number(inputElement.value) >= currentYear + 2) && inputElement.value.length === maxLength) {
        inputElement.classList.add("is-invalid");
    } else {
        inputElement.classList.remove("is-invalid");
    }
}

const customStartingYearInput = document.getElementById('starting_year');
const customEndingYearInput = document.getElementById('ending_year');

if (customStartingYearInput && customEndingYearInput) {
    // Event listener for starting year input
    customStartingYearInput.addEventListener('input', function () {
        enforceMaxLength(customStartingYearInput, 4);
        updateYearStart(customStartingYearInput, customEndingYearInput);
    });

    // Event listener for ending year input
    customEndingYearInput.addEventListener('input', function () {
        enforceMaxLength(customEndingYearInput, 4);
        updateYearEnd(customStartingYearInput, customEndingYearInput);
    });
}

$("#document_college, #document_course, #document_yearLevel, #document_subject_type, #document_semester").change(function () {
    updateObject('#document_college', '#document_course', '#document_yearLevel', '#course_section', '#document_subject_name', '#document_subject_type', '#document_semester', '#starting_year', '#ending_year', '#document_page');
    updateDocumentName('#document_filename');
});

$("#course_section, #document_subject_name, #starting_year, #ending_year").on('input', function () {
    updateObject('#document_college', '#document_course', '#document_yearLevel', '#course_section', '#document_subject_name', '#document_subject_type', '#document_semester', '#starting_year', '#ending_year', '#document_page');
    updateDocumentName('#document_filename');
});