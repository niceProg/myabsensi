jQuery(document).ready(function () {
    // Initialize DataTables
    var table = $('#datatablesSimple').DataTable();
    var dayFilter = '';
    var monthFilter = '';

    // Use a custom search function
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        var date = new Date(data[2]); // assuming date is in the 3rd column and in 'yyyy-mm-dd' format
        if (
            (dayFilter === '' || date.getDate() === dayFilter) &&
            (monthFilter === '' || date.getMonth() + 1 === monthFilter) // getMonth() returns 0-11, so we add 1
        ) {
            return true;
        }
        return false;
    });

    // Day Filter
    $('#filterHari').on('change', function () {
        dayFilter = this.value ? parseInt(this.value, 10) : '';
        table.draw();
    });

    // Month Filter
    $('#filterBulan').on('change', function () {
        monthFilter = this.value ? parseInt(this.value, 10) : '';
        table.draw();
    });
});
