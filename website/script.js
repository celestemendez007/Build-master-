document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');

    // Toggle mobile menu
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
    });

    // Close mobile menu when clicking a link
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
        });
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(20, 80, 170, 0.98)';
            navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.5)';
        } else {
            navbar.style.background = 'rgba(20, 80, 170, 0.85)';
            navbar.style.boxShadow = 'none';
        }
    });

    // Modal Logic
    const modals = document.querySelectorAll('.modal');
    const openCompModalBtns = document.querySelectorAll('.open-comp-modal');
    const closeBtns = document.querySelectorAll('.close-modal');

    // Open specific modal
    openCompModalBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = btn.getAttribute('data-target');
            const modal = document.getElementById(targetId);
            if(modal) {
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
            }
        });
    });

    // Close modals
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            modals.forEach(m => m.style.display = 'none');
            document.body.style.overflow = 'auto';
        });
    });

    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });

    // Tabs Logic inside Modals
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Find parent modal
            const parentModal = btn.closest('.modal-content');
            
            // Deactivate all tabs in this modal
            parentModal.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
            parentModal.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Activate clicked tab
            btn.classList.add('active');
            const targetContent = document.getElementById(btn.getAttribute('data-tab'));
            if(targetContent) {
                targetContent.classList.add('active');
            }
        });
    });

    // --- Lógica para la Agenda en la Línea de Tiempo ---
    const timelineContents = document.querySelectorAll('.timeline-content');
    timelineContents.forEach(content => {
        // Al hacer clic, se abre/cierra la agenda togglenado la clase active en el contenedor principal
        const item = content.closest('.timeline-item');
        content.addEventListener('click', () => {
            item.classList.toggle('active');
        });
    });
});
