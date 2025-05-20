// Файл для обработки оценок
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем всплывающие подсказки для оценок
    const gradeSpans = document.querySelectorAll('.grade-badge');
    gradeSpans.forEach(span => {
        const gradeValue = span.dataset.value;
        const gradeDate = span.dataset.date;
        const gradeComment = span.dataset.comment || 'Без комментария';
        
        // Создаем подсказку с деталями
        const tooltip = `Дата: ${gradeDate}\nКомментарий: ${gradeComment}`;
        span.setAttribute('title', tooltip);
    });
    
    // Подтверждение удаления оценки
    const deleteGradeForm = document.getElementById('delete-grade-form');
    if (deleteGradeForm) {
        deleteGradeForm.addEventListener('submit', function(e) {
            const confirmed = confirm('Вы уверены, что хотите удалить эту оценку?');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }
    
    // Валидация формы оценки
    const gradeForm = document.getElementById('grade-form');
    if (gradeForm) {
        gradeForm.addEventListener('submit', function(e) {
            const gradeValue = document.getElementById('value').value;
            if (gradeValue < 1 || gradeValue > 5) {
                alert('Оценка должна быть в диапазоне от 1 до 5');
                e.preventDefault();
            }
        });
    }
});
