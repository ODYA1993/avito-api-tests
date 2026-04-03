import requests


class TestStatistic:

    def test_get_statistic_success(self, api_url, create_custom_item, delete_item):
        """Проверяем, что можно получить статистику по объявлению.
        Ожидаем: код 200, тело содержит likes, viewCount, contacts"""
        print("\nПолучение статистики по объявлению")

        # Создаём объявление с кастомной статистикой
        item_id = create_custom_item(
            likes=10,
            views=100,
            contacts=5
        )
        print(f"Создано объявление с ID: {item_id}")

        # Получаем статистику
        response = requests.get(f"{api_url}/api/1/statistic/{item_id}", timeout=10)

        assert response.status_code == 200, \
            f"Ожидался статус 200, получили {response.status_code}. Ответ: {response.text}"

        data = response.json()

        # Обрабатываем разные форматы ответа
        if isinstance(data, list):
            assert len(data) > 0, "Массив статистики не должен быть пустым"
            stat = data[0]
        elif isinstance(data, dict):
            stat = data
        else:
            assert False, f"Неожиданный тип ответа: {type(data)}"

        # Проверяем наличие всех полей
        expected_fields = ["likes", "viewCount", "contacts"]
        for field in expected_fields:
            assert field in stat, f"В статистике отсутствует поле '{field}'"

        # Проверяем типы данных
        assert isinstance(stat["likes"], int), f"likes должно быть целым числом, получили {type(stat['likes'])}"
        assert isinstance(stat["viewCount"],
                          int), f"viewCount должно быть целым числом, получили {type(stat['viewCount'])}"
        assert isinstance(stat["contacts"],
                          int), f"contacts должно быть целым числом, получили {type(stat['contacts'])}"

        # Проверяем, что значения не отрицательные
        assert stat["likes"] >= 0, f"likes не может быть отрицательным: {stat['likes']}"
        assert stat["viewCount"] >= 0, f"viewCount не может быть отрицательным: {stat['viewCount']}"
        assert stat["contacts"] >= 0, f"contacts не может быть отрицательным: {stat['contacts']}"

        # Проверяем, что значения соответствуют созданным
        assert stat["likes"] == 10, f"Ожидалось 10 лайков, получили {stat['likes']}"
        assert stat["viewCount"] == 100, f"Ожидалось 100 просмотров, получили {stat['viewCount']}"
        assert stat["contacts"] == 5, f"Ожидалось 5 контактов, получили {stat['contacts']}"

        print(
            f"✓ Статистика получена: лайки={stat['likes']}, просмотры={stat['viewCount']}, контакты={stat['contacts']}")

        # Очистка
        delete_item(item_id)