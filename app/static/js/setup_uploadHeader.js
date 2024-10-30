let collegesArray;
let collegeSelect, courseSelect, unitsSelect, yearLevelSelect;
let emptyOption = '<option value=""> </option>';
let zeroOption = '<option value="0"> </option>';
collegeSelect = document.getElementById('document_college');
courseSelect = document.getElementById('document_course');
unitsSelect = document.getElementById('document_subject_type');
yearLevelSelect = document.getElementById('document_yearLevel');

// Use collegeSelect, courseSelect, unitsSelect, and yearLevelSelect as needed
function populateCollege(colleges) {
    collegeSelect.innerHTML = emptyOption;
    courseSelect.innerHTML = emptyOption;

    colleges.forEach(college => {
        let collegeOption = `<option value="${college.college_id}">${college.college_name}</option>`;
        collegeSelect.innerHTML += collegeOption;
        coursesArray = [];
    });
}

function selectCollege(selectedCollegeId) {
    courseSelect.innerHTML = emptyOption;
    if (selectedCollegeId) {
        const selectedCollege = collegesArray.find(college => college.college_id === selectedCollegeId);
        selectedCollege.courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.course_id;
            option.textContent = course.course_name;
            courseSelect.appendChild(option);
        });
    }
}

collegeSelect.addEventListener('change', () => {
    const selectedCollegeId = parseInt(collegeSelect.value);
    selectCollege(selectedCollegeId);
});

function populateUnits(units) {
    unitsSelect.innerHTML = zeroOption;

    units.forEach(units => {
        let unitsOption = `<option value="${units.id}">${units.unit_abbrev}</option>`;
        unitsSelect.innerHTML += unitsOption;
    });
}

function populateYearLevel(academic_year_level) {
    yearLevelSelect.innerHTML = zeroOption;

    academic_year_level.forEach(year_item => {
        let year_levelOption = `<option value="${year_item.id}">${year_item.description}</option>`;
        yearLevelSelect.innerHTML += year_levelOption;
    });
}

function getCollege() {
    fetch('/fetch_selector/all')
        .then(response => response.json())
        .then(data => {
            collegesArray = data.college_courses;
            populateCollege(data.college_courses);
            populateUnits(data.units);
            populateYearLevel(data.year_level);
        })
        .catch(error => {
            console.error('Error fetching colleges:', error);
        });
}

getCollege();