# VAX Shop

**VAX Shop** არის Django REST Framework-ზე შექმნილი ონლაინ skate shop პროექტი, რომელსაც აქვს შავი/ყვითელი დიზაინის storefront და custom manager admin panel.

## პროექტის აღწერა

VAX Shop-ის მიზანია მომხმარებელს მისცეს საშუალება მარტივად დაათვალიეროს skate პროდუქტები, გამოიყენოს კატეგორიები და ფილტრები, დაამატოს პროდუქტები კალათაში და გააკეთოს შეკვეთა. პროექტში ასევე დამატებულია ადმინისტრატორის პანელი, საიდანაც შესაძლებელია პროდუქტების, ბრენდების, კატეგორიების და მომხმარებლების მართვა.

## გამოყენებული ტექნოლოგიები

* Python
* Django
* Django REST Framework
* JWT Authentication
* PostgreSQL
* Redis
* Celery
* Docker / Docker Compose
* HTML
* CSS
* JavaScript
* Swagger / drf-spectacular

## ფუნქციები

* JWT login/register
* მომხმარებლის და მენეჯერის როლები
* Intro screen **Enter shop** ღილაკით
* VAX storefront navbar dropdown-ებით: Skate, Brands, Clothes, Cart
* Skate კატეგორიები:

  * Decks
  * Complete Skateboards
  * Trucks
  * Wheels
  * Bearings
  * Parts
* Clothes კატეგორიები:

  * Shoes
  * T-Shirts
  * Outerwear
  * Pants
  * Shorts
  * Headwear
* პროდუქტის ფილტრაცია კატეგორიით, ბრენდით, ფასით, ზომით, ძებნით და სორტირებით
* Product cards main image და hover image-ით
* Product detail modal main, hover და ორი detail image-ით
* Cart და checkout
* მომხმარებლის პროფილი
* Purchase history
* Custom `/admin-panel/` მენეჯერებისთვის:

  * პროდუქტების დამატება/რედაქტირება/წაშლა
  * main, hover და detail images upload
  * კატეგორიების მართვა
  * ბრენდების მართვა
  * მომხმარებლების და როლების მართვა
* Django default admin panel ხელმისაწვდომია `/admin/`
* Swagger UI ხელმისაწვდომია `/api/schema/swagger-ui/`
* Docker კონტეინერები:

  * Django
  * PostgreSQL
  * Redis
  * Celery

## პროექტის გაშვება

```bash
cp .env.example .env
docker compose up --build
```

შემდეგ გახსენით:

```text
http://localhost:8000/
```

## Admin Panel

Custom manager panel:

```text
http://localhost:8000/admin-panel/
```

Django default admin panel:

```text
http://localhost:8000/admin/
```

## Admin მონაცემები

```text
Username: levan
Password: Ronaldo07#
Role: manager
```

## სატესტო მომხმარებელი

```text
Username: anzora
Password: Messy10#
Role: customer
```

## სასარგებლო ბრძანებები

მიგრაციების გაშვება:

```bash
docker compose exec django python manage.py migrate
```

Superuser-ის შექმნა:

```bash
docker compose exec django python manage.py createsuperuser
```

ტესტების გაშვება:

```bash
docker compose exec django pytest
```

Django shell-ში შესვლა:

```bash
docker compose exec django python manage.py shell
```

მომხმარებლის manager-ად გადაქცევა:

```python
from django.contrib.auth import get_user_model

User = get_user_model()

u = User.objects.get(username='your_username')
u.role = 'manager'
u.is_staff = True
u.is_superuser = True
u.save()
```

## Product Images

Product იყენებს შემდეგ სურათებს:

* `main_image` — მთავარი სურათი, რომელიც product card-ზე ჩანს
* `hover_image` — სურათი, რომელიც mouse hover-ზე ჩანს
* `detail_image_1` და `detail_image_2` — product detail modal-ში გამოსაჩენი დამატებითი სურათები

## API Endpoints

მთავარი endpoints:

```text
POST /api/auth/register/
POST /api/auth/login/
GET/PATCH /api/auth/me/

GET/POST /api/products/
GET/PATCH/DELETE /api/products/{id}/

GET/POST /api/categories/
GET/POST /api/brands/

GET/POST /api/orders/

GET/POST /api/auth/users/     manager only
```

Swagger API documentation:

```text
http://localhost:8000/api/schema/swagger-ui/
```

## შენიშვნა ჟიურისთვის

პროექტის შესამოწმებლად შეგიძლიათ გამოიყენოთ ზემოთ მოცემული admin და test user მონაცემები. Admin panel-იდან შესაძლებელია პროდუქტების, ბრენდების, კატეგორიების და მომხმარებლების მართვა. ჩვეულებრივ მომხმარებელს შეუძლია პროდუქტების დათვალიერება, ფილტრაცია, კალათაში დამატება და შეკვეთის გაკეთება.
