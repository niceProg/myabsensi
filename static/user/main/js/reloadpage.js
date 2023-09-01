// Misalkan Anda memiliki kode seperti ini untuk menangani streaming:
const videoElement = document.getElementById('videoElement');

if (!!window.EventSource) {
    var source = new EventSource('/user/masuk');

    source.addEventListener(
        'message',
        function (e) {
            if (e.data === 'redirect_required') {
                window.location.href = '/path_to_redirect_to'; // Ganti dengan URL tujuan Anda
            } else {
                var blob = new Blob([e.data], { type: 'image/jpeg' });
                var url = window.URL.createObjectURL(blob);
                videoElement.src = url;
            }
        },
        false,
    );
}
