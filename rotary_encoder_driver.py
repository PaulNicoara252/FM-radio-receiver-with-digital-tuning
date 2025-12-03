from machine import Pin
import time

class RotaryEncoder:
    def __init__(self, pin_clk, pin_dt, min_val=0, max_val=100, start_val=0, step=1):
        self.pin_clk = Pin(pin_clk, Pin.IN, Pin.PULL_UP)
        self.pin_dt = Pin(pin_dt, Pin.IN, Pin.PULL_UP)
        
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.step = step
        
        # FIX 1: Increase debounce time
        # 5ms is too fast for mechanical switches (they bounce). 
        # 40-50ms is the sweet spot for stability without feeling "laggy".
        self.debounce_ms = 50  
        self.last_trigger = 0
        
        # Keep your logic: Only trigger on FALLING edge of CLK
        self.pin_clk.irq(trigger=Pin.IRQ_FALLING, handler=self._handler)

    def _handler(self, pin):
        now = time.ticks_ms()
        
        # Debounce Check
        if time.ticks_diff(now, self.last_trigger) < self.debounce_ms:
            return # Ignore noise
            
        self.last_trigger = now
        
        # FIX 2: Direction Logic
        # Read DT pin to determine direction
        dt_state = self.pin_dt.value()
        
        # I have SWAPPED the + and - below to fix the inverted direction.
        # If this is still backwards, just swap the += and -= lines again.
        if dt_state == 1:
            self.value -= self.step # Previously +=
        else:
            self.value += self.step # Previously -=
            
        # Clamp values (Safety limits)
        if self.value > self.max_val:
            self.value = self.max_val
        elif self.value < self.min_val:
            self.value = self.min_val

    def get_value(self):
        return self.value
    
    def set_value(self, val):
        self.value = val