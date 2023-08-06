var lastUpdate = null; // Penyimpanan waktu update terakhir
var tabel = $('#tabelRecordTerbaru');

function updateTable() {
    $.ajax({
        url: '/absensi/latestRecordPulang',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            var latestRecord = data.latestRecordPulang;

            // Jika data belum pernah diterima atau ada record baru
            if (!lastUpdate || new Date(latestRecord.timestamp) > lastUpdate) {
                // Simpan waktu update
                lastUpdate = new Date(latestRecord.timestamp);

                // Ambil tabel dan kosongkan isinya
                tabel.empty();

                // Buat baris baru
                var tr = $('<tr>');

                // Tambahkan data ke baris
                $.each(latestRecord, function (index, value) {
                    tr.append('<td>' + value + '</td>');
                });

                // Tambahkan baris ke tabel
                tabel.append(tr);
                lastUpdate = null;
            }
        },
        error: function (error) {
            console.error('Error:', error);
        },
    });
}

setInterval(updateTable, 2000);
