"""
Модуль управления миссиями
"""
import time
from typing import List
from pymavlink import mavutil

def clear_mission(master: mavutil.mavlink_connection) -> None:
    """Очистка миссии."""
    print("[МИССИЯ] Очистка...")
    master.mav.mission_clear_all_send(master.target_system, master.target_component)
    time.sleep(1)

def upload_simple_mission(master: mavutil.mavlink_connection, lat: float, lon: float) -> bool:
    """
    Загрузка простой миссии (1 точка).
    ИСПРАВЛЕННАЯ ВЕРСИЯ - использует MISSION_ITEM_INT.
    """
    print("[МИССИЯ]")
    
    # 1. Очищаем
    clear_mission(master)
    
    # 2. Отправляем количество точек (1 точка) с указанием типа миссии
    print("[МИССИЯ] Отправка MISSION_COUNT...")
    master.mav.mission_count_send(
        master.target_system,
        master.target_component,
        1,  # 1 точка
        mavutil.mavlink.MAV_MISSION_TYPE_MISSION  # Важно: указываем тип!
    )
    
    # 3. Ждем запрос точки 0 (теперь MISSION_REQUEST_INT)
    print("[МИССИЯ] Ожидание запроса точки...")
    msg = master.recv_match(type=['MISSION_REQUEST_INT', 'MISSION_REQUEST'], blocking=True, timeout=8.0)
    
    if msg is None:
        print("[МИССИЯ] Нет запроса точки (таймаут)")
        return False
    
    print(f"[МИССИЯ] Получен запрос: {msg.get_type()}, seq={msg.seq}")
    
    # 4. Отправляем точку в формате MISSION_ITEM_INT
    lat_int = int(lat * 1e7)
    lon_int = int(lon * 1e7)
    
    print(f"[МИССИЯ] Отправка точки: lat={lat_int}, lon={lon_int}")
    
    master.mav.mission_item_int_send(
        master.target_system,
        master.target_component,
        0,  # seq
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,  # Фрейм
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,  # Команда
        1,  # current = да, это текущая точка
        1,  # autocontinue
        0.0, 0.0, 0.0, 0.0,  # param1-4
        lat_int, lon_int,  # x, y (lat, lon)
        10.0,  # alt (метры)
        mavutil.mavlink.MAV_MISSION_TYPE_MISSION  # Тип миссии
    )
    
    print("[МИССИЯ] Точка отправлена, ожидание подтверждения...")
    
    # 5. Ждем подтверждения MISSION_ACK
    msg = master.recv_match(type='MISSION_ACK', blocking=True, timeout=5.0)
    
    if msg is None:
        print("[МИССИЯ] Нет подтверждения (таймаут)")
        return False
    
    print(f"[МИССИЯ] Получен ACK: type={msg.type}")
    
    # type=0 означает MAV_MISSION_ACCEPTED (успех)
    if msg.type == 0:
        print("[МИССИЯ] Миссия успешно загружена!")
        return True
    else:
        print(f"[МИССИЯ] Ошибка загрузки: код {msg.type}")
        return False 