# -*- coding: utf-8 -*-
"""
CLI sender for ESP32 PWM controller.
"""

import argparse
import csv
import time
from pwm_link import PWMLink


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", default="COM8")
    p.add_argument("--cmd", choices=["ping", "arm", "disarm", "stop", "set"], required=True)
    p.add_argument("--us", type=int, help="pulse width for --cmd set (1000..2000)")
    p.add_argument("--csv", help="optional csv log file")
    args = p.parse_args()

    log_writer = None
    f = None
    if args.csv:
        f = open(args.csv, "a", newline="")
        log_writer = csv.writer(f)
        if f.tell() == 0:
            log_writer.writerow(["epoch_s", "cmd", "value", "reply"])

    with PWMLink(port=args.port) as link:
        if args.cmd == "ping":
            reply = link.ping()
            value = ""
        elif args.cmd == "arm":
            reply = link.arm()
            value = 1000
        elif args.cmd == "disarm":
            reply = link.disarm()
            value = 0
        elif args.cmd == "stop":
            reply = link.stop()
            value = 0
        else:
            if args.us is None:
                raise SystemExit("Need --us for cmd=set")
            reply = link.set_pwm_us(args.us)
            value = args.us

        print("REPLY:", reply)

        if log_writer:
            log_writer.writerow([time.time(), args.cmd, value, reply if reply else ""])
            f.flush()

    if f:
        f.close()


if __name__ == "__main__":
    main()