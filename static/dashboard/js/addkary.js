document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('.btn-warning.btn-lg').addEventListener('click', function (event) {
        event.preventDefault();

        // Mengambil URL dari atribut href
        var trainingUrl = this.getAttribute('href');

        // Mengambil URL redirect dari atribut data-redirect-url
        var redirectUrl = this.getAttribute('data-redirect-url');

        // Mengirim permintaan GET ke backend untuk memulai proses training
        fetch(trainingUrl, {
            method: 'GET',
        })
            .then((response) => {
                if (response.status === 200) {
                    swal({
                        title: 'Berhasil!',
                        text: 'Training telah selesai.',
                        icon: 'success',
                        button: 'Lanjut',
                    }).then(() => {
                        // Setelah Sweet Alert ditutup, arahkan ke URL yang ditentukan oleh backend
                        window.location.href = redirectUrl;
                    });
                } else {
                    swal('Oops!', 'Ada kesalahan saat melakukan training. Silahkan coba lagi.', 'error');
                }
            })
            .catch((error) => {
                swal('Oops!', 'Ada kesalahan saat mengirim permintaan. Silahkan coba lagi.', 'error');
            });
    });
});
