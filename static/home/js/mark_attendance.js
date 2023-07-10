// Fungsi untuk melakukan permintaan ke endpoint '/mark_attendance' pada Flask
function aksesMasuk() {
    fetch('/absensi/mark_attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                if (data.confidence > 70) {
                    // Menampilkan data identitas karyawan jika berhasil
                    const karyawanContainer = document.getElementById('karyawan-container');
                    karyawanContainer.innerHTML = `
                        <p>Nama: ${data.data_karyawan.nama}</p>
                        <p>Jabatan: ${data.data_karyawan.jabatan}</p>
                        <p>NIDN / NIPY: ${data.data_karyawan.nidn_nipy}</p>
                        <p>Jenis Kelamin: ${data.data_karyawan.jkl}</p>
                    `;
                } else {
                    // Menampilkan pesan jika tingkat kepercayaan di bawah 70%
                    alert('Tingkat kepercayaan deteksi wajah kurang dari 70%');
                }
            } else {
                alert(data.message);
                // const karyawanContainer = document.getElementById('karyawan-container');
                // // Menampilkan pesan jika gagal
                // karyawanContainer.innerHTML = `<p>${data.message}</p>`;
                // alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}
