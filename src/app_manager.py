import serial
import queue
import data
from data_structs import Struct
from rich.console import Console
from rich.table import Table

TEMP_MAX = 40.0
TEMP_CIRCLE_RAD = 70


def rgb_to_hex(r, g, b):
    return "#" + ("{:02X}" * 3).format(r, g, b)


def temp_to_color(temp: float) -> str:
    t = max(0.0, min(1.0, temp / TEMP_MAX))
    r = int(122 + (230 - 122) * t)
    g = int(230 + (14 - 230) * t)
    b = 14
    return rgb_to_hex(r, g, b)


class SensorData:
    def __init__(self):
        self.temp = 22.0
        self.humidity = 70
        self.pressure = 1000.0


class AppManager:
    def __init__(self, sensor_data: SensorData, con, window, config):
        self.sensor_data = sensor_data
        self.con = con
        self.w = window
        self.config = config
        self._console = Console()

    def save_to_db(self):
        print("zapisano")
        struct = Struct(
            temperatura=self.sensor_data.temp,
            cisnienie=self.sensor_data.pressure,
            wilgotnosc=int(self.sensor_data.humidity),
        )
        data.put_data(self.con, struct)

    def print_table(self):
        rows = data.get_all(self.con)

        table = Table(title="Pomiary")
        table.add_column("Temperatura (°C)", style="cyan", no_wrap=True)
        table.add_column("Ciśnienie (hPa)", style="magenta")
        table.add_column("Wilgotność (%)", style="green")
        table.add_column("Data pomiaru", style="white")

        for r in rows:
            table.add_row(
                str(r.temperatura),
                str(r.cisnienie),
                str(r.wilgotnosc),
                r.data_pomiaru or "",
            )

        self._console.print(table)

    def parse_line(self, line: str):
        try:
            parts = line.split(",")
            self.sensor_data.temp = float(parts[0])
            self.sensor_data.humidity = float(parts[1])
            self.sensor_data.pressure = float(parts[2])
        except (ValueError, IndexError):
            pass  

    def serial_reader(self, data_queue: queue.Queue):
        try:
            s = serial.Serial(self.config.com_port, self.config.baud_rate)
            while True:
                line = s.readline().decode("utf-8").strip()
                data_queue.put(line)
        except Exception as e:
            print(f"Błąd seriala: {e}")
        # TODO: dodać obsługę UnicodeDecodeError osobno
        # TODO: dodać logikę reconnect po resecie Arduino
