pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

const pdfCanvas = document.getElementById('pdf-canvas');
const drawCanvas = document.getElementById('draw-canvas');
const pdfCtx = pdfCanvas.getContext('2d');
const drawCtx = drawCanvas.getContext('2d');

const scaleFactor = window.MEASURE_CONFIG.scaleFactor;
let points = [];
let currentTool = 'polygon';
let isDragging = false;
let dragIndex = -1;

if (window.MEASURE_CONFIG.fileType === 'pdf') {
    const loadingTask = pdfjsLib.getDocument('/' + window.MEASURE_CONFIG.filePath);
    loadingTask.promise.then(function(pdf) {
        pdf.getPage(1).then(function(page) {
            const container = document.getElementById('canvas-container');
            const scale = container.clientWidth / page.getViewport({scale: 1}).width;
            const viewport = page.getViewport({scale: scale});

            pdfCanvas.height = viewport.height;
            pdfCanvas.width = viewport.width;
            drawCanvas.height = viewport.height;
            drawCanvas.width = viewport.width;

            page.render({
                canvasContext: pdfCtx,
                viewport: viewport
            });
        });
    });
}

function redraw() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);

    if (points.length === 0) return;

    drawCtx.beginPath();
    drawCtx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
        drawCtx.lineTo(points[i].x, points[i].y);
    }
    // Close path if enough points and not just a line tool
    if (points.length >= 3 && currentTool !== 'line') {
        drawCtx.closePath();
        drawCtx.fillStyle = 'rgba(26, 86, 219, 0.2)';
        drawCtx.fill();
    }

    drawCtx.strokeStyle = '#1a56db';
    drawCtx.lineWidth = 2;
    drawCtx.stroke();

    // Draw vertices
    points.forEach((p, i) => {
        drawCtx.beginPath();
        drawCtx.arc(p.x, p.y, 5, 0, 2 * Math.PI);
        drawCtx.fillStyle = (i === dragIndex) ? '#f59e0b' : '#1a56db';
        drawCtx.fill();
        drawCtx.strokeStyle = 'white';
        drawCtx.lineWidth = 1;
        drawCtx.stroke();
    });

    if (points.length >= 3) {
        calculateArea();
        document.getElementById('btn-save-room').disabled = false;
    }
}

drawCanvas.addEventListener('mousedown', function(e) {
    const rect = drawCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Check if clicking existing point
    for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const dist = Math.sqrt((p.x - x)**2 + (p.y - y)**2);
        if (dist < 8) {
            isDragging = true;
            dragIndex = i;
            redraw();
            return;
        }
    }

    // If Magic Wand
    if (currentTool === 'magic') {
        autoDetectRoom(x, y);
        return;
    }

    // If polygon tool, add point
    if (currentTool === 'polygon' || currentTool === 'line') {
        points.push({x: x, y: y});
        redraw();
    }
});

drawCanvas.addEventListener('mousemove', function(e) {
    if (isDragging && dragIndex !== -1) {
        const rect = drawCanvas.getBoundingClientRect();
        points[dragIndex].x = e.clientX - rect.left;
        points[dragIndex].y = e.clientY - rect.top;
        redraw();
    }
});

drawCanvas.addEventListener('mouseup', function(e) {
    isDragging = false;
    dragIndex = -1;
    redraw();
});

function autoDetectRoom(startX, startY) {
    document.getElementById('loading-overlay').classList.remove('hidden');

    // Simulate detection (in a real app, this would use computer vision)
    setTimeout(() => {
        // Create a default box around click point
        const pixelsPerMeter = 1 / scaleFactor;
        const boxSize = pixelsPerMeter * 4; // 4 meters
        const half = boxSize / 2;

        points = [
            {x: startX - half, y: startY - half},
            {x: startX + half, y: startY - half},
            {x: startX + half, y: startY + half},
            {x: startX - half, y: startY + half}
        ];

        document.getElementById('loading-overlay').classList.add('hidden');
        redraw();

        document.getElementById('room_name').value = "Pièce Auto";
        // Switch back to polygon tool for editing
        currentTool = 'polygon';
        updateToolButtons(document.getElementById('tool-polygon'));

    }, 600);
}

function calculateArea() {
    let area = 0;
    const n = points.length;

    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        area += points[i].x * points[j].y;
        area -= points[j].x * points[i].y;
    }

    area = Math.abs(area) / 2;
    const realArea = area * Math.pow(scaleFactor, 2);

    document.getElementById('calculated_area').textContent = realArea.toFixed(2) + ' m²';
}

document.getElementById('btn-clear').addEventListener('click', function() {
    points = [];
    redraw();
    document.getElementById('calculated_area').textContent = '- m²';
    document.getElementById('btn-save-room').disabled = true;
});

document.getElementById('btn-save-room').addEventListener('click', function() {
    const name = document.getElementById('room_name').value || 'Pièce';
    const type = document.getElementById('room_type').value;

    let area = 0;
    const n = points.length;
    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        area += points[i].x * points[j].y;
        area -= points[j].x * points[i].y;
    }
    area = Math.abs(area) / 2 * Math.pow(scaleFactor, 2);

    let perimeter = 0;
    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        const dx = points[j].x - points[i].x;
        const dy = points[j].y - points[i].y;
        perimeter += Math.sqrt(dx*dx + dy*dy);
    }
    perimeter *= scaleFactor;

    fetch('/api/projects/' + window.MEASURE_CONFIG.projectId + '/rooms', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            plan_id: window.MEASURE_CONFIG.planId,
            name: name,
            room_type: type,
            area: area,
            perimeter: perimeter,
            polygon_data: points
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            location.reload();
        }
    });
});

document.getElementById('tool-polygon').addEventListener('click', function() {
    currentTool = 'polygon';
    updateToolButtons(this);
});

document.getElementById('tool-line').addEventListener('click', function() {
    currentTool = 'line';
    updateToolButtons(this);
});

document.getElementById('tool-magic').addEventListener('click', function() {
    currentTool = 'magic';
    updateToolButtons(this);
});

function updateToolButtons(activeBtn) {
    ['tool-polygon', 'tool-line', 'tool-magic'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn === activeBtn) {
            btn.classList.add('bg-primary', 'text-white');
            btn.classList.remove('border', 'border-gray-300');
        } else {
            btn.classList.remove('bg-primary', 'text-white');
            btn.classList.add('border', 'border-gray-300');
        }
    });
}
