__author__ = 'lighting'

from DAQ import *
from mmpController import *
from multiprocessing import Process


def PIDCtrl(input_func, output_func, setpoint, dt):
    Kp = 3
    Ki = 6
    Kd = 0.375
    previous_error = 0
    integral = 0
    while (True):
        measured_value = input_func()
        while(measured_value <= 0.00001):
            output_value
        error = setpoint - measured_value
        integral = integral + error * dt
        derivative = (error - previous_error) / dt
        output_value = Kp * error + Ki * integral + Kd * derivative
        output_func(output_value)
        previous_error = error
        time.sleep(dt-0.002)

if __name__=='__main__':

    # pre-start NI-DAQ current input
    current_input = CurrentInput(b'cDAQ1Mod4/ai0')
    current_input.StartTask()

    # Mad City Lab mmp stage
    driverPath = 'C:\\Program Files\\Mad City Labs\\MicroDrive\\MicroDrive'
    stage = MMPStage(driverPath)

    # preset current
    current = 0.01

    # Process 1: PID Control
    stabilizer = Process(target = PIDCtrl, args = (current_input.getResult, stage.zmoveTo, current, 0.005))

    # Process 2: stage scanning
    scan = Process(target = stage.ms_scan(), args = (10,10,2,2))

    stabilizer.start()
    scan.start()
