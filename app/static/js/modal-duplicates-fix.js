/**
 * Устранение проблемы дублирования модальных окон
 * Этот скрипт предотвращает отображение нескольких модальных окон одновременно
 * и устраняет проблему с модальными окнами внутри таблиц
 */

(function() {
    // Выполняем после загрузки DOM
    document.addEventListener('DOMContentLoaded', function() {
        // Проверка, не запущен ли скрипт уже (предотвращаем множественный запуск)
        if (window._modalDuplicatesFixApplied) return;
        window._modalDuplicatesFixApplied = true;
        
        // Добавляем класс к body для управления привязкой модальных окон
        document.body.classList.add('modals-fix-ready');
        /**
         * Функция для закрытия всех открытых модальных окон
         * кроме указанного (если передан)
         * @param {HTMLElement|null} exceptModal - модальное окно, которое нужно оставить открытым
         */
        function closeAllModalsExcept(exceptModal = null) {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(function(modal) {
                if (exceptModal !== modal) {
                    try {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) {
                            modalInstance.hide();
                        }
                    } catch (e) {
                        console.error('Не удалось закрыть модальное окно:', e);
                    }
                }
            });
        }

        // Глобально доступная функция для закрытия всех модальных окон
        window.closeAllModals = function() {
            closeAllModalsExcept();
        };        // Обработка кнопок, открывающих модальные окна
        const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
        modalTriggers.forEach(function(trigger) {
            // Проверяем, не был ли триггер уже обработан
            if (trigger.hasAttribute('data-modal-trigger-processed')) return;
            
            // Помечаем триггер как обработанный
            trigger.setAttribute('data-modal-trigger-processed', 'true');
            
            trigger.addEventListener('click', function(e) {
                // Предотвращаем множественные срабатывания
                if (e._modalTriggerProcessed) return;
                e._modalTriggerProcessed = true;
                
                // Закрываем все модальные окна перед открытием нового
                closeAllModals();
                
                // Перед открытием нового модального окна закрываем все существующие
                const targetModalId = trigger.getAttribute('data-bs-target');
                if (targetModalId) {
                    const targetModal = document.querySelector(targetModalId);
                    // Проверяем наличие целевого модального окна
                    if (!targetModal) {
                        console.error('Целевое модальное окно не найдено:', targetModalId);
                        return;
                    }
                    
                    // Используем setTimeout для избежания гонки условий с Bootstrap
                    setTimeout(() => {
                        // Проверка, что модальное окно не открыто
                        if (!targetModal.classList.contains('show')) {
                            try {
                                const modalInstance = new bootstrap.Modal(targetModal);
                                modalInstance.show();
                            } catch (err) {
                                console.error('Не удалось открыть модальное окно:', err);
                            }
                        }
                    }, 50);
                }
            });
        });

        // Следим за событиями модальных окон
        document.body.addEventListener('show.bs.modal', function(event) {
            // Получаем модальное окно, которое вызвало событие
            const modal = event.target;
            
            // Даем немного времени, чтобы закрыть другие окна
            setTimeout(() => closeAllModalsExcept(modal), 10);
            
            // Добавляем атрибут, чтобы отметить, что это последнее открытое модальное окно
            modal.setAttribute('data-active-modal', 'true');
            
            // Проверяем z-index, чтобы убедиться, что модалки не перекрываются
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length > 0) {
                const highestZIndex = Array.from(openModals)
                    .map(m => parseInt(window.getComputedStyle(m).zIndex) || 1050)
                    .reduce((max, val) => Math.max(max, val), 1050);
                
                modal.style.zIndex = (highestZIndex + 10).toString();
            }
        });
        
        // Обрабатываем закрытие модальных окон
        document.body.addEventListener('hidden.bs.modal', function(event) {
            // Удаляем атрибут с закрытого модального окна
            event.target.removeAttribute('data-active-modal');
            
            // Проверяем, остались ли открытые модальные окна
            if (!document.querySelector('.modal.show')) {
                // Если нет открытых модальных окон, убираем стили блокировки
                document.body.style.paddingRight = '';
                document.body.classList.remove('modal-open');
            }
        });

        // Устанавливаем обработчик для клавиши Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' || e.keyCode === 27) {
                // Закрываем последнее открытое модальное окно
                const activeModal = document.querySelector('.modal[data-active-modal="true"]');
                if (activeModal) {
                    const modalInstance = bootstrap.Modal.getInstance(activeModal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                } else {
                    // Если нет помеченного активного окна, закрываем все
                    closeAllModalsExcept();
                }
            }
        });
    });
})();
