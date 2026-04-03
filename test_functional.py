import requests

class TestFunctional:

    def test_delete_item_not_available_in_get(self, create_custom_item, delete_item, api_url):
        """Проверяем, что после удаления объявление больше не доступно через GET."""
        print("\nПроверка: после удаления, объявление не возвращается в GET")

        # Создаём объявление через фикстуру
        item_id = create_custom_item()
        print(f"Создано объявление: {item_id}")

        # Проверяем, что объявление доступно
        get_before = requests.get(f"{api_url}/api/1/item/{item_id}", timeout=10)
        assert get_before.status_code == 200, "Объявление не найдено сразу после создания"

        # Удаляем через фикстуру
        success = delete_item(item_id)
        assert success is True, "Не удалось удалить объявление"
        print("Объявление удалено")

        # Проверяем, что объявление больше не доступно
        import time
        time.sleep(0.5)  # Небольшая задержка для синхронизации

        get_after = requests.get(f"{api_url}/api/1/item/{item_id}", timeout=10)

        assert get_after.status_code == 404, \
            f"После удаления GET вернул {get_after.status_code}, ожидался 404"

        print("Подтверждено: удалённое объявление недоступно")

    def test_delete_item_statistic_also_deleted(self, create_custom_item, delete_item, api_url):
        """Проверяем, что после удаления объявления статистика тоже удаляется."""
        print("\nПроверка: после удаления статистика недоступна")

        # Создаём объявление с кастомной статистикой
        item_id = create_custom_item()
        print(f"Создано объявление: {item_id}")

        # Проверяем, что статистика существует до удаления
        stat_before = requests.get(f"{api_url}/api/1/statistic/{item_id}", timeout=10)
        assert stat_before.status_code == 200, \
            f"Статистика не найдена до удаления. Статус: {stat_before.status_code}"
        print("✓ Статистика существовала до удаления")

        # Удаляем объявление
        success = delete_item(item_id)
        assert success is True, "Не удалось удалить объявление"
        print("Объявление удалено")

        # Небольшая задержка для синхронизации
        import time
        time.sleep(0.5)

        # Проверяем, что статистика тоже удалена
        stat_after = requests.get(f"{api_url}/api/1/statistic/{item_id}", timeout=10)

        assert stat_after.status_code == 404, \
            f"После удаления статистика вернула {stat_after.status_code}, ожидался 404"

        print("Подтверждено: статистика удалена вместе с объявлением")

    def test_seller_multiple_items(self, api_url, create_multiple_items):
        """Проверяем, что продавец может создать несколько объявлений."""
        print("\nПроверка: продавец создаёт несколько объявлений")

        # Фикстура уже создала объявления
        items_data = create_multiple_items(count=3)
        seller_id = items_data["seller_id"]
        expected_ids = items_data["ids"]
        expected_count = len(expected_ids)

        print(f"Продавец ID: {seller_id}")
        print(f"Ожидаемые ID объявлений: {expected_ids}")

        # Получаем все объявления продавца
        get_response = requests.get(f"{api_url}/api/1/{seller_id}/item", timeout=10)
        assert get_response.status_code == 200, f"Ошибка получения объявлений: {get_response.status_code}"

        items = get_response.json()

        # Обрабатываем разные форматы ответа
        if isinstance(items, dict) and "items" in items:
            items = items["items"]

        # Проверяем, что создано минимум ожидаемое количество объявлений
        assert len(items) >= expected_count, \
            f"Найдено {len(items)} объявлений, ожидалось минимум {expected_count}"

        # Ищем наши созданные объявления среди всех
        found_ids = []
        for item in items:
            item_seller_id = item.get("sellerId") or item.get("sellerID")
            if item_seller_id == seller_id:
                item_id = item.get("id")
                if item_id in expected_ids:
                    found_ids.append(item_id)

        # Проверяем, что все наши объявления найдены
        assert len(found_ids) == expected_count, \
            f"Найдено только {len(found_ids)} из {expected_count} созданных объявлений"

        print(f"Продавец {seller_id} имеет {len(items)} объявлений")
        print(f"Все созданные объявления найдены: {found_ids}")
        print("Тестовые данные будут удалены фикстурой автоматически")