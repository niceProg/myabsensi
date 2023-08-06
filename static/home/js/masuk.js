var lastUpdateMasuk = null; // Penyimpanan waktu update terakhir untuk absen masuk
var lastUpdatePulang = null; // Penyimpanan waktu update terakhir untuk absen pulang
var tabel = $('#tabelRecordTerbaru');

function updateTable(url) {
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            var latestRecord;
            var lastUpdate;
            if (url == '/absensi/latestRecordMasuk') {
                latestRecord = data.latestRecordMasuk;
                lastUpdate = lastUpdateMasuk;
            } else if (url == '/absensi/latestRecordPulang') {
                latestRecord = data.latestRecordPulang;
                lastUpdate = lastUpdatePulang;
            }

            var waktuMasuk = latestRecord.waktu_masuk != 'Belum absen' ? new Date(latestRecord.waktu_masuk) : null;
            var waktuPulang = latestRecord.waktu_pulang != 'Belum absen' ? new Date(latestRecord.waktu_pulang) : null;

            // Jika data belum pernah diterima atau ada record baru
            if (!lastUpdate || (waktuMasuk && waktuMasuk > lastUpdate) || (waktuPulang && waktuPulang > lastUpdate)) {
                // Simpan waktu update
                if (url == '/absensi/latestRecordMasuk') {
                    lastUpdateMasuk = new Date();
                    lastUpdateMasuk = null;
                } else if (url == '/absensi/latestRecordPulang') {
                    lastUpdatePulang = new Date();
                    lastUpdatePulang = null;
                }

                // Ambil tabel dan kosongkan isinya
                tabel.empty();

                // Buat baris baru
                var tr = $('<tr>');

                // Tambahkan data ke baris
                $.each(latestRecord, function (index, value) {
                    tr.append('<td>' + value + '</td>');
                    // lastUpdate = null;
                });

                // Tambahkan baris ke tabel
                tabel.append(tr);
                // lastUpdate = null;
            }
        },
        error: function (error) {
            console.error('Error:', error);
        },
    });
}

setInterval(function () {
    updateTable('/absensi/latestRecordMasuk');
    lastUpdateMasuk = null;
}, 2000);
setInterval(function () {
    updateTable('/absensi/latestRecordPulang');
    lastUpdatePulang = null;
}, 2000);
