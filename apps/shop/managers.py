from django.db import models


class PublishedProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')
