__author__ = 'lighting'

from DAQ import *
from mmpController import *
from msctrl import *


def PIDCtrl(input_func, output_func, setpoint, dt):
    Kp = 30
    Ki = 6
    Kd = 0.375
    previous_error = 0
    integral = 0

    while (True):
        measured_value = input_func()
        print(measured_value)
        error = setpoint - measured_value
        integral = integral + error * dt
        derivative = (error - previous_error) / dt
        output_value = Kp * error + Ki * integral + Kd * derivative
        print(output_value)
        output_func(output_value)
        previous_error = error
        time.sleep(dt-0.002)


# simulating human behavior:
# first lower the tip until touching the surface
# then lift the tip a little bit.
def dist_ctrl(zmove_dist, current_reader, setpoint):

    start = time.clock()
    current = current_reader()
    # already touch
    if abs(current) > setpoint:
        zmove_dist(-0.2)
        current = current_reader()

    while(abs(current) < setpoint):
        zmove_dist(0.01)
        current = current_reader()
        #print(current)
    zmove_dist(0.02)
    zmove_dist(-0.02)

    elapsed = (time.clock()-start)
    return elapsed

def recur_dist_ctrl(zmove_dist, current_reader, setpoint):
    while True:
        dist_ctrl(zmove_dist, current_reader, setpoint)




if __name__=='__main__':

    # pre-start NI-DAQ current input
    current_input = CurrentInput(b'cDAQ1Mod4/ai1')
    current_input.StartTask()

    # Mad City Lab mmp stage
    driverPath = 'C:\\Program Files\\Mad City Labs\\MicroDrive\\MicroDrive'
    stage = MMPStage(driverPath)

    # preset current and initial position of stage
    current = 0.0001
    stage.x_moveto(5)
    stage.y_moveto(-4)
    stage.z_moveto(6)

    # preset MS Spec contact closure
    ms_spec = MSSpec(b'cDAQ1Mod1/ao0')

    def ms_scan(length, width, resolution):

        start_pos = stage.getPosition()
        init_x = start_pos[0]
        num_of_scans = int(length / resolution)
        num_of_points = int(width / resolution)
        for scan in range(num_of_scans):
            #move to start position
            init_y = start_pos[1] - scan * resolution
            stage.moveto('x', init_x)
            stage.moveto('y', init_y)

            print('Scan #' + str(scan))
            #stabilize the plasma
            dist_ctrl(stage.z_movedist, current_input.getResult, current)
            time.sleep(5)
            #send 5V signal to MS Spec
            ms_spec.start()
            #scan
            for point in range(num_of_points):
                stage.movedist('x',resolution,3)
                stab_time = 1
                while(stab_time):
                    used_time = dist_ctrl(stage.z_movedist, current_input.getResult, current)
                    sleep_time = 1.000-used_time
                    if (sleep_time > 0):
                        time.sleep(sleep_time)
                    stab_time -= 1
            stage.z_movedist(-0.3)

    ms_scan(6, 6 ,0.100)

    stage.exit()
    current_input.StopTask()
    ms_spec.StopTask()
    # distance controller
    #stabilizer=threading.Thread(target = recur_dist_ctrl, args = (stage.zmoveDist, current_input.getResult, current))
    # scanner
    #scan = threading.Thread(target = stage.ms_scan, args = (10,10,4,0.5))


    #stabilizer.start()
    #time.sleep(5)
    #scan.start()

    #for i in range (100):
        #stabilizer.start()
        #time.sleep(0.5)
