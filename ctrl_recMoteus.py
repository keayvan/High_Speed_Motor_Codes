import asyncio
import math
import moteus
import time
import threading
from moteus import moteus_tool
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class CsvController(moteus.Controller):
    """Operates a controller, while writing data to a CSV file.

    Every operation which results in a query, will emit a single line
    to the CSV file.  The set of values to be written will be those
    which are configured in the `query_resolution` kwarg parameter.

    This is a context manager, and can be used with `with` statements.

    """

    def __init__(self,
                 filename=None,
                 *args,
                 relative_time=True,
                 **kwargs):
        super(CsvController, self).__init__(*args, **kwargs)

        self.fields = [field for field, resolution in
                       moteus.QueryParser.parse(self.make_query().data)]

        self.fd = open(filename, "w")
        self.relative_time = relative_time
        self._start_time = time.time()

        def format_reg(x):
            try:
                return moteus.Register(x).name
            except TypeError:
                return f'0x{x:03x}'

        print(",".join(["time"] + list(map(format_reg, self.fields))),
              file=self.fd)

    # Override the base `execute` method, but if a result is returned,
    # emit a line to the CSV file.
    async def execute(self, command):
        result = await super(CsvController, self).execute(command)

        if result is not None:
            now = time.time()
            output_time = now - self._start_time if self.relative_time else now
            print(",".join(list(map(str,
                                    [output_time] +
                                    [result.values.get(x, 0)
                                     for x in self.fields]))),
                  file=self.fd)

        return result

    def __enter__(self):
        self.fd.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.fd.__exit__(exc_type, exc_value, traceback)


async def wait_stopped(controller, time_s, period_s=0.025):
    '''Hold the controller at the current position for a given amount of
    time.'''

    start = time.time()
    while True:
        now = time.time()
        if (now - start) > time_s:
            return

        await controller.set_position(position=math.nan, velocity=0.0)
        await asyncio.sleep(period_s)


async def main(filename,pos=50, vel_limit=5, accel_limit=2, vel=[2000], stop_flag=[False]):
    qr = moteus.QueryResolution()
    qr.power = moteus.F32
    qr.q_current = moteus.F32
    qr.d_current = moteus.F32

    with CsvController(filename, query_resolution=qr) as c:
        await c.set_stop()

        while not stop_flag[0]:
            await c.set_position_wait_complete(position=pos, velocity_limit=vel_limit, accel_limit=accel_limit, velocity=[x / 60 for x in vel][0])
            #await wait_stopped(c, 1.0)

            #await c.set_position_wait_complete(position=0, velocity_limit=vel, accel_limit=accel_limit, velocity=vel[0])
            #await wait_stopped(c, 1.0)

def listen_for_velocity_change(vel, stop_flag):
    while True:
        try:
            command = input("Enter new velocity or 's' to stop: ")
            if command.lower() == "s":
                stop_flag[0] = True
                break
            new_vel = float(command)
            vel[0] = new_vel
        except ValueError:
            print("Invalid input. Please enter a number or 's'.")


if __name__ == '__main__':
    pos = math.nan
    vel_limit = math.nan
    accel_limit = 20
    vel = [2000]  # Use a list to allow modification in the thread
    stop_flag = [False]  # Use a list to allow modification in the thread
    velocity_thread = threading.Thread(target=listen_for_velocity_change, args=(vel, stop_flag))
    velocity_thread.start()
    fldr_name = './data/resultMoteus/'
    file_name = 'test.csv'
    asyncio.run(main(filename=file_name,pos=pos, vel_limit=vel_limit, accel_limit=accel_limit, vel=vel, stop_flag=stop_flag))