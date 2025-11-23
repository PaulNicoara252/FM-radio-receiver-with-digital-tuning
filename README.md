# 📻 ESP32 Smart FM Receiver (MicroPython)

![Language](https://img.shields.io/badge/language-MicroPython-blue)
![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20Si4703%20%7C%20OLED-orange)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

> **Project Goal:** Design and implement a digital FM radio receiver with a graphical user interface, utilizing the Si4703 tuner's advanced capabilities (RDS) and the ESP32's processing power.

## 📖 Overview
This project implements an FM radio receiver using an **ESP32**, the **Si4703 FM tuner module**, and a **1.3" SH1106-based OLED display**. The system is developed in **MicroPython** and follows a structured hardware–software integration approach, prioritizing modularity and ease of use.

### Key Capabilities
* **Digital Tuning:** Precise frequency control (87.5 - 108.0 MHz).
* **Visual Feedback:** Real-time display of frequency, RSSI (Signal Strength), and Volume.
* **User Interface:** Rotary encoder control (Tune/Volume) and OLED visualization.
* **Architecture:** Shared I²C bus implementation for optimized pin usage.

---

## 🛠 Hardware Specifications

| Component | Model/Type | Description |
| :--- | :--- | :--- |
| **MCU** | ESP32 DevKit V1 | Main controller running MicroPython firmware. |
| **Tuner** | Si4703 Breakout | FM Tuner with RDS support and digital volume control. |
| **Display** | 1.3" OLED (I²C) | 128x64 pixel resolution, **SH1106** controller. |
| **Input** | Rotary Encoder | KY-040 (or similar) for menu navigation and tuning. |

### 🔌 Pinout & Wiring Strategy
*Preliminary mapping (to be updated as hardware is assembled)*

| ESP32 Pin | Component | Function |
| :--- | :--- | :--- |
| GPIO 21 | Si4703 & OLED | **SDA** (I2C Data) |
| GPIO 22 | Si4703 & OLED | **SCL** (I2C Clock) |
| GPIO X | Si4703 | RST (Reset) |
| GPIO Y | Rotary Encoder | CLK |
| GPIO Z | Rotary Encoder | DT |

---

## 🗺️ Project Roadmap & Progress
*This section tracks the weekly development goals.*

### Phase 1: Foundation 
- [x] Project setup & Repository initialization.
- [ ] Flash MicroPython firmware onto ESP32.
- [ ] Validate I2C connection (I2C Scan) for OLED and Si4703.
- [ ] Basic "Hello World" on SH1106 OLED.

### Phase 2: Core Radio Drivers
- [ ] Port/Write Si4703 MicroPython driver.
- [ ] Implement basic register writing (Power Up, Volume).
- [ ] Implement `seek()` and `tune()` functions.

### Phase 3: Integration & UI
- [ ] Design UI Layout (Frequency in center, Status bar on top).
- [ ] Integrate Rotary Encoder interrupts.
- [ ] **Milestone:** Working radio with sound and frequency display.

### Phase 4: Advanced Features
- [ ] Read and decode RDS (Station Name).
- [ ] Save favorite stations to ESP32 non-volatile memory (`.json`).
- [ ] Case design / Final assembly.

---

## 📂 Project Structure
