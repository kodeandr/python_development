"""
Модуль управления полетом дрона.
Исправленная версия.
"""
import time
from typing import Optional, Tuple
from pymavlink import mavutil

class FlightControlError(Exception):
    pass

def wait_for_ack(master, command, timeout=10.0):
    """Ждет подтверждение команды."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        msg = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=0.5)
        if msg is not None and msg.command == command:
            return msg
    return None

def set_mode(master, mode_name, timeout=10.0):
    """Установка режима."""
    mode_mapping = master.mode_mapping()
    if mode_mapping is None or mode_name not in mode_mapping:
        print(f"[УПРАВЛЕНИЕ] Режим '{mode_name}' недоступен")
        return False
    
    mode_id = mode_mapping[mode_name]
    print(f"[УПРАВЛЕНИЕ] Установка режима '{mode_name}' (id={mode_id})")
    
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    
    # Проверяем изменение режима через HEARTBEAT
    start_time = time.time()
    while time.time() - start_time < timeout:
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=0.5)
        if msg is not None and hasattr(msg, 'custom_mode'):
            if msg.custom_mode == mode_id:
                print(f"[УПРАВЛЕНИЕ] Режим '{mode_name}' установлен")
                return True
    print(f"[УПРАВЛЕНИЕ] Таймаут установки режима")
    return False

def set_mode_guided(master):
    return set_mode(master, "GUIDED")

def set_mode_auto(master):
    return set_mode(master, "AUTO")

def arm(master, timeout=15.0):
    """ARM двигателей."""
    print("[УПРАВЛЕНИЕ] Отправка команды ARM...")
    
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,  # arm
        0, 0, 0, 0, 0, 0
    )
    
    # Ждем подтверждения
    ack = wait_for_ack(master, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout)
    if ack is not None:
        if ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("[УПРАВЛЕНИЕ] ARM подтвержден")
            return True
        else:
            print(f"[УПРАВЛЕНИЕ] Ошибка ARM: код {ack.result}")
            return False
    
    print("[УПРАВЛЕНИЕ] Таймаут ожидания ARM")
    return False

def disarm(master, timeout=10.0):
    """DISARM двигателей."""
    print("[УПРАВЛЕНИЕ] Отправка команды DISARM...")
    
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,  # disarm
        0, 0, 0, 0, 0, 0
    )
    
    ack = wait_for_ack(master, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout)
    if ack is not None and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("[УПРАВЛЕНИЕ] DISARM подтвержден")
        return True
    
    print("[УПРАВЛЕНИЕ] Таймаут ожидания DISARM")
    return False

def takeoff(master, altitude, timeout=10.0):
    """Взлет на заданную высоту."""
    print(f"[УПРАВЛЕНИЕ] Команда взлета на {altitude} м...")
    
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0, 0, 0, 0,
        0, 0, altitude
    )
    
    ack = wait_for_ack(master, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, timeout)
    if ack is not None and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("[УПРАВЛЕНИЕ] Команда взлета принята")
        return True
    
    print("[УПРАВЛЕНИЕ] Таймаут подтверждения взлета")
    return False

def land(master, timeout=10.0):
    """Посадка."""
    print("[УПРАВЛЕНИЕ] Команда посадки...")
    
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0,
        0, 0, 0, 0,
        0, 0, 0
    )
    
    ack = wait_for_ack(master, mavutil.mavlink.MAV_CMD_NAV_LAND, timeout)
    if ack is not None and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("[УПРАВЛЕНИЕ] Команда посадки принята")
        return True
    
    print("[УПРАВЛЕНИЕ] Таймаут подтверждения посадки")
    return False

def wait_for_altitude(state_getter, target_alt, tolerance=1.0, timeout=60.0):
    """Ожидание высоты."""
    print(f"[УПРАВЛЕНИЕ] Ожидание высоты {target_alt}±{tolerance} м...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        state = state_getter()
        if abs(state.alt_rel_m - target_alt) <= tolerance:
            print(f"[УПРАВЛЕНИЕ] Высота {state.alt_rel_m:.1f} м достигнута")
            return True
        print(f"  Текущая высота: {state.alt_rel_m:.1f} м")
        time.sleep(1)
    
    print(f"[УПРАВЛЕНИЕ] Таймаут ожидания высоты")
    return False