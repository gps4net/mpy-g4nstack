import machine, time, struct, binascii

class g4ngps:

	def __init__(self, port, speed):
		self.uart = machine.UART(port, speed)
		self.uart.init(speed, bits=8, parity=None, stop=1)

	def qsysinf(self):
		self.uart.write('QSYSINF//')
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read(73)
			sysinf = {
				'rti': res[7:15],
				'hhmmss': res[15:21],
				'ddmmyyyy': res[23:31],
				'syncage': struct.unpack("<I", binascii.unhexlify(res[31:39]))[0],
				'psn': res[39:47],
				'hwcode': res[47:49],
				'bootver': res[49:51],
				'swv': res[51:53],
				'sbn': res[53:55],
				'frmwopt': res[55:71],
			}
			return sysinf

	def qsysrtc(self):
		self.uart.write('QSYSRTC//')
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read(77)
			sysrtc = {
				'hhmmss': res[7:13],
				'us': res[13:15],
				'ddmmyyyy': res[15:23],
				'dow': res[23:25],
				'uptime': struct.unpack('>I', binascii.unhexlify(res[25:33]))[0],
				'rtcepoch': struct.unpack('>I', binascii.unhexlify(res[33:51]))[0],
				'rtclastepoch': struct.unpack('>I', binascii.unhexlify(res[41:49]))[0],
				'rtcdeltaepoch': struct.unpack('>I', binascii.unhexlify(res[49:57]))[0],
				'rtcdrift': struct.unpack('>H', binascii.unhexlify(res[57:61]))[0],
				'rtcstatus': res[61:63],
			}
			return sysrtc

	def setrtc(self):
		rtc = machine.RTC()
		sysrtc = self.qsysrtc()
		# initialize rtc (year, month, day, weekday, hours, minutes, seconds, usec)
		rtc.init(tuple([int(sysrtc['ddmmyyyy'][4:8]), int(sysrtc['ddmmyyyy'][2:4]), int(sysrtc['ddmmyyyy'][0:2]), int(sysrtc['dow'][0:2]) - 1, int(sysrtc['hhmmss'][0:2]), int(sysrtc['hhmmss'][2:4]), int(sysrtc['hhmmss'][4:6]), int(sysrtc['us'][0:2])]))
