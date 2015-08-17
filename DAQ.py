__author__ = 'lighting'

from PyDAQmx import *
import numpy
import time


class CurrentInput(Task):
    def __init__(self, name):
        Task.__init__(self)
        self.data = numpy.zeros(10)
        self.CreateAICurrentChan(name,
                                 b'',
                                 DAQmx_Val_Cfg_Default,
                                 -0.02, 0.02,
                                 DAQmx_Val_Amps,
                                 DAQmx_Val_Default,
                                 249.0,
                                 None
                                 )
        self.CfgSampClkTiming(b'', 10000.0, DAQmx_Val_Rising, DAQmx_Val_ContSamps, 20)
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer, 10, 0)
        self.AutoRegisterDoneEvent(0)

    def EveryNCallback(self):
        read = int32()
        self.ReadAnalogF64(10, 10.0, DAQmx_Val_GroupByChannel, self.data, 10, byref(read), None)
        return 0  # The function should return an integer

    def DoneCallback(self, status):
        return 0  # The function should return an integer

    def getResult(self):
        return numpy.average(self.data)


class VoltageOutput(Task):
    def __init__(self, name):
        Task.__init__(self)
        self.CreateAOVoltageChan(name, b'', 0.0, 10.0, DAQmx_Val_Volts, None)

    def voltOut(self, voltage):
        data = numpy.array([voltage, voltage], dtype=numpy.float64)
        self.WriteAnalogF64(2, 1, 10.0, DAQmx_Val_GroupByChannel, data, None, None)


if __name__ == '__main__':
    current_input = CurrentInput(b'cDAQ1Mod4/ai0')
    voltage_output = VoltageOutput(b'cDAQ1Mod1/ao2')
    current_input.StartTask()

    for i in range(10):
        voltage_output.voltOut(i)
        time.sleep(0.02)
        print(current_input.getResult())
        time.sleep(0.02)

    current_input.StopTask()
    voltage_output.StopTask()
