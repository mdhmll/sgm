// Дополнительная функциональность JavaScript для приложения

// Функция для подтверждения действий удаления
function confirmDelete(message) {
    return confirm(message || 'Вы уверены, что хотите удалить этот элемент?');
}

// Автоматически добавлять CSRF-токен во все POST-запросы
function addCSRFToken() {
    // Получаем CSRF-токен из мета-тега
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        const token = metaTag.getAttribute('content');
        
        // Добавляем токен во все формы без токена
        document.querySelectorAll('form[method="post"]').forEach(function(form) {
            if (!form.querySelector('input[name="csrf_token"]')) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                input.value = token;
                form.appendChild(input);
            }
        });
        
        // Добавляем csrf-токен во все AJAX-запросы
        // Это гарантирует, что все fetch/ajax запросы также будут защищены
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {
            options = options || {};
            
            // Только для POST, PUT, PATCH, DELETE запросов
            if (options.method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method.toUpperCase())) {
                if (!(options.headers instanceof Headers)) {
                    options.headers = new Headers(options.headers || {});
                }
                options.headers.set('X-CSRFToken', token);
            }
            
            return originalFetch(url, options);
        };
    }
}

// Включаем все всплывающие подсказки (tooltips) и фиксируем модальные окна
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем CSRF-токен во все формы и AJAX-запросы
    addCSRFToken();
    
    // Инициализация всплывающих подсказок Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            boundary: document.body // Фиксируем границы для предотвращения смещения
        });
    });
    
    // Активируем специальный режим обработки модальных окон
    // Детальная логика находится в файле modal-fix.js
    document.body.setAttribute('data-modal-handler', 'enabled');
    
    // Закрытие модальных окон по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.querySelector('.modal.show')) {
            let openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                let modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) modalInstance.hide();
            });
        }
    });
    
    // Автоматическое закрытие флеш-сообщений после 5 секунд
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Подсветка текущего пункта меню
    var currentPage = window.location.pathname;
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(function(link) {
        var href = link.getAttribute('href');
        if (currentPage === href || currentPage.startsWith(href) && href !== '/') {
            link.classList.add('active');
        }
    });
});