import requests

class TestDelete:

    def test_delete_item_success(self, create_custom_item, delete_item, api_url):
        """Проверяем, что можно удалить существующее объявление. Ожидаем: код 200"""
        print("\nУдаление существующего объявления")

        # Создаём объявление через фикстуру
        item_id = create_custom_item()
        print(f"Создано объявление: {item_id}")

        # Удаляем через фикстуру
        success = delete_item(item_id)
        assert success is True, f"Не удалось удалить объявление {item_id}"

        print(f"Объявление {item_id} удалено")

        # Проверяем, что объявление действительно удалено (должен быть 404)
        import time

        for attempt in range(3):
            get_response = requests.get(f"{api_url}/api/1/item/{item_id}", timeout=10)

            if get_response.status_code == 404:
                print("Объявление больше не существует")
                break
            elif attempt < 2:
                print(f"Попытка {attempt + 1}: GET вернул {get_response.status_code}, ждём...")
                time.sleep(1)
            else:
                assert False, f"После удаления GET вернул {get_response.status_code}, ожидался 404"

        print("Тест пройден")