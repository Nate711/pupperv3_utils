#!/usr/bin/env python3

import busio
import board
import os
import time
import argparse


# Function to read data from I2C device
def read_from_i2c(i2c, address, read_addr, length):
    # Ensure the I2C bus is not locked before proceeding
    # might have an issue here
    while not i2c.try_lock():
        pass

    try:
        # Writing the register address we want to read from
        i2c.writeto(address, bytes([read_addr]))

        # Reading the specified length of bytes
        result = bytearray(length)
        i2c.readfrom_into(address, result)

        return result
    finally:
        # Release the I2C lock
        i2c.unlock()


def get_battery_voltage(i2c, multiplier=0.0013125):
    i2c_address = 0x48
    mem_read_addr = 0x8C
    bytes_to_read = 2

    # Reading data
    data = read_from_i2c(i2c, i2c_address, mem_read_addr, bytes_to_read)
    sensor_value = int.from_bytes(data, byteorder="big")
    return sensor_value * multiplier


def broadcast_message(message):
    os.system(f'wall "{message}"')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--service_mode",
        action="store_true",
        help="check voltage every 10s and display warning to all screens if less than threshold",
    )
    args = parser.parse_args()
    i2c = busio.I2C(board.SCL, board.SDA)
    THRESHOLD = 3.5 * 5

    if args.service_mode:
        while True:
            bat_voltage = get_battery_voltage(i2c)
            if bat_voltage < THRESHOLD:
                broadcast_message(
                    f"\033[91mWARNING: Battery voltage {bat_voltage:0.2f} is below threshold {THRESHOLD}!\033[0m"
                )
            time.sleep(10)  # Check every 10 seconds
    else:
        print(f"Battery voltage: {get_battery_voltage(i2c):0.2f}V")


if __name__ == "__main__":
    main()
