import pytest
import requests

BASE_URL = "https://qa-internship.avito.com"


@pytest.fixture
def api_url():
    return BASE_URL


@pytest.fixture
def create_custom_item():
    """Создаёт объявление с кастомными параметрами"""

    def _create(seller_id=112233, name="Наименование", price=1000, likes=5, views=5, contacts=5):
        payload = {
            "sellerID": seller_id,
            "name": name,
            "price": price,
            "statistics": {"likes": likes, "viewCount": views, "contacts": contacts}
        }
        response = requests.post(f"{BASE_URL}/api/1/item", json=payload)

        assert response.status_code == 200, f"Ошибка: {response.status_code} - {response.text}"

        response_data = response.json()
        status_text = response_data.get("status", "")

        assert " - " in status_text, f"Неожиданный формат ответа: {status_text}"
        item_id = status_text.split(" - ")[1]

        return item_id

    return _create


@pytest.fixture
def delete_item():
    """Удаляет объявление по ID"""

    def _delete(item_id):
        try:
            response = requests.delete(f"{BASE_URL}/api/2/item/{item_id}")
            if response.status_code == 200:
                print(f"✓ Удалено объявление {item_id}")
                return True
            else:
                print(f"✗ Не удалось удалить {item_id}: статус {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Ошибка при удалении {item_id}: {e}")
            return False

    return _delete


@pytest.fixture
def create_multiple_items(create_custom_item, delete_item):
    """Создаёт несколько объявлений и удаляет после теста"""
    created_ids = []

    def _create(count=3, seller_id=112233):
        for i in range(count):
            item_id = create_custom_item(name=f"Наименование {i + 1}")
            created_ids.append(item_id)
            print(f"[fixture] Создано объявление {i + 1}: {item_id}")

        return {
            "seller_id": seller_id,
            "ids": created_ids
        }

    yield _create

    # Очистка после теста
    if created_ids:
        print(f"\n[cleanup] Удаляем {len(created_ids)} объявлений...")
        for item_id in created_ids:
            delete_item(item_id)


@pytest.fixture
def try_create_item(create_custom_item):
    """Пытается создать объявление, но не падает при ошибке"""
    def _try_create(**kwargs):
        try:
            item_id = create_custom_item(**kwargs)
            return {"success": True, "item_id": item_id, "error": None}
        except AssertionError as e:
            return {"success": False, "item_id": None, "error": str(e)}
    return _try_create