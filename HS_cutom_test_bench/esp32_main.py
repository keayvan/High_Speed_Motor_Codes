from machine import Pin, PWM
import sys
import select
import time

PWM_PIN = 13
PERIOD_US = 20000
FREQ = 1_000_000 // PERIOD_US

pwm_pin = Pin(PWM_PIN, Pin.OUT, value=0)
pwm = None
armed = False
current_us = 0


def ensure_pwm():
    global pwm
    if pwm is None:
        pwm = PWM(pwm_pin)
        pwm.freq(FREQ)


def set_pulse_us(pulse_us: int):
    global current_us
    ensure_pwm()
    duty = int(pulse_us * 65535 / PERIOD_US)
    pwm.duty_u16(duty)
    current_us = pulse_us


def detach_output():
    global pwm, current_us

    if pwm is not None:
        try:
            pwm.deinit()
        except Exception:
            pass
        pwm = None

    pwm_pin.init(Pin.OUT)
    pwm_pin.value(0)

    current_us = 0


def stop_output():
    global current_us
    ensure_pwm()
    set_pulse_us(1000)
    current_us = 1000


def status_text():
    return f"armed={int(armed)} pwm={current_us}"


# Startup: keep it safe (no signal)
detach_output()
print("READY")


while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()

        if not line:
            continue

        cmd = line.upper()

        if cmd == "PING":
            print(f"OK: PING {status_text()}")

        elif cmd == "ARM":
            armed = True
            stop_output()
            print("OK: ARM 1000")

        elif cmd == "DISARM":
            armed = False
            detach_output()
            print("OK: DISARM DETACHED")

        elif cmd == "STOP":
            armed = False
            stop_output()
            print("OK: STOP 1000")

        else:
            try:
                us = int(line)

                if us == 1000:
                    armed = False
                    stop_output()
                    print("OK: STOP 1000")

                elif 1000 <= us <= 2000:
                    if not armed:
                        print("BLOCKED: DISARMED")
                    else:
                        set_pulse_us(us)
                        print(f"OK: {us}")

                else:
                    print("Range 1000-2000")

            except Exception:
                print("Invalid input")

    time.sleep_ms(2)