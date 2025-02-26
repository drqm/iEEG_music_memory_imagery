#54121 -+sycu 6y
from psychopy import parallel
import serial

##### Set port address to match your local machine

#paddress = '/dev/parport0' # '0xDFF8' or 'COM1' in Windows
paddress = 'COM5'#'/dev/ttyUSB0'#'COM3' #in Windows

##################################################

try:
    port = serial.Serial(paddress)#,115200) works with biosemi
    port_type = 'serial'
except NotImplementedError:
    port = parallel.setPortAddress(address=paddress)
    port_type = 'parallel'
except:
    port_type = 'Not set'

print('port type: {}'.format(port_type))

if port_type == 'parallel':
    def setParallelData(code=1):
        port.setData(code)
        print('trigger sent {}'.format(code))
elif port_type == 'serial':
    def setParallelData(code=1):
        port.write(bytes(str(code).encode()))
        #port.write(str.encode(str(code)))#ode.encode()))
        #port.write(code)
        print('trigger sent {}'.format(code))
else:
    def setParallelData(code=1):
        print('trigger not sent {}'.format(code))
