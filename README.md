# Создание сайтов JTI в Resolver

Скрипт по автоматическому созданию сайтов JTI по запросам в системе Resolver.

## Запуск

- Скачайте код
- Установите зависимости командой  
```pip install -r requirements.txt```
- Запустите скрипт командой  
```python3 manage.py create```

## Переменные окружения

Для корректной работы кода, необходимы переменные окружения. Чтобы их определить, создайте файл `.env` рядом с `main.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

* `EMAIL` - Логин для Resolver.
* `PASSWORD` - Пароль для Resolver.
* `GOOGLE_API` - Ключ API для Google Maps.

Например:  
```
EMAIL=john.smith@domain.com
PASSWORD=V3r9Str0ngP4ssw0rd
GOOGLE_API=123google456api789key
```
