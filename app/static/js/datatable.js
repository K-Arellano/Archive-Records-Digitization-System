$(document).ready(function () {
    var recordsDataTable = $('#recordsTable').DataTable({
        stripeClasses: [],
        language: {
            paginate: {
                previous: '<a class="fa-solid fa-caret-left"></a>',
                next: '<a class="fa-solid fa-caret-right"></a>',
            }
        },
        'processing': true,
        'responsive': true,
        'serverSide': true,
        'serverMethod': 'post',
        'ajax': {
            'url': '/records_data',
            'headers': { 'X-CSRFToken': '{{ csrf_token() }}' },
            'data': function (data) {
                data.filterSearch = $('#filterSearch').val();
                data.filterCollege = $('#filterCollege').val();
                data.filterCourse = $('#filterCourse').val();
                data.filterSemester = $('#filterSemester').val();
                data.filterYear = $('#filterYear').val();
            }
        },
        'lengthMenu': [[25, 50, 100, 10000], [25, 50, 100, "All"]],
        'columns': [
            { data: 'id', orderable: true, className: 'bg-transparent' },
            { data: 'FullName', orderable: true, className: 'text-truncate' },
            { data: 'College', orderable: true, className: 'text-center' },
            { data: 'Course', orderable: true, className: 'text-center' },
            { data: 'Section', orderable: true, className: 'text-center' },
            { data: 'Subject', orderable: false, className: 'text-truncate' },
            { data: 'Unit', orderable: false, className: 'text-center' },
            { data: 'Semester', orderable: false, className: 'text-center' },
            { data: 'SchoolYear', orderable: true, className: 'text-center' },
            {
                'data': 'id',
                title: 'Action',
                wrap: true,
                orderable: false,
                "render": function (data, type, row) {
                    const viewIcon = '<span class="fa-solid fa-eye"></span>'
                    const editIcon = '<span class="fa-solid fa-pen"></span>'
                    const deleteIcon = '<span class="fa-solid fa-trash"></span>'

                    const viewLink = '<a id="viewThis" onclick= "viewImage(' + data + ')">' + viewIcon + '</a>';
                    const editLink = '<a id="editThis" onclick= "editRecord(' + data + ')">' + editIcon + '</a>';
                    const deleteLink = '<a id="deleteThis" onclick= "deleteRecord(' + data + ')">' + deleteIcon + '</a>';

                    return `<div class="d-flex justify-content-between mx-2 fs-medium">` + viewLink + ' ' + editLink + ' ' + deleteLink + `</div>`;
                }
            }
        ],
        aoColumnDefs: [{
            bSortable: false,
            aTargets: [-1]
        }]
    });

    $('#filterSearch').keyup(function () {
        recordsDataTable.draw();
    });

    $('#filterCollege').change(function () {
        recordsDataTable.draw();
    });
    $('#filterCourse').change(function () {
        recordsDataTable.draw();
    });
    $('#filterSemester').change(function () {
        recordsDataTable.draw();
    });
    $('#filterYear').change(function () {
        recordsDataTable.draw();
    });
});

$(document).ready(function () {
    var table = $('#recordsTable').DataTable();

    $('#filterShow').on('change', function () {
        var length = $(this).val();
        table.page.len(length).draw();
    });
});
