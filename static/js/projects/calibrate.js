pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

let point1 = null;
let point2 = null;
const canvas = document.getElementById('pdf-canvas');
const ctx = canvas ? canvas.getContext('2d') : null;

if (window.CALIBRATE_CONFIG.fileType === 'pdf') {
    const loadingTask = pdfjsLib.getDocument('/' + window.CALIBRATE_CONFIG.filePath);
    loadingTask.promise.then(function(pdf) {
        pdf.getPage(1).then(function(page) {
            const container = document.getElementById('canvas-container');
            const scale = container.clientWidth / page.getViewport({scale: 1}).width;
            const viewport = page.getViewport({scale: scale});

            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            page.render(renderContext);
        });
    });

    canvas.addEventListener('click', function(e) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (!point1) {
            point1 = {x: x, y: y};
            document.getElementById('point1').value = `(${x.toFixed(0)}, ${y.toFixed(0)})`;
            drawPoint(x, y, 'blue');
        } else if (!point2) {
            point2 = {x: x, y: y};
            document.getElementById('point2').value = `(${x.toFixed(0)}, ${y.toFixed(0)})`;
            drawPoint(x, y, 'red');
            drawLine(point1, point2);
            checkEnableButton();
        }
    });
}


function drawPoint(x, y, color) {
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
}

function drawLine(p1, p2) {
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.strokeStyle = 'green';
    ctx.lineWidth = 2;
    ctx.stroke();
}

function checkEnableButton() {
    const distance = document.getElementById('real_distance').value;
    document.getElementById('btn-calibrate').disabled = !(point1 && point2 && distance);
}

document.getElementById('real_distance').addEventListener('input', checkEnableButton);

document.getElementById('btn-reset').addEventListener('click', function() {
    point1 = null;
    point2 = null;
    document.getElementById('point1').value = '';
    document.getElementById('point2').value = '';
    document.getElementById('real_distance').value = '';
    location.reload();
});

document.getElementById('btn-calibrate').addEventListener('click', function() {
    const distance = parseFloat(document.getElementById('real_distance').value);

    fetch('/api/plans/' + window.CALIBRATE_CONFIG.planId + '/calibrate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            point1: point1,
            point2: point2,
            real_distance: distance
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Calibration réussie! Échelle: ' + data.scale_factor.toFixed(6) + ' m/px');
            window.location.href = window.CALIBRATE_CONFIG.measureUrl;
        } else {
            alert('Erreur: ' + data.error);
        }
    });
});
