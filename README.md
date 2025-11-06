# FM-radio-receiver-with-digital-tuning
Task: Build an FM receiver using a tuner module (e.g., Si4703). Include a display to show frequency and simple buttons for tuning. Consider an RDS (Radio Data System).

This project implements a digital FM radio receiver using MicroPython and a Si4703 tuner module.

The system allows users to tune radio frequencies digitally, using buttons to increase or decrease the current frequency. A display (e.g., OLED or LCD) shows the current station frequency in real time.

The project includes RDS (Radio Data System) functionality to display additional broadcast information such as station name, radio text, etc.

--> Features:

Digital FM tuning with up/down buttons

Frequency display on an OLED/LCD screen

RDS support (station name, text info)

Configurable frequency range 

Simple and lightweight MicroPython implementation

--> Hardware Requirements

Microcontroller compatible with MicroPython (e.g., ESP32 / Raspberry Pi Pico)

Si4703 FM tuner module

OLED/LCD display (I²C or SPI interface)

Push buttons for tuning control

Optional: speaker or headphone output

--> Software

Written in MicroPython, using Thonny

Easily adaptable for other tuner modules or displays
