function toggleClimQty(select) {
    const container = document.getElementById('clim-qty-container');
    container.style.display = select.value === 'aucune' ? 'none' : 'block';
}

function togglePoolOptions(select) {
    const container = document.getElementById('pool-options');
    container.classList.toggle('hidden', select.value === 'non');
}

document.getElementById('questions-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Réponses enregistrées! Vous pouvez maintenant générer un devis.');
    window.location.href = this.dataset.redirectUrl;
});
