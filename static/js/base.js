function toggleMobileMenu() {
    const sidebar = document.querySelector('aside');
    const isHidden = sidebar.classList.toggle('hidden');
    sidebar.classList.toggle('fixed');
    sidebar.classList.toggle('inset-0');
    sidebar.classList.toggle('z-50');

    const btn = document.querySelector('button[onclick="toggleMobileMenu()"]');
    if (btn) btn.setAttribute('aria-expanded', !isHidden);
}

function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    const btn = document.getElementById('user-menu-button');
    const isHidden = menu.classList.contains('hidden');

    if (isHidden) {
        menu.classList.remove('hidden');
        btn.setAttribute('aria-expanded', 'true');
    } else {
        menu.classList.add('hidden');
        btn.setAttribute('aria-expanded', 'false');
    }
}

// Close dropdowns when clicking outside
window.addEventListener('click', function(e) {
    const menu = document.getElementById('user-menu');
    const btn = document.getElementById('user-menu-button');

    if (menu && !menu.classList.contains('hidden') && !menu.contains(e.target) && !btn.contains(e.target)) {
        menu.classList.add('hidden');
        btn.setAttribute('aria-expanded', 'false');
    }
});

// Close on Escape key
window.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const menu = document.getElementById('user-menu');
        const btn = document.getElementById('user-menu-button');

        if (menu && !menu.classList.contains('hidden')) {
            menu.classList.add('hidden');
            btn.setAttribute('aria-expanded', 'false');
            btn.focus();
        }
    }
});

// Form loading state handler
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form[data-submit-loading]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.disabled) {
                const loadingText = btn.getAttribute('data-loading-text') || 'Chargement...';

                // Set width to current width to prevent layout shift
                // btn.style.width = `${btn.offsetWidth}px`; // Optional: might cause issues if text is longer

                btn.disabled = true;
                btn.classList.add('opacity-75', 'cursor-not-allowed');
                btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> ${loadingText}`;
            }
        });
    });
});
