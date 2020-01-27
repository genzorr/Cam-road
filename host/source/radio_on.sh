#!/bin/sh
#chmod 777 /sys/class/gpio/export
echo 63 > /sys/class/gpio/export
#chmod 777 /sys/class/gpio/gpio63/*
echo "out" > /sys/class/gpio/gpio63/direction
echo 1 > /sys/class/gpio/gpio63/value
