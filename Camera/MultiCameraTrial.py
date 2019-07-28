import OpenMVCamera as MVcam
import cv2

camera0 = MVcam.OpenMVCamera('CAMERA 0', '/dev/ttyACM0')
camera1 = MVcam.OpenMVCamera('CAMERA 1', '/dev/ttyACM1')
# camera0.format('640x480')
# camera1.format('640x480')
for i in range(3):
    camera0.flash(b'pink', 100)
    camera1.flash(b'green', 100)
while True:
    camera0.photo()
    camera1.photo()
    keyCode = cv2.waitKey(1) & 0xff
    # Stop the program on the ESC key
    if keyCode == 27:
        break

cv2.waitKey(0)
cv2.destroyAllWindows()
camera1.close()