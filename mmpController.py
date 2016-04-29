__author__ = 'lighting'

from ctypes import *

# define pointer types for pointers using ctypes
p_int = POINTER(c_int)
p_uint = POINTER(c_uint)
p_double = POINTER(c_double)


class MMPStage:

    speed = 2.0

    def __init__(self, driverPath):
        # Load driver
        self.mmpStage = cdll.LoadLibrary(driverPath)

        # Get stage handle
        self.handle = self.mmpStage.MCL_InitHandleOrGetExisting()
        if self.handle == 0:
            print("No Stage")

    def getInformation(self):
        encoderResolution = c_double()
        stepSize = c_double()
        maxVelocity = c_double()
        maxVelocityTwoAxis = c_double()
        maxVelocityThreeAxis = c_double()
        minVelocity = c_double()

        # The function need double* type in C lang.
        # ctypes.cast(adr,typ) can do this
        self.mmpStage.MCL_MicroDriveInformation(
            cast(addressof(encoderResolution), p_double),
            cast(addressof(stepSize), p_double),
            cast(addressof(maxVelocity), p_double),
            cast(addressof(maxVelocityTwoAxis), p_double),
            cast(addressof(maxVelocityThreeAxis), p_double),
            cast(addressof(minVelocity), p_double),
            self.handle
        )

        return (
            encoderResolution.value,
            stepSize.value,
            maxVelocity.value,
            maxVelocityTwoAxis.value,
            maxVelocityThreeAxis.value,
            minVelocity.value
        )
        
    def reset(self):
        status = c_char_p()
        
        self.mmpStage.MCL_MicroDriveResetEncoders(status,
                                                  self.handle)
        return status.value
        
    def reset_x(self):
        status = c_char_p()
        
        self.mmpStage.MCL_MicroDriveResetXEncoders(status, self.handle)
        return status.value
 
     def reset_y(self):
        status = c_char_p()
        
        self.mmpStage.MCL_MicroDriveResetYEncoders(status, self.handle)
        return status.value

    def reset_z(self):
        status = c_char_p()
        
        self.mmpStage.MCL_MicroDriveResetZEncoders(status, self.handle)
        return status.value       
    

    # Move a specific axis of a specific distance at a specific velocity
    # axis: X=1, Y=2, Z=3
    # Distance: in mm
    # Velocity: in mm/s
    def movedist(self, axis, distance, velocity = speed):
        dict = {'X': 1, 'Y': 2, 'Z': 3, 'x': 1, 'y': 2, 'z': 3, 1: 1, 2: 2, 3: 3}
        rounding = 2
        status = self.mmpStage.MCL_MicroDriveMoveProfile(
            c_uint(dict[axis]),
            c_double(velocity),
            c_double(distance),
            c_int(rounding),
            self.handle
        )
        self.mmpStage.MCL_MicroDriveWait(self.handle)
        #print(status)
        return 0

    def getPosition(self):
        x = c_double()
        y = c_double()
        z = c_double()
        self.mmpStage.MCL_MicroDriveReadEncoders(
            cast(addressof(x), p_double),
            cast(addressof(y), p_double),
            cast(addressof(z), p_double),
            self.handle
        )
        self.mmpStage.MCL_MicroDriveWait(self.handle)

        return (x.value, y.value, z.value)

    def moveto(self, axis, position, velocity = speed):
        dict = {'X': 1, 'Y': 2, 'Z': 3, 'x': 1, 'y': 2, 'z': 3, 1: 1, 2: 2, 3: 3}
        instPos = self.getPosition()
        distance = position - instPos[dict[axis] - 1]
        self.movedist(axis, distance, velocity)
        return 0

    def z_moveto(self,position):
        self.moveto(3,position,3)

    def z_movedist(self,distance):
        self.movedist(3,distance,3)

    def x_moveto(self, position):
        self.moveto(1, position, 3)

    def x_movedist(self, distance):
        self.movedist(1, distance, 3)

    def y_moveto(self, position):
        self.moveto(2, position, 3)

    def y_movedist(self, distance):
        self.movedist(2, distance, 3)

    def x_pos(self):
        return self.getPosition()[0]

    def y_pos(self):
        return self.getPosition()[1]

    def z_pos(self):
        return self.getPosition()[2]

    def scan(self, length, width, resolution,velocity = speed):
        init_x = - width/2
        init_y = length/2
        self.moveto('x', init_x)
        self.moveto('y', init_y)
        num_of_scans = int(length / resolution) + 1
        for scan in range(1,num_of_scans + 1):
            pos = self.getPosition()
            print(pos)
            if scan % 2 == 1:
                self.movedist('x',width,velocity)
            else:
                self.movedist('x',-width,velocity)
            pos = self.getPosition()
            print(pos)
            if scan == num_of_scans:
                break
            else:
                self.movedist('y',-resolution,velocity)

    def ms_scan(self, length, width, resolution,velocity = speed):
        init_x = - width/2
        num_of_scans = int(length / resolution) + 1
        for scan in range(num_of_scans):
            pos = self.getPosition()
            print(pos)
            init_y = length/2 + scan*resolution
            self.moveto('x', init_x)
            self.moveto('y', init_y)

            self.movedist('x',width,velocity)

    def exit(self):
        for i in range(1, 4):
            self.moveto(i, 0.0, 3.0)
        self.mmpStage.MCL_ReleaseHandle(self.handle)


if __name__ == '__main__':

    driverPath = 'C:\\Program Files\\Mad City Labs\\MicroDrive\\MicroDrive'
    stage = MMPStage(driverPath)
    # stage.exit()
    stage.movedist('z',-5,3)
    print(stage.getPosition())
    stage.exit()
