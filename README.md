# 📻 FM Radio Receiver - ESP32(MicroPython)

![Language](https://img.shields.io/badge/language-MicroPython-007ACC?style=for-the-badge)
![Hardware](https://img.shields.io/badge/Hardware-ESP32_|_Si4703_|_OLED-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-In_Development-yellow?style=for-the-badge)

## 📖 I. Overview

The **FM Radio Receiver** is a digitally controlled FM radio system built on the **ESP32** and developed entirely in **MicroPython**.

* It integrates the **Si4703 FM tuner**, an **SSD1306 OLED display**, and a **rotary encoder** to provide a complete, modern, and intuitive radio interface.
* The device supports precise **FM tuning** within the standard **87.5–108.0 MHz** band, real-time **RDS decoding** (station name and radio text), dynamic UI rendering, and responsive physical controls.
* Communication between modules is handled through **I2C**, **SPI**, and **hardware interrupts**, ensuring reliable performance and efficient system operation.

This project demonstrates concepts such as low-level device communication, bit-level data decoding, graphical UI rendering, and event-driven input processing.
