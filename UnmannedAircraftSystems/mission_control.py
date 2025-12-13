"""
Модуль управления миссиями дрона.
Реализует неблокирующую загрузку миссий с использованием состояния дрона.
"""
from dataclasses import dataclass
from typing import List, Optional
import time
from pymavlink import mavutil
from drone_monitor import DroneState  # Импортируем для использования состояния

@dataclass
class MissionItem:
    """
    Один пункт миссии в формате MISSION_ITEM_INT.
    """
    seq: int
    frame: int
    command: int
    current: int
    autocontinue: int
    param1: float
    param2: float
    param3: float
    param4: float
    x: int  # lat * 1e7
    y: int  # lon * 1e7
    z: float  # alt (м)

class MissionControlError(Exception):
    """Класс для ошибок управления миссиями."""
    pass

def clear_mission(master: mavutil.mavlink_connection, state: DroneState, timeout: float = 15.0) -> bool:
    """
    Очистка текущей миссии на борту.
    Возвращает True в случае успеха.
    """
    print("[МИССИЯ] Очистка текущей миссии...")
    
    # Сбрасываем флаги состояния
    state.mission_ack_received = False
    state.mission_item_requested = None
    
    # Отправляем команду очистки
    master.mav.mission_clear_all_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_MISSION_TYPE_MISSION
    )
    
    # Ждем подтверждения через обновление состояния
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Проверяем флаг состояния (обрабатывается в мониторе)
        if state.mission_ack_received:
            state.mission_ack_received = False
            print("[МИССИЯ] Миссия успешно очищена")
            return True
        
        # Также можно проверить напрямую
        msg = master.recv_match(
            type=['MISSION_ACK', 'COMMAND_ACK'],
            blocking=False,
            timeout=0.1
        )
        
        if msg is not None:
            if msg.get_type() == 'MISSION_ACK' and msg.type == 0:  # MAV_MISSION_ACCEPTED
                print("[МИССИЯ] Миссия успешно очищена (MISSION_ACK)")
                return True
            elif msg.get_type() == 'COMMAND_ACK' and msg.command == mavutil.mavlink.MAV_CMD_MISSION_CLEAR_ALL:
                if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                    print("[МИССИЯ] Миссия успешно очищена (COMMAND_ACK)")
                    return True
    
    print("[МИССИЯ] Таймаут ожидания подтверждения очистки миссии")
    return False

