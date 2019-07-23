# #!/usr/bin/env python2.7
# import opencv as cv
import serial
import struct
port = 'COM3'
sp = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=None, dsrdtr=True)
sp.setDTR(True) # dsrdtr is ignored on Windows.
sp.write(b"ledb1")
#sp.write(b"photo")
#sp.flush()
#size = struct.unpack('<L', sp.read(4))[0]
#print("Picture of Size:",size)
#img = sp.read(size)
#sp.close()

#print(img)
#with open("img.jpg", "wb+") as f:
#    f.write(img)