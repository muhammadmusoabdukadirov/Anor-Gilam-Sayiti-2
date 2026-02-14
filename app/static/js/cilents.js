        // Sahifa yuklanganda
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Mijozlar sahifasi yuklandi');
            
            // DataTables ni ishga tushirish
            $('#clientsTable').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/1.13.4/i18n/uz.json"
                },
                "pageLength": 10,
                "order": [[0, "desc"]]
            });
        });

        // Qidirish funksiyasi
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#clientsTable tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                    row.classList.add('animate-fade');
                } else {
                    row.style.display = 'none';
                }
            });
        });

        // Filter tugmalari
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                // Barcha filterlardan active classini olib tashlash
                filterButtons.forEach(b => b.classList.remove('active'));
                // Bosilgan tugmaga active classini qo'shish
                this.classList.add('active');
                
                const filterType = this.id;
                filterTable(filterType);
            });
        });

        // Jadvalni filtrlash
        function filterTable(filterType) {
            const rows = document.querySelectorAll('#clientsTable tbody tr');
            
            rows.forEach(row => {
                const statusBadge = row.querySelector('.status-badge');
                const dateCell = row.querySelector('.date-cell');
                let showRow = true;
                
                switch(filterType) {
                    case 'filterNew':
                        if (!row.querySelector('.status-new') || 
                            !row.querySelector('.status-new').textContent.includes('Yangi')) {
                            showRow = false;
                        }
                        break;
                    case 'filterToday':
                        if (!dateCell || !dateCell.textContent.includes('Bugun')) {
                            showRow = false;
                        }
                        break;
                    case 'filterAll':
                        showRow = true;
                        break;
                }
                
                if (showRow) {
                    row.style.display = '';
                    row.classList.add('animate-fade');
                } else {
                    row.style.display = 'none';
                }
            });
        }

        // Jadvalni saralash
        let sortDirection = true;
        function sortTable(columnIndex) {
            const table = document.getElementById('clientsTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                const aValue = a.cells[columnIndex].textContent;
                const bValue = b.cells[columnIndex].textContent;
                
                // Raqamli ustunlar uchun
                if (columnIndex === 0) { // ID ustuni
                    return sortDirection ? 
                        parseInt(aValue.replace('#', '')) - parseInt(bValue.replace('#', '')) :
                        parseInt(bValue.replace('#', '')) - parseInt(aValue.replace('#', ''));
                }
                
                // Sana ustuni uchun
                if (columnIndex === 5) {
                    const aDate = new Date(aValue.split(' ')[2]); // Sana qismini ajratish
                    const bDate = new Date(bValue.split(' ')[2]);
                    return sortDirection ? aDate - bDate : bDate - aDate;
                }
                
                // Matn ustunlari uchun
                return sortDirection ? 
                    aValue.localeCompare(bValue) : 
                    bValue.localeCompare(aValue);
            });
            
            // Yo'nalishni o'zgartirish
            sortDirection = !sortDirection;
            
            // O'q belgisini yangilash
            const headers = table.querySelectorAll('thead th i');
            headers.forEach(icon => {
                icon.className = 'fas fa-sort';
            });
            headers[columnIndex].className = sortDirection ? 
                'fas fa-sort-up' : 'fas fa-sort-down';
            
            // Yangilangan qatorlarni qo'shish
            rows.forEach(row => tbody.appendChild(row));
        }

        // Mijozni ko'rish
        function viewClient(id) {
            Swal.fire({
                title: 'Mijoz ma\'lumotlari',
                html: `<div style="text-align: left; padding: 20px;">
                    <p><strong>ID:</strong> #${id}</p>
                    <p><strong>Ism:</strong> Mijoz ismi</p>
                    <p><strong>Telefon:</strong> +998 90 123 45 67</p>
                    <p><strong>Manzil:</strong> Toshkent shahri</p>
                    <p><strong>Gilam turi:</strong> Yun gilam</p>
                    <p><strong>Sana:</strong> 2024-02-20</p>
                    <p><strong>Izoh:</strong> Tezroq kelish kerak</p>
                </div>`,
                icon: 'info',
                confirmButtonColor: '#d62828',
                confirmButtonText: 'Yopish'
            });
        }

        // Mijozni tahrirlash
        function editClient(id) {
            Swal.fire({
                title: 'Mijozni tahrirlash',
                html: `<input type="text" id="editName" class="swal2-input" placeholder="Ism">
                       <input type="tel" id="editPhone" class="swal2-input" placeholder="Telefon">
                       <input type="text" id="editAddress" class="swal2-input" placeholder="Manzil">
                       <select id="editStatus" class="swal2-input">
                           <option value="new">Yangi</option>
                           <option value="processing">Jarayonda</option>
                           <option value="completed">Tugatilgan</option>
                       </select>`,
                showCancelButton: true,
                confirmButtonText: 'Saqlash',
                cancelButtonText: 'Bekor qilish',
                confirmButtonColor: '#d62828',
                preConfirm: () => {
                    return {
                        name: document.getElementById('editName').value,
                        phone: document.getElementById('editPhone').value,
                        address: document.getElementById('editAddress').value,
                        status: document.getElementById('editStatus').value
                    }
                }
            }).then(result => {
                if (result.isConfirmed) {
                    Swal.fire('Saqlangan!', 'Mijoz ma\'lumotlari yangilandi.', 'success');
                    // Bu yerda serverga so'rov yuboriladi
                }
            });
        }

        // Mijozni o'chirish
        function deleteClient(id) {
            Swal.fire({
                title: 'Haqiqatan ham o\'chirilsinmi?',
                text: "Bu amalni qaytarib bo'lmaydi!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d62828',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Ha, o\'chirish!',
                cancelButtonText: 'Bekor qilish'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Bu yerda serverga o'chirish so'rovi yuboriladi
                    const row = document.querySelector(`tr:has(td:first-child strong:contains("#${id}"))`);
                    if (row) {
                        row.style.animation = 'fadeOut 0.5s ease-out';
                        setTimeout(() => row.remove(), 500);
                    }
                    
                    Swal.fire(
                        'O\'chirildi!',
                        'Mijoz ro\'yxatdan o\'chirildi.',
                        'success'
                    );
                }
            });
        }

        // Yangilash tugmasi
        document.getElementById('refreshBtn').addEventListener('click', function() {
            this.classList.add('fa-spin');
            setTimeout(() => {
                this.classList.remove('fa-spin');
                // Bu yerda ma'lumotlarni yangilash kodi bo'ladi
                Swal.fire({
                    title: 'Yangilandi!',
                    text: 'Ma\'lumotlar muvaffaqiyatli yangilandi.',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                });
            }, 1000);
        });

        // Export funksiyalari
        document.getElementById('exportPDF').addEventListener('click', function() {
            Swal.fire({
                title: 'PDF yuklanmoqda...',
                text: 'Hujjat tayyorlanmoqda',
                icon: 'info',
                timer: 2000,
                showConfirmButton: false
            });
            
            setTimeout(() => {
                Swal.fire(
                    'Muvaffaqiyatli!',
                    'PDF hujjat yuklandi.',
                    'success'
                );
            }, 2000);
        });

        document.getElementById('exportExcel').addEventListener('click', function() {
            Swal.fire({
                title: 'Excel yuklanmoqda...',
                text: 'Fayl tayyorlanmoqda',
                icon: 'info',
                timer: 2000,
                showConfirmButton: false
            });
            
            setTimeout(() => {
                Swal.fire(
                    'Muvaffaqiyatli!',
                    'Excel fayli yuklandi.',
                    'success'
                );
            }, 2000);
        });

        // Sahifalash
        const pageButtons = document.querySelectorAll('.page-btn:not(.disabled)');
        pageButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                if (this.classList.contains('disabled')) return;
                
                // Barcha tugmalardan active classini olib tashlash
                document.querySelectorAll('.page-btn').forEach(b => {
                    b.classList.remove('active');
                });
                
                // Bosilgan tugmaga active classini qo'shish
                this.classList.add('active');
                
                // Bu yerda sahifalash logikasi bo'ladi
                console.log('Sahifa o\'zgartirildi:', this.textContent);
            });
        });

        // Animatsiya CSS qo'shish
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(20px); }
            }
            
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            .fa-spin {
                animation: spin 1s linear infinite;
            }
        `;
        document.head.appendChild(style);
