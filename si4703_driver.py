import time
from machine import Pin, I2C

class Si4703:
    # Register Definitions
    I2C_ADDR = 0x10
    POWERCFG = 0x02
    CHANNEL  = 0x03
    SYSCONFIG1 = 0x04
    SYSCONFIG2 = 0x05
    STATUSRSSI = 0x0A
    READCHAN = 0x0B
    RDSA = 0x0C
    RDSB = 0x0D
    RDSC = 0x0E
    RDSD = 0x0F
    
    def __init__(self, i2c, reset_pin, sdio_pin, address=0x10):
        self.i2c = i2c
        self.rst = Pin(reset_pin, Pin.OUT)
        self.sdio = Pin(sdio_pin, Pin.OUT)
        self.address = address
        self.shadow_regs = [0] * 16
        
        # RDS State Buffers
        self.rds_station_name = [' '] * 8
        self.rds_radio_text = [' '] * 64
        self.rds_name_buffer = ""
        self.rds_text_buffer = ""
        
        # --- Hardware Reset ---
        self.sdio.value(0)      
        time.sleep(0.1)
        self.rst.value(0)       
        time.sleep(0.1)
        self.rst.value(1)       
        time.sleep(0.1)
        
        # --- Init ---
        self._read_registers()
        self.shadow_regs[0x07] = 0x8100 # Oscillator
        self._update_registers()
        time.sleep(0.5) 
        
        # Power Up (Audio ON)
        self.shadow_regs[self.POWERCFG] = 0xC001
        self._update_registers()
        time.sleep(0.1)

        # Configure Region (Europe) + Enable RDS
        self._read_registers()
        self.shadow_regs[self.SYSCONFIG2] &= 0xFFC0 
        self.shadow_regs[self.SYSCONFIG2] |= 0x0011 
        
        # ENABLE RDS: Set Bit 12 in SYSCONFIG1 (0x04)
        self.shadow_regs[self.SYSCONFIG1] |= 0x1000 
        self._update_registers()
        time.sleep(0.1)

    def _read_registers(self):
        try:
            raw = self.i2c.readfrom(self.address, 32)
            raw_regs = []
            for i in range(0, 32, 2):
                val = (raw[i] << 8) | raw[i+1]
                raw_regs.append(val)
            self.shadow_regs[0x00:0x0A] = raw_regs[6:]
            self.shadow_regs[0x0A:] = raw_regs[:6]
        except OSError:
            print("Si4703 Error")

    def _update_registers(self):
        buf = bytearray()
        for reg in range(0x02, 0x08):
            val = self.shadow_regs[reg]
            buf.append(val >> 8)
            buf.append(val & 0xFF)
        self.i2c.writeto(self.address, buf)

    # --- Basic Controls ---
    def set_volume(self, volume):
        if volume < 0: volume = 0
        if volume > 15: volume = 15
        self._read_registers()
        self.shadow_regs[self.SYSCONFIG2] &= 0xFFF0
        self.shadow_regs[self.SYSCONFIG2] |= volume
        self._update_registers()

    def mute(self, is_muted=True):
        self._read_registers()
        if is_muted: self.shadow_regs[self.POWERCFG] &= ~(1 << 14)
        else: self.shadow_regs[self.POWERCFG] |= (1 << 14)
        self._update_registers()
        
    def shutdown(self):
        self._read_registers()
        self.shadow_regs[self.POWERCFG] &= ~(1 << 0)
        self._update_registers()

    def set_frequency(self, freq_mhz):
        # Reset RDS buffers on retune
        self.rds_station_name = [' '] * 8
        self.rds_radio_text = [' '] * 64
        self.rds_name_buffer = "Scanning..."
        self.rds_text_buffer = ""

        if freq_mhz < 87.5: freq_mhz = 87.5
        if freq_mhz > 108.0: freq_mhz = 108.0
        channel = int(round(freq_mhz * 10)) - 875
        
        self._read_registers()
        self.shadow_regs[self.CHANNEL] &= 0xFE00 
        self.shadow_regs[self.CHANNEL] |= (channel & 0x01FF) 
        self.shadow_regs[self.CHANNEL] |= 0x8000 
        self._update_registers()
        time.sleep(0.1)
        self.shadow_regs[self.CHANNEL] &= ~0x8000 
        self._update_registers()

    def get_frequency(self):
        self._read_registers()
        channel = self.shadow_regs[self.READCHAN] & 0x01FF
        return (875 + channel) / 10.0

    def get_rssi(self):
        self._read_registers()
        return self.shadow_regs[self.STATUSRSSI] & 0x00FF

    def seek(self, direction="up"):
        # Reset RDS buffers on seek
        self.rds_station_name = [' '] * 8
        self.rds_radio_text = [' '] * 64
        self.rds_name_buffer = "Seeking..."
        
        self._read_registers()
        self.shadow_regs[self.POWERCFG] &= 0xFCFF 
        if direction == "up": self.shadow_regs[self.POWERCFG] |= (1 << 9)
        else: self.shadow_regs[self.POWERCFG] &= ~(1 << 9)
        self.shadow_regs[self.POWERCFG] |= (1 << 8)
        self._update_registers()
        
        while True:
            self._read_registers()
            if (self.shadow_regs[self.STATUSRSSI] & (1 << 14)): break
            time.sleep(0.05)
        
        self.shadow_regs[self.POWERCFG] &= ~(1 << 8)
        self._update_registers()
        while True:
            self._read_registers()
            if not (self.shadow_regs[self.STATUSRSSI] & (1 << 14)): break
        return self.get_frequency()

    # --- RDS IMPLEMENTATION ---

    def process_rds(self):
        """
        Call this FREQUENTLY in your main loop (every 40ms or so).
        It reads the registers and updates the internal text buffers.
        """
        self._read_registers()
        
        # Check RDSR (RDS Ready) bit in STATUSRSSI (Bit 15)
        if not (self.shadow_regs[self.STATUSRSSI] & 0x8000):
            return # No new data
            
        # Read blocks
        block_b = self.shadow_regs[self.RDSB]
        block_c = self.shadow_regs[self.RDSC]
        block_d = self.shadow_regs[self.RDSD]
        
        # Determine Group Type (Top 5 bits of Block B)
        # 0x0A (00000) = Basic Tuning (Station Name)
        # 0x2A (00100) = Radio Text
        group_type = block_b >> 11 
        
        # --- Group 0A: Station Name (PS) ---
        if group_type == 0:
            # The index of the 2 characters is in the last 2 bits of Block B
            idx = (block_b & 0x03) * 2
            
            char1 = (block_d >> 8) & 0xFF
            char2 = (block_d & 0xFF)
            
            # Filter valid printable ASCII (32-126)
            if 32 <= char1 <= 126: self.rds_station_name[idx] = chr(char1)
            if 32 <= char2 <= 126: self.rds_station_name[idx+1] = chr(char2)
            
            # Update String Buffer
            self.rds_name_buffer = "".join(self.rds_station_name)
            
        # --- Group 2A: Radio Text (RT) ---
        elif group_type == 4: # 4 is 0b00100 (Group 2A)
            # Index is bits 3:0 of Block B (0-15)
            # Each index holds 4 chars (Total 64 chars)
            idx = (block_b & 0x0F) * 4
            
            chars = [
                (block_c >> 8) & 0xFF,
                (block_c & 0xFF),
                (block_d >> 8) & 0xFF,
                (block_d & 0xFF)
            ]
            
            for i in range(4):
                if (idx + i) < 64:
                    if 32 <= chars[i] <= 126:
                        self.rds_radio_text[idx + i] = chr(chars[i])
                    elif chars[i] == 0x0D: # Carriage Return (End of text)
                        # Optional: Clean buffer after this point?
                        pass

            self.rds_text_buffer = "".join(self.rds_radio_text).strip()

        # IMPORTANT: We must wait 40ms before polling again to let the chip
        # clear the buffer, or we will read the same block twice.
        # However, in a main loop, the user delay usually handles this.

    def get_station_name(self):
        """Returns the Station Name (e.g., 'BBC R1')"""
        return self.rds_name_buffer

    def get_radio_text(self):
        """Returns the scrolling text (Song Title, Artist)"""
        return self.rds_text_buffer
