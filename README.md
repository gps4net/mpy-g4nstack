# mpy-g4nstack
MicroPython library for G4N devices 

Load the library onto your G4N01ARD device preflashed with MicroPython.

`$ mpremote <port> run g4ngps.py`

For a production setup, compile it with mpy-cross and copy it to :lib:

```
$ mpy-cross -o g4ngps.mpy g4ngps.py
$ mpremote <port> mkdir :lib
$ mpremote <port> cp g4ngps.mpy :lib/g4ngps.mpy
```

Open the serial REPL with mpremote or screen:

`$ mpremote <port>`

or 

`$ screen <port> 115200`

```
## open connection to GPS on UART2, speed 115200, RX pin GPIO25, TX pin GPIO26
gps = g4ngps(2, speed=115200, rx=25, tx=26)
## initialize the ESP32 RTC with the time from G4NGPS
gps.setrtc()
## show the RTC datetime value
machine.RTC().datetime()
## issue a QSYSINF comand
gps.qsysinf()
```

Initializing the compiled module is done a bit differently:

```
import g4ngps
## open connection to GPS on UART2, speed 115200, RX pin GPIO25, TX pin GPIO26
gps = g4ngps.g4ngps(2, speed=115200, rx=25, tx=26)
## issue a QSYSINF comand
gps.qsysinf()
```
