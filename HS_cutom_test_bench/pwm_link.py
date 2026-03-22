# -*- coding: utf-8 -*-

import time
import serial


class PWMLink:
    def __init__(self, port="COM8", baud=115200, timeout=1.0, boot_delay_s=2.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.boot_delay_s = boot_delay_s
        self.ser = None

    def open(self):
        if self.ser and self.ser.is_open:
            return

        self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)

        try:
            self.ser.dtr = False
        except Exception:
            pass

        try:
            self.ser.rts = False
        except Exception:
            pass

        time.sleep(self.boot_delay_s)

        try:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
        except Exception:
            pass

    def close(self):
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None

    def _send_line(self, text: str, read_reply=True):
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial not open. Call open() first.")

        self.ser.write((text + "\n").encode("utf-8"))
        self.ser.flush()

        if not read_reply:
            return None

        reply = self.ser.readline().decode(errors="ignore").strip()
        return reply if reply else None

    def ping(self):
        return self._send_line("PING", read_reply=True)

    def arm(self):
        return self._send_line("ARM", read_reply=True)

    def disarm(self):
        return self._send_line("DISARM", read_reply=True)

    def stop(self):
        return self._send_line("STOP", read_reply=True)

    def set_pwm_us(self, us: int, read_reply=True):
        return self._send_line(str(int(us)), read_reply=read_reply)

    def safe_disarm(self):
        try:
            reply = self.disarm()
            time.sleep(0.15)
            return reply
        except Exception:
            return None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.safe_disarm()
        finally:
            self.close()