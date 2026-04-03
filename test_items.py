import requests


class TestItems:
    """Класс с тестами для объявлений"""

    def test_create_item_with_zero_statistics(self, create_custom_item, delete_item, api_url):
        """Проверяем, что можно создать объявление с нулевой статистикой"""
        print("\nСоздание объявления с нулевой статистикой")

        item_id = create_custom_item(
            name="Товар с нулевой статистикой",
            price=100,
            likes=0,
            views=0,
            contacts=0
        )

        # Получаем объявление
        response = requests.get(f"{api_url}/api/1/item/{item_id}", timeout=10)
        assert response.status_code == 200

        item = response.json()[0]

        # Проверяем, что статистика = 0
        assert item["statistics"]["likes"] == 0
        assert item["statistics"]["viewCount"] == 0
        assert item["statistics"]["contacts"] == 0

        print("Статистика с нулевыми значениями сохранилась корректно")

        delete_item(item_id)

    def test_create_item_success(self, create_custom_item, delete_item, api_url):
        """Проверяем, что можно создать объявление со всеми полями. Ожидаем: код 200, в ответе UUID"""
        print("\nСоздание объявления со всеми полями")

        # Создаём объявление с нужными параметрами
        item_id = create_custom_item(
            name="Name",
            price=5000,
            likes=10,
            views=100,
            contacts=5
        )

        # Проверяем формат UUID
        assert len(item_id) == 36, f"Неверная длина UUID: {len(item_id)}, получено: {item_id}"
        assert item_id.count("-") == 4, f"Неверный формат UUID: {item_id}"
        assert item_id.replace("-", "").isalnum(), f"UUID содержит недопустимые символы: {item_id}"

        print(f"Создано объявление с ID: {item_id}")

        # Получаем созданное объявление и проверяем поля
        get_response = requests.get(f"{api_url}/api/1/item/{item_id}", timeout=10)
        assert get_response.status_code == 200, "Не удалось получить созданное объявление"

        item_data = get_response.json()
        if isinstance(item_data, list):
            item = item_data[0]
        else:
            item = item_data

        # Проверяем значения полей
        assert item["name"] == "Name", f"Имя не совпадает: {item['name']} != Name"
        assert item["price"] == 5000, f"Цена не совпадает: {item['price']} != 5000"

        # Дополнительно проверим статистику
        assert item["statistics"]["likes"] == 10, "Likes не совпадают"
        assert item["statistics"]["viewCount"] == 100, "Views не совпадают"
        assert item["statistics"]["contacts"] == 5, "Contacts не совпадают"

        print(f"Проверено: имя='{item['name']}', цена={item['price']}")
        print(
            f"Статистика: лайки={item['statistics']['likes']}, просмотры={item['statistics']['viewCount']}, контакты={item['statistics']['contacts']}")
        print("Тест пройден")

        # Очистка
        delete_item(item_id)

    def test_get_item_by_id_success(self, create_custom_item, delete_item, api_url):
        """Проверяем, что можно получить объявление по его ID."""
        print("\nПолучение существующего объявления по ID")

        # Создаём тестовое объявление
        item_id = create_custom_item()
        print(f"Тестируем объявление с ID: {item_id}")

        # Получаем объявление по ID
        response = requests.get(f"{api_url}/api/1/item/{item_id}", timeout=10)

        assert response.status_code == 200, \
            f"Ожидался статус 200, получили {response.status_code}"

        data = response.json()

        # Проверяем структуру ответа
        assert isinstance(data, list), "Ответ должен быть массивом"
        assert len(data) > 0, "Массив не должен быть пустым"

        item = data[0]

        # Проверяем наличие основных полей
        required_fields = ["id", "sellerId", "name", "price", "statistics"]
        for field in required_fields:
            assert field in item, f"В ответе отсутствует поле '{field}'"

        # Проверяем, что ID совпадает
        assert item["id"] == item_id, \
            f"ID в ответе '{item['id']}' не совпадает с запрошенным '{item_id}'"

        # Проверяем типы данных
        assert isinstance(item["sellerId"], int), "sellerId должно быть числом"
        assert isinstance(item["name"], str), "name должно быть строкой"
        assert isinstance(item["price"], int), "price должно быть числом"

        # Проверяем статистику
        statistics = item["statistics"]
        assert isinstance(statistics, dict), "statistics должно быть объектом"

        expected_stats = ["likes", "viewCount", "contacts"]
        for field in expected_stats:
            assert field in statistics, f"В statistics отсутствует поле '{field}'"

        print(f"Объявление получено: {item['name']} - {item['price']} руб.")

        # Очистка
        delete_item(item_id)

    def test_get_items_by_seller_success(self, create_multiple_items, api_url):
        """Проверяем, что можно получить все объявления продавца.
        Ожидаем: код 200, массив из 3 объявлений, у каждого sellerId совпадает"""
        print("\nПолучение всех объявлений продавца")

        # Создаём 3 объявления через фикстуру
        items_data = create_multiple_items(count=3)
        seller_id = items_data["seller_id"]
        expected_ids = items_data["ids"]
        expected_count = len(expected_ids)

        print(f"Тестируем продавца с ID: {seller_id}")
        print(f"Создано объявлений: {expected_count}")

        # Получаем все объявления продавца
        response = requests.get(f"{api_url}/api/1/{seller_id}/item", timeout=10)
        assert response.status_code == 200, f"Ожидался 200, получили {response.status_code}"

        items = response.json()

        # Проверяем, что ответ - массив
        assert isinstance(items, list), "Ответ должен быть массивом"

        # Проверяем, что получили хотя бы наши объявления
        assert len(items) >= expected_count, \
            f"Ожидалось минимум {expected_count} объявлений, получили {len(items)}"

        # Собираем ID всех объявлений продавца
        found_ids = []
        for item in items:
            if item.get("sellerId") == seller_id:
                found_ids.append(item.get("id"))

        # Проверяем, что все наши объявления есть в списке
        for expected_id in expected_ids:
            assert expected_id in found_ids, f"Объявление {expected_id} не найдено у продавца"

        print(f"Найдено {len(found_ids)} объявлений продавца {seller_id}")
        print("Очистка будет выполнена фикстурой автоматически")