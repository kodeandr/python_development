import requests

# Адрес API для создания ресурса (POST)
url = 'https://jsonplaceholder.typicode.com/posts'

# Данные нового поста
data = {
    'title': 'Новый пост',
    'body': 'Это тестовый контент моего первого поста.',
    'userId': 1  # Можно задать произвольный userId
}

try:
    # Отправляем POST-запрос
    response = requests.post(url, json=data)
    
    if response.status_code == 201:  # Успешное создание ресурса
        new_post = response.json()
        print(f'ID созданного поста: {new_post["id"]}')
        print('Содержание:')
        print(new_post['title'])
        print(new_post['body'])
    elif response.status_code == 400:  # Ошибка Bad Request
        print("Ошибка 400: Некорректный запрос.")
    elif response.status_code == 404:  # Ресурс не найден
        print("Ошибка 404: Запрашиваемый ресурс не существует.")
    else:
        print(f'Ошибка: {response.status_code}. Сообщение сервера: {response.text}')
except Exception as e:
    print(f'Возникла ошибка: {e}')