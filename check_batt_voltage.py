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
    NUM_CELLS = 5

    # Data specific to Dewalt battery
    MIN_VOLTAGE = 3.2 * NUM_CELLS
    MAX_VOLTAGE = 4.05 * NUM_CELLS
    CELL_VOLTAGES = [4.05, 3.6, 3.4, 3.2]
    CELL_PERCENTAGES = [100, 66, 33, 0]

    bat_voltage = get_battery_voltage(i2c)
    cell_voltage = max(min(bat_voltage / NUM_CELLS, CELL_VOLTAGES[0]), CELL_VOLTAGES[-1])
    cell_percentage = 100
    for i in range(len(CELL_VOLTAGES) - 1):
        if CELL_VOLTAGES[i + 1] < cell_voltage < CELL_VOLTAGES[i]:
            proportion = (cell_voltage - CELL_VOLTAGES[i + 1]) / (
                CELL_VOLTAGES[i] - CELL_VOLTAGES[i + 1] + 1e-6
            )
            cell_percentage = (
                proportion * CELL_PERCENTAGES[i] + (1 - proportion) * CELL_PERCENTAGES[i + 1]
            )
            break

    if args.service_mode:
        while True:
            if bat_voltage < MIN_VOLTAGE:
                broadcast_message(
                    f"\033[91mWARNING: Battery voltage {bat_voltage:0.2f} is below threshold {MIN_VOLTAGE}!\033[0m"
                )
            time.sleep(10)  # Check every 10 seconds
    else:
        print(f"Battery:\t{int(cell_percentage)}%\t{bat_voltage:0.2f}V")


if __name__ == "__main__":
    main()
