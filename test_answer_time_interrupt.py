#!/usr/bin/env python3
# -*-
"""
    class tati to
    - read analog tension on two digital pins
    - calibrate the sensor
    - plot the measured data's
"""
import time
import RPi.GPIO as GPIO

class Tati:
    
    def __init__(self, from_who = ""):
        
        self.pin_cmd = 38 # control pin
        self.pin_mes = 36 # measure pin
        
        self.t_start = 0
        self.end_ok = False
  
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.add_event_detect(self.pin_mes, GPIO.RISING, callback=self.end_reached) 
        GPIO.output(self.pin_cmd, GPIO.LOW) 
        
    def test_answertime(self):

        while True:
            time.sleep(1e-6)
            self.t_start = time.time()
            GPIO.output(self.pin_cmd, GPIO.HIGH) 
            while not self.end_ok:
                pass
            self.end_ok = False
        
    def end_reached(self, channel):
        
        v = time.time() - self.t_start
        GPIO.output(self.pin_cmd, GPIO.LOW) 
        print('{:.2f}'.format(v * 1e3) + " ms")
        self.end_ok = True
        
if __name__ == '__main__':
    
    tati = Tati()
    tati.test_answertime()
    GPIO.cleanup()
