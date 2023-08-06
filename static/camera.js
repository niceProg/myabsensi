document.addEventListener('DOMContentLoaded', function () {
    var startCameraBtn = document.getElementById('aksesMasukButton');
    var videoElement = document.getElementById('videoElement');

    // Tambahkan event listener pada button ketika diklik
    startCameraBtn.addEventListener('click', function () {
        // Mendapatkan izin akses kamera
        navigator.mediaDevices
            .getUserMedia({ video: true })
            .then(function (stream) {
                // Gunakan stream video yang diterima untuk menampilkan gambar dari kamera
                videoElement.srcObject = stream;
            })
            .catch(function (error) {
                console.error('Tidak dapat mengakses kamera: ', error);
            });
    });
});