def upload_mission(master: mavutil.mavlink_connection,
                   items: List[MissionItem],
                   state: DroneState,
                   timeout_per_item: float = 3.0,
                   overall_timeout: float = 45.0) -> bool:
    """
    Неблокирующая загрузка миссии.
    Возвращает True в случае успеха.
    """
    count = len(items)
    if count == 0:
        print("[МИССИЯ] Пустая миссия")
        return True
    
    print(f"[МИССИЯ] Начало загрузки миссии из {count} точек...")
    
    # Сбрасываем флаги состояния
    state.mission_item_requested = None
    state.mission_ack_received = False
    
    # 1. Отправляем количество точек
    print(f"[МИССИЯ] Отправка MISSION_COUNT ({count} точек)...")
    master.mav.mission_count_send(
        master.target_system,
        master.target_component,
        count,
        mavutil.mavlink.MAV_MISSION_TYPE_MISSION
    )
    
    # 2. Ждем запросы точек и отправляем их
    sent_seqs = set()
    start_time = time.time()
    last_request_time = start_time
    
    while len(sent_seqs) < count and time.time() - start_time < overall_timeout:
        current_time = time.time()
        
        # Проверяем, не слишком ли давно был последний запрос
        if current_time - last_request_time > 2.0 and len(sent_seqs) < count:
            # Запрашиваем следующую точку
            next_seq = len(sent_seqs)
            print(f"[МИССИЯ] Запрашиваем точку {next_seq}...")
            master.mav.mission_request_int_send(
                master.target_system,
                master.target_component,
                next_seq,
                mavutil.mavlink.MAV_MISSION_TYPE_MISSION
            )
            last_request_time = current_time
        
        # Проверяем запрос точки через состояние (обрабатывается в мониторе)
        if state.mission_item_requested is not None:
            seq = state.mission_item_requested
            state.mission_item_requested = None
            last_request_time = current_time
            
            if 0 <= seq < count and seq not in sent_seqs:
                item = items[seq]
                print(f"[МИССИЯ] Получен запрос точки {seq}. Отправка...")
                
                master.mav.mission_item_int_send(
                    master.target_system,
                    master.target_component,
                    item.seq,
                    item.frame,
                    item.command,
                    item.current,
                    item.autocontinue,
                    item.param1,
                    item.param2,
                    item.param3,
                    item.param4,
                    item.x,
                    item.y,
                    item.z,
                    mavutil.mavlink.MAV_MISSION_TYPE_MISSION
                )
                sent_seqs.add(seq)
                print(f"[МИССИЯ] Отправлена точка {seq} ({len(sent_seqs)}/{count})")
        
        # Проверяем подтверждение всей миссии
        if state.mission_ack_received:
            state.mission_ack_received = False
            print(f"[МИССИЯ] Миссия успешно загружена! Отправлено {len(sent_seqs)} точек")
            return True
        
        # Короткая пауза
        time.sleep(0.1)
    
    # 3. Проверяем, все ли точки отправлены
    if len(sent_seqs) == count:
        # Если все точки отправлены, но нет подтверждения, запрашиваем подтверждение
        print("[МИССИЯ] Все точки отправлены, проверяем подтверждение...")
        
        # Проверяем состояние
        if state.mission_ack_received:
            state.mission_ack_received = False
            print("[МИССИЯ] Миссия загружена (подтверждение в состоянии)")
            return True
        
        # Или ждем MISSION_ACK напрямую
        ack_timeout = 5.0
        ack_start = time.time()
        while time.time() - ack_start < ack_timeout:
            msg = master.recv_match(
                type='MISSION_ACK',
                blocking=True,
                timeout=0.5
            )
            if msg is not None:
                if msg.type == 0:  # MAV_MISSION_ACCEPTED
                    print("[МИССИЯ] Миссия успешно загружена")
                    return True
                else:
                    print(f"[МИССИЯ] Ошибка загрузки миссии: код {msg.type}")
                    return False
            
            # Также проверяем состояние
            if state.mission_ack_received:
                state.mission_ack_received = False
                print("[МИССИЯ] Миссия загружена (подтверждение в состоянии после ожидания)")
                return True
    
    print(f"[МИССИЯ] Таймаут загрузки. Отправлено точек: {len(sent_seqs)}/{count}")
    return False

def download_mission(master: mavutil.mavlink_connection,
                     state: DroneState,
                     timeout: float = 30.0) -> Optional[List[MissionItem]]:
    """
    Чтение миссии с борта (неблокирующая версия).
    Возвращает список точек миссии или None в случае ошибки.
    """
    print("[МИССИЯ] Запрос списка миссии...")
    
    # Отправляем запрос списка миссии
    master.mav.mission_request_list_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_MISSION_TYPE_MISSION
    )
    
    # Ждем MISSION_COUNT
    start_time = time.time()
    count = None
    
    while time.time() - start_time < timeout:
        msg = master.recv_match(
            type=['MISSION_COUNT', 'MISSION_ACK'],
            blocking=True,
            timeout=0.5
        )
        
        if msg is None:
            continue
        
        if msg.get_type() == 'MISSION_COUNT':
            count = msg.count
            print(f"[МИССИЯ] Миссия содержит {count} точек")
            break
        
        elif msg.get_type() == 'MISSION_ACK':
            print(f"[МИССИЯ] Ошибка запроса списка: тип {msg.type}")
            return None
    
    if count is None:
        print("[МИССИЯ] Не получен MISSION_COUNT")
        return None
    
    if count == 0:
        print("[МИССИЯ] Миссия пуста")
        return []
    
    # Запрашиваем каждую точку
    items: List[MissionItem] = []
    
    for seq in range(count):
        print(f"[МИССИЯ] Запрос точки seq={seq}...")
        
        # Отправляем запрос точки
        master.mav.mission_request_int_send(
            master.target_system,
            master.target_component,
            seq,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )
        
        # Ждем MISSION_ITEM_INT
        item_timeout = 5.0
        item_start = time.time()
        item_received = False
        
        while time.time() - item_start < item_timeout:
            msg = master.recv_match(
                type=['MISSION_ITEM_INT', 'MISSION_ACK'],
                blocking=True,
                timeout=0.5
            )
            
            if msg is None:
                continue
            
            if msg.get_type() == 'MISSION_ITEM_INT':
                if msg.seq == seq:
                    items.append(
                        MissionItem(
                            seq=msg.seq,
                            frame=msg.frame,
                            command=msg.command,
                            current=msg.current,
                            autocontinue=msg.autocontinue,
                            param1=msg.param1,
                            param2=msg.param2,
                            param3=msg.param3,
                            param4=msg.param4,
                            x=msg.x,
                            y=msg.y,
                            z=msg.z,
                        )
                    )
                    item_received = True
                    print(f"[МИССИЯ] Получена точка seq={seq}")
                    break
            
            elif msg.get_type() == 'MISSION_ACK':
                print(f"[МИССИЯ] Ошибка при запросе точки seq={seq}: тип {msg.type}")
                return None
        
        if not item_received:
            print(f"[МИССИЯ] Таймаут ожидания точки seq={seq}")
            return None
    
    print(f"[МИССИЯ] Успешно получено {len(items)} точек миссии")
    return items

