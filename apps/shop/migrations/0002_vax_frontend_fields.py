# Generated for VAX frontend upgrades
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='department',
            field=models.CharField(choices=[('skate', 'Skate'), ('clothes', 'Clothes')], default='skate', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='department',
            field=models.CharField(choices=[('skate', 'Skate'), ('clothes', 'Clothes')], default='skate', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.CharField(blank=True, max_length=60),
        ),
        migrations.AddField(
            model_name='product',
            name='hover_image',
            field=models.ImageField(blank=True, null=True, upload_to='products/hover/'),
        ),
        migrations.AddField(
            model_name='product',
            name='detail_image_1',
            field=models.ImageField(blank=True, null=True, upload_to='products/detail/'),
        ),
        migrations.AddField(
            model_name='product',
            name='detail_image_2',
            field=models.ImageField(blank=True, null=True, upload_to='products/detail/'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='main_image',
            field=models.ImageField(blank=True, null=True, upload_to='products/main/'),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('name', 'department')},
        ),
    ]
