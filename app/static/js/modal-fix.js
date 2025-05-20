/**
 * Решение проблемы "дрожания" модальных окон (v2.0)
 *
 * Этот скрипт решает проблему дрожания (смещения) модальных окон при их открытии/закрытии.
 * Основная причина проблемы - изменение ширины страницы из-за появления/исчезновения полосы прокрутки.
 */

// Запускаем после полной загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    
    // ЧАСТЬ 1: ГЛОБАЛЬНЫЕ НАСТРОЙКИ
    
    // Определяем ширину полосы прокрутки для текущего браузера
    const scrollbarWidth = calculateScrollbarWidth();
    
    // Применяем глобальные стили для предотвращения дрожания
    const style = document.createElement('style');
    style.innerHTML = `
        body.modal-fix-applied {
            overflow-y: scroll !important; /* Всегда показываем вертикальную прокрутку */
            padding-right: 0 !important;   /* Избегаем смещения контента */
        }
        body.modal-open-fixed {
            overflow: hidden !important;   /* Блокируем прокрутку при открытом модальном окне */
            position: fixed !important;    /* Фиксируем позицию страницы */
            width: 100% !important;        /* Предотвращаем смещение контента */
        }
        .modal-dialog.no-jump {
            transform: none !important;    /* Отключаем анимацию, которая может вызывать дрожание */
            margin: 1.75rem auto !important; /* Фиксированный отступ сверху */
        }
    `;
    document.head.appendChild(style);
    
    // Сразу добавляем класс для постоянного отображения полосы прокрутки
    document.body.classList.add('modal-fix-applied');
    
    // ЧАСТЬ 2: ОБРАБОТКА МОДАЛЬНЫХ ОКОН
    
    // Получаем все модальные окна
    const modals = document.querySelectorAll('.modal');
    let scrollY = 0; // Для сохранения позиции прокрутки
    
    modals.forEach(function(modal) {
        // Статически позиционируем внутренний контент для предотвращения дрожания
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.position = 'relative';
        }
        
        // Отключаем встроенную анимацию Bootstrap для большей стабильности
        const modalDialog = modal.querySelector('.modal-dialog');
        if (modalDialog) {
            modalDialog.classList.add('no-jump');
        }
          // ПЕРЕД ОТКРЫТИЕМ МОДАЛЬНОГО ОКНА
        modal.addEventListener('show.bs.modal', function(event) {
            // Закрываем все другие открытые модальные окна
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(function(openModal) {
                if (openModal !== modal) {
                    // Получаем экземпляр Bootstrap Modal и закрываем его
                    const modalInstance = bootstrap.Modal.getInstance(openModal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            });
            
            // Сохраняем текущую позицию прокрутки
            scrollY = window.scrollY;
            
            // Применяем классы и стили для фиксации страницы
            setTimeout(function() {
                document.body.classList.add('modal-open-fixed');
                document.body.style.top = `-${scrollY}px`;
            }, 10); // Небольшая задержка для синхронизации с анимацией Bootstrap
        });
        
        // ПОСЛЕ ОТКРЫТИЯ
        modal.addEventListener('shown.bs.modal', function() {
            // Окончательно фиксируем модальное окно
            modalDialog?.classList.add('modal-fixed-dialog');
        });
        
        // ПЕРЕД ЗАКРЫТИЕМ
        modal.addEventListener('hide.bs.modal', function() {
            // Подготавливаемся к восстановлению прокрутки
            modalDialog?.classList.remove('modal-fixed-dialog');
        });
        
        // ПОСЛЕ ЗАКРЫТИЯ
        modal.addEventListener('hidden.bs.modal', function() {
            // Восстанавливаем все стили и классы
            document.body.classList.remove('modal-open-fixed');
            document.body.style.top = '';
            
            // Восстанавливаем позицию прокрутки
            window.scrollTo(0, scrollY);
        });
    });
    
    // ЧАСТЬ 3: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    
    // Функция для расчёта ширины полосы прокрутки
    function calculateScrollbarWidth() {
        // Создаём элемент с прокруткой
        const outer = document.createElement('div');
        outer.style.visibility = 'hidden';
        outer.style.overflow = 'scroll';
        document.body.appendChild(outer);
        
        // Создаём внутренний элемент
        const inner = document.createElement('div');
        outer.appendChild(inner);
        
        // Вычисляем разницу в ширине
        const scrollbarWidth = outer.offsetWidth - inner.offsetWidth;
        
        // Удаляем временные элементы
        outer.parentNode.removeChild(outer);
        
        return scrollbarWidth;
    }
});
