import requests


class TestNegative:

    def test_create_item_no_seller_id(self, api_url):
        """Проверяем, что нельзя создать объявление без поля sellerID."""
        print("\nСоздание объявления без sellerID")

        payload = {
            "name": "Name",
            "price": 5000,
            "statistics": {"likes": 10, "viewCount": 100, "contacts": 5}
        }

        response = requests.post(f"{api_url}/api/1/item", json=payload, timeout=10)
        assert response.status_code == 400
        print("Сервер вернул 400, поле sellerID обязательно")

    def test_create_item_no_name(self, api_url):
        """Проверяем, что нельзя создать объявление без поля name."""
        print("\nСоздание объявления без name")

        payload = {
            "sellerID": 112233,
            "price": 5000,
            "statistics": {"likes": 10, "viewCount": 100, "contacts": 5}
        }

        response = requests.post(f"{api_url}/api/1/item", json=payload, timeout=10)
        assert response.status_code == 400
        print("Сервер вернул 400, поле name обязательно")

    def test_create_item_empty_name(self, api_url):
        """Проверяем, что нельзя создать объявление с пустым name."""
        print("\nСоздание объявления с пустым name")

        payload = {
            "sellerID": 112233,
            "name": "",
            "price": 5000,
            "statistics": {"likes": 10, "viewCount": 100, "contacts": 5}
        }

        response = requests.post(f"{api_url}/api/1/item", json=payload, timeout=10)
        assert response.status_code == 400
        print("Сервер вернул 400, name не может быть пустым")

    def test_create_item_negative_price(self, api_url):
        """Проверяем, что нельзя создать объявление с отрицательной ценой."""
        print("\nСоздание объявления с отрицательной ценой")

        payload = {
            "sellerID": 112233,
            "name": "Name",
            "price": -100,
            "statistics": {"likes": 10, "viewCount": 100, "contacts": 5}
        }

        response = requests.post(f"{api_url}/api/1/item", json=payload, timeout=10)
        assert response.status_code == 400
        print("✓ Сервер вернул 400, цена не может быть отрицательной")

    def test_create_item_zero_price(self, api_url, delete_item):
        """Проверяем, можно ли создать объявление с ценой 0."""
        print("\nСоздание объявления с ценой 0")

        payload = {
            "sellerID": 112233,
            "name": "Бесплатный товар",
            "price": 0,
            "statistics": {"likes": 10, "viewCount": 100, "contacts": 5}
        }

        response = requests.post(f"{api_url}/api/1/item", json=payload, timeout=10)

        if response.status_code == 200:
            print("API принимает цену 0")
            item_id = response.json()["status"].split(" - ")[1]

            get_response = requests.get(f"{api_url}/api/1/item/{item_id}", timeout=10)
            item = get_response.json()[0]
            assert item["price"] == 0

            delete_item(item_id)
        elif response.status_code == 400:
            print("⚠️ API не принимает цену 0")
        else:
            assert False, f"Неожиданный статус: {response.status_code}"

    def test_create_item_invalid_seller_id_type(self, api_url):
        """Проверяем, что нельзя передать строку вместо числа в sellerID."""
        print("\nСоздание объявления с sellerID в виде строки")

        payload = {
            "sellerID": "abc",
            "name": "Name",
            "price": 100,
            "statistics": {"likes": 10, "viewCount": 100, "contacts": 5}
        }

        response = requests.post(f"{api_url}/api/1/item", json=payload)
        assert response.status_code == 400
        print("Сервер вернул 400, ошибка валидации типа данных")

    def test_get_nonexistent_item(self, api_url):
        """Проверяем, что GET по несуществующему ID возвращает 404."""
        print("\nПолучение несуществующего объявления")

        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{api_url}/api/1/item/{fake_id}", timeout=10)
        assert response.status_code == 404
        print("Сервер вернул 404, объявление не найдено")

    def test_get_item_invalid_id_format(self, api_url):
        """Проверяем, что невалидный ID (не UUID) вызывает ошибку."""
        print("\nПолучение объявления по ID не в формате UUID")

        invalid_id = "invalid-id-format"
        response = requests.get(f"{api_url}/api/1/item/{invalid_id}", timeout=10)
        assert response.status_code in [400, 404]
        print("Сервер вернул ошибку на невалидный формат ID")

    def test_delete_nonexistent_item(self, api_url):
        """Проверяем, что DELETE несуществующего объявления возвращает 404."""
        print("\nУдаление несуществующего объявления")

        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(f"{api_url}/api/2/item/{fake_id}")
        assert response.status_code == 404
        print("Сервер вернул 404, нельзя удалить несуществующее объявление")

    def test_wrong_http_method(self, create_custom_item, delete_item, api_url):
        """Проверяем, что DELETE на GET-эндпоинт возвращает 405."""
        print("\nИспользование неверного HTTP метода")

        item_id = create_custom_item()
        print(f"Создано объявление для теста: {item_id}")

        response = requests.delete(f"{api_url}/api/1/item/{item_id}", timeout=10)
        assert response.status_code == 405
        print("Сервер вернул 405, метод не поддерживается")

        delete_item(item_id)

    def test_wrong_content_type(self, api_url):
        """Проверяем, что неправильный Content-Type вызывает ошибку."""
        print("\nЗапрос с неверным Content-Type")

        payload = '{"sellerID": 112233, "name": "Name", "price": 5000}'

        response = requests.post(
            f"{api_url}/api/1/item",
            data=payload,
            headers={"Content-Type": "text/plain"},
            timeout=10
        )

        assert response.status_code in [400, 415]
        print("Сервер отклонил запрос с неправильным Content-Type")