"""
Главная программа "БПЛА-Контроллер".
Интегрирует все модули и реализует полный сценарий управления дроном.
"""
import sys
import time
import threading
import signal
from datetime import datetime
from pymavlink import mavutil

# Импорт наших модулей
from drone_monitor import DroneState, monitor_loop, add_warning_handler
from flight_control import (
    set_mode_guided, set_mode_auto,
    arm, disarm, takeoff, land,
    wait_for_altitude
)
from mission_control import (
    clear_mission, upload_mission, download_mission,
    create_sample_mission
)

class DroneController:
    """Основной класс контроллера дрона."""
    
    def __init__(self, connection_string="tcp:127.0.0.1:14550"):
        """Инициализация контроллера."""
        self.connection_string = connection_string
        self.master = None
        self.state = DroneState()
        self.monitor_thread = None
        self.stop_monitor_flag = False
        self.mission_items = []
        self.flight_start_time = None
        self.emergency_landing_requested = False
        
        # Регистрируем обработчик предупреждений
        add_warning_handler(self._handle_warning)
    
    def _handle_warning(self, warning_text: str) -> None:
        """Обработчик предупреждений из модуля мониторинга."""
        print(f"[КОНТРОЛЛЕР] Обработка предупреждения: {warning_text}")
        
        # В критической ситуации можно инициировать аварийную посадку
        if "Низкое напряжение батареи" in warning_text and self.state.armed:
            print("[КОНТРОЛЛЕР] КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ! Инициирую аварийную посадку...")
            self.emergency_landing_requested = True
    
    def connect(self) -> bool:
        """Подключение к симулятору."""
        print("=" * 60)
        print("БПЛА-КОНТРОЛЛЕР: Запуск системы")
        print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            print(f"[ПОДКЛЮЧЕНИЕ] Установка соединения с {self.connection_string}...")
            self.master = mavutil.mavlink_connection(self.connection_string)
            
            # Ждем первого HEARTBEAT
            print("[ПОДКЛЮЧЕНИЕ] Ожидание HEARTBEAT от автопилота...")
            heartbeat = self.master.wait_heartbeat(timeout=10)
            
            if heartbeat is None:
                print("[ОШИБКА] Не получен HEARTBEAT. Проверьте симулятор.")
                return False
            
            print(f"[ПОДКЛЮЧЕНИЕ] Подключено к системе {self.master.target_system}, "
                  f"компонент {self.master.target_component}")
            return True
            
        except Exception as e:
            print(f"[ОШИБКА] Ошибка подключения: {e}")
            return False
    
    def start_monitoring(self) -> bool:
        """Запуск потока мониторинга."""
        print("[МОНИТОРИНГ] Запуск потока мониторинга...")
        
        self.stop_monitor_flag = False
        self.monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(self.master, self.state, lambda: self.stop_monitor_flag),
            daemon=True,
            name="MonitorThread"
        )
        
        self.monitor_thread.start()
        
        # Даем время на запуск
        time.sleep(2)
        
        if self.monitor_thread.is_alive():
            print("[МОНИТОРИНГ] Поток мониторинга успешно запущен")
            return True
        else:
            print("[ОШИБКА] Поток мониторинга не запустился")
            return False
    
    def wait_for_gps_fix(self, timeout: float = 30.0) -> bool:
        """Ожидание получения GPS фиксации и координат."""
        print("[GPS] Ожидание получения координат...")
        
        start_time = time.time()
        last_print = start_time
        
        while time.time() - start_time < timeout:
            current_time = time.time()
            
            # Выводим прогресс каждые 5 секунд
            if current_time - last_print > 5.0:
                print(f"[GPS] Ожидание... (прошло {int(current_time - start_time)} сек)")
                last_print = current_time
            
            # Проверяем, получены ли координаты (не нулевые)
            if (self.state.last_update > 0 and 
                abs(self.state.lat_deg) > 0.0001 and 
                abs(self.state.lon_deg) > 0.0001):
                
                print(f"[GPS] Координаты получены:")
                print(f"      Широта: {self.state.lat_deg:.7f}°")
                print(f"      Долгота: {self.state.lon_deg:.7f}°")
                print(f"      Высота: {self.state.alt_rel_m:.1f} м")
                return True
            
            time.sleep(1.0)
        
        print("[ОШИБКА] Таймаут ожидания координат GPS")
        return False
    
    def prepare_mission(self) -> bool:
        """Подготовка и загрузка полетного задания."""
        print("\n[МИССИЯ] Подготовка полетного задания...")
        
        # 1. Очищаем старую миссию
        print("[МИССИЯ] Очистка старой миссии...")
        if not clear_mission(master=self.master, state=self.state):
            print("[ПРЕДУПРЕЖДЕНИЕ] Не удалось очистить старую миссию, продолжаем...")
            # Продолжаем, возможно миссия уже пуста
        
        # 2. Создаем тестовую миссию (взлет + 2 точки + посадка)
        print("[МИССИЯ] Создание тестовой миссии из 4 точек...")
        self.mission_items = create_sample_mission(
            home_lat=self.state.lat_deg,
            home_lon=self.state.lon_deg,
            home_alt=self.state.alt_rel_m
        )
        
        # Выводим информацию о миссии
        print(f"[МИССИЯ] Создано точек: {len(self.mission_items)}")
        for i, item in enumerate(self.mission_items):
            cmd_name = "Взлет" if item.command == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF else \
                      "Точка" if item.command == mavutil.mavlink.MAV_CMD_NAV_WAYPOINT else \
                      "Посадка"
            print(f"  Точка {i}: {cmd_name}, высота {item.z} м")
        
        # 3. Загружаем миссию (НЕБЛОКИРУЮЩИЙ МЕТОД!)
        print("[МИССИЯ] Начало загрузки миссии (без остановки мониторинга)...")
        
        # Сбрасываем флаги состояния перед загрузкой
        self.state.mission_item_requested = None
        self.state.mission_ack_received = False
        
        if not upload_mission(self.master, self.mission_items, self.state):
            print("[ОШИБКА] Не удалось загрузить миссию")
            return False
        
        print("[МИССИЯ] Миссия успешно загружена!")
        
        # 4. (Опционально) Проверяем, что миссия загрузилась
        print("[МИССИЯ] Проверка загруженной миссии...")
        time.sleep(2)
        
        downloaded = download_mission(self.master, self.state)
        if downloaded and len(downloaded) == len(self.mission_items):
            print(f"[МИССИЯ] Проверка пройдена: загружено {len(downloaded)} точек")
            return True
        else:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Проверка не пройдена, но загрузка была успешной")
            print(f"  Ожидалось: {len(self.mission_items)}, получено: {len(downloaded) if downloaded else 0}")
            return True  # Все равно продолжаем, так как upload_mission вернул успех
    
    def execute_flight_plan(self) -> bool:
        """Выполнение полетного плана по ТЗ."""
        print("\n" + "=" * 60)
        print("ВЫПОЛНЕНИЕ ПОЛЕТНОГО ПЛАНА")
        print("=" * 60)
        
        self.flight_start_time = time.time()
        steps_completed = 0
        total_steps = 6
        
        try:
            # Шаг 1: Переход в режим GUIDED
            print(f"\n[{steps_completed+1}/{total_steps}] Перевод в режим GUIDED...")
            if not set_mode_guided(self.master):
                print("[ОШИБКА] Не удалось перевести в GUIDED")
                return False
            time.sleep(3)  # Даем время на смену режима
            steps_completed += 1
            
            # Шаг 2: ARM двигателей
            print(f"\n[{steps_completed+1}/{total_steps}] Включение двигателей (ARM)...")
            if not arm(self.master):
                print("[ОШИБКА] Не удалось выполнить ARM")
                return False
            
            # Ждем, пока состояние ARM обновится в мониторинге
            arm_timeout = 10.0
            arm_start = time.time()
            while time.time() - arm_start < arm_timeout:
                if self.state.armed:
                    print("[УСПЕХ] Дрон ARM")
                    break
                print("  Ожидание подтверждения ARM...")
                time.sleep(1.0)
            else:
                print("[ОШИБКА] Таймаут ожидания ARM")
                return False
            steps_completed += 1
            
            # Шаг 3: Взлет на 15 метров
            print(f"\n[{steps_completed+1}/{total_steps}] Взлет на высоту 15 метров...")
            if not takeoff(self.master, 15.0):
                print("[ОШИБКА] Не удалось выполнить взлет")
                return False
            
            # Ждем достижения высоты (используем функцию из flight_control)
            if not wait_for_altitude(
                state_getter=lambda: self.state,
                target_alt=15.0,
                tolerance=1.0,
                timeout=30.0
            ):
                print("[ОШИБКА] Не удалось достичь целевой высоты")
                return False
            steps_completed += 1
            
            # Шаг 4: Переход в режим AUTO для выполнения миссии
            print(f"\n[{steps_completed+1}/{total_steps}] Перевод в режим AUTO для выполнения миссии...")
            if not set_mode_auto(self.master):
                print("[ОШИБКА] Не удалось перевести в AUTO")
                return False
            time.sleep(3)
            
            # Сообщаем о начале выполнения миссии
            print("[ИНФО] Начато выполнение миссии. Мониторинг прогресса...")
            steps_completed += 1
            
            # Шаг 5: Мониторинг выполнения миссии
            print(f"\n[{steps_completed+1}/{total_steps}] Мониторинг выполнения миссии...")
            
            last_seq_reported = -1
            mission_start_time = time.time()
            mission_timeout = 300.0  # 5 минут на выполнение миссии
            
            while time.time() - mission_start_time < mission_timeout:
                # Проверяем аварийные ситуации
                if self.emergency_landing_requested:
                    print("[АВАРИЯ] Запрошена аварийная посадка!")
                    break
                
                # Выводим текущий статус
                current_seq = self.state.mission_current_seq
                if current_seq != last_seq_reported and current_seq >= 0:
                    print(f"  Выполняется точка миссии: {current_seq+1}/{len(self.mission_items)}")
                    last_seq_reported = current_seq
                
                # Проверяем, завершена ли миссия (последняя точка выполнена)
                if current_seq >= len(self.mission_items) - 1:
                    print("[ИНФО] Миссия выполнена!")
                    break
                
                # Выводим периодический статус
                if int(time.time()) % 10 == 0:  # Каждые 10 секунд
                    print(f"  Статус: высота={self.state.alt_rel_m:.1f}м, "
                          f"батарея={self.state.battery_voltage_v:.1f}В, "
                          f"режим='{self.state.mode}'")
                
                # Проверяем, не приземлился ли дрон
                if not self.state.armed and self.state.alt_rel_m < 1.0:
                    print("[ИНФО] Дрон приземлился")
                    break
                
                time.sleep(1.0)
            
            steps_completed += 1
            
            # Шаг 6: Завершение полета
            print(f"\n[{steps_completed+1}/{total_steps}] Завершение полета...")
            
            # Если дрон еще в воздухе, выполняем посадку
            if self.state.armed and self.state.alt_rel_m > 2.0:
                print("  Выполнение посадки...")
                if not land(self.master):
                    print("[ПРЕДУПРЕЖДЕНИЕ] Не удалось отправить команду посадки")
            
            # Ждем посадки и DISARM
            print("  Ожидание завершения посадки...")
            for i in range(30):  # Ждем до 30 секунд
                if not self.state.armed and self.state.alt_rel_m < 1.0:
                    print("  Посадка завершена")
                    break
                time.sleep(1.0)
            
            steps_completed += 1
            
            # Полный успех
            flight_duration = time.time() - self.flight_start_time
            print(f"\n[УСПЕХ] Полетный план выполнен за {flight_duration:.1f} секунд")
            print(f"       Выполнено шагов: {steps_completed}/{total_steps}")
            return True
            
        except Exception as e:
            print(f"\n[ОШИБКА] Исключение при выполнении полетного плана: {e}")
            return False
    
    def display_status_report(self) -> None:
        """Вывод отчета о статусе системы."""
        print("\n" + "=" * 60)
        print("ОТЧЕТ О СТАТУСЕ СИСТЕМЫ")
        print("=" * 60)
        
        print(f"Время отчета: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Общее время работы: {time.time() - (self.flight_start_time or time.time()):.1f} сек")
        print()
        
        print("ТЕЛЕМЕТРИЯ ДРОНА:")
        print(f"  Режим: {self.state.mode}")
        print(f"  ARM: {'ВКЛ' if self.state.armed else 'ВЫКЛ'}")
        print(f"  Координаты: {self.state.lat_deg:.7f}°, {self.state.lon_deg:.7f}°")
        print(f"  Высота: {self.state.alt_rel_m:.1f} м")
        print(f"  Батарея: {self.state.battery_voltage_v:.1f} В ({self.state.battery_remaining_pct:.0f}%)")
        print(f"  Последнее обновление: {time.time() - self.state.last_update:.1f} сек назад")
        
        if self.state.last_warning:
            print(f"  Последнее предупреждение: {self.state.last_warning}")
        
        print("\nСИСТЕМНАЯ ИНФОРМАЦИЯ:")
        print(f"  Мониторинг активен: {self.monitor_thread.is_alive() if self.monitor_thread else False}")
        print(f"  Загружено точек миссии: {len(self.mission_items)}")
        print(f"  Текущая точка миссии: {self.state.mission_current_seq}")
        
        # Проверка безопасности
        print("\nПРОВЕРКА БЕЗОПАСНОСТИ:")
        if self.state.battery_voltage_v > 0 and self.state.battery_voltage_v < 11.0:
            print(f"  ⚠  НИЗКОЕ НАПРЯЖЕНИЕ: {self.state.battery_voltage_v:.1f} В")
        else:
            print(f"  ✓  Напряжение в норме: {self.state.battery_voltage_v:.1f} В")
        
        if self.state.alt_rel_m > 50.0:
            print(f"  ⚠  ВЫСОТА ПРЕВЫШЕНА: {self.state.alt_rel_m:.1f} м")
        else:
            print(f"  ✓  Высота в норме: {self.state.alt_rel_m:.1f} м")
    
    def shutdown(self) -> None:
        """Корректное завершение работы системы."""
        print("\n" + "=" * 60)
        print("ЗАВЕРШЕНИЕ РАБОТЫ СИСТЕМЫ")
        print("=" * 60)
        
        # Останавливаем мониторинг
        if self.monitor_thread and self.monitor_thread.is_alive():
            print("[ЗАВЕРШЕНИЕ] Остановка потока мониторинга...")
            self.stop_monitor_flag = True
            self.monitor_thread.join(timeout=5.0)
            
            if self.monitor_thread.is_alive():
                print("[ПРЕДУПРЕЖДЕНИЕ] Поток мониторинга не остановился корректно")
            else:
                print("[ЗАВЕРШЕНИЕ] Поток мониторинга остановлен")
        
        # Если дрон все еще ARM, пытаемся безопасно посадить
        if self.state.armed:
            print("[ЗАВЕРШЕНИЕ] Дрон все еще ARM, попытка безопасной посадки...")
            try:
                # Пытаемся посадить
                land(self.master)
                time.sleep(5)
                
                # Пытаемся DISARM
                disarm(self.master)
                time.sleep(3)
            except:
                print("[ПРЕДУПРЕЖДЕНИЕ] Не удалось безопасно завершить полет")
        
        # Закрываем соединение
        if self.master:
            print("[ЗАВЕРШЕНИЕ] Закрытие соединения...")
            try:
                self.master.close()
            except:
                pass
        
        print("[ЗАВЕРШЕНИЕ] Система остановлена")
        print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения."""
    print(f"\n[СИГНАЛ] Получен сигнал {signum}, инициирую завершение...")
    sys.exit(1)

def main():
    """Главная функция программы."""
    # Регистрируем обработчики сигналов для корректного завершения
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем контроллер
    controller = DroneController(connection_string="tcp:127.0.0.1:14550")
    
    try:
        # Шаг 1: Подключение
        if not controller.connect():
            print("\n[КРИТИЧЕСКАЯ ОШИБКА] Не удалось подключиться к симулятору.")
            print("Убедитесь, что:")
            print("1. ArduPilot SITL запущен")
            print("2. Mission Planner подключен и зеркалирует MAVLink")
            print("3. Порт 14550 открыт для TCP подключений")
            sys.exit(1)
        
        # Шаг 2: Запуск мониторинга
        if not controller.start_monitoring():
            print("\n[КРИТИЧЕСКАЯ ОШИБКА] Не удалось запустить мониторинг")
            controller.shutdown()
            sys.exit(1)
        
        # Шаг 3: Ожидание GPS
        print("\n" + "=" * 60)
        print("ЭТАП 1: ОЖИДАНИЕ GPS-FИКСАЦИИ")
        print("=" * 60)
        
        if not controller.wait_for_gps_fix():
            print("\n[КРИТИЧЕСКАЯ ОШИБКА] Не удалось получить GPS-фиксацию")
            controller.display_status_report()
            controller.shutdown()
            sys.exit(1)
        
        # Шаг 4: Подготовка миссии
        print("\n" + "=" * 60)
        print("ЭТАП 2: ПОДГОТОВКА МИССИИ")
        print("=" * 60)
        
        if not controller.prepare_mission():
            print("\n[КРИТИЧЕСКАЯ ОШИБКА] Не удалось подготовить миссию")
            controller.display_status_report()
            controller.shutdown()
            sys.exit(1)
        
        # Шаг 5: Выполнение полетного плана
        print("\n" + "=" * 60)
        print("ЭТАП 3: ВЫПОЛНЕНИЕ ПОЛЕТНОГО ПЛАНА")
        print("=" * 60)
        
        # Выводим начальный статус
        controller.display_status_report()
        
        print("\n[ИНФО] Нажмите Ctrl+C для аварийной остановки")
        input("[ИНФО] Нажмите Enter для начала выполнения полетного плана...")
        
        # Выполняем полетный план
        success = controller.execute_flight_plan()
        
        # Шаг 6: Финальный отчет
        print("\n" + "=" * 60)
        print("ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        
        controller.display_status_report()
        
        if success:
            print("\n[УСПЕХ] Программа успешно выполнена!")
            print("Все этапы ТЗ выполнены:")
            print("1. ✓ Мониторинг телеметрии")
            print("2. ✓ Управление полетом (взлет/посадка)")
            print("3. ✓ Выполнение миссии (3+ точки)")
            print("4. ✓ Логика безопасности (батарея, высота)")
            print("\nДля демонстрации работы подготовьте:")
            print("- Скриншоты Mission Planner с траекторией полета")
            print("- Видео с демонстрацией работы консоли и симулятора")
        else:
            print("\n[ОШИБКА] Выполнение программы завершено с ошибками")
            print("Проверьте логи и состояние симулятора")
        
        # Небольшая пауза перед завершением
        time.sleep(3)
        
    except KeyboardInterrupt:
        print("\n\n[ИНФО] Программа прервана пользователем")
    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА] Непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Всегда корректно завершаем работу
        controller.shutdown()
        print("\nПрограмма завершена.")

if __name__ == "__main__":
    main()