# VAX Shop

Django REST Framework skate shop project with a black/yellow storefront and custom manager admin panel.

## Features

- JWT login/register
- Customer and manager roles
- Burrow-style intro screen with **Enter shop** button
- VAX storefront navbar with dropdowns: Skate, Brands, Clothes, Cart
- Skate categories: Decks, Complete Skateboards, Trucks, Wheels, Bearings, Parts
- Clothes categories: Shoes, T-Shirts, Outerwear, Pants, Shorts, Headwear
- Product filters by category, brand, price, size, search, sort
- Product cards with main image and hover image
- Product detail modal with main, hover and two detail images
- Cart and checkout
- Custom `/admin-panel/` for managers:
  - add/edit/delete products
  - upload main, hover and detail images
  - manage categories
  - manage brands
  - manage accounts and roles
- Default Django admin still available at `/admin/`
- Swagger UI at `/api/schema/swagger-ui/`
- Docker: Django, PostgreSQL, Redis, Celery

## Run

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
http://localhost:8000/
```

Manager panel:

```text
http://localhost:8000/admin-panel/
```

## Useful commands

```bash
docker compose exec django python manage.py migrate
docker compose exec django python manage.py createsuperuser
docker compose exec django pytest
```

To make a manager from shell:

```bash
docker compose exec django python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='your_username')
u.role = 'manager'
u.is_staff = True
u.is_superuser = True
u.save()
```

## Product images

Product uses:

- `main_image` — normal card image
- `hover_image` — shown when mouse is on product card
- `detail_image_1` and `detail_image_2` — visible inside product detail modal

## API

Main endpoints:

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
