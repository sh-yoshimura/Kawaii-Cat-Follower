document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const playground = document.getElementById('playground');
    const catCharacter = document.getElementById('cat-character');
    const catImg = catCharacter.querySelector('.cat-img');
    const catBubble = document.getElementById('cat-bubble');
    const effectsContainer = document.getElementById('effects-container');
    const clickCountEl = document.getElementById('click-count');
    const totalDistanceEl = document.getElementById('total-distance');
    const soundToggleBtn = document.getElementById('sound-toggle');
    const soundIcon = document.getElementById('sound-icon');

    // App State
    let soundEnabled = true;
    let clickCount = 0;
    let totalDistancePixels = 0;

    // Relative Position State (0.0 to 1.0 ratio of screen dimensions)
    let relX = 0.5;
    let relY = 0.5;

    // Pixel Coordinates
    let currentX = window.innerWidth * relX;
    let currentY = window.innerHeight * relY;
    let targetX = currentX;
    let targetY = currentY;

    let isMoving = false;
    let baseSpeed = 6;
    let animFrameId = null;

    // Preload Animation Assets
    const catIdleImage = 'assets/cat.png';
    const catWalkFrames = ['assets/cat_walk1.png', 'assets/cat_walk2.png'];

    [catIdleImage, ...catWalkFrames].forEach(src => {
        const img = new Image();
        img.src = src;
    });

    // Helper: Dynamic Cat Dimensions based on CSS responsiveness
    function getCatDimensions() {
        const rect = catCharacter.getBoundingClientRect();
        return {
            width: rect.width || 100,
            height: rect.height || 100
        };
    }

    // Sound Synthesizer (Web Audio API)
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    function initAudio() {
        if (!audioCtx) {
            audioCtx = new AudioContext();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
    }

    function playMeowSound() {
        if (!soundEnabled) return;
        initAudio();
        if (!audioCtx) return;

        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc.type = 'sine';
            const now = audioCtx.currentTime;

            osc.frequency.setValueAtTime(650, now);
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.15);
            osc.frequency.exponentialRampToValueAtTime(520, now + 0.4);

            gain.gain.setValueAtTime(0, now);
            gain.gain.linearRampToValueAtTime(0.2, now + 0.05);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start(now);
            osc.stop(now + 0.4);
        } catch (e) {
            console.warn('Audio playback error:', e);
        }
    }

    function playStepSound() {
        if (!soundEnabled) return;
        initAudio();
        if (!audioCtx) return;

        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            const now = audioCtx.currentTime;

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(400 + Math.random() * 100, now);
            osc.frequency.exponentialRampToValueAtTime(200, now + 0.08);

            gain.gain.setValueAtTime(0.05, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start(now);
            osc.stop(now + 0.08);
        } catch (e) {
            // Ignore step audio fail
        }
    }

    // Set Position in Viewport
    function setCatPosition(x, y) {
        const dims = getCatDimensions();
        const clampedX = Math.max(dims.width / 2, Math.min(x, window.innerWidth - dims.width / 2));
        const clampedY = Math.max(dims.height / 2, Math.min(y, window.innerHeight - dims.height / 2));

        currentX = clampedX;
        currentY = clampedY;
        relX = currentX / window.innerWidth;
        relY = currentY / window.innerHeight;

        catCharacter.style.transform = `translate3d(${currentX - dims.width / 2}px, ${currentY - dims.height / 2}px, 0)`;
    }

    // Initialize Cat Position
    setCatPosition(currentX, currentY);

    // Pointer Handler (Handles Click & Touch Seamlessly)
    function handlePointerAction(clientX, clientY, targetEl) {
        if (targetEl.closest('.app-header') || targetEl.closest('.app-footer')) {
            return;
        }

        // Check if user clicked directly on the cat
        if (targetEl.closest('#cat-character')) {
            triggerPurrEffect();
            return;
        }

        const dims = getCatDimensions();
        targetX = Math.max(dims.width / 2, Math.min(clientX, window.innerWidth - dims.width / 2));
        targetY = Math.max(dims.height / 2, Math.min(clientY, window.innerHeight - dims.height / 2));

        clickCount++;
        clickCountEl.textContent = clickCount;

        // Spawn Paw Print & Ripple Effects
        createClickEffects(targetX, targetY);

        // Sound & Speech
        playMeowSound();
        showSpeechBubble(['とことこ…', 'ニャ〜！', 'おさんぽ！', 'まて〜！', 'なになに？'][Math.floor(Math.random() * 5)]);

        if (!isMoving) {
            isMoving = true;
            catCharacter.classList.remove('idle');
            catCharacter.classList.add('walking');
            updateMotion();
        }
    }

    playground.addEventListener('pointerdown', (e) => {
        handlePointerAction(e.clientX, e.clientY, e.target);
    });

    // Main Motion Loop & Walking Frame Switcher
    let stepTimer = 0;
    let walkFrameIndex = 0;

    function updateMotion() {
        const dx = targetX - currentX;
        const dy = targetY - currentY;
        const distance = Math.hypot(dx, dy);

        // Speed adapts dynamically to screen scale
        const currentSpeed = Math.max(4, Math.min(baseSpeed, window.innerWidth * 0.01));

        if (distance < currentSpeed + 1) {
            // Reached target
            setCatPosition(targetX, targetY);

            isMoving = false;
            catCharacter.classList.remove('walking');
            catCharacter.classList.add('idle');
            catImg.src = catIdleImage; // Reset to idle posture
            cancelAnimationFrame(animFrameId);
            return;
        }

        // Calculate direction & orientation
        const angle = Math.atan2(dy, dx);
        const vx = Math.cos(angle) * currentSpeed;
        const vy = Math.sin(angle) * currentSpeed;

        setCatPosition(currentX + vx, currentY + vy);
        totalDistancePixels += currentSpeed;

        // Update Stats (100px approx = 1 meter)
        totalDistanceEl.textContent = `${(totalDistancePixels / 100).toFixed(1)} m`;

        // Flip image based on direction (facing left or right)
        if (dx < -5) {
            catImg.style.transform = 'scaleX(-1)';
        } else if (dx > 5) {
            catImg.style.transform = 'scaleX(1)';
        }

        // Footstep sound & paw trail interval + Frame Flip for real walking movement
        stepTimer++;
        if (stepTimer % 8 === 0) {
            walkFrameIndex = (walkFrameIndex + 1) % catWalkFrames.length;
            catImg.src = catWalkFrames[walkFrameIndex];
        }

        if (stepTimer % 16 === 0) {
            playStepSound();
            spawnTrailPaw(currentX, currentY);
        }

        animFrameId = requestAnimationFrame(updateMotion);
    }

    // Effect Creators
    function createClickEffects(x, y) {
        // Ripple Ring
        const ripple = document.createElement('div');
        ripple.className = 'click-ripple';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        effectsContainer.appendChild(ripple);

        // Target Paw Mark
        const paw = document.createElement('div');
        paw.className = 'paw-print';
        paw.style.left = `${x}px`;
        paw.style.top = `${y}px`;
        paw.textContent = '🐾';
        effectsContainer.appendChild(paw);

        setTimeout(() => {
            ripple.remove();
            paw.remove();
        }, 1200);
    }

    function spawnTrailPaw(x, y) {
        const dims = getCatDimensions();
        const trailPaw = document.createElement('div');
        trailPaw.className = 'paw-print';
        trailPaw.style.fontSize = '1rem';
        trailPaw.style.left = `${x}px`;
        trailPaw.style.top = `${y + dims.height / 3}px`;
        trailPaw.style.opacity = '0.5';
        trailPaw.textContent = '🐾';
        effectsContainer.appendChild(trailPaw);

        setTimeout(() => trailPaw.remove(), 800);
    }

    function triggerPurrEffect() {
        playMeowSound();
        showSpeechBubble('ゴロゴロ…❤️');

        catCharacter.classList.add('purring');
        setTimeout(() => catCharacter.classList.remove('purring'), 1200);

        // Spawn Heart Particles
        for (let i = 0; i < 5; i++) {
            const heart = document.createElement('div');
            heart.className = 'heart-particle';
            heart.textContent = '💖';
            heart.style.left = `${currentX}px`;
            heart.style.top = `${currentY - 20}px`;
            heart.style.setProperty('--dx', `${(Math.random() - 0.5) * 80}px`);
            effectsContainer.appendChild(heart);

            setTimeout(() => heart.remove(), 1000);
        }
    }

    function showSpeechBubble(text) {
        catBubble.textContent = text;
        catBubble.classList.add('active');
        setTimeout(() => {
            catBubble.classList.remove('active');
        }, 1800);
    }

    // Toggle Sound Button
    soundToggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        soundEnabled = !soundEnabled;
        soundIcon.textContent = soundEnabled ? '🔊' : '🔇';
    });

    // Window Resize / Orientation Change Handler
    window.addEventListener('resize', () => {
        const newX = window.innerWidth * relX;
        const newY = window.innerHeight * relY;
        setCatPosition(newX, newY);
    });
});
