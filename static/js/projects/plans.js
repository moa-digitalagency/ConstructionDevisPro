document.getElementById('plan_file').addEventListener('change', function(e) {
    var fileName = e.target.files[0] ? e.target.files[0].name : '';
    document.getElementById('file_name').textContent = fileName ? 'Fichier sélectionné: ' + fileName : '';
});
