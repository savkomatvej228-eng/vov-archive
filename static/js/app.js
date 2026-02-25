// Файл можно оставить пустым или добавить общие скрипты.
// Например, автоматическое обновление даты (если не используете встроенный скрипт).
document.addEventListener('DOMContentLoaded', function() {
    const dateSpan = document.getElementById('current-date');
    if (dateSpan) {
        const d = new Date();
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        dateSpan.innerText = `${day}.${month}.1945`;
    }
});