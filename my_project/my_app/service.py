import time
import requests
from django.core.files.base import ContentFile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from .models import Product


class DNSScraperService:
    """
    Сервис для парсинга товаров с сайта DNS-shop.
    Использует Selenium для обхода защиты и загрузки динамического контента.
    """
    BASE_URL = "https://dns-shop.by"

    def __init__(self):
        # Настройка Chrome для работы в фоновом режиме (headless)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Подмена User-Agent для минимизации вероятности блокировки
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    def download_image(self, url):
        """
        Загружает изображение по URL и преобразует его в ContentFile для Django.
        """
        if not url:
            return None
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Извлекаем имя файла из URL
                file_name = url.split("/")[-1].split("?")[0]
                return ContentFile(response.content, name=file_name)
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")
        return None

    def run(self):
        """
        Основной цикл парсинга: категории -> подразделы -> товары.
        """
        main_url = f"{self.BASE_URL}/ru/category/e3d826d63bb17fd7/tehnika-dla-kuhni/"
        try:
            self.driver.get(main_url)
            time.sleep(5)  # Ожидание загрузки JS
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Получаем первые 3 подкатегории (например, посудомойки разных типов)
            sub_categories = soup.select('a.subcategory__item')[:3]
            parsed_products = []

            for sub in sub_categories:
                category_name = sub.get_text(strip=True)
                category_url = self.BASE_URL + sub.get('href')

                # Переход в конкретную подкатегорию
                self.driver.get(category_url)
                time.sleep(5)
                sub_soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # Собираем до 10 товаров из каждой категории
                product_cards = sub_soup.select('.catalog-product')[:10]

                for card in product_cards:
                    name_el = card.select_one('.catalog-product__name')
                    price_el = card.select_one('.product-buy__price') or card.select_one('.catalog-product__price')
                    img_el = card.select_one('.catalog-product__image img')

                    if name_el:
                        product_link = self.BASE_URL + name_el.get('href')
                        # Обработка Lazy Loading изображений
                        img_url = img_el.get('data-src') or img_el.get('src') if img_el else None

                        # Создаем запись в БД или получаем существующую по ссылке
                        product_obj, created = Product.objects.get_or_create(
                            link=product_link,
                            defaults={
                                'category_name': category_name,
                                'name': name_el.get_text(strip=True),
                                'price': price_el.get_text(strip=True) if price_el else "Цена не указана"
                            }
                        )

                        # Если товар новый и у него есть картинка — скачиваем её
                        if created and img_url:
                            image_file = self.download_image(img_url)
                            if image_file:
                                product_obj.image.save(image_file.name, image_file, save=True)

                        parsed_products.append(product_obj)

            return parsed_products

        finally:
            # Всегда закрываем браузер после завершения работы
            self.driver.quit()