"""
Главная программа
"""
import sys
import time
import threading
from pymavlink import mavutil
from drone_monitor import DroneState, monitor_loop
from flight_control import set_mode_guided, set_mode_auto, arm, takeoff, land
from mission_control import upload_simple_mission

def wait_for_gps(state: DroneState, timeout=30.0):
    """Ожидание GPS-фиксации."""
    print("[GPS] Ожидание координат...")
    start = time.time()
    while time.time() - start < timeout:
        if state.lat_deg != 0 and state.lon_deg != 0:
            print(f"[GPS] Получено: {state.lat_deg:.6f}, {state.lon_deg:.6f}")
            return True
        time.sleep(1)
    print("[GPS] Таймаут!")
    return False

def wait_for_altitude(state: DroneState, target_alt, tolerance=1.0, timeout=30.0):
    """Ожидание высоты."""
    print(f"[ВЫСОТА] Ожидание {target_alt} м...")
    start = time.time()
    while time.time() - start < timeout:
        if state.alt_rel_m >= target_alt - tolerance:
            print(f"[ВЫСОТА] Достигнуто: {state.alt_rel_m:.1f} м")
            return True
        print(f"  текущая: {state.alt_rel_m:.1f} м")
        time.sleep(1)
    return False

def main():
    # 1. Подключение
    print("="*50)
    print("БПЛА-Контроллер")
    print("="*50)
    
    try:
        master = mavutil.mavlink_connection("tcp:127.0.0.1:14550")
        master.wait_heartbeat()
        print(f"[ПОДКЛЮЧЕНИЕ] Система {master.target_system}, компонент {master.target_component}")
    except:
        print("[ОШИБКА] Не удалось подключиться. Запущен ли SITL?")
        sys.exit(1)
    
    # 2. Запуск мониторинга
    state = DroneState()
    stop_monitor = False
    monitor_thread = threading.Thread(
        target=monitor_loop,
        args=(master, state, lambda: stop_monitor),
        daemon=True
    )
    monitor_thread.start()
    time.sleep(2)
    
    try:
        # 3. Ждем GPS
        if not wait_for_gps(state):
            stop_monitor = True
            sys.exit(1)
        
        # 4. ПОДГОТОВКА МИССИИ (останавливаем мониторинг на время загрузки)
        print("\n[ЭТАП] Подготовка миссии")
        print("[МИССИЯ] Останавливаем мониторинг для загрузки...")
        stop_monitor = True
        monitor_thread.join(timeout=2)
        
        # Загружаем простую миссию
        if not upload_simple_mission(master, state.lat_deg, state.lon_deg):
            print("[ОШИБКА] Не удалось загрузить миссию")
            # Перезапускаем мониторинг
            stop_monitor = False
            monitor_thread = threading.Thread(
                target=monitor_loop,
                args=(master, state, lambda: stop_monitor),
                daemon=True
            )
            monitor_thread.start()
            sys.exit(1)
        
        # Перезапускаем мониторинг
        print("[МИССИЯ] Перезапуск мониторинга...")
        stop_monitor = False
        monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(master, state, lambda: stop_monitor),
            daemon=True
        )
        monitor_thread.start()
        time.sleep(2)
        
        # 5. УПРАВЛЕНИЕ ПОЛЕТОМ
        print("\n[ЭТАП] Управление полетом")
        print("[ИНФО] Нажмите Enter для начала...")
        input()
        
        # Шаг 1: GUIDED
        set_mode_guided(master)
        print(f"  Режим: {state.mode}")
        
        # Шаг 2: ARM
        arm(master)
        for _ in range(10):
            if state.armed:
                print("  Дрон ARM")
                break
            time.sleep(1)
        
        # Шаг 3: Взлет на 10м
        takeoff(master, 10.0)
        if not wait_for_altitude(state, 10.0):
            print("[ОШИБКА] Взлет не удался")
        else:
            print("[УСПЕХ] Взлет выполнен!")
            time.sleep(5)  # Висение 5 секунд
            
            # Шаг 4: AUTO (выполнение миссии)
            print("\n[ЭТАП] Выполнение миссии")
            set_mode_auto(master)
            print(f"  Режим: {state.mode}")
            
            # Ждем 30 секунд выполнения миссии
            print("  Выполнение миссии (15 сек)...")
            for i in range(15):
                print(f"    t={i}: высота={state.alt_rel_m:.1f}м, режим={state.mode}")
                time.sleep(1)
            
            # Шаг 5: Посадка
            print("\n[ЭТАП] Посадка")
            land(master)
            time.sleep(20)
            
            print("\n" + "="*50)
            print("[УСПЕХ] Программа выполнена!")
            print("="*50)
        
    except KeyboardInterrupt:
        print("\n[ИНФО] Прервано пользователем")
    except Exception as e:
        print(f"\n[ОШИБКА] {e}")
    finally:
        # Завершение
        print("\n[ЗАВЕРШЕНИЕ] Остановка...")
        stop_monitor = True
        monitor_thread.join(timeout=2)
        print("Программа завершена.")

if __name__ == "__main__":
    main()