from rest_framework import viewsets, views, permissions
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .service import DNSScraperService


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для просмотра списка товаров.
    ReadOnlyModelViewSet позволяет только читать данные (GET запросы).
    """
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer

    # По умолчанию права доступа берутся из settings.py (AllowAny).
    # Если нужно закрыть каталог от неавторизованных, раскомментируй ниже:
    # permission_classes = [permissions.IsAuthenticated]


class StartParserView(views.APIView):
    """
    API для запуска робота-парсера.
    """

    # РЕКОМЕНДАЦИЯ: Чтобы робота не запускал кто угодно,
    # раскомментируй строку ниже (тогда запуск будет только для админов/авторизованных)
    # permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        # URL категории для парсинга (кухонная техника)
        main_url = "https://dns-shop.by/ru/category/e3d826d63bb17fd7/tehnika-dla-kuhni/"

        # Инициализируем наш сервис-робот
        scraper = DNSScraperService()

        try:
            # Запускаем сбор данных (метод run из services.py)
            parsed_items = scraper.run()  # или scraper.run(main_url) в зависимости от версии сервиса

            return Response({
                "status": "success",
                "message": "Робот успешно собрал данные",
                "count": len(parsed_items)
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Ошибка при работе робота: {str(e)}"
            }, status=500)