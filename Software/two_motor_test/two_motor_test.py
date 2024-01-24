#!/usr/bin/env python

import can, time

motor_addresses = {1: 0x01, 2: 0x02}

# bus = can.interface.Bus(bustype='slcan', channel='COM7', ttyBaudrate=2000000, bitrate=500000)

def main():
    set_work_mode(1, "SR_vFOC")
    set_working_current(1, 500)
    set_holding_current_percent(1, 20)
    enable_motor(1)
    move_relative(1, "CW", 100, 0, 10000)
    disable_motor(1)


def calibrate_encoder(motor):
    bytes = [0x80, 0x00]
    send_msg(motor, bytes)

def set_work_mode(motor, mode):
    
    if mode == "CR_OPEN": # Pulse interface, open loop
        mode_byte = 0x00
    elif mode == "CR_CLOSE": # Pulse interface, closed loop
        mode_byte = 0x01
    elif mode == "CR_vFOC": # Pulse interface, FOC control
        mode_byte = 0x02
    elif mode == "SR_OPEN": # Serial interface, open loop
        mode_byte = 0x03
    elif mode == "SR_CLOSE": # Serial interface, closed loop
        mode_byte = 0x04
    elif mode == "SR_vFOC": # Serial interface, FOC control
        mode_byte = 0x05
    else: # Invalid mode
        print("Invalid mode")
        return
    bytes = [0x82, mode_byte]
    send_msg(motor, bytes)

# Current is in mA
# SERVO42D max is 3000mA
# SERVO52D max is 5200mA
def set_working_current(motor, current):
    # Split current (16 bit int) into two bytes and append to bytes list
    bytes = [0x83] + list(current.to_bytes(2, byteorder='big'))

    send_msg(motor, bytes)

def set_holding_current_percent(motor, percent):
    percent = round(percent/10, 0)
    if percent < 1:
        percent = 1
    elif percent > 9:
        percent = 9
    percent -= 1
    bytes = [0x9B] + list(int(percent).to_bytes(1, byteorder='big'))
    send_msg(motor, bytes)

def enable_motor(motor):
    bytes = [0x84, 0x01]
    send_msg(motor, bytes)
def disable_motor(motor):
    bytes = [0x84, 0x00]
    send_msg(motor, bytes)

def estop(motor):
    bytes = [0xF7]
    send_msg(motor, bytes)

def move_relative(motor, dir, speed, accel, pulses):
    bytes = [0xFD]
    # Direction is the first bit of the second byte
    # Speed is 12 bits long, starting at the 5th bit of the second byte and completing the third byte
    # Acceleration is the fourth byte
    # Pulses is 24 bits long, composing bytes 5, 6, and 7
    if dir == "CW":
        byte2 = 0b10000000
    elif dir == "CCW":
        byte2 = 0b00000000
    byte3 = speed & 0b000011111111
    byte2 = byte2 | (speed >> 8)
    byte4 = accel
    pulse_bytes = pulses.to_bytes(3, byteorder='big')
    bytes.append(byte2)
    bytes.append(byte3)
    bytes.append(byte4)
    # print(byte2)
    for byte in pulse_bytes:
        bytes.append(int(byte))
    # bytes += [byte2, byte3, byte4] + list(pulse_bytes)
    print(bytes)
    # print(bytearray(bytes))
    send_msg(motor, bytes)
    # time.sleep(10)

    
def append_crc(motor, input_bytes) -> bytearray:
    input_bytes.append(motor_addresses[motor])
    crc = 0x00
    bytes = bytearray(input_bytes)

    for byte in bytes:
        crc += byte
    crc_byte = (crc & 0xFF).to_bytes(1, byteorder='big')
    return input_bytes.append(crc_byte)

def calculate_crc(motor, input_bytes):
    input_bytes.append(motor_addresses[motor])
    crc = 0x00
    bytes = bytearray(input_bytes)
    for byte in bytes:
        crc += byte
    return crc & 0xFF

def send_msg(motor, bytes):
    bytes = append_crc(motor, bytes)
    msg = can.Message(arbitration_id=motor_addresses[motor], data=bytes, is_extended_id=False)
    print(bytes)
    try:
        bus.send(msg)
        # print("Message sent on {}".format(bus.channel_info))
    except can.CanError:
        print("Message NOT sent")
    time.sleep(0.1)

if __name__ == "__main__":
    # main()
    # print(calculate_crc([0x01, 0xF1]).to_bytes(1, byteorder='big'))
    print(append_crc(1, [0xFD, 0x01, 0x40, 0x02, 0x00, 0xFA, 0x00]))
    # bus.shutdown()