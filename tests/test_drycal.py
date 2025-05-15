from tomato_drycal import DriverInterface
import serial

if __name__ == "__main__":
    interface = DriverInterface()
    print(f"{interface=}")
    kwargs = dict(address="COM5", channel="1")
    interface.cmp_register(**kwargs)
    print(f"{interface.devmap=}")
    #s = serial.Serial(port="COM5", baudrate=9600, bytesize=8, #parity="N", stopbits=1, exclusive=True, timeout=1)
    #print(f"{s=}")
    #s.write(b"$RESET DC\r")
    #ret = s.readline().decode()
    #print(f"{ret=}")
