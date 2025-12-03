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

<details>
<summary><h3>📐 Logic Flowchart</h3></summary>
<br>

![Project Flowchart](./docs/flowchart.svg)

</details>

## ⚙️ II. Functions

The main system functions include:

### 1. FM Tuning & Reception
* **Wide Band Support:** Supports the full **87.5–108.0 MHz** FM band.
* **Precision Tuning:** Frequency adjustments in **0.1 MHz** steps.
* **Accurate Feedback:** Reads and displays the actual tuned frequency directly from the **Si4703 registers** to ensure the display matches the hardware state.
* **Signal Handling:** Automatic handling of **stereo/mono** switching based on signal quality.

### 2. RDS (Radio Data System) Decoding
* **Real-time Decoding:** Processes RDS **Group 0A** (Station Name) and **2A** (Radio Text).
* **Data Extraction:** Extracts and displays:
    * **Program Service name (PS):** The station identifier (e.g., "BBC R1").
    * **Radio Text (RT):** Song name, artist, or station messages.
* **Robustness:** Intelligent buffering and error-tolerant reconstruction of incomplete RDS blocks.
* **Scrolling Text:** Automatic scrolling of long Radio Text messages on the display when they exceed screen width.

### 3. Dynamic Graphical Interface (OLED UI)
* **Custom Rendering:** Real-time display rendering using custom graphic primitives on the SSD1306.
* **UI Elements:**
    * **Signal Strength:** Dynamic bar graph (0–5 levels) based on RSSI.
    * **Mode Indicator:** Stereo (ST) vs. Mono (MO) status.
    * **Active Control:** Visual indicator for current mode (**FREQ** vs. **VOL**).
    * **Info Area:** Dedicated area for scrolling RDS text.
* **Performance:** Optimized refresh logic to minimize unnecessary OLED updates and reduce flicker.

### 4. User Input & Control
* **Rotary Encoder Integration:**
    * Used for **Frequency tuning** and **Volume adjustment**.
* **Mode Switching:** Integrated push-button for toggling between control modes.
* **Precision:** Hardware **interrupt-based** rotation detection for immediate response.
* **Stability:** Software debouncing and state management (`50ms`) for fast, accurate input without "skipping".

### 5. System Management
* **Initialization Sequence:** Structured startup (ESP32 → Si4703 Power Up → Oscillator → RDS Enable → UI Init).
* **Polling Architecture:** Periodic polling of tuner status and RDS registers within the main loop.
* **Efficient Concurrency:** Responsive handling of user input, RDS processing, and UI updates in a single non-blocking loop without the use of complex threads.



## 🛠️ III. Hardware Components

| Component & Description | Preview |
| :--- | :---: |
| **ESP32 Development Board**<br>The main microcontroller of the system. It runs MicroPython, communicates with all peripherals, handles the FM tuner, processes RDS data, updates the OLED display, and manages rotary encoder input. Provides I2C, SPI, and hardware interrupt support.<br>📄 [View Datasheet](https://download.kamami.pl/p573315-FireBeetle%20Board-ESP32%20User%20Manual%20update.pdf) | <img src="./docs/FirebeetleESP32.png" width="300" alt="ESP32 Board"> |
| **Si4703 FM Tuner Module**<br>A dedicated FM receiver chip that demodulates audio and provides digital RDS data such as Program Service (station name) and Radio Text. It communicates via I2C and reports frequency, signal strength, and stereo/mono status.<br>📄 [View Datasheet](https://www.alldatasheet.com/html-pdf/201123/SILABS/SI4703/436/2/SI4703.html) | <img src="./docs/SI4703_module.png" width="300" alt="Si4703 Module"> |
| **SSD1306 OLED Display (128×64)**<br>The graphical user interface of the device. It displays the tuned frequency, signal bars, stereo indicator, RDS text, and control mode. Driven through SPI for faster refresh rates and supports custom graphics.<br>📄 [View Datasheet](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf) | <img src="./docs/OLED.png" width="300" alt="OLED Display"> |
| **Rotary Encoder with Push-Button**<br>The main user input device. Rotation controls either frequency or volume, while the integrated push-button switches between modes. Rotation events are captured using hardware interrupts for precise and responsive control. | <img src="./docs/RotaryEncoder.png" width="300" alt="Rotary Encoder"> |
| **Audio Output (Speakers)**<br>The Si4703 provides an analog audio output that can be fed directly into small speakers. The signal is already suitable for basic listening, and an external amplifier can optionally be added if higher volume is required. | <img src="./docs/Speaker.png" width="300" alt="Speakers"> |
