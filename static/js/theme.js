function syncButtonLoading() {
    document.getElementById('syncButton').classList.add('box-amber')
    document.getElementById('syncButton').classList.remove('box-green')
}

function syncButtonLoaded() {
    document.getElementById('syncButton').classList.add('box-green')
    document.getElementById('syncButton').classList.remove('box-amber')
}