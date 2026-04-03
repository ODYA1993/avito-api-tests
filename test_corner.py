import requests

import requests

import requests

BASE_URL = "https://qa-internship.avito.com"


class TestCornerCases:

    def test_post_creates_new_id_each_time(self, create_custom_item, delete_item):
        """Проверяем, что каждый POST запрос создаёт новое объявление с разным ID."""
        print("\nПроверка создания уникальных ID при POST запросах")

        created_ids = []

        # Создаём два объявления
        for i in range(2):
            item_id = create_custom_item()
            created_ids.append(item_id)
            print(f"Создано объявление {i + 1} с ID: {item_id}")

        # Проверяем, что ID разные
        assert len(set(created_ids)) == len(created_ids), \
            f"Найдены дубликаты ID: {created_ids}"

        print("Все ID уникальны")

        # Очистка
        for item_id in created_ids:
            delete_item(item_id)

    def test_very_long_name(self, create_custom_item, delete_item):
        """Проверяем, как API обрабатывает очень длинное название."""
        print("\nПроверка с очень длинным названием (1000 символов)")

        long_name = "A" * 1000

        # Создаём объявление с длинным названием
        item_id = create_custom_item(name=long_name)
        print(f"Создано объявление с ID: {item_id}")

        # Получаем созданное объявление и проверяем название
        get_response = requests.get(f"{BASE_URL}/api/1/item/{item_id}", timeout=10)
        assert get_response.status_code == 200, "Не удалось получить объявление"

        item_data = get_response.json()
        if isinstance(item_data, list):
            item = item_data[0]
        else:
            item = item_data

        actual_name = item.get("name") or item.get("Name") or item.get("title")

        if len(actual_name) == 1000:
            print(f"API принял все 1000 символов")
            assert actual_name == long_name, "Название было изменено, хотя длина сохранилась"
        elif len(actual_name) < 1000:
            print(f"API обрезал название до {len(actual_name)} символов")
        else:
            assert False, f"Странная длина названия: {len(actual_name)}"

        # Очистка
        delete_item(item_id)

    def test_special_characters_in_name(self, create_custom_item, delete_item):
        """Проверяем, что специальные символы корректно сохраняются в поле name."""
        print("\nПроверка специальных символов в названии")

        special_name = "!@#$%^&*()_+{}:\"<>?'"

        # Создаём объявление со спецсимволами
        item_id = create_custom_item(seller_id=123456, name=special_name)
        print(f"Создано объявление с ID: {item_id}")

        # Получаем объявление и проверяем название
        get_response = requests.get(f"{BASE_URL}/api/1/item/{item_id}", timeout=10)
        assert get_response.status_code == 200

        item = get_response.json()[0]

        assert item["name"] == special_name, \
            f"Название изменилось: было '{special_name}', стало '{item['name']}'"

        print(f"Специальные символы сохранились: {item['name']}")

        # Очистка
        delete_item(item_id)

    def test_empty_body_post(self, api_url):
        """Проверяем, что пустое тело запроса вызывает ошибку."""
        print("\nPOST запрос с пустым телом")

        response = requests.post(f"{api_url}/api/1/item", json={}, timeout=10)

        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")

        assert response.status_code != 200, \
            f"Сервер вернул 200 при пустом теле. Это ошибка API! Ответ: {response.text}"

        assert response.status_code >= 400, \
            f"Ожидалась ошибка, получили {response.status_code}"

        print(f"Сервер вернул ошибку {response.status_code} при пустом теле запроса")

    def test_price_float_value(self, try_create_item, delete_item):
        """Проверяем, что API не принимает дробные значения в поле price."""
        print("\nПроверка price с плавающей точкой")

        result = try_create_item(price=100.50)

        if result["success"]:
            # Если вдруг создалось - удаляем и падаем
            delete_item(result["item_id"])
            assert False, "API не должен принимать дробную цену!"
        else:
            # Проверяем, что ошибка связана с price
            assert "400" in result["error"] or "цена" in result["error"].lower(), \
                f"Неожиданная ошибка: {result['error']}"
            print("API корректно отклонил запрос с дробной ценой")

    def test_very_large_seller_id(self, create_custom_item, delete_item):
        """Проверяем, как API обрабатывает очень большой sellerID. Ожидаемый результат: код 200 или 400"""
        print("\nПроверка с большим sellerID")

        try:
            # Пробуем создать с большим sellerID
            item_id = create_custom_item(seller_id=999999999999999999)
            print(f"API принял большой sellerID, создан ID: {item_id}")
            # Очистка, если создалось
            delete_item(item_id)

        except AssertionError as e:
            # Если create_custom_item упал из-за статуса не 200
            if "Ошибка:" in str(e):
                print("API отклонил большой sellerID (вернул не 200)")
            else:
                raise e

        print("Тест пройден (оба варианта допустимы)")

