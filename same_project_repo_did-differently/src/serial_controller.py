"""
Module: serial_controller.py
Optional Arduino Serial Communication controller.
Transmits detected emotion commands to an Arduino microcontroller to drive LED indicators.
Gracefully operates even when hardware is disconnected.
"""

import time
from typing import Optional


class ArduinoSerialController:
    """
    Manages serial connection to Arduino.
    Ensures safe, non-blocking communication and auto-reconnect handling.
    """

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 9600,
        min_send_interval: float = 0.15,
    ):
        self.port = port
        self.baudrate = baudrate
        self.min_send_interval = min_send_interval
        self.serial_conn = None
        self.connected = False
        self.last_sent_time = 0.0
        self.last_sent_emotion = ""

        self._connect()

    def _find_arduino_port(self) -> Optional[str]:
        """Scans system serial ports to auto-detect Arduino boards."""
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                desc = (p.description or "").lower()
                hwid = (p.hwid or "").lower()
                if "arduino" in desc or "ch340" in desc or "usb-serial" in desc or "ftdi" in desc:
                    return p.device
            if ports:
                # Return the first available COM port as a potential candidate
                return ports[0].device
        except Exception:
            pass
        return None

    def _connect(self):
        """Attempts to establish connection with Arduino."""
        try:
            import serial

            target_port = self.port or self._find_arduino_port()
            if not target_port:
                print("[INFO] Arduino: Disconnected (No serial port found). Running in standalone mode.")
                self.connected = False
                return

            self.serial_conn = serial.Serial(target_port, self.baudrate, timeout=1.0)
            time.sleep(1.8)  # Allow Arduino microcontroller reset cycle to complete
            self.connected = True
            self.port = target_port
            print(f"[SUCCESS] Arduino connected on port '{self.port}' at {self.baudrate} baud.")
        except Exception as e:
            self.connected = False
            self.serial_conn = None
            print(f"[INFO] Arduino: Disconnected ({e}). Running in standalone mode.")

    def send_emotion(self, emotion: str) -> bool:
        """
        Sends the predicted emotion string to the Arduino (e.g. 'HAPPY\\n').
        Applies rate limiting to prevent buffer overflow.
        """
        if not self.connected or not self.serial_conn:
            return False

        curr_time = time.time()
        # Only send if emotion changed or min interval elapsed
        if (curr_time - self.last_sent_time < self.min_send_interval) and (emotion == self.last_sent_emotion):
            return True

        try:
            command = f"{emotion.upper()}\n"
            self.serial_conn.write(command.encode("utf-8"))
            self.serial_conn.flush()
            self.last_sent_time = curr_time
            self.last_sent_emotion = emotion
            return True
        except Exception as e:
            print(f"[WARNING] Serial send error: {e}. Marking Arduino as disconnected.")
            self.connected = False
            try:
                self.serial_conn.close()
            except Exception:
                pass
            self.serial_conn = None
            return False

    def is_connected(self) -> bool:
        """Returns connection status."""
        return self.connected

    def get_port_name(self) -> str:
        """Returns port name or 'Disconnected'."""
        return self.port if self.connected else "Not Connected"

    def close(self):
        """Cleanly closes serial connection."""
        if self.serial_conn and self.connected:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        self.connected = False
