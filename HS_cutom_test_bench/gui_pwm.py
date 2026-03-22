# -*- coding: utf-8 -*-

import tkinter as tk
import time
import csv
from collections import deque

from pwm_link import PWMLink

START_ARMED = False
ARMING_DELAY_MS = 2000


def run_gui(port="COM8", plot=False,
            pwm_min=1000, pwm_max=2000,
            send_debounce_ms=30,
            window_s=10, update_ms=50,
            csv_path="pwm_log.csv"):

    root = tk.Tk()
    root.title("PWM Control")

    link = PWMLink(port=port)
    try:
        link.open()
        print(f"Serial opened on {port}")
    except Exception as e:
        print("Serial open error:", e)
        link = None

    armed_state = {"value": False}
    arming_state = {"value": False}

    value_var = tk.StringVar(value="DISARMED")
    reply_var = tk.StringVar(value="(connected)" if link else "(no link)")
    status_var = tk.StringVar(value="DISARMED")

    pending = {"id": None}
    is_stopping = {"value": False}

    csv_file = None
    csv_writer = None
    if csv_path:
        try:
            csv_file = open(csv_path, "a", newline="")
            csv_writer = csv.writer(csv_file)
            if csv_file.tell() == 0:
                csv_writer.writerow(["epoch_s", "event", "value", "reply"])
        except Exception as e:
            print("CSV open error:", e)
            csv_file = None
            csv_writer = None

    def log_event(event, value=None, reply=None):
        if not csv_writer:
            return
        csv_writer.writerow([
            time.time(),
            event,
            "" if value is None else value,
            "" if reply is None else reply
        ])
        csv_file.flush()

    tk.Label(root, text="Pulse width (µs)").pack(pady=6)

    scale = tk.Scale(
        root,
        from_=pwm_min,
        to=pwm_max,
        orient="horizontal",
        length=520
    )
    scale.set(pwm_min)
    scale.configure(state="disabled")
    scale.pack(padx=10, pady=6)

    tk.Label(root, textvariable=value_var, font=("Arial", 14)).pack(pady=2)
    tk.Label(root, textvariable=reply_var).pack(pady=2)
    tk.Label(root, textvariable=status_var, font=("Arial", 10, "italic")).pack(pady=2)

    canvas = None
    ax = None
    line = None
    ts = deque()
    pws = deque()
    t0 = time.time()

    if plot:
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        fig = Figure(figsize=(6.6, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("PWM (µs)")
        ax.set_ylim(pwm_min - 50, pwm_max + 50)
        line, = ax.plot([], [])

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().pack(padx=10, pady=10, fill="both", expand=True)

    def log_point(us):
        t = time.time() - t0
        ts.append(t)
        pws.append(us)
        while ts and (ts[-1] - ts[0]) > window_s:
            ts.popleft()
            pws.popleft()

    def update_plot():
        if plot and ts:
            line.set_data(list(ts), list(pws))
            ax.set_xlim(max(0, ts[-1] - window_s), max(window_s, ts[-1]))
            canvas.draw_idle()
        root.after(update_ms, update_plot)

    def safe_link_call(fn, *args, **kwargs):
        if link is None:
            return "NO LINK"
        try:
            reply = fn(*args, **kwargs)
            print("Serial reply:", repr(reply))
            return reply
        except Exception as e:
            print("Serial exception:", e)
            return f"SERIAL ERR: {e}"

    def cancel_pending_send():
        if pending["id"] is not None:
            try:
                root.after_cancel(pending["id"])
            except Exception:
                pass
            pending["id"] = None

    def update_button_states():
        if arming_state["value"]:
            arm_btn.configure(state="disabled")
            disarm_btn.configure(state="normal")
            scale.configure(state="disabled")
            status_var.set("ARMING...")
        elif armed_state["value"]:
            arm_btn.configure(state="disabled")
            disarm_btn.configure(state="normal")
            scale.configure(state="normal")
            status_var.set("ARMED")
        else:
            arm_btn.configure(state="normal")
            disarm_btn.configure(state="disabled")
            scale.configure(state="disabled")
            status_var.set("DISARMED")

    def finish_arming():
        arming_state["value"] = False
        armed_state["value"] = True
        value_var.set(f"{pwm_min} µs")
        reply_var.set("ARMED AND READY")
        update_button_states()
        log_event("armed_ready", pwm_min, "ready")

    def do_arm():
        print("DEBUG: do_arm called")
        is_stopping["value"] = False
        cancel_pending_send()

        reply = safe_link_call(link.arm) if link else None

        arming_state["value"] = True
        armed_state["value"] = False

        scale.set(pwm_min)
        value_var.set(f"{pwm_min} µs")
        reply_var.set(reply if reply else "ARMING...")
        update_button_states()
        log_event("arm", pwm_min, reply)

        if plot:
            log_point(pwm_min)

        root.after(ARMING_DELAY_MS, finish_arming)

    def do_disarm():
        print("DEBUG: do_disarm called")
        is_stopping["value"] = True
        cancel_pending_send()

        arming_state["value"] = False
        armed_state["value"] = False

        reply = safe_link_call(link.disarm) if link else None

        value_var.set("DISARMED")
        reply_var.set(reply if reply else "DISARMED")
        log_event("disarm", 0, reply)

        if plot:
            log_point(0)

        update_button_states()

        root.update_idletasks()
        time.sleep(0.15)
        is_stopping["value"] = False

    def do_stop():
        print("DEBUG: do_stop called")
        is_stopping["value"] = True
        cancel_pending_send()

        arming_state["value"] = False
        armed_state["value"] = False

        reply = safe_link_call(link.stop) if link else None

        value_var.set("STOPPED")
        reply_var.set(reply if reply else "STOPPED")
        log_event("stop", pwm_min, reply)

        if plot:
            log_point(pwm_min)

        update_button_states()

        root.update_idletasks()
        time.sleep(0.15)
        is_stopping["value"] = False

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=8)

    arm_btn = tk.Button(
        btn_frame,
        text="ARM",
        font=("Arial", 12, "bold"),
        bg="green",
        fg="white",
        width=10,
        command=do_arm
    )
    arm_btn.grid(row=0, column=0, padx=6)

    disarm_btn = tk.Button(
        btn_frame,
        text="DISARM",
        font=("Arial", 12, "bold"),
        width=10,
        command=do_disarm
    )
    disarm_btn.grid(row=0, column=1, padx=6)

    stop_btn = tk.Button(
        root,
        text="STOP",
        font=("Arial", 14, "bold"),
        bg="red",
        fg="white",
        width=12,
        height=2,
        command=do_stop
    )
    stop_btn.pack(pady=8)

    def send_pwm(us):
        pending["id"] = None

        if is_stopping["value"]:
            return

        if arming_state["value"]:
            reply_var.set("ARMING... WAIT")
            return

        if not armed_state["value"]:
            reply_var.set("DISARMED - blocked")
            return

        value_var.set(f"{us} µs")
        reply = safe_link_call(link.set_pwm_us, us) if link else None
        reply_var.set(reply if reply else "(no reply)")
        status_var.set("ARMED")
        log_event("set", us, reply)

        if plot:
            log_point(us)

    def on_slider(_v=None):
        cancel_pending_send()
        pending["id"] = root.after(send_debounce_ms, lambda: send_pwm(int(scale.get())))

    scale.configure(command=on_slider)

    def on_close():
        print("DEBUG: on_close called")
        is_stopping["value"] = True
        cancel_pending_send()

        try:
            if link:
                try:
                    safe_link_call(link.disarm)
                    time.sleep(0.2)
                finally:
                    link.close()
        finally:
            if csv_file:
                csv_file.close()
            root.destroy()

    if START_ARMED:
        do_arm()
    else:
        armed_state["value"] = False
        arming_state["value"] = False
        value_var.set("DISARMED")
        status_var.set("DISARMED")
        update_button_states()

    root.after(update_ms, update_plot)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    run_gui(port="COM8", plot=True)