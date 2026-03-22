import time
from pwm_link import PWMLink

schedule = [

    (3, 1800),
    (5, 1100),
    (7, 1000),
    (10,1000)
]


def run_schedule(schedule, port="COM8"):
    schedule = sorted(schedule, key=lambda x: x[0])

    with PWMLink(port=port) as link:
        print(link.arm())

        t0 = time.time()

        for target_t, pwm_us in schedule:
            while True:
                elapsed = time.time() - t0
                remaining = target_t - elapsed
                if remaining <= 0:
                    break
                time.sleep(min(0.001, remaining))

            if pwm_us == 1000:
                reply = link.stop()
            else:
                reply = link.set_pwm_us(pwm_us, read_reply=True)

            print(f"t={target_t:.2f}s  pwm={pwm_us}  reply={reply}")

        print(link.disarm())


if __name__ == "__main__":
    run_schedule(schedule)