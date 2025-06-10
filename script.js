// webapp/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Получаем объект для взаимодействия с Telegram
    const tg = window.Telegram.WebApp;

    // --- ДАННЫЕ (для демо берем прямо из JS) ---
    // В реальном проекте эти данные будут приходить с вашего бэкенда.
    const products = [
        // ИЗМЕНЕНИЕ: Пути к картинкам теперь относительные, от корня сайта.
        // Ваш веб-сервер (Nginx) должен быть настроен так, чтобы 
        // раздавать папку /images как статическую директорию.
        { id: 1, name: "Туфли 'Fuego'", price: 5200, img: "/images/product_1.jpg" },
        { id: 2, name: "Платье 'Rhytm'", price: 3800, img: "/images/product_2.jpg" },
        { id: 3, name: "Ботинки 'El Paso'", price: 4500, img: "/images/product_3.jpg" },
        { id: 4, name: "Юбка 'Carmen'", price: 3100, img: "/images/product_4.jpg" }
    ];

    const productList = document.getElementById('product-list');
    let cart = []; // Наша корзина (массив ID товаров)

    // --- Отрисовка товаров ---
    function renderProducts() {
        productList.innerHTML = ''; // Очищаем список перед отрисовкой
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <img src="${product.img}" alt="${product.name}">
                <div class="product-title">${product.name}</div>
                <div class="product-price">${product.price} руб.</div>
                <button class="add-to-cart-btn" data-id="${product.id}">В корзину</button>
            `;
            productList.appendChild(card);
        });
    }

    // --- Логика корзины ---
    productList.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('add-to-cart-btn')) {
            const productId = parseInt(e.target.dataset.id);
            cart.push(productId);
            // Даем пользователю тактильную обратную связь
            try {
                tg.HapticFeedback.notificationOccurred('success');
            } catch (e) {
                console.log('Haptic feedback is not available on this platform.');
            }
            updateMainButton();
        }
    });

    // --- Взаимодействие с Telegram ---
    tg.ready(); // Сообщаем Telegram, что приложение готово

    // Настраиваем главную кнопку Telegram
    const mainButton = tg.MainButton;
    mainButton.textColor = '#FFFFFF';
    mainButton.color = '#2cab37'; // Зеленый цвет для кнопки
    
    // Функция для обновления состояния главной кнопки
    function updateMainButton() {
        if (cart.length > 0) {
            mainButton.setText(`Добавить в корзину (${cart.length})`);
            if (!mainButton.isVisible) {
                mainButton.show();
            }
        } else {
            if (mainButton.isVisible) {
                mainButton.hide();
            }
        }
    }

    // Обработчик нажатия на главную кнопку
    tg.onEvent('mainButtonClicked', function() {
        // При нажатии отправляем данные о корзине в бот
        // Данные должны быть в формате строки JSON
        const dataToSend = JSON.stringify({
            'source': 'webapp_catalog',
            'items': cart
        });
        tg.sendData(dataToSend);
    });

    // --- Начальный запуск ---
    updateMainButton(); // Скрываем кнопку при запуске, если корзина пуста
    renderProducts();
});