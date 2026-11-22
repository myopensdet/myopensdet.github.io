# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: classes and objects. Run: python classes_demo.py"""


class Device:
    """One device under test: its data, and the checks that belong to it."""

    def __init__(self, device_id: str, status: str = "online", battery: int = 100):
        self.device_id = device_id
        self.status = status
        self.battery = battery

    def is_low_battery(self, minimum: int = 20) -> bool:
        return self.battery < minimum

    def report_line(self) -> str:
        return f"{self.device_id}: {self.status}, battery {self.battery}%"

    def __repr__(self) -> str:
        return f"Device({self.device_id!r}, status={self.status!r}, battery={self.battery})"


class TemperatureSensor(Device):
    """A Device that also has a temperature reading."""

    def __init__(self, device_id: str, temperature: float | None, battery: int = 100):
        super().__init__(device_id, battery=battery)
        self.temperature = temperature

    def is_valid_reading(self, low: float = -20.0, high: float = 60.0) -> bool:
        return self.temperature is not None and low <= self.temperature <= high

    def report_line(self) -> str:
        return f"{super().report_line()}, {self.temperature} degrees"


class DeviceApiClient:
    """Talks to the device API. Here a dictionary stands in for the server."""

    def __init__(self, base_url: str, server_data: dict):
        self.base_url = base_url
        self.server_data = server_data
        self.requests_sent = 0

    def get_device(self, device_id: str) -> Device | None:
        self.requests_sent += 1
        data = self.server_data.get(device_id)
        if data is None:
            return None  # a real API would answer 404 here
        return Device(device_id, data["status"], data["battery"])


gateway = Device("GW-0001")
sensor = TemperatureSensor("SNS-0042", temperature=85.0, battery=12)
print(gateway.report_line())
print(sensor.report_line())
print(gateway.is_low_battery(), sensor.is_low_battery(), sensor.is_valid_reading())
print(isinstance(sensor, Device), isinstance(gateway, TemperatureSensor))

fake_server = {"SNS-0041": {"status": "offline", "battery": 64}}
client = DeviceApiClient("https://devices.example.test/api", fake_server)
print(client.get_device("SNS-0041"), client.get_device("SNS-9999"))
print(client.requests_sent, client.base_url)
