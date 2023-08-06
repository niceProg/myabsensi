// Fungsi untuk akses masuk
// function aksesMasuk() {
//     navigator.mediaDevices
//         .getUserMedia({ video: true })
//         .then(function (stream) {
//             // Mendapatkan elemen video
//             var video = document.getElementById('videoElement');

//             // Mengubah sumber video ke URL feed kamera akses masuk
//             video.src = Masuk + '?mode=masuk';
//             // video.src = url;
//         })
//         .catch(function (error) {
//             console.error('Tidak dapat mengakses kamera: ', error);
//         });
// }

function aksesMasuk() {
    // Mendapatkan posisi saat ini
    if ('geolocation' in navigator) {
        var options = {
            enableHighAccuracy: true,
        };

        navigator.geolocation.getCurrentPosition(
            function (position) {
                var userLat = position.coords.latitude;
                var userLon = position.coords.longitude;

                console.log('Latitude:', userLat);
                console.log('Longitude:', userLon);

                var officeLat = -7.0052185; // Latitude kantor
                var officeLon = 109.1423485; // Longitude kantor

                var R = 6371; // Radius bumi dalam kilometer
                var dLat = toRad(officeLat - userLat);
                var dLon = toRad(officeLon - userLon);
                var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(toRad(userLat)) * Math.cos(toRad(officeLat)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
                var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                var distance = R * c; // Jarak dalam kilometer

                if (distance <= 0.2) {
                    // Karyawan berada dalam radius kantor
                    Swal.fire('Sukses!', 'Anda berada di lokasi kampus. Silahkan atur sisi wajah untuk mencatat absen ', 'success');
                    navigator.mediaDevices
                        .getUserMedia({ video: true })
                        .then(function (stream) {
                            // Mendapatkan elemen video
                            var video = document.getElementById('videoElement');

                            // Mengubah sumber video ke URL feed kamera akses masuk
                            video.src = Masuk + '?mode=masuk';
                            // video.src = url;
                        })
                        .catch(function (error) {
                            Swal.fire('Oops...', 'Anda menolak izin akses kamera', 'error');
                            console.error('Tidak dapat mengakses kamera: ', error);
                        });
                } else {
                    // Karyawan berada di luar radius kantor
                    Swal.fire('Oops...', 'Anda tidak berada dalam radius kantor.', 'error');
                }
            },
            function (error) {
                Swal.fire('Oops...', 'Anda menolak izin akses lokasi', 'error');
                console.error('Tidak dapat mengakses geolocation: ', error);
                // Tindakan jika akses geolocation ditolak atau gagal
            },
            options,
        );
    } else {
        // Perangkat tidak mendukung geolocation
        console.error('Geolocation tidak didukung pada perangkat ini.');
    }
}

function toRad(value) {
    return (value * Math.PI) / 180;
}

// Fungsi untuk akses pulang
function aksesPulang() {
    navigator.mediaDevices
        .getUserMedia({ video: true })
        .then(function (stream) {
            // Mendapatkan elemen video
            var video = document.getElementById('videoElement');

            // Mengubah sumber video ke URL feed kamera akses masuk
            video.src = Pulang + '?mode=pulang';
            // video.src = url;
        })
        .catch(function (error) {
            console.error('Tidak dapat mengakses kamera: ', error);
        });
}
