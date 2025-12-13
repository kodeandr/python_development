"""
Модуль мониторинга состояния дрона 
"""
from dataclasses import dataclass
import time
from pymavlink import mavutil

@dataclass
class DroneState:
    """Структура с текущим состоянием дрона."""
    last_update: float = 0.0
    mode: str = ""
    armed: bool = False
    lat_deg: float = 0.0
    lon_deg: float = 0.0
    alt_rel_m: float = 0.0
    battery_voltage_v: float = 0.0

def monitor_loop(master: mavutil.mavlink_connection,
                state: DroneState,
                stop_flag_getter=lambda: False) -> None:
    """
    Цикл опроса MAVLink-сообщений.
    """
    print("[МОНИТОРИНГ] Цикл запущен")
    
    while not stop_flag_getter():
        msg = master.recv_match(blocking=True, timeout=0.5)
        now = time.time()
        
        if msg is None:
            continue
            
        msg_type = msg.get_type()
        
        if msg_type == 'HEARTBEAT':
            # Режим и ARM
            state.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            mode_mapping = master.mode_mapping()
            if mode_mapping:
                inv_mapping = {v: k for k, v in mode_mapping.items()}
                state.mode = inv_mapping.get(msg.custom_mode, f"UNKNOWN({msg.custom_mode})")
                
        elif msg_type == 'GLOBAL_POSITION_INT':
            # Координаты
            state.lat_deg = msg.lat / 1e7
            state.lon_deg = msg.lon / 1e7
            state.alt_rel_m = msg.relative_alt / 1000.0
            
        elif msg_type == 'SYS_STATUS' and msg.voltage_battery > 0:
            # Батарея
            state.battery_voltage_v = msg.voltage_battery / 1000.0
        
        state.last_update = now
    
    print("[МОНИТОРИНГ] Цикл остановлен") 