# API Тесты

## Описание
Автотесты для API объявлений

#### BASE_URL: https://qa-internship.avito.com

## Установка

#### Клонировать репозиторий
```bash
git clone https://github.com/ODYA1993/avito-api-tests.git
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
