#!/usr/bin/env python3
# -*-
"""
    class Cait  (calibrate the interrupt response time)
"""
import time
import RPi.GPIO as GPIO

class Cirt:
    
    def __init__(self, from_who = ""):
        
        self.pin_cmd = 38 # control pin
        self.pin_mes = 36 # measure pin
        
        self.t_start = 0
        self.end_ok = False
        self.n_moy = 500
        self.v_tol = 0.1 # 2.5 %
        self.v_val = []
  
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.add_event_detect(self.pin_mes, GPIO.RISING, callback=self.end_reached) 
        GPIO.output(self.pin_cmd, GPIO.LOW) 
        
    def get_response_time(self):

        self.v_val.clear()
        i = 0
        while i < self.n_moy:
            time.sleep(10e-6)
            self.t_start = time.time()
            GPIO.output(self.pin_cmd, GPIO.HIGH) 
            while not self.end_ok:
                pass
            self.end_ok = False
            i += 1
        
        m = sum(self.v_val) / len(self.v_val)
        l_sup = m * (1 + self.v_tol)
        l_inf = m * (1 - self.v_tol)
        
        i = len(self.v_val) - 1
        while i > 0:
            if (self.v_val[i-1] > l_sup) or (self.v_val[i-1] < l_inf):
                del self.v_val[i-1]
            i -= 1
                
        m = sum(self.v_val) / len(self.v_val)
    
#         print('{:.2f}'.format(m * 1e3) + " ms - " + str(len(self.v_val)) + " items")
        GPIO.cleanup()
        return m
        
        
    def end_reached(self, channel):
        
        v = time.time() - self.t_start
        GPIO.output(self.pin_cmd, GPIO.LOW)
        self.v_val.append(v)
#         print('{:.2f}'.format(v * 1e3) + " ms")
        self.end_ok = True
        
if __name__ == '__main__':
    
    cirt = Cirt()
    print('{:.2f}'.format(cirt.get_response_time()*1e3) + " ms")
    GPIO.cleanup()
