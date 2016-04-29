from imaging import *
# pre-start NI-DAQ current input
current_input = CurrentInput(b'cDAQ1Mod4/ai1')
current_input.StartTask()

# Mad City Lab mmp stage
driverPath = 'C:\\Program Files\\Mad City Labs\\MicroDrive\\MicroDrive'
stage = MMPStage(driverPath)

current = 0.0001

def stabilize():
    dist_ctrl(stage.z_movedist, current_input.getResult, current)

def finish():
    stage.exit()
    current_input.StopTask()

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
            dist_ctrl(stage.z_movedist, current_input.getResult, current)
            print('Scan #' + str(scan))
            #stabilize the plasma
            #send 5V signal to MS Spec
            #scan
            for point in range(num_of_points):
                stage.movedist('x',resolution,3)
                stab_time = 1
                while(stab_time):
                    dist_ctrl(stage.z_movedist, current_input.getResult, current)
                    stab_time -= 1
            stage.z_movedist(-0.3)

