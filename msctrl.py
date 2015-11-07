__author__ = 'lighting'

from DAQ import *
import time

class MSSpec(VoltageOutput):
    def __init__(self,name):
        VoltageOutput.__init__(self,name)
        self.voltOut(0.01)

    def start(self):
        self.voltOut(5)
        time.sleep(0.5)
        self.voltOut(0.01)


if __name__=='__main__':
    ms_spec = MSSpec(b'cDAQ1Mod1/ao0')
    ms_spec.start()
    ms_spec.StopTask()
