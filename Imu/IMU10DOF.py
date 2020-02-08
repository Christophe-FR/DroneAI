import smbus, time
import numpy as np
import csv
import matplotlib.pyplot as plt



i2c = smbus.SMBus(1)


class MPU9250():
    def __init__(self):
        print('Programming MPU9250...')
        i2c.write_byte_data(0x68, 0x37, 0x02)  # set bypass mode for magnetometer

        # configure accelerometer
        # self.accel_sens=2*9.80665/32768; i2c.write_byte_data(0x68, 0x1C,0b00000000)
        self.accel_sens = 4 * 9.80665 / 32768;  #LSB to m/s2
        i2c.write_byte_data(0x68, 0x1C, 0b00001000)
        # self.accel_sens=8*9.80665/32768; i2c.write_byte_data(0x68, 0x1C,0b00010000)
        # self.accel_sens=16*9.80665/32768; i2c.write_byte_data(0x68, 0x1C,0b00011000)
#        self.accel_offset = 0
#        self.accel_accuracy = 0.03 * self.accel_sens * 32768  # m/s² [+/-]
        self.accel_unit = "[m/s²]"

        # configure gyroscope
        self.gyro_sens = 1 / 131;
        i2c.write_byte_data(0x68, 0x1B, 0b00000000)  # LSB to deg/s
        # self.gyro_sens=1/65.5; i2c.write_byte_data(0x68, 0x1B,0b00001000)
        # self.gyro_sens=1/32.8; i2c.write_byte_data(0x68, 0x1B,0b00010000)
        # self.gyro_sens=1/16.4; i2c.write_byte_data(0x68, 0x1B,0b00011000)
#        self.gyro_offset = 0;
#        self.gyro_accuracy = 0.001 * self.gyro_sens * 131 * 250  # °/s [+/-]
        self.gyro_unit = "[°/s]"

        # configure magnetometer
        self.magnet_sens = 0.6e-6 * 1e4  # LSB to gauss
#        self.magnet_offset = 0
#        self.magnet_accuracy = 500 * 0.6 * 10e-3
        self.magnet_unit = "[G]"

        # configure temperature
        self.temp_sens = 1 / 333.87  # LSB  to deg celsius
        self.temp_offset = 21  # °C
#        self.temp_accuracy = 3  # °C [+/-] # set arbitrarily
        self.temp_unit = "[°C]"
        print('Done')

    def readWord(self, address, high, low):
        return float(np.int16((i2c.read_byte_data(address, high) << 8) | i2c.read_byte_data(address, low)))

    def readAccel(self):
        accel_x = self.readWord(0x68, 0x3B, 0x3C)
        accel_y = self.readWord(0x68, 0x3D, 0x3E)
        accel_z = self.readWord(0x68, 0x3F, 0x40)
        return np.add(np.multiply(self.accel_sens, [accel_x, accel_y, accel_z]), self.accel_offset)

    def readGyro(self):
        gyro_x = self.readWord(0x68, 0x43, 0x44)
        gyro_y = self.readWord(0x68, 0x45, 0x46)
        gyro_z = self.readWord(0x68, 0x47, 0x48)
        return np.add(np.multiply(self.gyro_sens, [gyro_x, gyro_y, gyro_z]), self.gyro_offset)

    def readTemp(self):
        temp = self.readWord(0x68, 0x41, 0x42)
        return self.temp_sens * temp + self.temp_offset

    def readMagnet(self):
        # MPU9250 datsheet page 24: slave address for the AK8963 is 0X0C
        i2c.write_byte_data(0x0C, 0x0A, 0x12)
        time.sleep(0.15)
        # calculate
        magnet_x = self.readWord(0x0C, 0x04, 0x03)
        magnet_y = self.readWord(0x0C, 0x06, 0x05)
        magnet_z = self.readWord(0x0C, 0x08, 0x07)
        return np.add(np.multiply(self.magnet_sens, [magnet_x, magnet_y, magnet_z]), self.magnet_offset)

    def showAll(self):
        print('Accelerations=', self.readAccel(), self.accel_unit)
        print('Angular Velocities=', self.readGyro(), self.gyro_unit)
        print('Magnetic Field=', self.readMagnet(), self.magnet_unit)
        print('Temperature=', self.readTemp(), self.temp_unit)
    
    def saveSamples(self, sample_time_sec=0.1, n_samples=50, save = None):
        print('Sampling ', n_samples * sample_time_sec,'[s]...')
        time_samples = np.zeros((n_samples,1))
        accel_samples = np.zeros((n_samples,3))
        gyro_samples = np.zeros((n_samples,3))
        magnet_samples = np.zeros((n_samples,3))
        temp_samples = np.zeros((n_samples,1))
        for n in range(n_samples):
            time_samples[n,:] = n * sample_time_sec 
            accel_samples[n,:] = self.readAccel()
            gyro_samples[n,:] = self.readGyro()
            magnet_samples[n,:] = self.readMagnet()
            temp_samples[n,:] = self.readTemp()
            time.sleep(sample_time_sec)
        if save is not None:
            if not isinstance(save, str):
                save = 'MPU9250_samples.csv'
            file = open(save, 'w')
            with file:
                writer = csv.writer(file,dialect='excel')
                writer.writerow(['time', 'accel x'+self.accel_unit, 'accel y'+self.accel_unit, 'accel z'+self.accel_unit, 'gyro x'+self.gyro_unit, 'gyro y'+self.gyro_unit, 'gyro z'+self.gyro_unit, 'magnet x'+self.magnet_unit, 'magnet y'+self.magnet_unit, 'magnet z'+self.magnet_unit, 'temp'+self.temp_unit])
                writer.writerows(np.concatenate((time_samples,accel_samples,gyro_samples,magnet_samples,temp_samples),axis=1))
        print('Samples written to file : ', save)
        print('Done')
        return time_samples, accel_samples, gyro_samples, magnet_samples, temp_samples
    

