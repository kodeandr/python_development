import requests

# URL ресурса posts
url = 'https://jsonplaceholder.typicode.com/posts'

# Выполняем get запрос
response = requests.get(url)

# Если код состояния "200 - успешный запрос"
if response.status_code == 200:

    # Преобразуем полученный JSON в список объектов
    data = response.json()

    # Берём первые 5 элементов списка
    first_five_posts = data[:5]

    # Проходим по каждому посту и выводим title и body
    for post in first_five_posts:
        print(f'Title: {post['title']}')
        print(f'Body: {post['body']}\n')

# Иначе выводим ошибку
else:
    print('Ошибка при выполнении запроса: ', response.status_code)