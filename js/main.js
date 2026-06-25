document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'g') {
        e.preventDefault();
        document.body.classList.toggle('show-grid');
    }
});

const hamburger = document.querySelector('.nav-hamburger');
const navLinks = document.querySelector('.nav-links');

hamburger.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('nav-open');
    hamburger.setAttribute('aria-expanded', isOpen);
});

document.querySelectorAll('.copy-code-button').forEach((button) => {
    button.addEventListener('click', () => {
        const code = button.closest('.code-card').querySelector('code').textContent;
        navigator.clipboard.writeText(code).then(() => {
            const originalLabel = button.textContent;
            button.textContent = 'Copied!';
            setTimeout(() => {
                button.textContent = originalLabel;
            }, 1500);
        }).catch(() => {});
    });
});
