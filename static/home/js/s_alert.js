$.get('http://127.0.0.1:9999/absensi/get_last_detected_face', function (data) {
    if (data.status == 'success') {
        // Jika id_karyawan ada, berarti wajah berhasil diidentifikasi
        swal('Sukses!', 'Wajah berhasil diidentifikasi sebagai ' + data.nama_lengkap + '!', 'success');
    } else {
        // Jika tidak, tampilkan pesan error
        swal('Gagal!', data.message, 'error');
    }
});
