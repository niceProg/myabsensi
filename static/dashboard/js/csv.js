document.addEventListener('DOMContentLoaded', function () {
    const printButton = document.getElementById('Print');
    const exportButton = document.getElementById('CSV');
    const dataTabel = document.getElementById('datatablesSimple');

    // Inisialisasi Simple-DataTables
    const table = new simpleDatatables.DataTable(dataTabel);

    printButton.addEventListener('click', function () {
        // Add styles
        let style = document.createElement('style');
        style.innerHTML = `
        @media print {
            /* Your styles here. For example: */
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 0px solid black;
                padding: 15px;
                text-align: left;
            }
        }
    `;
        document.head.appendChild(style);

        // Print the table with added styles
        printJS({
            printable: 'datatablesSimple',
            type: 'html',
            honorColor: true,
            targetStyles: ['*'],
        });

        // Remove the styles after printing
        document.head.removeChild(style);
    });

    exportButton.addEventListener('click', function () {
        exportToCSV(table);
    });

    // Fungsi untuk export CSV
    function exportToCSV(table) {
        const rows = Array.from(dataTabel.querySelectorAll('tbody tr'));
        const headers = Array.from(dataTabel.querySelectorAll('thead th')).map((header) => `"${header.innerText}"`);
        const csvContent = [headers.join(';')];

        rows.forEach(function (row) {
            const cells = Array.from(row.querySelectorAll('td'));
            if (cells.length === 0 || cells.every((cell) => cell.innerText.trim() === '')) {
                // Skip empty rows
                return;
            }
            const rowData = cells.map((cell) => `"${cell.innerText.replace(/"/g, '""')}"`).join(';');
            csvContent.push(rowData);
        });

        const csvData = csvContent.join('\n');
        const filename = 'data.csv';

        // Buat elemen link untuk mengunduh file CSV
        const link = document.createElement('a');
        link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvData);
        link.download = filename;

        // Simulasikan klik pada link untuk mengunduh file CSV
        link.click();
    }

    function escapeCSV(text) {
        let escapedText = text;
        if (escapedText.includes(',') || escapedText.includes('\n') || escapedText.includes('\r') || escapedText.includes('"')) {
            escapedText = `"${escapedText.replace(/"/g, '""')}"`;
        }
        return escapedText;
    }
});