def create_sample_mission(home_lat: float, home_lon: float, 
                         home_alt: float = 0.0) -> List[MissionItem]:
    """
    Создание тестовой миссии по ТЗ (3 точки, включая взлет и посадку).
    home_lat, home_lon: координаты домашней позиции (градусы)
    home_alt: высота домашней позиции (метры)
    Возвращает список точек миссии.
    """
    # Преобразуем координаты в целочисленный формат (deg * 1e7)
    lat_int = int(home_lat * 1e7)
    lon_int = int(home_lon * 1e7)
    
    # Параметры миссии
    takeoff_alt = 15.0  # Высота взлета
    waypoint_alt = 20.0  # Высота точек маршрута
    waypoint_distance = 0.0001  # Смещение в градусах (~11 метров на экваторе)
    
    # 1. Взлет (MAV_CMD_NAV_TAKEOFF)
    takeoff_item = MissionItem(
        seq=0,
        frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        command=mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        current=1,  # Текущая точка при старте миссии
        autocontinue=1,
        param1=15.0,  # Минимальный питч (для взлета)
        param2=0,     # Пустой
        param3=0,     # Пустой
        param4=0,     # Yaw угол
        x=lat_int,
        y=lon_int,
        z=takeoff_alt
    )
    
    # 2. Первая точка маршрута (MAV_CMD_NAV_WAYPOINT)
    wp1_item = MissionItem(
        seq=1,
        frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        current=0,
        autocontinue=1,
        param1=0,   # Hold time
        param2=10.0, # Acceptance radius (м)
        param3=0,   # Pass through waypoint
        param4=0,   # Yaw угол
        x=lat_int + int(waypoint_distance * 1e7),  # Смещение на восток
        y=lon_int,
        z=waypoint_alt
    )
    
    # 3. Вторая точка маршрута (MAV_CMD_NAV_WAYPOINT)
    wp2_item = MissionItem(
        seq=2,
        frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        current=0,
        autocontinue=1,
        param1=0,   # Hold time
        param2=10.0, # Acceptance radius
        param3=0,   # Pass through waypoint
        param4=0,   # Yaw угол
        x=lat_int,
        y=lon_int + int(waypoint_distance * 1e7),  # Смещение на север
        z=waypoint_alt
    )
    
    # 4. Возврат в домашнюю позицию (MAV_CMD_NAV_RETURN_TO_LAUNCH)
    rtl_item = MissionItem(
        seq=3,
        frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        command=mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
        current=0,
        autocontinue=0,  # Последняя точка
        param1=0,  # Empty
        param2=0,  # Empty
        param3=0,  # Empty
        param4=0,  # Yaw угол
        x=0,
        y=0,
        z=0  # Высота не используется для RTL
    )
    
    return [takeoff_item, wp1_item, wp2_item, rtl_item]
