"""
Модуль управления полетом
"""
import time
from pymavlink import mavutil

def set_mode_guided(master: mavutil.mavlink_connection) -> None:
    """Перевод в режим GUIDED."""
    print("[УПР] Перевод в GUIDED...")
    mode_id = master.mode_mapping()["GUIDED"]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    time.sleep(2)

def set_mode_auto(master: mavutil.mavlink_connection) -> None:
    """Перевод в режим AUTO."""
    print("[УПР] Перевод в AUTO...")
    mode_id = master.mode_mapping()["AUTO"]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    time.sleep(2)

def arm(master: mavutil.mavlink_connection) -> None:
    """ARM двигателей."""
    print("[УПР] ARM...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0
    )
    time.sleep(2)

def takeoff(master: mavutil.mavlink_connection, alt_m: float) -> None:
    """Взлет на заданную высоту."""
    print(f"[УПР] Взлет на {alt_m} м...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, alt_m
    )

def land(master: mavutil.mavlink_connection) -> None:
    """Посадка."""
    print("[УПР] Посадка...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0, 0, 0, 0, 0, 0, 0, 0
    ) 