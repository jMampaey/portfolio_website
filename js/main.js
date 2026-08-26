const mainNav = document.querySelector('.main-nav');
const hamburger = document.querySelector('.nav-hamburger');
const navLinks = document.querySelector('.nav-links');

const SCROLL_OFFSET = 24;

function smoothScrollToElement(target, duration = 600) {
    const startY = window.scrollY;
    const targetY = startY + target.getBoundingClientRect().top - SCROLL_OFFSET;
    const startTime = performance.now();

    function step(now) {
        const progress = Math.min((now - startTime) / duration, 1);
        const eased = progress < 0.5
            ? 4 * progress * progress * progress
            : 1 - Math.pow(-2 * progress + 2, 3) / 2;
        window.scrollTo(0, startY + (targetY - startY) * eased);
        if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
}

document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
        const target = document.querySelector(link.getAttribute('href'));
        if (!target) return;
        e.preventDefault();
        history.pushState(null, '', link.getAttribute('href'));
        smoothScrollToElement(target);
    });
});

if (window.location.hash) {
    const hashTarget = document.querySelector(window.location.hash);
    if (hashTarget) {
        window.scrollTo(0, 0);
        requestAnimationFrame(() => smoothScrollToElement(hashTarget));
    }
}

const NAV_SCROLL_THRESHOLD = 32;
let lastScrollY = window.scrollY;
window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;
    mainNav.classList.toggle('nav-scrolled', currentScrollY > 0);

    if (navLinks.classList.contains('nav-open')) {
        lastScrollY = currentScrollY;
    } else if (Math.abs(currentScrollY - lastScrollY) > NAV_SCROLL_THRESHOLD) {
        mainNav.classList.toggle('nav-hidden', currentScrollY > lastScrollY);
        lastScrollY = currentScrollY;
    }
}, { passive: true });

document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'g') {
        e.preventDefault();
        document.body.classList.toggle('show-grid');
    }
});

function setNavOpen(isOpen) {
    navLinks.classList.toggle('nav-open', isOpen);
    hamburger.setAttribute('aria-expanded', isOpen);
    document.body.classList.toggle('nav-scroll-lock', isOpen);
}

hamburger.addEventListener('click', () => {
    setNavOpen(!navLinks.classList.contains('nav-open'));
});

navLinks.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => setNavOpen(false));
});

Prism.hooks.add('after-highlight', (env) => {
    if (!env.element.closest('.code-block')) return;
    const lines = env.element.innerHTML.split('\n');
    if (lines[lines.length - 1] === '') lines.pop();
    env.element.innerHTML = lines.map(line => `<span class="code-line">${line || ' '}</span>`).join('');
});

document.querySelectorAll('.copy-code-button').forEach((button) => {
    button.addEventListener('click', () => {
        const codeEl = button.closest('.code-card').querySelector('code');
        const lines = codeEl.querySelectorAll('.code-line');
        const code = lines.length
            ? Array.from(lines).map(l => l.textContent).join('\n')
            : codeEl.textContent;
        navigator.clipboard.writeText(code).then(() => {
            const originalLabel = button.textContent;
            button.textContent = 'Copied!';
            setTimeout(() => {
                button.textContent = originalLabel;
            }, 1500);
        }).catch(() => {});
    });
});
