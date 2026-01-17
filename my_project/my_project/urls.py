from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
# Импорт стандартных функций для работы с JWT-токенами
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Импорт ваших представлений (проверьте, что My_app.vews совпадает с вашим названием папки и файла)
from my_app.views import ProductViewSet, StartParserView

# Настройка автоматического роутера для API товаров
router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    # Панель управления администратора
    path('admin/', admin.site.urls),

    # Основные API маршруты для товаров (получение списка и т.д.)
    path('api/', include(router.urls)),

    # Маршрут для запуска парсинга (POST запрос)
    path('api/parse-dns/', StartParserView.as_view(), name='parse_dns'),

    # --- ЭНДПОИНТЫ ДЛЯ АВТОРИЗАЦИИ (JWT) ---

    # Маршрут для логина: отправляем username и password -> получаем токены
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Маршрут для обновления токена доступа, когда старый истек
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# --- ОБРАБОТКА МЕДИА-ФАЙЛОВ ---
# Этот блок позволяет Django "отдавать" картинки из папки media вашему React-фронтенду
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)