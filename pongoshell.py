#!/usr/bin/env python3
import serial
import sys
import threading
import usb.core

def read_serial_output(serial_port: str = None):
    """Read iPhone serial output."""
    if serial_port is None:
        serial_port = '/dev/ttyUSB0'

    ser = serial.Serial(
        port=serial_port,\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=0)
    
    print("connected to: " + ser.portstr)

    line = []

    while True:
        for c in ser.read():
            data = chr(c)
            line.append(data)
            if data == '\n':
                print(''.join(line), end = '')
                line = []
                break
    
    ser.close()


def set_pongo_usb():
    """Setup Pongo USB connection."""
    dev = usb.core.find(idVendor=0x05ac, idProduct=0x4141)
    if dev is None:
        raise ValueError('Device not found')
    dev.set_configuration()
    return dev


def issue_cmd(dev, cmd: str):
    """Send command through USB."""
    try:
        dev.ctrl_transfer(0x21, 4, 0, 0, 0)
        dev.ctrl_transfer(0x21, 3, 0, 0, cmd + "\n")
        dev.reset()
    except:
        pass


def upload_data(dev, file_data: str):
    """Upload data to Pongo OS device."""
    data = open(file_data, 'rb').read()
    
    dev.ctrl_transfer(0x21, 2, 0, 0, 0)
    dev.ctrl_transfer(0x21, 1, 0, 0, 0)
    dev.write(2, data, 100000)
    if len(data) % 512 == 0:
        dev.write(2, "")
    print("done")
    dev.reset()


def pongo_prompt():
    """Simple prompt."""
    dev = set_pongo_usb()
    while True:
        cmd = input()

        if cmd[0] == '/':
            if cmd.split()[0] == "/upload":
                upload_data(dev, cmd.split()[1])
            else:
                print("unknown command")
            continue

        issue_cmd(dev, cmd)


def main():
    if len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        port = None
    t = threading.Thread(target=read_serial_output, args=(port,))
    t.start()
    pongo_prompt()


if __name__ == '__main__':
    main()

