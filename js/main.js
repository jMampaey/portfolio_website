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
