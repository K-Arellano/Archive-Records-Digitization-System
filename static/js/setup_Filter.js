let collegesArray;

const collegeSelector = document.getElementById('filterCollege');
const courseSelect = document.getElementById('filterCourse');
const yearLevelSelect = document.getElementById('filterYear');

function populateCollege(colleges) {
    collegeSelector.innerHTML = '<option value = ""> College </option>';
    courseSelect.innerHTML = '<option value = ""> Course </option>';

    colleges.forEach(college => {
        let collegeOption = `<option value="${college.college_name}">${college.college_name}</option>`;
        collegeSelector.innerHTML += collegeOption;
    });
}

function selectCollege(selectedCollegeName) {
    courseSelect.innerHTML = '<option value=""> Course </option>';
    const college_pointer = collegesArray.find(college => college.college_name === selectedCollegeName);
    college_pointer.courses.forEach(course => {
        const option = document.createElement('option');
        option.value = course.course_name;
        option.textContent = course.course_name;
        courseSelect.appendChild(option);
    });
}

collegeSelector.addEventListener('change', () => {
    const college_selector = collegeSelector.value;
    selectCollege(college_selector);
});

function populateYearLevel(academic_year_level) {
    yearLevelSelect.innerHTML = '<option value=""> Year Level </option>';

    academic_year_level.forEach(year_item => {
        let year_levelOption = `<option value="${year_item.description}">${year_item.description}</option>`;
        yearLevelSelect.innerHTML += year_levelOption;
    });
}

function editPopulateSelector(data, documentsData) {
    const edit_collegeSelector = document.getElementById('update_documentCollege');
    const edit_courseSelect = document.getElementById('update_documentCourse');
    const edit_year_level = document.getElementById('update_documentYear_level');
    const edit_units = document.getElementById('update_documentUnit');
    let temp_collegesArray = data.college_courses;

    function edit_populateCollege(colleges) {
        edit_collegeSelector.innerHTML = '<option value = ""> College </option>';
        edit_courseSelect.innerHTML = '<option value = ""> Course </option>';

        colleges.forEach(college => {
            let edit_collegeText = '(' + college.college_name + ') ' + college.college_description;
            let edit_collegeOption = `<option value="${college.college_id}" ${documentsData.college === college.college_id ? 'selected' : ''} >${edit_collegeText }</option>`;
            edit_collegeSelector.innerHTML += edit_collegeOption;
        });
    }

    function setCoursesUpdate(selectedCollegeid, selectedCourseID) {
        const selected_college_id = parseInt(selectedCollegeid);
        edit_courseSelect.innerHTML = '<option value=""> </option>';

        const selectedCollege = collegesArray.find(college => college.college_id === selected_college_id);
        if (selectedCollege) {
            selectedCollege.courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course.course_id;
                option.textContent = '(' + course.course_name + ') ' + course.course_description;
                if (selectedCourseID !== 0) {
                    if (course.course_id === selected_college_id) {
                        option.selected = true;
                    }
                }
                edit_courseSelect.appendChild(option);
            });
        }
    }

    function editDocument_populateUnits(units) {
        edit_units.innerHTML = `<option value="0" ${documentsData.unit === 0 ? 'selected' : ''} >  </option>`;

        units.forEach(units_item => {
            let unitsOption = `<option value="${units_item.id}" ${documentsData.unit === units_item.id ? 'selected' : ''} >${units_item.unit_abbrev}</option>`;
            edit_units.innerHTML += unitsOption;
        });
    }

    function editDocument_populateYearLevel(academic_year_level) {
        edit_year_level.innerHTML = `<option value="0" ${documentsData.year_level === 0 ? 'selected' : ''} >  </option>`;

        academic_year_level.forEach(year_item => {
            let year_levelOption = `<option value="${year_item.id}" ${documentsData.year_level === year_item.id ? 'selected' : ''} >${year_item.description}</option>`;
            edit_year_level.innerHTML += year_levelOption;
        });
    }

    if (edit_collegeSelector && edit_courseSelect && edit_year_level && edit_units) {
        edit_populateCollege(data.college_courses);
        editDocument_populateUnits(data.units);
        editDocument_populateYearLevel(data.year_level);

        setCoursesUpdate(documentsData.college, documentsData.course);
        edit_collegeSelector.addEventListener('change', () => {
            const edit_college_selector = edit_collegeSelector.value;
            setCoursesUpdate(edit_college_selector, 0);
        });
    }

}

function updateHeader(documentsData) {
    fetch('/fetch_selector/all')
        .then(response => response.json())
        .then(data => {
            editPopulateSelector(data, documentsData);
        })
        .catch(error => {
            console.error('Error fetching colleges:', error);
        });
}

function updateFilter() {
    fetch('/fetch_selector/all')
        .then(response => response.json())
        .then(data => {
            collegesArray = data.college_courses;
            populateCollege(data.college_courses);
            populateYearLevel(data.year_level);
            editPopulateSelector(data);
        })
        .catch(error => {
            console.error('Error fetching colleges:', error);
        });
}

updateFilter();