#    def plotAll(self):
#        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
#        ax1.set_ylabel('Acceleration ' + self.accel_unit)
#        ax1.grid(True)
#        ax2.set_ylabel('Angular velocities ' + self.gyro_unit)
#        ax2.grid(True)
#        ax3.set_ylabel('Magnetic field ' + self.magnet_unit)
#        ax3.grid(True)
#        ax4.set_ylabel('Temperature ' + self.temp_unit)
#        ax4.grid(True)
#        i = 0
#        while True:
#            i = i + 1
#            Accel = self.readAccel()
#            ax1.scatter(i, Accel[0], color='r', s=15)
#            ax1.scatter(i, Accel[1], color='g', s=15)
#            ax1.scatter(i, Accel[2], color='b', s=15)
#            ax1.legend(['acc_x','acc_y','acc_z'])
#            Gyro=self.readGyro()
#            ax2.scatter(i, Gyro[0], color='r', s=15)
#            ax2.scatter(i, Gyro[1], color='g', s=15)
#            ax2.scatter(i, Gyro[2], color='b', s=15)
#            ax2.legend(['omeg_x', 'omeg_y', 'omeg_z'])
#            Magnet=self.readMagnet()
#            ax3.scatter(i, Magnet[0], color='r', s=15)
#            ax3.scatter(i, Magnet[1], color='g', s=15)
#            ax3.scatter(i, Magnet[2], color='b', s=15)
#            ax3.legend(['b_x', 'b_y', 'b_z'])
#            ax4.scatter(i, self.readTemp(), color='k', s=15)
#            ax4.legend(['temp'])
#            plt.pause(0.001)
#            # Stop plotting if figure is closed
#            if not (plt.fignum_exists(fig.number)):
#                break
#
#        plt.show()
#
#    def saveCalibratedData(self):
#        calibration = {'accel_sens': self.accel_sens,
#                       'accel_offset': self.accel_offset,
#                       'gyro_sens': self.gyro_sens,
#                       'gyro_offset': self.gyro_offset,
#                       'magnet_sens': self.magnet_sens,
#                       'magnet_offset': self.magnet_offset,
#                       'temp_sens': self.temp_sens,
#                       'temp_offset': self.temp_offset}
#        csvwriter = csv.writer(open("MPU9250_Calib.csv", "w"))
#        for key, val in calibration.items():
#            csvwriter.writerow([key, val])
#
#    def load(self):
#        with open('MPU9250_Calib.csv', mode='r') as infile:
#            reader = csv.reader(infile)
#            calibration = dict((rows[0], rows[1]) for rows in reader)
#            self.accel_sens = calibration['accel_sens']
#            self.accel_offset = calibration['accel_offset']
#            self.gyro_sens = calibration['gyro_sens']
#            self.gyro_offset = calibration['gyro_offset']
#            self.magnet_sens = calibration['magnet_sens']
#            self.magnet_offset = calibration['magnet_offset']
#            self.temp_sens = calibration['temp_sens']
#            self.temp_offset = calibration['temp_offset']


