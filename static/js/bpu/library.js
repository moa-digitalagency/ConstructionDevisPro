function openOverrideModal(articleId, code, designation) {
    document.getElementById('override-form').action = '/bpu/article/' + articleId + '/override';
    document.getElementById('article-id').value = articleId;
    document.getElementById('modal-code').value = code;
    document.getElementById('modal-designation').value = designation;
    document.getElementById('override-modal').classList.remove('hidden');
}

function closeOverrideModal() {
    document.getElementById('override-modal').classList.add('hidden');
}
