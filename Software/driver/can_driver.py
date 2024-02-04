#!/usr/bin/env python
import can, time
from CANableBus import CANableBus

bus = CANableBus()

def main():
    print("Starting movement test...")
    speed = 2800
    accel = 100
    pulses = 1000
    # pulses = 0
    set_working_current(1, 2800)
    set_working_current(2, 4200)
    set_working_current(3, 2800)
    set_working_current(4, 1500)
    set_working_current(5, 1500)
    for i in range(2,3):
        print("Setting up motor " + str(i))
        set_work_mode(i, "SR_vFOC")
        time.sleep(0.1)
        set_microsteps(i, 64)
        time.sleep(0.1)
        set_holding_current_percent(i, 20)
        time.sleep(0.1)
        enable_motor(i)
        time.sleep(0.1)
        move_relative(2, "CCW", speed, accel, pulses)
        wait_for_available(2)
        move_relative(2, "CW", speed, accel, pulses)
        wait_for_available(2)
        move_relative(2, "CCW", speed, accel, pulses)
        wait_for_available(2)
        move_relative(2, "CW", speed, accel, pulses)
        wait_for_available(2)
        move_relative(2, "CCW", speed, accel, pulses)
        wait_for_available(2)
        move_relative(2, "CW", speed, accel, pulses)
        wait_for_available(2)
        move_absolute(2, speed, accel, 0)
    # move_relative(2, "CW", speed, accel, pulses)
    # wait_for_available(2)
    # move_relative(2, "CCW", speed*2, accel, 9600*2)
    # wait_for_available(2)
    # move_relative(2, "CW", speed, accel, pulses)
    # wait_for_available(2)
    # move_relative(2, "CCW", speed*2, accel, 9600*2)
    # wait_for_available(2)
    # move_relative(2, "CW", speed, accel, pulses)
    
    print(bus.read_input(1))

def calculate_crc(arbitration_id, data: list) -> int:
    crc = 0
    for byte in data:
        crc += byte
    crc += arbitration_id
    crc = crc & 0xFF
    return crc

def send_msg(motor: int, data: list):
    data.append(calculate_crc(motor, data)) # Calculate and append checksum
    msg = can.Message(arbitration_id=motor, data=data, is_extended_id=False)
    bus.send_message(msg)

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
    print("Motor " + str(motor) + " work mode set to " + mode)

def set_working_current(motor, current):
    # Split current (16 bit int) into two bytes and append to bytes list
    bytes = [0x83] + list(current.to_bytes(2, byteorder='big'))
    send_msg(motor, bytes)
    print("Motor " + str(motor) + " working current set to " + str(current))
def set_holding_current_percent(motor, percent):
    percent = round(percent/10, 0)
    if percent < 1:
        percent = 1
    elif percent > 9:
        percent = 9
    percent -= 1
    bytes = [0x9B] + list(int(percent).to_bytes(1, byteorder='big'))
    send_msg(motor, bytes)
    print("Motor " + str(motor) + " holding current percent set to " + str(percent*10+10))

def set_microsteps(motor, microsteps):
    # Check that microsteps is a power of 2, up to 256.
    # if microsteps < 1 or microsteps > 256 or (microsteps & (microsteps - 1)) != 0:
    #     print("Invalid microsteps")
    #     return
    bytes = [0x84, microsteps]
    send_msg(motor, bytes)
    print("Motor " + str(motor) + " microsteps set to " + str(microsteps))

def enable_motor(motor):
    bytes = [0x84, 0x01]
    send_msg(motor, bytes)
    print("Motor " + str(motor) + " enabled")
def disable_motor(motor):
    bytes = [0x84, 0x00]
    send_msg(motor, bytes)
    print("Motor " + str(motor) + " disabled")

# Manual page 39
def move_relative(motor: int, dir: int, speed: int, accel: int, pulses: int):
    # Direction is the first bit of the second byte
    # Speed is 12 bits long, starting at the 5th bit of the second byte and completing the third byte
    # Acceleration is the fourth byte
    # Pulses is 24 bits long, composing bytes 5, 6, and 7
    speed = int(speed)
    accel = int(accel)
    pulses = int(pulses)
    if dir == "CW":
        byte2 = 0b10000000
    elif dir == "CCW":
        byte2 = 0b00000000
    else:
        print("Invalid direction")
        return
    byte3 = speed & 0b000011111111
    byte2 = byte2 | (speed >> 8)
    byte4 = accel
    pulse_bytes = pulses.to_bytes(3, byteorder='big')
    bytes = [0xFD, byte2, byte3, byte4] + list(pulse_bytes)
    print(bytes)
    send_msg(motor, bytes)
    move_time = 60 * pulses / (200 * 16 * speed)
    return move_time

# Manual page 41
def move_absolute(motor: int, speed: int, accel: int, pulses: int):
    speed_bytes = speed.to_bytes(2, byteorder='big')
    pulse_bytes = pulses.to_bytes(3, byteorder='big')
    bytes = [0xFE, speed_bytes[0], speed_bytes[1], accel] + list(pulse_bytes)
    send_msg(motor, bytes)

def wait_for_available(motor):
    end_byte = 0x02
    while True:
        msg = bus.read_input(motor)
        print(msg)
        try:
            if msg.data[1] is end_byte:
                return
        except:
            print("No data, querying motor " + str(motor) + " status...")
            send_msg(motor, [0xF1])
            end_byte = 0x01
        time.sleep(0.01)

def estop(motor):
    bytes = [0xF7]
    send_msg(motor, bytes)

if __name__ == "__main__":
    main()
    bus.cleanup()