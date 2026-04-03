# API Тесты

## Описание
Автотесты для API объявлений

#### BASE_URL: https://qa-internship.avito.com

## Установка

#### Клонировать репозиторий
```bash
git clone <url>
````
#### Установить зависимости
```bash
pip install -r requirements.txt
```
# Запуск тестов

Запустить все тесты
```bash
python -m pytest -v
```

Запустить все тесты с подробным выводом
```bash
python -m pytest -v -s
```
Запустить конкретный класс
```bash
pytest test_items.py::TestItems -v
```
