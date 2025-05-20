/**
 * scroll-lock.js - Улучшенный способ предотвращения прокрутки при открытии модальных окон
 * Дополнительный модуль для решения проблемы дрожания модальных окон
 */

(function() {
    // Сохраняем ширину полосы прокрутки
    const scrollbarWidth = getScrollbarWidth();
    
    // Переменная для отслеживания состояния блокировки
    let lockState = {
        locked: false,
        scrollTop: 0,
        previousPaddingRight: ''
    };
    
    // Измеряем ширину полосы прокрутки
    function getScrollbarWidth() {
        // Создаем внешний div
        const outer = document.createElement('div');
        outer.style.visibility = 'hidden';
        outer.style.width = '100px';
        outer.style.msOverflowStyle = 'scrollbar'; // нужно для WinJS приложений
        
        document.body.appendChild(outer);
        
        const widthNoScroll = outer.offsetWidth;
        // Принудительное появление scrollbar
        outer.style.overflow = 'scroll';
        
        // Добавляем внутренний div
        const inner = document.createElement('div');
        inner.style.width = '100%';
        outer.appendChild(inner);        
        
        const widthWithScroll = inner.offsetWidth;
        
        // Удаляем divs
        outer.parentNode.removeChild(outer);
        
        return widthNoScroll - widthWithScroll;
    }
    
    // Функция для блокировки прокрутки
    window.lockScroll = function() {
        if (lockState.locked) return;
        
        // Сохраняем текущую позицию прокрутки
        lockState.scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        lockState.previousPaddingRight = document.body.style.paddingRight;
        
        // Применяем фиксированную позицию к body
        document.body.style.top = `-${lockState.scrollTop}px`;
        document.body.style.position = 'fixed';
        document.body.style.width = '100%';
        
        // Компенсируем ширину полосы прокрутки, чтобы избежать смещения контента
        if (window.innerWidth > document.documentElement.clientWidth) {
            document.body.style.paddingRight = `${scrollbarWidth}px`;
            
            // Также добавляем отступ для fixed-элементов
            const fixedElements = document.querySelectorAll('.navbar-fixed-top, .navbar-sticky-top, .sticky-top');
            fixedElements.forEach(el => {
                el.style.paddingRight = `${scrollbarWidth}px`;
            });
        }
        
        lockState.locked = true;
    };
    
    // Функция для разблокировки прокрутки
    window.unlockScroll = function() {
        if (!lockState.locked) return;
        
        // Восстанавливаем позицию
        document.body.style.position = '';
        document.body.style.width = '';
        document.body.style.top = '';
        document.body.style.paddingRight = lockState.previousPaddingRight;
        
        // Возвращаем отступы fixed-элементов
        const fixedElements = document.querySelectorAll('.navbar-fixed-top, .navbar-sticky-top, .sticky-top');
        fixedElements.forEach(el => {
            el.style.paddingRight = '';
        });
        
        // Восстанавливаем позицию прокрутки
        window.scrollTo(0, lockState.scrollTop);
        
        lockState.locked = false;
    };
      // Автоматическое связывание с модальными окнами Bootstrap
    document.addEventListener('DOMContentLoaded', function() {
        // Обрабатываем события модальных окон
        document.body.addEventListener('shown.bs.modal', function(event) {
            // Проверяем, есть ли уже открытые модальные окна
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length > 1) {
                // Если есть несколько открытых модальных окон, закрываем все, кроме текущего
                openModals.forEach(function(modal) {
                    if (modal !== event.target) {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) {
                            modalInstance.hide();
                        }
                    }
                });
            }
            window.lockScroll();
        });
        
        document.body.addEventListener('hidden.bs.modal', function() {
            if (!document.querySelector('.modal.show')) {
                // Разблокируем только если нет других открытых модальных окон
                window.unlockScroll();
            }
        });
        
        // Глобальная функция для закрытия всех модальных окон
        window.closeAllModals = function() {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(function(modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        };
    });
})();
