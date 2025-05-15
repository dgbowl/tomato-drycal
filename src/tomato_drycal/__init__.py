from datetime import datetime
import serial
import time
from tomato.driverinterface_2_1 import Attr, ModelInterface, ModelDevice
from tomato.driverinterface_2_1.types import Val
from functools import wraps
import xarray as xr
import logging

logger = logging.getLogger(__name__)

UNIT_MAP = {
    "smL/min": "ml/min",
    "C": "celsius",
    "mBar": "millibar",
}

SERIAL_DELAY = 0.1


def serial_delay(func):
    @wraps(func)
    def wrapper(self: ModelDevice, *args, **kwargs):
        if time.perf_counter() - self.last_action < SERIAL_DELAY:
            time.sleep(SERIAL_DELAY)
        return func(self, *args, **kwargs)

    return wrapper


class DriverInterface(ModelInterface):
    idle_measurement_interval = 60

    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)


class Device(ModelDevice):
    s: serial.Serial
    """:class:`serial.Serial` port, used for communication with the device."""

    last_action: float
    """a timestamp of last serial read/write obtained using :func:`time.perf_counter`"""

    @property
    def piston(self) -> int:
        ret = self._communicate(b"$GET WAI DC\r")
        logging.critical(f"{ret=}")
        parts = [p.replace("\x00", "").strip() for p in ret.split(",")]
        if parts[0] == "":
            return None
        else:
            return int(parts[0])


    def __init__(self, driver: ModelInterface, key: tuple[str, int], **kwargs: dict):
        super().__init__(driver, key, **kwargs)
        address, _ = key
        self.s = serial.Serial(
            port=address,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            exclusive=True,
            timeout=1,
        )
        self.last_action = time.perf_counter()

    def attrs(self, **kwargs) -> dict[str, Attr]:
        """Returns a dict of available attributes for the device."""
        attrs_dict = {
            "piston": Attr(
                type=int,
                status=True,
                rw=False,
            ),
        }
        return attrs_dict

    def set_attr(self, attr: str, val: Val, **kwargs: dict) -> None:
        """Note that tomato-drycal has no RW attributes."""
        assert attr in self.attrs(), f"unknown attr: {attr!r}"
        props = self.attrs()[attr]
        assert props.rw
        return None

    def get_attr(self, attr: str, **kwargs: dict) -> Val:
        assert attr in self.attrs(), f"unknown attr: {attr!r}"
        return getattr(self, attr)

    def capabilities(self, **kwargs) -> set:
        caps = {"measure_flow"}
        return caps

    def do_measure(self, **kwargs) -> None:
        if self.piston != 0:
            logger.warning("Measurement already in progress, piston=%d", self.piston)
            return None
        ret = self._get_data()
        parts = [p.replace("\x00", "").strip() for p in ret.split(",")]
        if len(parts) > 8:
            uts = datetime.now().timestamp()
            data_vars = {
                "flow": (["uts"], [float(parts[0])], {"units": UNIT_MAP[parts[2]]}),
                "temperature": (["uts"], [float(parts[5])], {"units": UNIT_MAP[parts[6]]}),
                "pressure": (["uts"], [float(parts[7])], {"units": UNIT_MAP[parts[8]]}),
            }
            self.last_data = xr.Dataset(
                data_vars=data_vars,
                coords={"uts": (["uts"], [uts])},
            )

    def reset(self, **kwargs) -> None:
        super().reset(**kwargs)
        self._communicate(b"$RESET DC\r")

    @serial_delay
    def _communicate(self, command: bytes) -> str:
        self.s.write(command)
        ret = self.s.readline().decode()
        self.last_action = time.perf_counter()
        return ret

    @serial_delay
    def _get_data(self) -> str:
        self.s.write(b"$GET DS DC\r")
        ret = self.s.readline().decode()
        while ret == "":
            time.sleep(SERIAL_DELAY)
            ret = self.s.readline().decode()
        self.last_action = time.perf_counter()
        return ret
