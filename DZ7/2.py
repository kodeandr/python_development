import requests
import json

def get_weather_data(city_name, api_key):
    """
    Получает данные о погоде для указанного города
    """
    # Базовый URL API OpenWeather
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    # Параметры запроса
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric',  # для получения температуры в Цельсиях
        'lang': 'ru'        # для получения описания на русском
    }
    
    try:
        # Отправка GET-запроса
        response = requests.get(base_url, params=params)
        
        # Проверка статуса ответа
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Ошибка: Неверный API ключ")
        elif response.status_code == 404:
            print("Ошибка: Город не найден")
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения: {e}")
        return None

def display_weather(weather_data):
    """
    Отображает информацию о погоде
    """
    if weather_data:
        # Извлечение данных из JSON
        city = weather_data['name']
        country = weather_data['sys']['country']
        temperature = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        
        # Вывод информации
        print("\n" + "="*40)
        print(f"Погода в городе: {city}, {country}")
        print("="*40)
        print(f"🌡 Температура: {temperature}°C")
        print(f"💭 Ощущается как: {feels_like}°C")
        print(f"☁️ Описание: {description.capitalize()}")
        print(f"💧 Влажность: {humidity}%")
        print(f"📊 Давление: {pressure} hPa")
        print("="*40)
    else:
        print("Не удалось получить данные о погоде")

def main():
    """
    Основная функция программы
    """
    # Ваш API ключ (замените на свой)
    API_KEY = "185213fafac3142a4af1762cdba66b26"  
    
    print("🌤 Программа для получения данных о погоде")
    print("Для выхода введите 'quit' или 'exit'")
    
    while True:
        # Получение названия города от пользователя
        city_name = input("\nВведите название города: ").strip()
        
        # Проверка на выход
        if city_name.lower() in ['quit', 'exit', 'выход']:
            print("До свидания!")
            break
        
        if not city_name:
            print("Пожалуйста, введите название города")
            continue
        
        # Получение данных о погоде
        print("Получение данных...")
        weather_data = get_weather_data(city_name, API_KEY)
        
        # Отображение результатов
        display_weather(weather_data)

if __name__ == "__main__":
    # Запуск основной программы
    main()