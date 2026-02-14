       // Theme toggle funksiyasi
        document.addEventListener('DOMContentLoaded', function() {
            const themeToggle = document.getElementById('themeToggle');
            const themeIcon = document.getElementById('themeIcon');
            const themeText = document.getElementById('themeText');
            const themeIndicator = document.getElementById('themeIndicator');
            
            // Mavjud temani olish
            let currentTheme = localStorage.getItem('theme') || 'light';
            
            // Tema o'rnatish funksiyasi
            function setTheme(theme) {
                if (theme === 'dark') {
                    document.body.classList.add('dark-mode');
                    themeIcon.className = 'fas fa-sun';
                    themeText.textContent = '🌙';
                    themeIndicator.style.background = 'rgba(255,255,255,0.1)';
                    themeIndicator.style.color = 'white';
                } else {
                    document.body.classList.remove('dark-mode');
                    themeIcon.className = 'fas fa-moon';
                    themeText.textContent = '🌞';
                    themeIndicator.style.background = 'rgba(0,0,0,0.1)';
                    themeIndicator.style.color = 'black';
                }
                localStorage.setItem('theme', theme);
                currentTheme = theme;
            }
            
            // Tugma bosilganda
            themeToggle.addEventListener('click', function() {
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                setTheme(newTheme);
                
                // Kichik bildirishnoma
                const notification = document.createElement('div');
                notification.textContent = newTheme === 'dark' ? '🌙 Tun rejimi yoqildi' : '🌞 Kun rejimi yoqildi';
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: ${newTheme === 'dark' ? '#333' : '#fff'};
                    color: ${newTheme === 'dark' ? '#fff' : '#333'};
                    padding: 10px 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    z-index: 1001;
                    font-weight: bold;
                    transition: opacity 0.3s;
                `;
                document.body.appendChild(notification);
                
                // 3 soniyadan keyin olib tashlash
                setTimeout(() => {
                    notification.style.opacity = '0';
                    setTimeout(() => notification.remove(), 300);
                }, 3000);
            });
            
            // Boshlang'ich tema
            setTheme(currentTheme);
            
            // Vaqtga qarab avtomatik o'zgartirish (19:00-06:00 oralig'ida)
            function checkTimeForTheme() {
                const hour = new Date().getHours();
                if (localStorage.getItem('theme') === 'auto') {
                    if (hour >= 19 || hour < 6) {
                        setTheme('dark');
                    } else {
                        setTheme('light');
                    }
                }
            }
            
            // Har soat tekshirish
            checkTimeForTheme();
            setInterval(checkTimeForTheme, 60000); // Har minut
        });
        
        // Form validation
        document.querySelector('form').addEventListener('submit', function(e) {
            const phone = document.getElementById('phone').value;
            const phoneRegex = /^\+998\d{9}$/;
            
            if (!phoneRegex.test(phone.replace(/\s/g, ''))) {
                alert('Iltimos, to\'g\'ri telefon raqam kiriting (+998XXXXXXXXX)');
                e.preventDefault();
            }
        });