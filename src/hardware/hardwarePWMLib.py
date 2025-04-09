"""
This library is from https://pypi.org/project/rpi-hardware-pwm/

It provides access to hardware PWM via the sysfs interface on the Raspberry Pi.
You must enable the overlay in /boot/config.txt with:
dtoverlay=pwm-2chan

Example usage:
    pwm = HardwarePWM(0, hz=20)
    pwm.start(100)
    pwm.change_duty_cycle(50)
    pwm.change_frequency(50)
    pwm.stop()

Notes:
    - For RPi 1,2,3,4: use chip=0; for RPi 5: use chip=2
    - Channels 0, 1, 2, 3 are supported
    - Must set duty cycle to 0 before changing frequency
    - sysfs PWM documentation: https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

class HardwarePWMError(Exception):
    pass

class HardwarePWM:
    def __init__(self, channel: int, frequency_hz: float, chip: int = 0) -> None:
        if channel not in {0, 1, 2, 3}:
            raise HardwarePWMError("Only channels 0–3 are supported.")

        self._chip_path = f"/sys/class/pwm/pwmchip{chip}"
        self._pwm_path = f"{self._chip_path}/pwm{channel}"
        self._channel = channel
        self._duty_cycle = 0.0
        self._frequency_hz = frequency_hz

        if not os.path.isdir(self._chip_path):
            raise HardwarePWMError("Missing overlay: add 'dtoverlay=pwm-2chan' to /boot/config.txt and reboot.")
        if not os.access(os.path.join(self._chip_path, "export"), os.W_OK):
            raise HardwarePWMError(f"No write access to {self._chip_path}")
        if not os.path.isdir(self._pwm_path):
            self._export_pwm()

        # Set frequency once everything is ready
        while True:
            try:
                self.set_frequency(frequency_hz)
                break
            except PermissionError:
                continue

    def _export_pwm(self) -> None:
        self._write(self._channel, os.path.join(self._chip_path, "export"))

    def _write(self, value: int, filepath: str) -> None:
        with open(filepath, "w") as f:
            f.write(f"{value}\n")

    def start(self, duty_cycle: float) -> None:
        self.set_duty_cycle(duty_cycle)
        self._write(1, os.path.join(self._pwm_path, "enable"))

    def stop(self) -> None:
        self.set_duty_cycle(0)
        self._write(0, os.path.join(self._pwm_path, "enable"))

    def set_duty_cycle(self, duty_cycle: float) -> None:
        if not (0 <= duty_cycle <= 100):
            raise HardwarePWMError("Duty cycle must be between 0 and 100.")

        self._duty_cycle = duty_cycle
        period_ns = int((1 / self._frequency_hz) * 1_000_000_000)
        duty_ns = int(period_ns * duty_cycle / 100)
        self._write(duty_ns, os.path.join(self._pwm_path, "duty_cycle"))

    def set_frequency(self, frequency_hz: float) -> None:
        if frequency_hz < 0.1:
            raise HardwarePWMError("Frequency must be >= 0.1 Hz.")

        self._frequency_hz = frequency_hz
        current_duty = self._duty_cycle

        if current_duty > 0:
            self.set_duty_cycle(0)

        period_ns = int((1 / frequency_hz) * 1_000_000_000)
        self._write(period_ns, os.path.join(self._pwm_path, "period"))

        self.set_duty_cycle(current_duty)