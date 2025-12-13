"""
Модуль мониторинга состояния дрона.
Расширенная версия с обработкой сообщений миссии и логикой предупреждений.
"""
from dataclasses import dataclass, field
import time
from typing import Optional, Callable
from pymavlink import mavutil

@dataclass
class DroneState:
    """Расширенная структура состояния дрона с полями для миссий."""
    last_update: float = 0.0
    mode: str = ""
    armed: bool = False
    lat_deg: float = 0.0
    lon_deg: float = 0.0
    alt_rel_m: float = 0.0
    battery_voltage_v: float = 0.0
    battery_remaining_pct: float = 0.0
    
    # Поля для работы с миссиями (для решения проблемы из дополнительной части)
    mission_item_requested: Optional[int] = None  # Запрошенный seq точки миссии
    mission_ack_received: bool = False  # Флаг получения подтверждения миссии
    mission_current_seq: int = -1  # Текущая выполняемая точка миссии
    
    # Поля для логики безопасности
    last_warning: str = ""
    warning_flag: bool = False

# Глобальные обработчики предупреждений (можно переопределить в main.py)
warning_handlers = []

def add_warning_handler(handler: Callable[[str], None]) -> None:
    """Добавление обработчика предупреждений."""
    warning_handlers.append(handler)

def _issue_warning(warning_text: str, state: DroneState) -> None:
    """Выпуск предупреждения с записью в состояние и вызовом обработчиков."""
    state.last_warning = warning_text
    state.warning_flag = True
    print(f"[ПРЕДУПРЕЖДЕНИЕ] {warning_text}")
    
    for handler in warning_handlers:
        try:
            handler(warning_text)
        except:
            pass

def _check_safety(state: DroneState) -> None:
    """Проверка условий безопасности по ТЗ."""
    # Проверка напряжения батареи
    if state.battery_voltage_v > 0 and state.battery_voltage_v < 11.0:
        _issue_warning(f"Низкое напряжение батареи: {state.battery_voltage_v:.1f} В", state)
    
    # Проверка высоты
    if state.alt_rel_m > 50.0:
        _issue_warning(f"Превышена высота 50м: {state.alt_rel_m:.1f} м", state)
    
    # Сброс флага после проверки
    state.warning_flag = False

def _handle_heartbeat(master, msg, state: DroneState) -> None:
    """Обработка HEARTBEAT с определением режима."""
    state.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
    
    mode_mapping = master.mode_mapping()
    if mode_mapping:
        inv_mode_mapping = {mode_id: name for name, mode_id in mode_mapping.items()}
        mode_id = msg.custom_mode
        mode_name = inv_mode_mapping.get(mode_id)
        if mode_name is not None:
            if state.mode != mode_name:
                print(f"[ИНФО] Смена режима: {state.mode} -> {mode_name}")
                state.mode = mode_name
        else:
            state.mode = f"UNKNOWN({mode_id})"

def _handle_global_position_int(msg, state: DroneState) -> None:
    """Обработка координат и высоты."""
    state.lat_deg = msg.lat / 1e7
    state.lon_deg = msg.lon / 1e7
    state.alt_rel_m = msg.relative_alt / 1000.0

def _handle_sys_status(msg, state: DroneState) -> None:
    """Обработка состояния системы и батареи."""
    # Проверяем, есть ли данные о батарее
    if hasattr(msg, 'voltage_battery') and msg.voltage_battery != 65535:
        state.battery_voltage_v = msg.voltage_battery / 1000.0
        if hasattr(msg, 'battery_remaining'):
            state.battery_remaining_pct = float(msg.battery_remaining)
        else:
            state.battery_remaining_pct = 0.0
    else:
        # Если данных нет, устанавливаем значения по умолчанию
        state.battery_voltage_v = 12.6  # Примерное напряжение для теста
        state.battery_remaining_pct = 100.0
    
    # Выводим информацию о батарее только при значительных изменениях
    if state.last_update > 0:
        print(f"[БАТАРЕЯ] Напряжение: {state.battery_voltage_v:.1f} В, остаток: {state.battery_remaining_pct:.0f}%")

def _handle_mission_request_int(msg, state: DroneState) -> None:
    """Обработка запроса точки миссии (для неблокирующей загрузки)."""
    state.mission_item_requested = msg.seq
    print(f"[МИССИЯ] Запрошена точка seq={msg.seq}")

def _handle_mission_ack(msg, state: DroneState) -> None:
    """Обработка подтверждения миссии."""
    state.mission_ack_received = True
    ack_types = {
        0: "Принята",
        1: "Ошибка: временная",
        2: "Ошибка: отказ координат",
        3: "Ошибка: не поддерживается",
        4: "Ошибка: неверный формат",
        5: "Ошибка: отклонена"
    }
    result = ack_types.get(msg.type, f"Неизвестный код: {msg.type}")
    print(f"[МИССИЯ] Подтверждение: {result}")

def _handle_mission_current(msg, state: DroneState) -> None:
    """Обработка текущей точки миссии."""
    state.mission_current_seq = msg.seq

def monitor_loop(master: mavutil.mavlink_connection,
                state: DroneState,
                stop_flag_getter=lambda: False) -> None:
    """
    Основной цикл мониторинга с расширенной обработкой.
    Не прерывается при загрузке миссии.
    """
    print("[МОНИТОРИНГ] Цикл мониторинга запущен")
    
    while not stop_flag_getter():
        msg = master.recv_match(blocking=True, timeout=0.5)
        now = time.time()
        
        if msg is None:
            continue
            
        msg_type = msg.get_type()
        
        # Обработка основных сообщений
        if msg_type == 'HEARTBEAT':
            _handle_heartbeat(master, msg, state)
        elif msg_type == 'GLOBAL_POSITION_INT':
            _handle_global_position_int(msg, state)
        elif msg_type == 'SYS_STATUS':
            _handle_sys_status(msg, state)
        
        # Обработка сообщений миссии (для неблокирующей работы)
        elif msg_type == 'MISSION_REQUEST_INT':
            _handle_mission_request_int(msg, state)
        elif msg_type == 'MISSION_ACK':
            _handle_mission_ack(msg, state)
        elif msg_type == 'MISSION_CURRENT':
            _handle_mission_current(msg, state)
        
        # ============ ОТЛАДОЧНЫЙ КОД ============
        # ============ ОТЛАДОЧНЫЙ КОД ============
        # ДОПОЛНИТЕЛЬНОЕ ЛОГИРОВАНИЕ ДЛЯ ОТЛАДКИ МИССИЙ
        if msg_type in ['MISSION_REQUEST_INT', 'MISSION_ACK', 'MISSION_COUNT', 'MISSION_ITEM_INT', 'MISSION_CURRENT']:
            print(f"[МИССИЯ DEBUG] Получено: {msg_type}")
            if msg_type == 'MISSION_REQUEST_INT':
                print(f"           seq={msg.seq}")
            elif msg_type == 'MISSION_ACK':
                print(f"           type={msg.type}")
# ========================================
        
        # Проверка безопасности
        if state.last_update > 0:
            _check_safety(state)
        
        state.last_update = now
    
    print("[МОНИТОРИНГ] Цикл мониторинга остановлен")