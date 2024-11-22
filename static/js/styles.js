// Añade efectos suaves al hacer clic en el botón de regresar
document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.addEventListener('click', (event) => {
            event.preventDefault(); // Evita el redireccionamiento inmediato
            backButton.style.transition = 'transform 0.3s ease-in-out';
            backButton.style.transform = 'scale(0.9)';
            setTimeout(() => {
                window.location.href = backButton.href; // Redirecciona después del efecto
            }, 300);
        });
    }
});
