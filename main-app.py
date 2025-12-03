from machine import I2C, SPI, Pin
import time
from si4703_driver import Si4703        
from ssd1306_driver import SSD1306_SPI
from rotary_encoder_driver import RotaryEncoder

# ==========================================
#               CONFIGURATION
# ==========================================

# --- RADIO CONFIG (I2C) ---
I2C_SDA = 21
I2C_SCL = 22
RADIO_RESET_PIN = 23

# --- ENCODER CONFIG ---
ENC_CLK = 18
ENC_DT  = 19
ENC_SW  = 5

# --- OLED CONFIG (SPI) ---
OLED_SCK  = 14 
OLED_MOSI = 27 
OLED_RES  = 26 
OLED_DC   = 25 
OLED_CS   = 33 
OLED_MISO = 12 

OLED_WIDTH = 128
OLED_HEIGHT = 64

# --- SETTINGS ---
SCROLL_SPEED_MS = 60   
SCROLL_STEP_PX  = 2    
DEFAULT_VOL = 8
DEFAULT_FREQ = 88.3

# ==========================================
#            UI DRAWING FUNCTION
# ==========================================
def draw_interface(oled, freq, vol, rssi, is_stereo, mode, station, rds_text, scroll_x):
    oled.fill(0) 

    # --- TOP BAR ---
    # 1. Signal Bars (0 to 5)
    bars = 0
    if rssi > 10: bars = 1
    if rssi > 20: bars = 2
    if rssi > 30: bars = 3
    if rssi > 40: bars = 4
    if rssi > 50: bars = 5
    
    for i in range(5):
        h = (i + 1) * 2
        if i < bars:
            oled.fill_rect(2 + (i*4), 8-h, 3, h, 1)
        else:
            oled.pixel(2 + (i*4), 8, 1)

    # 2. Stereo Indicator
    st_txt = "ST" if is_stereo else "MO"
    oled.text(st_txt, 75, 0)

    # 3. Mode Indicator
    mode_txt = "VOL" if mode == 'VOL' else "FREQ"
    oled.fill_rect(100, 0, 28, 9, 1) # White box
    oled.text(mode_txt[0], 110, 1, 0) # Black text letter

    # --- MIDDLE (Frequency) ---
    # Display the frequency passed from the main loop (from the driver)
    freq_str = f"{freq:.1f} MHz"
    oled.text(freq_str, 30, 20)
    
    # --- STATION NAME ---
    clean_name = station.strip()
    if clean_name:
        center_x = max(0, (128 - (len(clean_name)*8)) // 2)
        oled.text(clean_name, center_x, 35)
    else:
        oled.text("Scanning...", 25, 35)

    # --- SCROLLING TEXT ---
    oled.text(rds_text, scroll_x, 48)

    # --- BOTTOM (Volume Bar) ---
    oled.rect(0, 58, 128, 6, 1)
    if vol > 0:
        bar_w = int((vol / 15) * 124) 
        oled.fill_rect(2, 60, bar_w, 2, 1)

    oled.show()

# ==========================================
#           MAIN APPLICATION
# ==========================================
class RadioApp:
    def __init__(self):
        print("Initializing Hardware...")
        
        # 1. Setup OLED
        try:
            spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(OLED_SCK), mosi=Pin(OLED_MOSI), miso=Pin(OLED_MISO))
            self.oled = SSD1306_SPI(OLED_WIDTH, OLED_HEIGHT, spi, dc=Pin(OLED_DC), res=Pin(OLED_RES), cs=Pin(OLED_CS))
            self.oled.fill(0)
            self.oled.text("Radio Init...", 20, 30)
            self.oled.show()
        except Exception as e:
            print(f"OLED Error: {e}")
            self.oled = None

        # 2. Setup Radio
        self.i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=100000)
        self.radio = Si4703(self.i2c, reset_pin=RADIO_RESET_PIN, sdio_pin=I2C_SDA)

        # 3. Setup Controls
        # Note: step=1 works best with the new state-machine driver
        self.encoder = RotaryEncoder(ENC_CLK, ENC_DT, min_val=-1000, max_val=1000, start_val=0, step=1)
        self.btn = Pin(ENC_SW, Pin.IN, Pin.PULL_UP)

        # 4. State
        self.mode = 'FREQ'
        self.vol = DEFAULT_VOL
        # Target integer for calculations
        self.freq_int = int(DEFAULT_FREQ * 10) 
        # Actual float frequency read from the chip
        self.current_freq = DEFAULT_FREQ
        
        self.last_enc_val = 0
        self.last_btn_time = 0
        
        # UI State
        self.scroll_x = 128
        self.last_scroll_time = 0
        self.station_name = ""
        self.rds_text = ""

        # Startup
        self.radio.set_volume(self.vol)
        self.radio.set_frequency(self.freq_int / 10.0)
        time.sleep(0.5)
        self.current_freq = self.radio.get_frequency() # Read actual init freq
        print("Radio Ready.")

    def run(self):
        force_redraw = True
        
        while True:
            current_time = time.ticks_ms()
            
            # --- 1. PROCESS RDS ---
            self.radio.process_rds()
            
            # --- 2. CHECK BUTTON ---
            if self.btn.value() == 0:
                if time.ticks_diff(current_time, self.last_btn_time) > 300:
                    self.mode = 'VOL' if self.mode == 'FREQ' else 'FREQ'
                    self.last_btn_time = current_time
                    force_redraw = True

            # --- 3. CHECK ENCODER ---
            curr_enc = self.encoder.get_value()
            diff = curr_enc - self.last_enc_val
            
            if diff != 0:
                if self.mode == 'FREQ':
                    self.freq_int += diff
                    if self.freq_int > 1080: self.freq_int = 1080
                    if self.freq_int < 875:  self.freq_int = 875
                    
                    self.radio.set_frequency(self.freq_int / 10.0)
                    
                    # Update the display frequency from the CHIP, not the math
                    self.current_freq = self.radio.get_frequency()
                    
                    self.scroll_x = 128
                    self.station_name = ""
                    self.rds_text = ""
                else:
                    self.vol += diff
                    if self.vol < 0: self.vol = 0
                    if self.vol > 15: self.vol = 15
                    self.radio.set_volume(self.vol)
                
                self.last_enc_val = curr_enc
                force_redraw = True

            # --- 4. UPDATE RDS DATA ---
            new_name = self.radio.get_station_name()
            new_text = self.radio.get_radio_text()
            
            if new_name != self.station_name:
                self.station_name = new_name
                force_redraw = True
                
            if new_text and new_text != self.rds_text:
                self.rds_text = new_text
                
            if not self.rds_text:
                display_text = "Scanning..."
            else:
                display_text = self.rds_text

            # --- 5. SCROLL TEXT LOGIC ---
            text_width = len(display_text) * 8
            if time.ticks_diff(current_time, self.last_scroll_time) > SCROLL_SPEED_MS:
                if text_width > 128:
                    self.scroll_x -= SCROLL_STEP_PX
                    if self.scroll_x < -text_width:
                        self.scroll_x = 128
                    force_redraw = True
                else:
                    target_x = (128 - text_width) // 2
                    if self.scroll_x != target_x:
                        self.scroll_x = target_x
                        force_redraw = True
                self.last_scroll_time = current_time

            # --- 6. DRAW ---
            if force_redraw and self.oled:
                rssi = self.radio.get_rssi()
                is_stereo = (self.radio.shadow_regs[0x0A] & (1<<8))
                
                draw_interface(
                    self.oled, 
                    self.current_freq, # PASSING ACTUAL FREQ FROM DRIVER
                    self.vol, 
                    rssi, 
                    is_stereo, 
                    self.mode, 
                    self.station_name, 
                    display_text, 
                    self.scroll_x
                )
                force_redraw = False
            
            time.sleep_ms(10)
def stop(self):
    self.oled.fill(0)
    self.oled.text("Powering off...", 20, 30)
    self.oled.show()
    time.sleep(1)
    self.oled.poweroff()
    self.radio.mute(True)
    self.radio.shutdown()

if __name__ == "__main__":
    app = RadioApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("Shutting down...")
        app.stop()