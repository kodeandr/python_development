"""
Домашнее задание 4: middleware для логирования (Booking + TaskManager).
Подготовил: Коробов Денис"""

import datetime
import logging
import inspect
import functools


# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('booking_middleware')


def log_middleware(func):
    """Логирует вызов, аргументы, результат или ошибку. Пробрасывает исключения."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        params = bound_args.arguments

        event_id = params.get('event_id')
        user_id = params.get('user_id')
        booking_id_arg = params.get('booking_id')

        # Логируем вызов 
        call_ctx = {
            'function': func.__name__,
            'event_id': event_id,
            'user_id': user_id,
            'booking_id': booking_id_arg
        }
        call_log = {k: v for k, v in call_ctx.items() if v is not None}
        logger.info(f"CALL {func.__name__}: {call_log}")

        try:
            result = func(*args, **kwargs)

            # Извлекаем booking_id из результата 
            booking_id_res = None
            if isinstance(result, dict):
                booking_id_res = result.get('booking_id')

            success_ctx = {
                'function': func.__name__,
                'event_id': event_id,
                'user_id': user_id,
                'booking_id': booking_id_res or booking_id_arg,
                'success': True
            }
            success_log = {k: v for k, v in success_ctx.items() if v is not None}
            logger.info(f"SUCCESS {func.__name__}: {success_log}")
            return result

        except (ValueError, KeyError) as e:
            if isinstance(e, KeyError):
                key = e.args[0] if e.args else 'unknown'
                error_msg = f"KeyError: key '{key}' not found in BOOKINGS_DB"
            else:
                error_msg = str(e)

            error_ctx = {
                'function': func.__name__,
                'event_id': event_id,
                'user_id': user_id,
                'booking_id': booking_id_arg,
                'success': False,
                'error': error_msg
            }
            error_log = {k: v for k, v in error_ctx.items() if v is not None}
            logger.error(f"ERROR {func.__name__}: {error_log}", exc_info=True)
            raise   # пробрасываем исключение дальше 

    return wrapper


# Исходные данные
EVENTS_DB = {
    1: {"title": "Football Match", "available_seats": 10, "date": datetime.date(2025, 7, 1)},
    2: {"title": "Basketball Playoffs", "available_seats": 5, "date": datetime.date(2025, 7, 2)},
    3: {"title": "Tennis Open", "available_seats": 3, "date": datetime.date(2025, 7, 3)},
}

BOOKINGS_DB = {}


@log_middleware
def create_booking(event_id: int, user_id: int) -> dict:
    """Создаёт бронь на мероприятие."""
    if event_id not in EVENTS_DB:
        raise ValueError(f"Event with id={event_id} does not exist.")

    event_info = EVENTS_DB[event_id]
    if event_info["available_seats"] <= 0:
        raise ValueError("No available seats.")

    event_info["available_seats"] -= 1

    booking_id = f"{int(datetime.datetime.now().timestamp())}_{user_id}"
    booking_data = {
        "booking_id": booking_id,
        "event_id": event_id,
        "user_id": user_id,
        "title": event_info["title"],
        "date": event_info["date"],
        "created_at": datetime.datetime.now()
    }
    BOOKINGS_DB[booking_id] = booking_data
    return booking_data


@log_middleware
def get_booking(booking_id: str) -> dict:
    """Возвращает данные брони по её идентификатору."""
    return BOOKINGS_DB[booking_id]


if __name__ == "__main__":
    print("--- Успешное создание брони ---")
    booking1 = create_booking(event_id=1, user_id=101)
    print("Результат:", booking1)

    print("\n--- Успешное получение брони ---")
    retrieved = get_booking(booking1["booking_id"])
    print("Результат:", retrieved)

    print("\n--- Ошибка: неверный event_id ---")
    try:
        create_booking(event_id=999, user_id=102)
    except ValueError as e:
        print("Ожидаемая ошибка:", e)

    print("\n--- Ошибка: неверный booking_id ---")
    try:
        get_booking("non_existent")
    except KeyError as e:
        print("Ожидаемая ошибка:", e)

    print("\n--- Исчерпание мест на событие 3 ---")
    for i in range(4):
        try:
            create_booking(event_id=3, user_id=200 + i)
        except ValueError as e:
            print(f"Попытка {i+1}: {e}")