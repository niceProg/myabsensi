$(document).ready(function () {
    var attendanceDetected = false;

    // Check attendance status
    $.ajax({
        url: '/absensi/check_attendance',
        method: 'GET',
        success: function (response) {
            attendanceDetected = response.attendance_detected;
        },
        error: function () {
            console.log('Error occurred during attendance check.');
        },
    });

    // Mark attendance
    $('#markAttendanceButton').click(function () {
        if (!attendanceDetected) {
            $.ajax({
                url: '/absensi/mark_attendance',
                method: 'POST',
                success: function (response) {
                    if (response.success) {
                        attendanceDetected = true;
                        showPopup();
                    } else {
                        showAlert(response.message);
                    }
                },
                error: function () {
                    console.log('Error occurred during marking attendance.');
                },
            });
        } else {
            showAlert('Karyawan telah absen sebelumnya.');
        }
    });

    function showPopup() {
        $('.popup').show();
    }

    function showAlert(message) {
        Swal.fire({
            title: 'Error!',
            text: message,
            icon: 'error',
            confirmButtonText: 'Ok',
        });
    }
});