# class TestCornerCases:
#
#     def test_post_creates_new_id_each_time(self, api_url, create_custom_item):
#         """Проверяем, что каждый POST запрос создаёт новое объявление с разным ID."""
#         print("\nПроверка создания уникальных ID при POST запросах")
#
#         created_ids = []
#
#         try:
#             # Отправляем два POST запроса
#             for i in range(2):
#                 test_item = create_custom_item()
#                 response = requests.post(f"{api_url}/api/1/item", json=test_item)
#
#                 assert response.status_code == 200, f"Запрос {i + 1} вернул {response.status_code}"
#
#                 item_id = self._extract_item_id(response)
#                 assert item_id is not None, f"Не удалось извлечь ID из ответа {i + 1}"
#
#                 created_ids.append(item_id)
#                 print(f"Создано объявление {i + 1} с ID: {item_id}")
#
#             # Проверяем, что ID разные
#             assert len(set(created_ids)) == len(created_ids), \
#                 f"Найдены дубликаты ID: {created_ids}"
#
#             print("Все ID уникальны")
#
#         finally:
#             # Очистка в любом случае
#             for item_id in created_ids:
#                 self._cleanup_item(api_url, item_id)
#
#     # Длинное name (1000 символов)
#     def test_very_long_name(self, api_url):
#         """ Проверяем, как API обрабатывает очень длинное название."""
#         print("\nПроверка с очень длинным названием (1000 символов)")
#
#         long_name = "A" * 1000
#
#         payload = {
#             "sellerID": 112233,  # рабочий sellerID
#             "name": long_name,
#             "price": 1000,
#             "statistics": {
#                 "likes": 5,
#                 "viewCount": 5,
#                 "contacts": 5
#             }
#         }
#
#         response = requests.post(f"{api_url}/api/1/item", json=payload)
#         print(f"Статус код: {response.status_code}")
#         print(f"Ответ: {response.text}")
#
#         if response.status_code == 200:
#             try:
#                 json_response = response.json()
#                 item_id = json_response["status"].split(" - ")[1]
#                 print(f"Создано объявление с ID: {item_id}")
#             except Exception as e:
#                 assert False, f"Не удалось извлечь ID: {e}"
#
#             get_response = requests.get(f"{api_url}/api/1/item/{item_id}")
#             assert get_response.status_code == 200, "Не удалось получить объявление"
#
#             item_data = get_response.json()
#             if isinstance(item_data, list):
#                 item = item_data[0]
#             else:
#                 item = item_data
#
#             actual_name = item.get("name") or item.get("Name") or item.get("title")
#
#             if len(actual_name) == 1000:
#                 print(f"API принял все 1000 символов")
#                 assert actual_name == long_name, "Название было изменено, хотя длина сохранилась"
#             elif len(actual_name) < 1000:
#                 print(f"API обрезал название до {len(actual_name)} символов")
#             else:
#                 assert False, f"Странная длина названия: {len(actual_name)}"
#
#             delete_resp = requests.delete(f"{api_url}/api/2/item/{item_id}")
#             assert delete_resp.status_code in [200, 204], "Не удалось удалить объявление"
#             print(f"Удалено объявление {item_id}")
#
#         elif response.status_code == 400:
#             try:
#                 error_data = response.json()
#                 print(f"Ошибка от API: {error_data}")
#
#                 error_message = str(error_data).lower()
#                 assert any(word in error_message for word in ["длин", "length", "max", "превышает", "long"]), \
#                     f"Сообщение об ошибке не связано с длиной названия: {error_data}"
#
#                 print("API корректно отклонил слишком длинное название")
#             except Exception as e:
#                 print(f"Не удалось распарсить ошибку: {e}")
#
#         else:
#             assert False, f"Неожиданный статус код: {response.status_code}, текст: {response.text}"
#
#     def test_special_characters_in_name(self, api_url):
#         """ Проверяем, что специальные символы корректно сохраняются в поле "name"."""
#         print("\nПроверка специальных символов в названии")
#
#         special_name = "!@#$%^&*()_+{}:\"<>?'"
#
#         payload = {
#             "sellerID": 123456,
#             "name": special_name,
#             "price": 1000,
#             "statistics": {
#                 "likes": 5,
#                 "viewCount": 5,
#                 "contacts": 5}
#         }
#
#         response = requests.post(f"{api_url}/api/1/item", json=payload)
#
#         assert response.status_code == 200, f"Ожидался 200, получили {response.status_code}"
#
#         item_id = response.json()["status"].split(" - ")[1]
#
#         get_response = requests.get(f"{api_url}/api/1/item/{item_id}")
#         assert get_response.status_code == 200
#
#         item = get_response.json()[0]
#
#         assert item["name"] == special_name, \
#             f"Название изменилось: было '{special_name}', стало '{item['name']}'"
#
#         print(f"Специальные символы сохранились: {item['name']}")
#
#         requests.delete(f"{api_url}/api/2/item/{item_id}")
#
#     def test_empty_body_post(self, api_url):
#         """ Проверяем, что пустое тело запроса вызывает ошибку."""
#         print("\nPOST запрос с пустым телом")
#
#         response = requests.post(f"{api_url}/api/1/item", json={})
#
#         print(f"Статус код: {response.status_code}")
#         print(f"Ответ: {response.text}")
#
#         assert response.status_code != 200, \
#             f"Сервер вернул 200 при пустом теле. Это ошибка API! Ответ: {response.text}"
#
#         assert response.status_code >= 400, \
#             f"Ожидалась ошибка, получили {response.status_code}"
#
#         print(f" Сервер вернул ошибку {response.status_code} при пустом теле запроса")
#
#     def test_price_float_value(self, api_url):
#         """ Проверяем, что API не принимает дробные значения в поле price."""
#         print("\n Проверка price с плавающей точкой")
#
#         payload = {
#             "sellerID": 112233,
#             "name": "Товар с дробной ценой",
#             "price": 100.50,
#             "statistics": {"likes": 5, "viewCount": 5, "contacts": 5}
#         }
#
#         response = requests.post(f"{api_url}/api/1/item", json=payload)
#
#         print(f"Статус: {response.status_code}")
#         print(f"Ответ: {response.text}")
#
#         assert response.status_code == 400, \
#             f"Ожидался 400, получили {response.status_code}"
#
#         print("API корректно отклонил запрос с дробной ценой")
#
#     def test_very_large_seller_id(self, api_url):
#         """ Проверяем, как API обрабатывает очень большой sellerID. Ожидаемый результат: код 200 или 400"""
#         print("\nПроверка с большим sellerID")
#
#         payload = {
#             "sellerID": 999999999999999999,
#             "name": "Товар",
#             "price": 1000,
#             "statistics": {"likes": 5, "viewCount": 5, "contacts": 5}
#         }
#
#         response = requests.post(f"{api_url}/api/1/item", json=payload)
#
#         print(f"Статус код: {response.status_code}")
#
#         assert response.status_code in [200, 400], \
#             f"Ожидался 200 или 400, получили {response.status_code}"
#
#         if response.status_code == 200:
#             item_id = response.json()["status"].split(" - ")[1]
#             requests.delete(f"{api_url}/api/2/item/{item_id}")
#             print("API принял большой sellerID")
#         else:
#             print("API отклонил большой sellerID")
#
#         print("Тест пройден (оба варианта допустимы)")