function openRenameModal(name) {
    document.getElementById('renameModal').classList.remove('hidden');
    document.getElementById('old_name').value = name;
    document.getElementById('new_name').value = name;
    document.getElementById('new_name').focus();
}

function closeRenameModal() {
    document.getElementById('renameModal').classList.add('hidden');
}
