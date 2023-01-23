# mpy-g4nstack
MicroPython library for G4N devices 

Load the library onto your G4N01ARD device preflashed with MicroPython.

`$ mpremote <port> run esp32-g4ngps.py`

Open the serial REPL with screen or mpremote:

`$ screen /dev/ttyUSB0 115200`

```
gps = g4ngps(2, 115200)
## initialize the ESP32 RTC with the time from G4NGPS
gps.setrtc()
## show the RTC datetime value
machine.RTC().datetime()
## issue a QSYSINF comand
gps.qsysinf()
```
