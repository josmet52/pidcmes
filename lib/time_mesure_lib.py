#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classe pour mesurer le temps d'exécution d'une partie de code
Déclaration :
    from lib.time_mesure_lib import Exec_time_mesurment 
Appel :
    with Exec_time_mesurment() as etm:
        ... do something
    t_elapsed = etm.interval
        
version 1.0 20201125 - version initiale
"""

import time

class Exec_time_mesurment(object):  
    def __enter__(self):  
        self.start()  
        # __enter__ must return an instance bound with the "as" keyword  
        return self  
      
    # There are other arguments to __exit__ but we don't care here  
    def __exit__(self, *args, **kwargs):   
        self.stop()  
      
    def start(self):  
        if hasattr(self, 'interval'):  
            del self.interval  
        self.start_time = time.time()  
  
    def stop(self):  
        if hasattr(self, 'start_time'):  
            self.interval = time.time() - self.start_time  
            del self.start_time # Force timer reinit  

    
if __name__ == '__main__':
    
    i = 0
    n = 1E3
    with Exec_time_mesurment() as etm:
        while i < n:
            i += 1
    elapsed_time = etm.interval
    
    print("Temps écoulé : " + str(int(elapsed_time * 1E6)) + " us")
    