from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.
    Преобразует данные из базы данных SQLite в JSON формат для фронтенда.
    """
    class Meta:
        model = Product
        # Мы включаем все поля модели, чтобы на фронтенде были доступны:
        # id, category_name, name, price, link, image и created_at
        fields = '__all__'