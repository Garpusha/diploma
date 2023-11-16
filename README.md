Дипломный проект


Вводные
1. Создать суперпользователя
2. Создать пользователя с ролью admin в админке и взять его токен для запросов с админскими правами. Токен задается произвольный.
3. У пользователя 3 возможные роли - админ, продавец, покупатель
4. У пользователя может быть только 1 активный заказ одновременно. Он создается через orders или при добавлении первого товара в корзину

Запросы:
1. Импорт данных **import_requests.http**
	POST http://localhost:8000/import/ - запрос, выполняется с токеном админа. 
	"file": "имя файла"
	
	users.yaml содержит данные пользователей
	data.yaml содержит данные по заказам, товарам, парметрам, категориям  и т.д.

2. Работа с пользователями **users_requests.http** 
	**GET http://localhost:8000/users/** - просмотр всех пользователей, работает без токена
	
	**POST http://localhost:8000/users/** - создание пользователя, токен админа
	    "name": "имя пользователя",
    	"password": "пароль",
    	"role": "роль (admin, buyer, seller)",
    	"email": "адрес почты",
    	"address_1": "", - необязательные поля
    	"address_2": "",
    	"address_3": "",
    	"address_4": "",
    	"address_5": "",
    	"token": "" - пустое поле
	**PATCH http://localhost:8000/users/** - изменение данных пользователя, поля как у запроса POST, токен админа или самого пользователя
	
	**DELETE http://localhost:8000/users/** - удаление пользователя, токен админа
		"name": "имя пользователя"

3. Работа с магазинами **store_requests.http**

    **GET http://localhost:8000/stores/** - просмотр всех магазинов
    **POST http://localhost:8000/stores/** - создание магазина, токен админа
        "name": "название",
        "owner": id владельца, пользователь должен существовать,
        "delivery_cost": цена доставки из магазина,
        "active": 1/0 магазин работает или нет. Если магазин не работает, его товары не появляются в прайсе и их нельзя положить в корзину
	**PATCH http://localhost:8000/stores/** - изменение параметров магазина. Токен админа или хозяина магазина
        "id": 1, - id магазина, который меняем 
        "name": "Связной",
        "owner": 2,
        "delivery_cost": 200,
        "active": 0
	**DELETE http://localhost:8000/stores/** - удаление магазина, токен админа

4. Категории **category_requests.http**

	**GET http://localhost:8000/categories/** - просмотр всех категорий
	**POST http://localhost:8000/categories/** - создание категории, токен админа
		"name": "Видеокарты"
	**DELETE http://localhost:8000/categories/** - удаление категории
        "name": "Видеокарты"
	**PATCH http://localhost:8000/categories/** - переименование категории
        "id": 6,
        "name": "Мыши"

5. Товары **product_requests.http** Удалять и изменять товары может только admin. Добавлять товар может админ или продавец

    **GET http://localhost:8000/products/** - просмотр всех доваров в БД
    **POST http://localhost:8000/products/** - создание товара
        "name": "имя продукта",
        "category": 3, id категории, должна существовать
        "description": "Описание"
    **DELETE http://localhost:8000/products/** - удаление товара
        "id": 8 id товара для удаления
    **PATCH http://localhost:8000/products/** - изменение товара
        "id": 8,
        "name": "Test product_2",
        "category": 3,
        "description": "New test product"

6. Параметры **parameter_requests.http** Удалять и переименовывать параметры может admin, добавлять может также seller 
    **GET http://localhost:8000/parameters/** - просмотр параметров товаров
    **POST http://localhost:8000/parameters/** - добавление параметра 
        "name": "имя параметра (память, диагональ экрана, батарея итд)"
    **DELETE http://localhost:8000/parameters/** - удаление параметра
        "id": 8
    **PATCH http://localhost:8000/parameters/** - изменение параметра
        "id": 8,
        "name": "CPU"

7. Заказы **order_requests.http** Все заказы видит только админ, пользователь видит только свои 
    **GET http://localhost:8000/orders/?user=buyer_1&status=completed**
    **GET http://localhost:8000/orders/**
    **POST http://localhost:8000/orders/**
        id: - убрать id, создавать по токену 
