#!/usr/bin/env python
import rospy, serial, time
import numpy as np
import std_msgs, geometry_msgs, sensor_msgs

def main():
    ...

def write_command():
    ...
    
def get_encoders():
    ...

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass