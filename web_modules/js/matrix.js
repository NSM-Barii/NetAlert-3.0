// Matrix rain effect for background

const canvas = document.getElementById('matrix');
const ctx = canvas.getContext('2d');

// Set canvas size
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Matrix characters
const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,.<>?/~`';
const charArray = chars.split('');

// Column settings
const fontSize = 14;
const columns = canvas.width / fontSize;
const drops = [];

// Initialize drops
for (let i = 0; i < columns; i++) {
    drops[i] = Math.random() * -100;
}

// Draw matrix rain
function drawMatrix() {
    // Fade effect
    ctx.fillStyle = 'rgba(10, 14, 26, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Set text style
    ctx.fillStyle = '#00ff41';
    ctx.font = fontSize + 'px monospace';

    // Draw characters
    for (let i = 0; i < drops.length; i++) {
        // Random character
        const char = charArray[Math.floor(Math.random() * charArray.length)];
        const x = i * fontSize;
        const y = drops[i] * fontSize;

        // Draw with varying opacity for depth effect
        const opacity = Math.random() * 0.5 + 0.5;
        ctx.fillStyle = `rgba(0, 255, 65, ${opacity})`;
        ctx.fillText(char, x, y);

        // Random reset
        if (y > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }

        // Move drop down
        drops[i]++;
    }
}

// Animation loop
let matrixInterval = setInterval(drawMatrix, 50);

// Handle window resize
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Recalculate columns
    const newColumns = canvas.width / fontSize;
    drops.length = 0;

    for (let i = 0; i < newColumns; i++) {
        drops[i] = Math.random() * -100;
    }
});

// Performance toggle - stop matrix if needed
window.toggleMatrix = function(enabled) {
    if (enabled && !matrixInterval) {
        matrixInterval = setInterval(drawMatrix, 50);
    } else if (!enabled && matrixInterval) {
        clearInterval(matrixInterval);
        matrixInterval = null;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
};
