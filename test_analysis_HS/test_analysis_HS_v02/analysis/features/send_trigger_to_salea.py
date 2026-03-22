# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 17:05:01 2026

@author: kkeramati
"""

from saleae.automation import Manager
import threading

from saleae import automation
from pathlib import Path
from saleae.automation.errors import DeviceError, InvalidRequestError


with Manager(port=10430) as m:
    print("Connected to Saleae Logic 2")

with automation.Manager.connect(port=10430) as manager:
    print(manager.get_devices())



# Connection / device
# -------------------------
ADDRESS = "localhost"
PORT = 10430
DEVICE_ID = "3E988F08F9058108"

# -------------------------
# Channels
# -------------------------
DIGITAL_CHANNELS = [0]                 # D0
ANALOG_CHANNELS  = list(range(8))      # A0..A7

# -------------------------
# Sample rates (MUST be one of the allowed pairs for this channel config)
# Your device error listed these as valid for the current config:
DIGITAL_SAMPLE_RATE = 6_250_000
ANALOG_SAMPLE_RATE  = 1_562_500        # <-- what you want

# Threshold (Logic Pro 8/16 valid: 1.2, 1.8, 3.3) :contentReference[oaicite:3]{index=3}
DIGITAL_THRESHOLD_V = 3.3

# Optional glitch filters (empty = none). :contentReference[oaicite:4]{index=4}
GLITCH_FILTERS = []  # example: [automation.GlitchFilterEntry(channel_index=0, pulse_width_seconds=1e-6)]

# -------------------------
# Capture settings
# -------------------------
BUFFER_SIZE_MB = None   # e.g. 1024 for 1 GB buffer, or None to use default. :contentReference[oaicite:5]{index=5}

# Trigger
TRIGGER_CH = 0
TRIGGER_TYPE = automation.DigitalTriggerType.RISING
AFTER_TRIGGER_S = 0.002  # 2 ms post-trigger

# “Stop” fallback: if trigger doesn’t happen within this time, force stop
STOP_AFTER_S = 10.0      # set None to disable timeout stop

# Output
OUT_PATH = Path(r"C:\temp\saleae_triggered_capture.sal")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def main():
    with automation.Manager.connect(address=ADDRESS, port=PORT) as manager:
        # (Optional) show devices once
        print("Devices:", manager.get_devices())

        device_configuration = automation.LogicDeviceConfiguration(
            enabled_digital_channels=DIGITAL_CHANNELS,
            enabled_analog_channels=ANALOG_CHANNELS,
            digital_sample_rate=DIGITAL_SAMPLE_RATE,
            analog_sample_rate=ANALOG_SAMPLE_RATE,
            digital_threshold_volts=DIGITAL_THRESHOLD_V,
            glitch_filters=GLITCH_FILTERS,
        )

        capture_configuration = automation.CaptureConfiguration(
            buffer_size_megabytes=BUFFER_SIZE_MB,
            capture_mode=automation.DigitalTriggerCaptureMode(
                trigger_type=TRIGGER_TYPE,
                trigger_channel_index=TRIGGER_CH,
                after_trigger_seconds=AFTER_TRIGGER_S,
            ),
        )

        try:
            with manager.start_capture(
                device_id=DEVICE_ID,
                device_configuration=device_configuration,
                capture_configuration=capture_configuration,
            ) as capture:

                # Optional timeout-stop thread (so you have a “stop command” even in trigger mode)
                stop_timer = None
                if STOP_AFTER_S is not None:
                    stop_timer = threading.Timer(STOP_AFTER_S, capture.stop)
                    stop_timer.daemon = True
                    stop_timer.start()

                print("Armed. Waiting for trigger (or timeout stop)...")
                # For DigitalTriggerCaptureMode you normally use wait(). :contentReference[oaicite:6]{index=6}
                # If the timer fires first, capture.stop() will end the capture.
                try:
                    capture.wait()
                except DeviceError:
                    # If we stopped early, wait() may raise depending on device state.
                    # We’ll still attempt to save if capture ended cleanly.
                    pass
                finally:
                    if stop_timer is not None:
                        stop_timer.cancel()

                capture.save_capture(str(OUT_PATH))
                print(f"Saved: {OUT_PATH}")

        except InvalidRequestError as e:
            print("InvalidRequestError:", e)
            print("➡️ Your sample rates must match one of the allowed pairs returned by Logic 2 for this channel set.")
        except DeviceError as e:
            print("DeviceError:", e)

if __name__ == "__main__":
    main()
