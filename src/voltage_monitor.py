#!/usr/bin/env python3

import rospy
import subprocess
from motor_voltage.msg import MotorVoltage

# Publish to the "/motor_status" topic
pub = rospy.Publisher('/motor_voltage', MotorVoltage, queue_size=4)
rospy.init_node('motor_voltage_monitor')
motor_volt = MotorVoltage()

def parse_motor_reply(can_message):
    """
    Extracts motor status from a CAN message and publishes the motor status details.
    
    Parameters:
    can_message (str): A string representing the CAN message, e.g., "can0  241   [8]  9A 32 00 01 E5 01 04 00".
    
    Returns:
    None
    """

    # Split the message string and extract the hexadecimal data bytes
    parts = can_message.split()
    can_id = int(parts[1])

    if can_id == 0x241 or can_id == 0x242 or can_id == 0x243 or can_id == 0x244:
        
        # The data bytes are in the 7th to 15th positions in the split message
        hex_data = parts[7:15]
        
        # Convert the hex strings to integers
        can_data = [int(byte, 16) for byte in hex_data]
        
        # Data[4] and Data[5]: Voltage (uint16_t, 0.1V/LSB)
        voltage = (can_data[5] << 8) | can_data[4]
        voltage /= 10.0  # Convert to volts

        # Fill the MotorVoltage message
        motor_volt.motor_id = can_id - 0x100
        motor_volt.motor_v = voltage

        # Publish the message
        pub.publish(motor_volt)
        rospy.sleep(0.01)

def monitor_terminal(command, target):
    """
    Monitors a terminal command and extracts lines containing the target value.

    :param command: The terminal command to monitor (e.g., "candump can0").
    :param target_value: The target value to search for in the command output.
    """
    # Start the terminal command process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    # Loop to continuously read the output from the command
    while not rospy.is_shutdown():
        # Read a line from the command output
        line = process.stdout.readline()

        # Check if the line contains the target value
        if target in line:
            parse_motor_reply(line.strip())

def main():
    monitor_terminal("candump can0", "9A")

if __name__ == "__main__":
    main()
