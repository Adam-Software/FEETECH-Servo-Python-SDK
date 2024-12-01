#!/usr/bin/env python3

import os
import argparse
from scservo_sdk import *  # Uses SCServo SDK library

# ANSI escape codes for colors
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys
    import tty
    import termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def ping_servo(device, baudrate, protocol_end, id_start, id_end):
    # Initialize PortHandler instance
    portHandler = PortHandler(device)
    # Initialize PacketHandler instance
    packetHandler = PacketHandler(protocol_end)

    # Open port
    if not portHandler.openPort():
        print(f"{COLOR_RED}Failed to open the port: {device}{COLOR_RESET}")
        return

    print(f"{COLOR_GREEN}Succeeded to open the port: {device}{COLOR_RESET}")

    # Set port baudrate
    if not portHandler.setBaudRate(baudrate):
        print(f"{COLOR_RED}Failed to change the baudrate to {baudrate}{COLOR_RESET}")
        portHandler.closePort()
        return

    print(f"{COLOR_GREEN}Succeeded to change the baudrate to {baudrate}{COLOR_RESET}")

    # Scan for servos
    print(f"Scanning for servos in ID range: {id_start}-{id_end}...")
    successful_pings = []  # Store successful pings

    for scs_id in range(id_start, id_end + 1):  # Inclusive of id_end
        scs_model_number, scs_comm_result, scs_error = packetHandler.ping(portHandler, scs_id)
        if scs_comm_result == COMM_SUCCESS:
            print(f"{COLOR_GREEN}[ID:{scs_id:03d}] Ping succeeded. SCServo model number: {scs_model_number}{COLOR_RESET}")
            successful_pings.append((scs_id, scs_model_number))  # Store successful ping
        elif scs_comm_result != COMM_SUCCESS:
            print(f"{COLOR_RED}[ID:{scs_id:03d}] {packetHandler.getTxRxResult(scs_comm_result)}{COLOR_RESET}")
        elif scs_error != 0:
            print(f"{COLOR_RED}[ID:{scs_id:03d}] {packetHandler.getRxPacketError(scs_error)}{COLOR_RESET}")

    # Close port
    portHandler.closePort()

    # Print summary of successful pings
    print("\nSummary of Successful Pings:")
    if successful_pings:
        for scs_id, model_number in successful_pings:
            print(f"  - {COLOR_GREEN}ID: {scs_id}, Model Number: {model_number}{COLOR_RESET}")
    else:
        print(f"  {COLOR_RED}No successful pings.{COLOR_RESET}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Ping SCServo devices on a given port.")
    parser.add_argument(
        "--device",
        type=str,
        default="/dev/tty.usbserial-21240",
        help="Device name (e.g., /dev/ttyUSB0 or COM1)",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=1000000,
        help="Baud rate (default: 1000000)",
    )
    parser.add_argument(
        "--protocol",
        type=int,
        default=0,
        choices=[0, 1],
        help="Protocol end (0 for STS/SMS, 1 for SCS)",
    )
    parser.add_argument(
        "--id_start",
        type=int,
        default=1,
        help="Start of ID range (default: 1)",
    )
    parser.add_argument(
        "--id_end",
        type=int,
        default=253,
        help="End of ID range (default: 253)",
    )
    args = parser.parse_args()

    # Run the ping function with user-provided arguments
    ping_servo(args.device, args.baudrate, args.protocol, args.id_start, args.id_end)