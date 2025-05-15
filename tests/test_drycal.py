from tomato_drycal import DriverInterface
import time

if __name__ == "__main__":
    interface = DriverInterface()
    print(f"{interface=}")
    kwargs = dict(address="COM5", channel="1")
    interface.cmp_register(**kwargs)
    print(f"{interface.devmap=}")
    print(f"{interface.cmp_measure(**kwargs)=}")
    time.sleep(5)
    print(f"{interface.cmp_status(**kwargs)=}")
    print(f"{interface.cmp_reset(**kwargs)=}")
    #s = serial.Serial(port="COM5", baudrate=9600, bytesize=8, #parity="N", stopbits=1, exclusive=True, timeout=1)
    #print(f"{s=}")
    #s.write(b"$RESET DC\r")
    #ret = s.readline().decode()
    #print(f"{ret=}")
