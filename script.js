// Confetti Animation on Page Load
function createConfetti() {
    const confettiContainer = document.getElementById('confettiContainer');
    const colors = ['#ff6b9d', '#c44569', '#8e44ad', '#ffd700', '#ff69b4', '#da70d6'];
    const confettiCount = 100;

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 3 + 's';
        confetti.style.animationDuration = (Math.random() * 3 + 3) + 's';
        confettiContainer.appendChild(confetti);

        // Remove confetti after animation
        setTimeout(() => {
            confetti.remove();
        }, 7000);
    }
}

// Create Floating Hearts
function createHearts() {
    const heartsContainer = document.getElementById('heartsContainer');
    const heartSymbols = ['❤️', '💕', '💖', '💗', '💓', '💝'];

    setInterval(() => {
        const heart = document.createElement('div');
        heart.className = 'heart';
        heart.textContent = heartSymbols[Math.floor(Math.random() * heartSymbols.length)];
        heart.style.left = Math.random() * 100 + '%';
        heart.style.animationDuration = (Math.random() * 10 + 10) + 's';
        heart.style.fontSize = (Math.random() * 20 + 15) + 'px';
        heartsContainer.appendChild(heart);

        // Remove heart after animation
        setTimeout(() => {
            heart.remove();
        }, 15000);
    }, 800);
}

// Create Sparkles
function createSparkles() {
    const sparklesContainer = document.getElementById('sparklesContainer');

    setInterval(() => {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        sparkle.style.left = Math.random() * 100 + '%';
        sparkle.style.top = Math.random() * 100 + '%';
        sparkle.style.animationDelay = Math.random() * 2 + 's';
        sparklesContainer.appendChild(sparkle);

        // Remove sparkle after animation
        setTimeout(() => {
            sparkle.remove();
        }, 8000);
    }, 300);
}

// Music Control
const musicToggle = document.getElementById('musicToggle');
const bgMusic = document.getElementById('bgMusic');
const musicIcon = document.getElementById('musicIcon');
let isPlaying = false;

musicToggle.addEventListener('click', () => {
    if (isPlaying) {
        bgMusic.pause();
        musicIcon.textContent = '🎵';
        isPlaying = false;
    } else {
        bgMusic.play().catch(error => {
            console.log('Audio playback failed:', error);
        });
        musicIcon.textContent = '🔇';
        isPlaying = true;
    }
});

// Love Letter Modal
const loveLetterBtn = document.getElementById('loveLetter');
const letterContent = document.getElementById('letterContent');
const closeLetter = document.getElementById('closeLetter');

loveLetterBtn.addEventListener('click', () => {
    letterContent.classList.add('active');
    document.body.style.overflow = 'hidden';
});

closeLetter.addEventListener('click', () => {
    letterContent.classList.remove('active');
    document.body.style.overflow = 'auto';
});

// Close letter when clicking outside
letterContent.addEventListener('click', (e) => {
    if (e.target === letterContent) {
        letterContent.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// Scroll Animation Observer
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all fade-in elements
document.querySelectorAll('.fade-in').forEach(element => {
    observer.observe(element);
});

// Fireworks Effect (Additional Visual)
function createFirework(x, y) {
    const colors = ['#ff6b9d', '#c44569', '#8e44ad', '#ffd700', '#ff69b4'];
    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'fixed';
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.width = '5px';
        particle.style.height = '5px';
        particle.style.borderRadius = '50%';
        particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '1000';

        const angle = (Math.PI * 2 * i) / particleCount;
        const velocity = 2 + Math.random() * 2;
        const vx = Math.cos(angle) * velocity;
        const vy = Math.sin(angle) * velocity;

        document.body.appendChild(particle);

        let posX = x;
        let posY = y;
        let opacity = 1;

        const animate = () => {
            posX += vx;
            posY += vy;
            opacity -= 0.02;

            particle.style.left = posX + 'px';
            particle.style.top = posY + 'px';
            particle.style.opacity = opacity;

            if (opacity > 0) {
                requestAnimationFrame(animate);
            } else {
                particle.remove();
            }
        };

        animate();
    }
}

// Random fireworks on page
function randomFireworks() {
    setInterval(() => {
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * (window.innerHeight / 2);
        createFirework(x, y);
    }, 3000);
}

// Name Entry Validation
const nameEntryScreen = document.getElementById('nameEntryScreen');
const nameInput = document.getElementById('nameInput');
const submitNameBtn = document.getElementById('submitName');
const errorMessage = document.getElementById('errorMessage');
const mainContent = document.getElementById('mainContent');

function checkName() {
    const enteredName = nameInput.value.trim().toLowerCase();

    if (enteredName === 'prionty') {
        // Correct name - show the website
        errorMessage.textContent = '';
        nameEntryScreen.classList.add('hidden');

        setTimeout(() => {
            nameEntryScreen.style.display = 'none';
            mainContent.style.display = 'block';

            // Start all animations
            createConfetti();
            createHearts();
            createSparkles();
            randomFireworks();

            // Trigger confetti again after 5 seconds
            setTimeout(createConfetti, 5000);
        }, 500);
    } else if (enteredName === '') {
        errorMessage.textContent = 'Please enter your name 💕';
        nameInput.style.borderColor = '#c44569';
        setTimeout(() => {
            nameInput.style.borderColor = '#ff6b9d';
        }, 500);
    } else {
        errorMessage.textContent = 'Sorry, this message is not for you 💔';
        nameInput.style.borderColor = '#c44569';
        nameInput.value = '';
        setTimeout(() => {
            nameInput.style.borderColor = '#ff6b9d';
            errorMessage.textContent = '';
        }, 2000);
    }
}

submitNameBtn.addEventListener('click', checkName);

nameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        checkName();
    }
});

// Initialize all animations (only when name is verified)
window.addEventListener('load', () => {
    // Focus on name input when page loads
    nameInput.focus();
});

// Add sparkle effect on hover for reason cards
document.querySelectorAll('.reason-card').forEach(card => {
    card.addEventListener('mouseenter', function (e) {
        const rect = this.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;

        // Create mini sparkle burst
        for (let i = 0; i < 10; i++) {
            const sparkle = document.createElement('div');
            sparkle.style.position = 'fixed';
            sparkle.style.left = x + 'px';
            sparkle.style.top = y + 'px';
            sparkle.style.width = '3px';
            sparkle.style.height = '3px';
            sparkle.style.borderRadius = '50%';
            sparkle.style.backgroundColor = '#ffd700';
            sparkle.style.boxShadow = '0 0 10px #ffd700';
            sparkle.style.pointerEvents = 'none';
            sparkle.style.zIndex = '100';

            const angle = (Math.PI * 2 * i) / 10;
            const distance = 50;
            const targetX = x + Math.cos(angle) * distance;
            const targetY = y + Math.sin(angle) * distance;

            document.body.appendChild(sparkle);

            sparkle.animate([
                { left: x + 'px', top: y + 'px', opacity: 1 },
                { left: targetX + 'px', top: targetY + 'px', opacity: 0 }
            ], {
                duration: 800,
                easing: 'ease-out'
            }).onfinish = () => sparkle.remove();
        }
    });
});

// Smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add typing effect to main heading
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.textContent = '';

    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

// Optional: Uncomment to enable typing effect on load
// window.addEventListener('load', () => {
//     const heading = document.querySelector('.main-heading');
//     const originalText = heading.textContent;
//     typeWriter(heading, originalText, 80);
// });
