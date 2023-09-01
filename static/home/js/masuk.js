$(document).ready(function () {
    let lastCountMasuk = 0;
    let lastCountPulang = 0;
    let countMasuk;
    let countPulang;

    checkNewAbsen();

    function checkNewAbsen() {
        countTodayAbsen();
        setTimeout(checkNewAbsen, 1000);
    }

    function countTodayAbsen() {
        $.ajax({
            url: '/user/absenterbaru',
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                countMasuk = data.countMasukToday;
                countPulang = data.countPulangToday;

                if (countMasuk > lastCountMasuk || countPulang > lastCountPulang) {
                    reloadTable();
                }

                lastCountMasuk = countMasuk;
                lastCountPulang = countPulang;
            },
            error: function (result) {
                console.log('Error retrieving count data!');
            },
        });
    }

    function reloadTable() {
        $.ajax({
            url: '/user/absenload',
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                const tbody = $('#absensiTable tbody');
                tbody.empty();

                const judul = ['Id Karyawan', 'Nama', 'Jabatan', 'Waktu Masuk', 'Waktu Pulang'];

                $.each(response.dataHariIni, function (index, item) {
                    for (let i = 0; i < judul.length; i++) {
                        tbody.append('<tr>' + '<th>' + judul[i] + '</th>' + '<td>' + item[i] + '</td>' + '</tr>');
                    }
                });
            },
            error: function (result) {
                console.log('Terjadi kesalahan saat mengambil data absensi!');
            },
        });
    }
});