class BMP280():
    def __init__(self):
        print('Programming BMP280...')
        i2c.write_byte_data(119, 0xF4, 0b00100111)  # enable pressure and temperature sensors
        self.dig_T1 = np.uint16(self.readWord(0x77, 0x89, 0x88))
        self.dig_T2 = self.readWord(0x77, 0x8B, 0x8A)
        self.dig_T3 = self.readWord(0x77, 0x8D, 0x8C)
        self.dig_P1 = np.uint16(self.readWord(0x77, 0x8F, 0x8E))
        self.dig_P2 = self.readWord(0x77, 0x91, 0x90)
        self.dig_P3 = self.readWord(0x77, 0x93, 0x92)
        self.dig_P4 = self.readWord(0x77, 0x95, 0x94)
        self.dig_P5 = self.readWord(0x77, 0x97, 0x96)
        self.dig_P6 = self.readWord(0x77, 0x99, 0x98)
        self.dig_P7 = self.readWord(0x77, 0x9B, 0x9A)
        self.dig_P8 = self.readWord(0x77, 0x9D, 0x9C)
        self.dig_P9 = self.readWord(0x77, 0x9F, 0x9E)
#        self.temp_accuracy = 1  # deg [+/-]
        self.temp_unit = '[°C]'
#        self.pressure_accuracy = 1  # hPa [+/-]
        self.pressure_unit = '[hPa]'
        self.pressure_sea_level = 1014.1 / ((1 - 453 / 44330) ** 5.255)
#        self.altitude_accuracy = 1  # m [+/-]
        self.altitude_unit = '[m]'
        print('Done')

    def readWord(self, address, high, low):
        return np.int16((i2c.read_byte_data(address, high) << 8) | i2c.read_byte_data(address, low))

    def readTemp(self):
        return ((self.readTempFine() * 5 + 128) >> 8) / 100

    def readTempFine(self):
        temp_raw = ((i2c.read_byte_data(0x77, 0xFA) << 8) | i2c.read_byte_data(0x77, 0xFB)) << 4 | (
                    (i2c.read_byte_data(0x77, 0xFC) >> 4) & 0xF)
        var1 = ((((temp_raw >> 3) - (self.dig_T1 << 1))) * (self.dig_T2)) >> 11
        var2 = (((((temp_raw >> 4) - (self.dig_T1)) * ((temp_raw >> 4) - (self.dig_T1))) >> 12) * (self.dig_T3)) >> 14;
        return var1 + var2

    def readPressure(self):
        pres_raw = ((i2c.read_byte_data(0x77, 0xF7) << 8) | i2c.read_byte_data(0x77, 0xF8)) << 4 | (
                    (i2c.read_byte_data(0x77, 0xF9) >> 4) & 0xF)
        var1 = self.readTempFine() / 2 - 64000;
        var2 = var1 * var1 * self.dig_P6 / 32768.0;
        var2 = var2 + (var1 * self.dig_P5) * 2;
        var2 = var2 / 4 + self.dig_P4 * 65536.0;
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        pres = 1048576.0 - pres_raw;
        pres = (pres - var2 / 4096.0) * 6250.0 / var1
        var1 = self.dig_P9 * pres * pres / 2147483648.0
        var2 = pres * self.dig_P8 / 32768.0
        return (pres + (var1 + var2 + self.dig_P7) / 16.0) / 100

    def readAltitude(self):
        return 44330 * (1.0 - (self.readPressure() / self.pressure_sea_level) ** 0.1903);

    def calibratePressureSeaLevel(self, altitude):
        self.pressure_sea_level = self.readPressure() / ((1 - altitude / 44330) ** 5.255)

    def showAll(self):
        print('Pressure=', self.readPressure(), '+/-', self.pressure_accuracy, self.pressure_unit)
        print('Altitude=', self.readAltitude(), '+/-', self.altitude_accuracy, self.altitude_unit)
        print('Temperature=', self.readTemp(), '+/-', self.temp_accuracy, self.temp_unit)

#    def plotAll(self):
#        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
#        ax1.set_ylabel('Pressure ' + self.pressure_unit)
#        ax1.grid(True)
#        ax2.set_ylabel('Altitude ' + self.altitude_unit)
#        ax2.grid(True)
#        ax3.set_ylabel('Temperature ' + self.temp_unit)
#        ax3.grid(True)
#        i = 0
#        while True:
#            i = i + 1
#            ax1.scatter(i, self.readPressure(), color='k', s=15)
#            ax1.legend(['pres'])
#            ax2.scatter(i, self.readAltitude(), color='k', s=15)
#            ax2.legend(['alt'])
#            ax3.scatter(i, self.readTemp(), color='k', s=15)
#            ax3.legend(['temp'])
#            plt.pause(0.001)
#            # Stop plotting if figure is closed
#            if not (plt.fignum_exists(fig.number)):
#                break
#
#        plt.show()


if __name__ == '__main__':
    mpu9250 = MPU9250()
    bmp280 = BMP280()
    mpu9250.showAll()
    bmp280.showAll()
    mpu9250.saveSamples()

    #mpu9250.plotAll()
    #bmp280.plotAll()
