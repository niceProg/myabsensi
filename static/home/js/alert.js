{% with messages = get_flashed_messages() %}
    {% if messages %}
        {% for message in messages %}
            swal.fire({
                title: "Pesan",
                text: "{{ message }}",
                icon: "success"  // Ganti dengan "error" untuk pesan error
            });
        {% endfor %}
    {% endif %}
{% endwith %}