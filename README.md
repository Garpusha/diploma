Дипломный проект  


Вводные  
1. Создать суперпользователя  
2. Создать пользователя с ролью admin в админке и взять его токен для запросов с админскими правами. Токен задается произвольный.  
3. У пользователя 3 возможные роли - админ, продавец, покупатель  
4. У пользователя может быть только 1 активный заказ одновременно. Он создается через orders или при добавлении первого товара в корзину  
5. .env-файл:  
    DB_ENGINE=django.db.backends.postgresql  
    DB_NAME=  
    DB_HOST=127.0.0.1  
    DB_PORT=5432  
    DB_USER=  
    DB_PASSWORD=  
    EMAIL_LOGIN=  
    EMAIL_PASSWORD=  

Запросы:
1. Импорт данных **import_requests.http**  
	POST http://localhost:8000/import/ - запрос, выполняется с токеном админа. Файл должен лежать в корневой папке проекта
	"file": "имя файла"  
	
	users.yaml содержит данные пользователей  
	data.yaml содержит данные по заказам, товарам, параметрам, категориям  и т.д.  

2. Работа с пользователями **users_requests.http**  
	**GET http://localhost:8000/users/** - просмотр всех пользователей, работает без токена  
	**POST http://localhost:8000/users/** - создание пользователя, нужен токен админа.
	"name": "имя пользователя",  
    	"password": "пароль",  
    	"role": "роль (admin, buyer, seller)",  
    	"email": "адрес почты",  
    	"address_1": "", - необязательные поля  
    	"address_2": "",  
    	"address_3": "",  
    	"address_4": "",  
    	"address_5": ""    	
	**PATCH http://localhost:8000/users/** - изменение данных пользователя (кроме имени), поля как у запроса POST, токен админа или самого пользователя  
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
    **POST http://localhost:8000/orders/**  - исполнение заказа, нужен токен покупателя  
        "id": 2  
    **PATCH http://localhost:8000/orders/** - Метод patch используется для отмены заказа, заказу проставляется статус canceled. Право только у админа и хозяина заказа  
        "id": 2  
    **DELETE http://localhost:8000/orders/** - Полное удаление заказа. Нужен токен амина или покупателя  
        "id": 2  
  
8. Авторизация **auth_requests.http** используется для выдачи нового токена, сброса пароля, активации нового  
По запросу с "operation": "authorize" можно получить новый токен, указав верный пароль. Если пользователь забыл пароль, по запросу "operation": "reset" ему на почту высылается новый токен. По запросу "operation": "activate" с новым токеном можно установить новый пароль.  
**POST http://localhost:8000/authorization/**  
    "operation": "authorize",  
    "username": "test_user",  
    "password": "12345"  
  
    "operation": "reset",  
    "username": "test_user"  
  
    "operation": "activate",  
    "username": "test_user",  
    "password": "password"  
  
9. Корзина заказов **cart_requests.http**  
**GET http://localhost:8000/cart** - вывод товаров в корзине, нужен токен. Пользователь видит свою корзину, админ все.  
**POST http://localhost:8000/cart/** - добавление довара в корзину из конкретного магазина. Токен пользователя  
    "product": 3,  
    "store": 1,  
    "quantity": 10  
**DELETE  http://localhost:8000/cart/**  Удаление товара из корзины, токен пользователя  
    "position": 19,  
    "quantity": 1  
  
10. Товары в магазине **product_in_store_requests.http** - добавлять, удалять и изменять наличие товара в магазине может только admin или хозяин магазина.  
**GET http://localhost:8000/product_in_store/?store=Связной&product=IPhone 14** вывод перечня товаров в магазинах  
**GET http://localhost:8000/product_in_store/**  
**POST http://localhost:8000/product_in_store/** - добавление товара в магазин. Нужен токен.  
    "product": 9,  
    "store": 8,  
    "quantity": 5,  
    "price": 200  
**PATCH http://localhost:8000/product_in_store/** - изменение количества товаров в магазине. Нужен токен.  
    "product": 9,  
    "store": 8,  
    "quantity": 15,  
    "price": 200  
**DELETE http://localhost:8000/product_in_store/** - удаление товара, нужен токен. Установить delete_product: yes, если необходимо полностью удалить позицию из перечня товаров магазина  
    "product": 1,  
    "store": 1,  
    "quantity": 40,  
    "delete_product": "no"  

11. Параметры товаров **http://localhost:8000/product_parameters/** - добавлять параметр может проавец и админ. Удалять и менять только админ.  
**GET http://localhost:8000/product_parameters/** - вывод текущих параметров
**POST http://localhost:8000/product_parameters/** - создание связи. Токен админа или продавца  
    "parameter": 5,  
    "product": 2,  
    "value": "600"  
**DELETE http://localhost:8000/product_parameters/** - удаление. Токен админа.  
    "id": 3  
**PATCH http://localhost:8000/product_parameters/** - изменение. Токен админа.  
    "id": 3,  
    "product": 2,  
    "parameter": 5,  
    "value": 1200  


