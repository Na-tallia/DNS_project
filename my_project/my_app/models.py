from django.db import models


class Product(models.Model):
    category_name = models.CharField(max_length=255, verbose_name="Категория")
    name = models.CharField(max_length=500, verbose_name="Наименование")
    price = models.CharField(max_length=100, null=True, blank=True, verbose_name="Цена")
    link = models.URLField(unique=True, verbose_name="Ссылка")
    # Фото будет сохраняться в папку media/products/
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Фото")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
# Create your models here.
