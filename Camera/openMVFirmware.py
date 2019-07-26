# USB VCP example.
# This example shows how to use the USB VCP class to send an image to PC on demand.
#
# WARNING:
# This script should NOT be run from the IDE or command line, it should be saved as main.py
# Note the following commented script shows how to receive the image from the host side.
#
# #!/usr/bin/env python2.7
# import sys, serial, struct
# port = '/dev/ttyACM0'
# sp = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
#             xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=None, dsrdtr=True)
# sp.setDTR(True) # dsrdtr is ignored on Windows.
# sp.write('snap')
# sp.flush()
# size = struct.unpack('<L', sp.read(4))[0]
# img = sp.read(size)
# sp.close()
#
# with open('img.jpg', 'w') as f:
#     f.write(img)
import sensor, image, time, ustruct
from pyb import USB_VCP
from pyb import LED

red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)
ir_led    = LED(4)

#usb.send('Camera initialization...')
blue_led.on()
usb = USB_VCP()
sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect
clock = time.clock()                # Create a clock object to track the FPS.

# sensor.set_gainceiling(16)
blue_led.off()
usb.send('Done')

contrast=0
brightness=0
saturation=0
vertical_flip=False
horizontal_flip=False
watchdog_led=True


while(True):
    cmd = usb.recv(5, timeout=2000)
    if (cmd == b'photo'):
        clock.tick()
        img = sensor.snapshot().compress()
        usb.send(ustruct.pack('<L', img.size()))
        usb.send(img)
    elif (cmd == b'frmps'):
        usb.send(clock.fps())
    elif (cmd == b'ledr0'):
        red_led.off()
    elif (cmd == b'ledr1'):
        red_led.on()
    elif (cmd == b'ledg0'):
        green_led.off()
    elif (cmd == b'ledg1'):
        green_led.on()
    elif (cmd == b'ledb0'):
        blue_led.off()
    elif (cmd == b'ledb1'):
        blue_led.on()
    elif (cmd == b'ledi0'):
        ir_led.off()
    elif (cmd == b'ledi1'):
        ir_led.on()
    elif (cmd == b'wlede'):
        watchdog_led=True
    elif (cmd == b'wledd'):
        watchdog_led=False
    elif (cmd == b'ctrt+'):
        contrast=max(contrast+1,3)
        sensor.set_contrast(constrast)
    elif (cmd == b'ctrt-'):
        contrast=min(contrast-1,-3)
        sensor.set_contrast(constrast)
    elif (cmd == b'brgt+'):
        brightness=max(brightness+1,3)
        sensor.set_brightness(brightness)
    elif (cmd == b'brgt-'):
        brightness=min(brightness-1,-3)
        sensor.set_brightness(brightness)
    elif (cmd == b'satr+'):
        saturation=max(saturation+1,3)
        sensor.set_saturation(saturation)
    elif (cmd == b'satr-'):
        saturation=min(saturation-1,-3)
        sensor.set_saturation(saturation)
    elif (cmd == b'width'):
        usb.send(sensor.width())
    elif (cmd == b'heigh'):
        usb.send(sensor.height())
    elif (cmd == b'q4vga'):
        sensor.set_framesize(sensor.QQQQVGA) #40x30
    elif (cmd == b'q3vga'):
        sensor.set_framesize(sensor.QQQVGA) #80x60
    elif (cmd == b'q2vga'):
        sensor.set_framesize(sensor.QQVGA) #160x120
    elif (cmd == b'q1vga'):
        sensor.set_framesize(sensor.QQVGA) #320x240
    elif (cmd == b'q0vga'):
        sensor.set_framesize(sensor.QQVGA) #640x480
    elif (cmd == b'vflip'):
        if vertical_flip :
            sensor.set_vflip(True)
        else:
            sensor.set_vflip(False)
        vertical_flip=~vertical_flip
    elif (cmd == b'hflip'):
        if horizontal_flip :
            sensor.set_hflip(True)
        else:
            sensor.set_hflip(False)
        horizontal_flip=~horizontal_flip
    elif (cmd == b'grays'):
        sensor.set_pixformat(sensor.GRAYSCALE)
    elif (cmd == b'color'):
        sensor.set_hflip(sensor.RGB565)
    else:
        if watchdog_led:
            blue_led.on()
            time.sleep(10)
            blue_led.off()

