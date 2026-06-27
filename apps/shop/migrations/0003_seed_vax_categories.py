from django.db import migrations
from django.utils.text import slugify


def seed_defaults(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Brand = apps.get_model('shop', 'Brand')
    defaults = [
        ('Decks', 'skate'), ('Complete Skateboards', 'skate'), ('Trucks', 'skate'),
        ('Wheels', 'skate'), ('Bearings', 'skate'), ('Parts', 'skate'),
        ('Shoes', 'clothes'), ('T-Shirts', 'clothes'), ('Outerwear', 'clothes'),
        ('Pants', 'clothes'), ('Shorts', 'clothes'), ('Headwear', 'clothes'),
    ]
    for name, department in defaults:
        Category.objects.get_or_create(name=name, department=department, defaults={'slug': f'{department}-{slugify(name)}'})
    Brand.objects.get_or_create(name='VAX', defaults={'slug': 'vax'})


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_vax_frontend_fields'),
    ]

    operations = [
        migrations.RunPython(seed_defaults, migrations.RunPython.noop),
    ]
