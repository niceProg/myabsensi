function checkNotificationForUser(id_karyawan) {
    $.ajax({
        url: `/user/absensi/check_for_notification/${id_karyawan}`,
        method: 'GET',
        success: function (data) {
            if (data.showNotification) {
                Swal.fire({
                    title: data.title,
                    text: data.text,
                    icon: 'success',
                    confirmButtonText: 'Oke',
                });
            }
        },
    });
}
