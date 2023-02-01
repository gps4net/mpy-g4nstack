import machine, time, struct, binascii, gc

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
				'psn': res[39:47].decode,
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
		
	def qgpsinf(self):
		self.uart.write("QGPSINF//")
		time.sleep_ms(100)
		if self.uart.any():
			res =self.uart.read(89)
			gpsinf = {
				'year': int(res[17:21],16),
				'month': int(res[15:17],16),
				'day': int(res[13:15],16),
				'hour': int(res[7:9],16),
				'minute': int(res[9:11],16),
				'sec': int(res[11:13],16),
				'lattitude': res[21:29], #break this into degrees and minutes 
				'longitude': res[29:39], #break this into degrees and minutes 
				'altitude': int(res[39:45],16), #don't know about this yet
        		'navstat': int(res[45:47],16), #<2 ideal, <3 excelet, <6 good, <11 moderate, <21 fair else poor
        		'sog': int(res[47:53],16), #km/h
        		#'cog': struct.unpack('>I', binascii.unhexlify(res[53:59]))[0],
				'cog': res[53:59],
        		'nosvgps': res[59:61],
        		'pdop': int(res[61:65],16),
        		'hdop': int(res[65:69],16),
        		'vdop': int(res[69:73],16),
        		'distance': int(res[73:81],16),
        		'trip_distance': int(res[81:89],16)

			}	 
			#todo interpret the raw data to get lat/lon corectly
			return gpsinf

#made a pseudo-read.until / method
	def read_until(self):
		res = b''
		while True:
			char = self.uart.read(1)
			if char == b'/':
				break
			res += char
		return res

#auto-complete parameters commands
	def qacivin(self):
		self.uart.write("QACIVIN//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			acivin={
				'vin': res[7:-2].decode()
			}
		return acivin

	def qacivrn(self):
		self.uart.write("QACIVRN//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			acivrn={
				'vrn': res[7:-2].decode()
			}
		return acivrn	

	def qacikfa(self):
		self.uart.write("QACIKFA//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			acikfa={
				'k_factor': int(res[7:-2],16)
			}
		return acikfa

	def qaciepd(self):
		self.uart.write("QACIEPD//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			aciepd={
				'drift_epoch': int(res[7:-2],16)
			}
		return aciepd

	def qacioeo(self):
		self.uart.write("QACIOEO//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			acieoe={
				'engine_on_time': int(res[7:-2],16)
			}
		return acieoe

	def qaciote(self):
		self.uart.write("QACIOTE//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			aciete={
				'engine_on_time': int(res[7:-2],16)
			}
		return aciete	
#end auto-complete parameters

#main system
	def qsyssts(self):
			self.uart.write("QSYSSTS//")
			time.sleep_ms(100)
			if self.uart.any():
				res = self.uart.read()
				syssts={
					'speed_threshold': int(res[7:-2],16)
				}
			return syssts

	def qsysstm(self):
			self.uart.write("QSYSSTM//")
			time.sleep_ms(100)
			if self.uart.any():
				res = self.uart.read()
				sysstm={
					'time_threshold': int(res[7:-2],16)
				}
			return sysstm
	
	def qsysled(self):
			self.uart.write("QSYSLED//")
			time.sleep_ms(100)
			if self.uart.any():
				res = self.uart.read()
				print(res)
				result_int = int(res[7:-2],16) #hex to int

				sysled={
					'led': res[7:],
					'led_can':(result_int & 0x8000 != 0),
					'led_wp':(result_int & 0x4000 != 0),
					'led_ignition':(result_int & 0x2000 != 0),
					'led_alarm':(result_int & 0x1000 != 0),
					'led_stationary_vehicle':(result_int & 0x0800 != 0),
					'led_external_serial_traffic':(result_int & 0x0400 !=0),
					'led_sim_selector':(result_int & 0x0200 != 0),
					'led_ftp_indicator':(result_int & 0x0100 != 0),
					'led_acc_antitheft':(result_int & 0x0080 != 0),
					'led_acc_movement':(result_int & 0x0040 != 0),
					'led_fuel_sensor':(result_int & 0x0020 != 0),
					'led_eng_running':(result_int & 0x0010 != 0),
					'led_ibu_auth':(result_int & 0x0008 != 0),
					'led_data_mode':(result_int & 0x0004 != 0)
				}
			return sysled

	def qsysrsu(self):
		self.uart.write("QSYSRSU//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			sysrsu={
				'auto_reset_threshold': int(res[7:-2],16)
			}
		return sysrsu

	def qsysset(self):
		self.uart.write("QSYSSET//")
		time.sleep_ms(100)
		res = b''
		while not self.uart.any():
			time.sleep_ms(10)
		res = self.uart.read()
		if res:
			result_int = int(res[7:-2],16)
			sysset={
				'force_transmission_after_system_change': (result_int & 0x40000000 == 0)
			}
			return sysset
		else:
			raise Exception("UART response was empty, try again")		

#selectors in main system

	def qsysfus(self):
		self.uart.write("QSYSFUS//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			sysfus={
				'total_fuel_selector_id': int(res[7:-2],16)
			}
		return sysfus

	def qsysosl(self):
		self.uart.write("QSYSOSL//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			sysosl={
				'odometer_selector_id': int(res[7:-2],16)
			}
		return sysosl

	def qsysssl(self):
		self.uart.write("QSYSSSL//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			sysssl={
				'speed_selector_id': int(res[7:-2],16)
			}
		return sysssl

	def qsystts(self):
		self.uart.write("QSYSTTS//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			systts={
				'ignition_selector_id': int(res[7:-2],16)
			}
		return systts

#work private system
	def qsyssym(self):
		self.uart.write("QSYSSYM//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			result_int = int(res[7:-2],16) #hex to int
			syssym={
				'work_private_active':(result_int & 0x8000 == 0),
				'triggered_by_IO': (result_int & 0x4000 != 0),
                'triggered_by_IO_negated': (result_int & 0x2000 != 0),
                'triggered_by_calendar':(result_int & 0x1000 != 0),
                'no_acq_private':(result_int & 0x0800 != 0),
                'no_trans_private':(result_int & 0x0400 != 0),
                'no_alarms_private':(result_int & 0x0200 != 0),
                'use_reserved_days':(result_int & 0x0100 != 0),
                'set_private_enable_relay':(result_int & 0x0080 != 0),
                'set_private_disable_relay':(result_int & 0x0040 != 0),
                'set_work_enable_relay':(result_int & 0x0020 != 0),
                'set_Work_disable_relay':(result_int & 0x0010 != 0),
			}
		return syssym

	#work private defined by calendar
	def qsysca0(self):
		private_intervals = {}
		for j in range(7):
			command = "QSYSSCA0" + str(j + 1) + "//"
			self.uart.write(command)
			time.sleep_ms(100)
			if self.uart.any():
				res = self.uart.read()
				res = res[9:-2]
				interval_int=[]
				intervals = bytearray(19)
				for i in range(19):
					intervals = int(res[i*2 : (i+1)*2], 16)
					interval_int.append(intervals)
				if j == 0:
					private_intervals['monday'] = interval_int
				elif j == 1:
					private_intervals['tuesday'] = interval_int
				elif j == 2:
					private_intervals['wednesday'] = interval_int
				elif j == 3:
					private_intervals['thursday'] = interval_int
				elif j == 4:
					private_intervals['friday'] = interval_int
				elif j == 5:
					private_intervals['saturday'] = interval_int
				elif j == 6:
					private_intervals['sunday'] = interval_int

		return private_intervals

	#reserved private days 
	def qsyswpd(self):
		command="QSYSWPD//"
		self.uart.write(command)
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			res = res[7:-2]
			reserved_days = bytearray(65)
			try:
				for i in range(65):
					if res[i*2 : (i+1)*2].decode() == "FF":
						break
					reserved_days[i] = int(res[i*2 : (i+1)*2], 16)
					print(reserved_days)
			except Exception as e:
				print("Error: ", e)

	def qsyswpf(self):
		command="QSYSWPF//"
		self.uart.write(command)
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			res = res[7:-2]
			syswpf={
				'work_private_time_filter': int(res,16)	
			}
		return syswpf

#system power management 45
	def qsyspmg(self):
		self.uart.write("QSYSPMG//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			result_int = int(res[7:-2],16) #hex to int
			syspmg={
				'power_management_enabled':(result_int & 0x80000000 == 0),
				'pmg_leds_off': (result_int & 0x40000000 != 0),
                'pdn_mode_level': (result_int & 0x20000000 != 0),
				'pdn_led_indicator' : (result_int & 0x10000000 != 0),
				'acc_charge_pdn' : (result_int & 0x08000000 != 0),
			}
		return syspmg

	#power saving wakeup sources
	def qsyswku(self):
		# print("Free memory at start: ", gc.mem_free())
		# print("Allocated memory at start: ", gc.mem_alloc())
		# mem_free_start= gc.mem_free()
		# mem_alloc_start=gc.mem_alloc()
		self.uart.write("QSYSPMG//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			result_int = int(res[7:-2],16) #hex to int
			syswku={
				'wakeup_source_enabled' :(result_int & 0x80000000 == 0),
    			'wakeup_source_volt_over' :(result_int & 0x40000000 != 0),
    			'wakeup_source_hour_match' :(result_int & 0x20000000 != 0),
    			'wakeup_source_calendar' :(result_int & 0x10000000 != 0),
    			'wakeup_source_acquisition' : (result_int & 0x08000000 != 0),
    			'wakeup_source_transmission' :(result_int & 0x04000000 != 0),
    			'wakeup_source_backButton' :(result_int & 0x02000000 != 0),
    			'wakeup_source_motion_sensor' :(result_int & 0x01000000 != 0),
    			'wakeup_source_volt_IO1Over' :(result_int & 0x00800000 != 0),
    			'wakeup_source_volt_IO2Over' :(result_int & 0x00400000 != 0),
    			'wakeup_source_voltIO3Over' :(result_int & 0x00200000 != 0),
    			'wakeup_source_voltIO4Over' :(result_int & 0x00100000 != 0),
    			'wakeup_source_voltIO1Under' :(result_int & 0x00080000 != 0),
    			'wakeup_source_voltIO2Under' :(result_int & 0x00040000 != 0),
    			'wakeup_source_voltIO3Under' :(result_int & 0x00020000 != 0),
    			'wakeup_source_voltIO4Under' :(result_int & 0x00010000 != 0),
    			'wakeup_source_ignitionOn' :(result_int & 0x00008000 != 0),
    			'wakeup_source_iButtonPresent' :(result_int & 0x00004000 != 0),
    			'wakeup_source_mov_acc_antitheft' :(result_int & 0x00002000 != 0),
    			'wakeup_source_mov_acc_mov': (result_int & 0x00001000 != 0)
			}

			# print("Free memory at end: ", gc.mem_free())
			# print("Allocated memory at end: ", gc.mem_alloc())
			# mem_free_end= gc.mem_free()
			# mem_alloc_end=gc.mem_alloc()
			# print("Diff free mem at end", mem_alloc_start-mem_free_end )
			# print("Diff alloc mem at end", mem_alloc_end-mem_alloc_start)	
		return syswku

	#wake-up hour match
	def qsyspwm(self):
		self.uart.write("QSYSPWM//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res =res[7:-2]
			qsyspwm={
				'wk_hour1': res[:2].decode() +":"+res[2:4].decode(),
				'wk_hour2': res[4:6].decode() +":"+res[6:8].decode(),
				'wk_hour3': res[8:10].decode() +":"+res[10:12].decode(),
				'wk_hour4': res[12:14].decode() +":"+res[14:16].decode(),
				'wk_hour5': res[16:18].decode() +":"+res[18:20].decode(),
				'wk_hour6': res[20:22].decode() +":"+res[22:24].decode(),
				'wk_hour7': res[24:26].decode() +":"+res[26:28].decode(),
				'wk_hour8': res[28:30].decode() +":"+res[30:32].decode(),
				'wk_hour9': res[32:34].decode() +":"+res[34:36].decode(),
				'wk_hour10': res[36:38].decode() +":"+res[38:40].decode(),
				'wk_hour11': res[40:42].decode() +":"+res[42:44].decode(),
				'wk_hour12': res[44:46].decode() +":"+res[46:48].decode(),
			}
			for i in range(1, 13):
				key = 'wk_hour' + str(i)
				if qsyspwm[key] == "99:99":
					qsyspwm[key] = None

		return qsyspwm	

	#wake-up calendar
	def qsyswc0(self):
		wkup_private_intervals = {}
		for j in range(7):
			command = "QSYSWKC0" + str(j + 1) + "//"
			self.uart.write(command)
			time.sleep_ms(100)
			if self.uart.any():
				res = self.uart.read()
				res = res[9:-2]
				interval_int=[]
				intervals = bytearray(19)
				for i in range(19):
					intervals = int(res[i*2 : (i+1)*2], 16)
					interval_int.append(intervals)	
				if j == 0:
					wkup_private_intervals['monday'] = interval_int
				elif j == 1:
					wkup_private_intervals['tuesday'] = interval_int
				elif j == 2:
					wkup_private_intervals['wednesday'] = interval_int
				elif j == 3:
					wkup_private_intervals['thursday'] = interval_int
				elif j == 4:
					wkup_private_intervals['friday'] = interval_int
				elif j == 5:
					wkup_private_intervals['saturday'] = interval_int
				elif j == 6:
					wkup_private_intervals['sunday'] = interval_int
		return wkup_private_intervals

	#power management full power
	def	qsyspmf(self):
		self.uart.write("QSYSPMF//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
		
			# result_int = int(res[7:-2],16) #hex to int
			result_1=int(res[7:-15],16)
			result_2=int(res[15:-2],16)
			
			syspmf={
				'sby_power_under_volt' : (result_1 & 0x40000000 != 0),
				'sby_at_hours' : (result_1 & 0x20000000 != 0),
				'sby_idle' : (result_1 & 0x10000000 != 0),
				'sby_after_acquisition' : (result_1 & 0x08000000 != 0),
				'sby_after_transmission' : (result_1 & 0x04000000 != 0),
				'sby_at_calendar' : (result_1 & 0x02000000 != 0),
				'sby_when_ignition_off' : (result_1 & 0x01000000 != 0),
				'sleep_power_under_volt' : (result_2 & 0x40000000 != 0),
				'sleep_at_hours' : (result_2 & 0x20000000 != 0),
				'sleep_idle' : (result_2 & 0x10000000 != 0),
				'sleep_after_acquisition' : (result_2 & 0x08000000 != 0),
				'sleep_after_transmission' : (result_2 & 0x04000000 != 0),
				'sleep_at_calendar' : (result_2& 0x02000000 != 0),
				'sleep_when_ignition_off' : (result_2 & 0x01000000 != 0)
    
			}
		return syspmf

	#power management standby
	def	qsyspmy(self):
		self.uart.write("QSYSPMY//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()

			syspmy={
				"fp_power_under_volt": (int(res[7:15],16) & 0x40000000 != 0),
				"fp_at_hours": (int(res[7:15],16) & 0x20000000 != 0),
				"fp_at_calendar": (int(res[7:15],16) & 0x10000000 != 0),
				"fp_for_acquisition": (int(res[7:15],16) & 0x08000000 != 0),
				"fp_for_transmission": (int(res[7:15], 16) & 0x04000000 != 0),
				"fp_motion_sensor": (int(res[7:15],16) & 0x01000000 != 0),
				"fp_over_voltage_ain1": (int(res[7:15],16) & 0x00800000 != 0),
				"fp_over_voltage_ain2": (int(res[7:15],16) & 0x00400000 != 0),
				"fp_over_voltage_ain3": (int(res[7:15],16) & 0x00200000 != 0),
				"fp_under_voltage_ain1": (int(res[7:15],16) & 0x00080000 != 0),
				"fp_under_voltage_ain2": (int(res[7:15],16) & 0x00040000 != 0),
				"fp_under_voltage_ain3": (int(res[7:15],16) & 0x00020000 != 0),
				"fp_ignition_on": (int(res[7:15],16) & 0x00008000 != 0),
				"fp_i_button_present": (int(res[7:15], 16) & 0x00004000 != 0),
				"fp_movement_accl_antitheft": (int(res[7:15], 16) & 0x00002000 != 0),
				"fp_movement_accl_movement_detector": (int(res[7:15],16) & 0x00001000 != 0),
				"fp_din4_pulled_gnd": (int(res[7:15],16) & 0x00000800 != 0),
				"fp_din5_pulled_gnd": (int(res[7:15],16) & 0x00000400 != 0),
				"fp_din6_pulled_gnd": (int(res[7:15],16) & 0x00000200 != 0),
				"sleep_power_under_volt": (int(res[15:-2],16) & 0x40000000 != 0),
				"sleep_after_period": (int(res[15:-2],16) & 0x10000000 != 0),
				"sleep_after_ignition_off": (int(res[15:-2],16) & 0x08000000 != 0)
			}
		return syspmy

	#power management sleep
	def qsyspms(self):
		self.uart.write("QSYSPMS//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			result_1 = int(res[7:15], 16)
			result_2 = int(res[15:-2], 16)
			syspms={
				"fpBatteryLow": (result_1 & 0x40000000 != 0),
				"fpAfterPeriod": (result_1 & 0x20000000 != 0),
				"fpIgnitionOn": (result_1 & 0x08000000 != 0),
				"fpIButtonB": (result_1 & 0x04000000 != 0),
				"fpMinuteMatch": (result_1 & 0x00800000 != 0),
				"fpHourMatch": (result_1 & 0x00400000 != 0),
				"fpWeekdayMatch": (result_1 & 0x00200000 != 0),
				"fpDayMatch": (result_1 & 0x00100000 != 0),
				"sbyBatteryLow": (result_2 & 0x40000000 != 0),
				"sbyAfterPeriod": (result_2 & 0x20000000 != 0),
				"sbyIgnitionOn": (result_2 & 0x08000000 != 0),
				"sbyIButtonB": (result_2 & 0x04000000 != 0),
				"sbyMinuteMatch": (result_2 & 0x00800000 != 0),
				"sbyHourMatch": (result_2 & 0x00400000 != 0),
				"sbyWeekdayMatch": (result_2 & 0x00200000 != 0),
				"sbyDayMatch": (result_2 & 0x00100000 != 0)
			}
		return syspms
			
	#power management sleep control week day
	def qsysslm(self):
		self.uart.write("QSYSSLM//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res = res[7:-2]
			res_str = res.decode()
			sysslm={
				'sleep_hour': None,
				'sleep_minute':None,
				'sleep_month_day':None,
				'sleep_week_day':None,
			}
			if(res_str[0:2]=='FF'):
				sysslm['sleep_hour'] = None
			else:
				sysslm['sleep_hour'] = int(res[0:2],16)
			if(res_str[2:4]=='FF'):
				sysslm['sleep_hour'] = None
			else:
				sysslm['sleep_minute'] = int(res[2:4],16)
			if(res_str[4:6]=='FF'):
				sysslm['sleep_month_day'] = None
			else:
				sysslm['sleep_month_day'] = int(res[4:6],16)		
			if(res_str[6:8]=='FF'):
				sysslm['sleep_week_day'] = None
			else:
				sysslm['sleep_week_day'] = int(res[6:8],16)
			
		return sysslm

	#power management delay full_power to stanby 
	def qsyspdl(self):
		self.uart.write("QSYSPDL//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res = res[7:-2]
			res_str=res.decode()
			syspdl={
				'delay_full_power_to_standby': None
			}	
			if(res_str=='FFFF'):
				syspdl['delay_full_power_to_standby':None]
			else:
				syspdl['delay_full_power_to_standby']:int(res,16)	
		return syspdl

	#power management delay full_power to sleep
	def qsyspds(self):
		self.uart.write("QSYSPDS//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res = res[7:-2]
			res_str=res.decode()
			syspds={
				'delay_full_power_to_sleep' : None
			}
			if(res_str=='FFFF'):
				syspds['delay_full_power_to_sleep': None]
			else:
				syspds['delay_full_power_to_sleep': int(res,16)]	
		return syspds	

	#power management full power hour parameters
	def qsysppm(self):
		self.uart.write("QSYSPPM//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res =res[7:-2]
			qsysppm={
				'fp_hour1': res[:2].decode() +":"+res[2:4].decode(),
				'tr_hour2': res[4:6].decode() +":"+res[6:8].decode(),
				'tr_hour3': res[8:10].decode() +":"+res[10:12].decode(),
				'tr_hour4': res[12:14].decode() +":"+res[14:16].decode(),
				'tr_hour5': res[16:18].decode() +":"+res[18:20].decode(),
				'tr_hour6': res[20:22].decode() +":"+res[22:24].decode(),
				'tr_hour7': res[24:26].decode() +":"+res[26:28].decode(),
				'tr_hour8': res[28:30].decode() +":"+res[30:32].decode(),
				'fp_hour9': res[32:34].decode() +":"+res[34:36].decode(),
				'fp_hour10': res[36:38].decode() +":"+res[38:40].decode(),
				'fp_hour11': res[40:42].decode() +":"+res[42:44].decode(),
				'fp_hour12': res[44:46].decode() +":"+res[46:48].decode(),
			}
			for i in range(1, 13):
				key = 'fp_hour' + str(i)
				if qsysppm[key] == "99:99":
					qsysppm[key] = None

		return qsysppm	

	#power management prewakeup interval
	def qsyspwk(self):
		self.uart.write("QSYSPWK//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res =res[7:-2]
			syspwk = {
				'prewakeup_interval':int(res,16)
			}
		return syspwk

	#power management stand by transition period
	def qsyssls(self):
		self.uart.write("QSYSSLS//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res =res[7:-2]
			syssls = {
				'stand_by_trasition_period':int(res,16)
			}
		return syssls	

	#power mamangement sleep transition period
	def qsysslc(self):
		self.uart.write("QSYSSLC//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res =res[7:-2]
			sysslc = {
				'sleep_trasition_period':int(res,16)
			}
		return sysslc

	#power management idle time
	def qsysidt(self):
		self.uart.write("QSYSIDT//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res =res[7:-2]
			sysslc = {
				'sleep_trasition_period':int(res,16)
			}
		return sysslc	

#Alarm system local network
	def qalmhst(self):
		self.uart.write("QALMHST//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res =int(res[7:-2],16)
			almhst = {
				"alarms": (res & 0x80000000 == 0),
				"overspeed": (res & 0x40000000 != 0),
				"ignition": (res & 0x20000000 != 0),
				"panic_button": (res & 0x10000000 != 0),
				"relay": (res & 0x08000000 != 0),
				"input_power_undervoltage": (res & 0x04000000 != 0),
				"input_power_overvoltage": (res & 0x02000000 != 0),
				"acc_voltage_under_threshold": (res & 0x01000000 != 0),
				"acc_error": (res & 0x00800000 != 0),
				"relay_disconnected": (res & 0x00400000 != 0),
				"ibutton_disconnected": (res & 0x00200000 != 0),
				"data_limit": (res & 0x00040000 != 0),
				"daily_traffic_exceeded": (res & 0x00020000 != 0),
				"monthly_traffic_exceeded": (res & 0x00010000 != 0),
				"gps_missing": (res & 0x00008000 != 0),
				"stationary_contact_on": (res & 0x00004000 != 0),
				"stationary_contact_off": (res & 0x00002000 != 0),
				"speed_exceeded_contact_off_threshold": (res & 0x00001000 != 0),
				"motion_sensor_movement": (res & 0x00000400 != 0),
				"private_alarm": (res & 0x00000100 != 0),
				"gps_jamming": (res & 0x00000040 != 0),
				"gsm_jamming": (res & 0x00000020 != 0),
				"accelerometer_antitheft_alarm": (res & 0x00000008 != 0),
				"downtime_alarm": (res & 0x00000004 != 0)
			}
		return almhst

#Alarm system roaming network
	def qalmrst(self):
		self.uart.write("QALMRST//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res =int(res[7:-2],16)
			almrst = {
				"alarms": (res & 0x80000000 == 0),
				"overspeed": (res & 0x40000000 != 0),
				"ignition": (res & 0x20000000 != 0),
				"panic_button": (res & 0x10000000 != 0),
				"relay": (res & 0x08000000 != 0),
				"input_power_undervoltage": (res & 0x04000000 != 0),
				"input_power_overvoltage": (res & 0x02000000 != 0),
				"acc_voltage_under_threshold": (res & 0x01000000 != 0),
				"acc_error": (res & 0x00800000 != 0),
				"relay_disconnected": (res & 0x00400000 != 0),
				"ibutton_disconnected": (res & 0x00200000 != 0),
				"data_limit": (res & 0x00040000 != 0),
				"daily_traffic_exceeded": (res & 0x00020000 != 0),
				"monthly_traffic_exceeded": (res & 0x00010000 != 0),
				"gps_missing": (res & 0x00008000 != 0),
				"stationary_contact_on": (res & 0x00004000 != 0),
				"stationary_contact_off": (res & 0x00002000 != 0),
				"speed_exceeded_contact_off_threshold": (res & 0x00001000 != 0),
				"motion_sensor_movement": (res & 0x00000400 != 0),
				"private_alarm": (res & 0x00000100 != 0),
				"gps_jamming": (res & 0x00000040 != 0),
				"gsm_jamming": (res & 0x00000020 != 0),
				"accelerometer_antitheft_alarm": (res & 0x00000008 != 0),
				"downtime_alarm": (res & 0x00000004 != 0)
			}
		return almrst	

#Alarm system overspeed speed threashold
	def qalmovs(self):
		self.uart.write("QALMOVS//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almovs={
				'overspeed_threshold':(res  & 0xffff) / 10
			}
		return almovs

	#Alarm system movement treshold
	def qalmovs(self):
		self.uart.write("QALMMOV//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almmov={
				'movement_threshold':(res  & 0xffff) / 10
			}
		return almmov

	#Alarm system stationary timer contact on
	def qalmstn(self):
		self.uart.write("QALMSTN//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almstn={
				'stationary_timer_contact_on':(res  & 0xffff)
			}
		return almstn

	#Alarm system stationary timer contact on
	def qalmstf(self):
		self.uart.write("QALMSTF//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almstf={
				'stationary_timer_contact_off':(res  & 0xffff)
			}
		return almstf

	#Alarm system speed threshold contact on
	def qalmssn(self):
		self.uart.write("QALMSSN//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almssn={
				'speed_threshold_contact_on':(res  & 0xffff) / 10
			}
		return almssn	

	#Alarm system speed threshold contact off
	def qalmssf(self):
		self.uart.write("QALMSSF//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almssf={
				'speed_threshold_contact_off':(res  & 0xffff) / 10
			}
		return almssf		

	#Alarm system  missing gps treshold
	def qalmgmt(self):
		self.uart.write("QALMGMT//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almgmt={
				'gps_missing_threshold':(res  & 0xffff)
			}
		return almgmt

	#Alarm system down time timer
	def qalmdta(self):
		self.uart.write("QALMDTA//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almdta={
				'down_time_timer':(res  & 0xffff)
			}
		return almdta


 	#Alarm system data flash limit
	def qalmdfl(self):
		self.uart.write("QALMDFL//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almdfl={
				'data_flash_limit':(res  & 0xffff)
			}
		return almdfl

	#Alarm system delay accelerometer movement threhold
	def qalmatd(self):
		self.uart.write("QALMDFL//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			almatd={
				'delay_acc_movement':(res  & 0xffff)
			}
		return almatd

#Transmission system
	#transmission on local network
	def qtrshst(self):
		self.uart.write("QTRSHST//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshst={
				"transmission": (res & 0x80000000 == 0),
				"interval_a_transmission": (res & 0x40000000 != 0),
				"interval_a_when_contact_on_transmission": (res & 0x20000000 != 0),
				"interval_a_when_contact_off_transmission": (res & 0x10000000 != 0),
				"interval_a_when_alarms_set_transmission": (res & 0x08000000 != 0),
				"interval_b_transmission": (res & 0x04000000 != 0),
				"interval_b_when_contact_on_transmission": (res & 0x02000000 != 0),
				"interval_b_when_contact_off_transmission": (res & 0x01000000 != 0),
				"interval_b_when_alarms_set_transmission": (res & 0x00800000 != 0),
				"alarm_transmission": (res & 0x00400000 != 0),
				"accumulated_data_transmission": (res & 0x00200000 != 0),
				"contact_transmission": (res & 0x00100000 != 0),
				"hour_match_transmission": (res & 0x00080000 != 0),
				"i_button_group_transmission": (res & 0x00040000 != 0),
				"daily_excessive_traffic": (res & 0x00020000 != 0),
				"monthly_excessive_traffic": (res & 0x00010000 != 0),
				"gps_valid_transmission": (res & 0x00008000 != 0),
				"trans_after_power_on": (res & 0x00004000 != 0),
				"delay_transmission": (res & 0x00002000 != 0),
				"clear_transmission": (res & 0x00001000 != 0),
				"trans_change_work_private": (res & 0x00000800 != 0),
				"epoch_interval_a_contact_on": (res & 0x00000400 != 0),
				"epoch_interval_a_contact_off": (res & 0x00000200 != 0),
				"epoch_interval_b_contact_on": (res & 0x00000100 != 0),
				"epoch_interval_b_contact_off": (res & 0x00000080 != 0),
				"epoch_enabled": (
					(res & 0x00000400) != 0 or (res & 0x00000200) != 0 or
					(res & 0x00000100) != 0 or (res & 0x00000080) != 0),
				"cumulative_distance": (res & 0x00000040 != 0),
				"allow_trans_gen_acq_engine": (res & 0x00000020 != 0),
				"transmit_rtc": (res & 0x00000010)
			}
		return trshst

	#transmission on roaming network
	def qtrsrst(self):
		self.uart.write("QTRSRST//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsrst={
				"transmission": (res & 0x80000000 == 0),
				"interval_a_transmission": (res & 0x40000000 != 0),
				"interval_a_when_contact_on_transmission": (res & 0x20000000 != 0),
				"interval_a_when_contact_off_transmission": (res & 0x10000000 != 0),
				"interval_a_when_alarms_set_transmission": (res & 0x08000000 != 0),
				"interval_b_transmission": (res & 0x04000000 != 0),
				"interval_b_when_contact_on_transmission": (res & 0x02000000 != 0),
				"interval_b_when_contact_off_transmission": (res & 0x01000000 != 0),
				"interval_b_when_alarms_set_transmission": (res & 0x00800000 != 0),
				"alarm_transmission": (res & 0x00400000 != 0),
				"accumulated_data_transmission": (res & 0x00200000 != 0),
				"contact_transmission": (res & 0x00100000 != 0),
				"hour_match_transmission": (res & 0x00080000 != 0),
				"i_button_group_transmission": (res & 0x00040000 != 0),
				"daily_excessive_traffic": (res & 0x00020000 != 0),
				"monthly_excessive_traffic": (res & 0x00010000 != 0),
				"gps_valid_transmission": (res & 0x00008000 != 0),
				"trans_after_power_on": (res & 0x00004000 != 0),
				"delay_transmission": (res & 0x00002000 != 0),
				"clear_transmission": (res & 0x00001000 != 0),
				"trans_change_work_private": (res & 0x00000800 != 0),
				"epoch_interval_a_contact_on": (res & 0x00000400 != 0),
				"epoch_interval_a_contact_off": (res & 0x00000200 != 0),
				"epoch_interval_b_contact_on": (res & 0x00000100 != 0),
				"epoch_interval_b_contact_off": (res & 0x00000080 != 0),
				"epoch_enabled": (
					(res & 0x00000400) != 0 or (res & 0x00000200) != 0 or
					(res & 0x00000100) != 0 or (res & 0x00000080) != 0),
				"cumulative_distance": (res & 0x00000040 != 0),
				"allow_trans_gen_acq_engine": (res & 0x00000020 != 0),
				"transmit_rtc": (res & 0x00000010)
			}
		return trsrst

	#transmission threshold accumulated data for local network
	def qtrshad(self):
		self.uart.write("QTRSHAD//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshad={
				"threshold_accumulated_data": ((res & 0xffff) /1024)
			}
		return trshad	

	#transmission threshold accumulated data for roaming network
	def qtrsrad(self):
		self.uart.write("QTRSRAD//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsrad={
				"threshold_accumulated_data": ((res & 0xffff) /1024)
			}
		return trsrad	

	#transmission interval a local network  
	def qtrshia(self):
		self.uart.write("QTRSHIA//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshia={
				"interval_a": res & 0xffff
			}	
		return trshia

	#transmission interval a roaming network  
	def qtrsria(self):
		self.uart.write("QTRSRIA//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsria={
				"interval_a": res & 0xffff
			}	
		return trsria

	#transmission interval b local network  
	def qtrshib(self):
		self.uart.write("QTRSHIB//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshib={
				"interval_b": res & 0xffff
			}	
		return trshib

	#transmission interval b roaming net
	def qtrsrib(self):
		self.uart.write("QTRSRIB//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsrib={
				"interval_b": res & 0xffff
			}	
		return trsrib

	#transmission hours roam net
	def qtrsrmt(self):
		self.uart.write("QTRSRMT//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=res[7:-2]
			trsrmt={
				'tr_hour1': res[:2].decode() +":"+res[2:4].decode(),
				'tr_hour2': res[6:8].decode() +":"+res[8:10].decode(),
				'tr_hour3': res[12:14].decode() +":"+res[14:16].decode(),
				'tr_hour4': res[18:20].decode() +":"+res[20:22].decode(),
				'tr_hour5': res[24:26].decode() +":"+res[26:28].decode(),
				'tr_hour6': res[30:32].decode() +":"+res[32:34].decode(),
				'tr_hour7': res[36:38].decode() +":"+res[38:40].decode(),
				'tr_hour8': res[42:44].decode() +":"+res[44:46].decode(),
			}
			for i in range(1, 9):
				key = 'tr_hour' + str(i)
				if trsrmt[key] == "99:99":
					trsrmt[key] = None
		return trsrmt

	#transmission hours local net
	def qtrshmt(self):
		self.uart.write("QTRSHMT//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=res[7:-2]
			trshmt={
				'tr_hour1': res[:2].decode() +":"+res[2:4].decode(),
				'tr_hour2': res[6:8].decode() +":"+res[8:10].decode(),
				'tr_hour3': res[12:14].decode() +":"+res[14:16].decode(),
				'tr_hour4': res[18:20].decode() +":"+res[20:22].decode(),
				'tr_hour5': res[24:26].decode() +":"+res[26:28].decode(),
				'tr_hour6': res[30:32].decode() +":"+res[32:34].decode(),
				'tr_hour7': res[36:38].decode() +":"+res[38:40].decode(),
				'tr_hour8': res[42:44].decode() +":"+res[44:46].decode(),
			}
			for i in range(1, 9):
				key = 'tr_hour' + str(i)
				if trshmt[key] == "99:99":
					trshmt[key] = None
		return trshmt		

	#transmission daily traffic ext sim ln
	def qtrshdl(self):
		self.uart.write("QTRSHDL//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshdl={
				'daily_traffic_limit_extern_sim': (res & 0xffffffff) / 1024
			}
		return trshdl
	#trasnmission daily traffic ext sim roam net
	def qtrsrdl(self):
		self.uart.write("QTRSRDL//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsrdl={
				'daily_traffic_limit_extern_sim': (res & 0xffffffff) / 1024
			}
		return trsrdl	

	#transmission daily traffic int sim ln
	def qtrshdc(self):
		self.uart.write("QTRSHDC//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshdc={
				'daily_traffic_limit_int_sim': (res & 0xffffffff) / 1024
			}
		return trshdc
	#trasnmission daily traffic int sim rn
	def qtrsrdc(self):
		self.uart.write("QTRSRDC//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsrdc={
				'daily_traffic_limit_int_sim': (res & 0xffffffff) / 1024
			}
		return trsrdc

	#transmission month traffic ext sim local network
	def qtrshml(self):
		self.uart.write("QTRSHML//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshml={
				'monthly_traffic_limit_extern_sim': (res & 0xffffffff) / 1048576
			}
		return trshml
	#trasnmission month traffic ext sim roaming network
	def qtrsrml(self):
		self.uart.write("QTRSRML//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsrml={
				'monthly_traffic_limit_extern_sim': (res & 0xffffffff) / 1048576
			}
		return trsrml	


	#transmission month traffic int sim local network
	def qtrshmc(self):
		self.uart.write("QTRSHMC//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshmc={
				'monthly_traffic_limit_int_sim': (res & 0xffffffff) / 1048576
			}
		return trshmc
	#trasnmission month traffic int sim roaming network
	def qtrsrmc(self):
		self.uart.write("QTRSRMC//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsrmc={
				'monthly_traffic_limit_int_sim': (res & 0xffffffff) / 1048576
			}
		return trsrmc		

	#transmission day of mothly traffic reset
	def qtrstdr(self):
		self.uart.write("QTRSTDR//")
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trstdr={
				'day_of_monthly_traffic_reset': (res & 0xff) 
			}
			if trstdr['day_of_monthly_traffic_reset'] >= 31:
				trstdr["day_of_monthly_traffic_reset"] = None
		return trstdr

	#delay transmision in seconds on local network
	def qtrshdt(self):
		self.uart.write("QTRSHDT//")		
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshdt={
				'delay_transmission_seconds' : res
			}
		return trshdt
	#delay transmision in seconds on roam network
	def qtrsrdt(self):
		self.uart.write("QTRSRDT//")		
		time.sleep_ms(100)
		if self.uart.any():	
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trsrdt={
				'delay_transmission_seconds' : res
			}
		return trsrdt

	#transmission at cumulative distance on local network
	def qtrshtd(self):
		self.uart.write("QTRSHTD//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshtd={
				'cumulative_distance_transmission' : res /1000
			}
		return trshtd
	#transmission at cumulative distance on roaming network
	def qtrsrtd(self):
		self.uart.write("QTRSRTD//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			res=int(res[7:-2],16)
			trshtd={
				'cumulative_distance_transmission' : res /1000
			}
		return trshtd

#IO system
	# Volt threshold work-private
	def qdiowpt(self):
		self.uart.write("QDIOWPT//")
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			result_int = int(res[7:-2],16)
			print(result_int)
			result_int = result_int & 0xffff
			print(result_int)
			f = result_int * 7.08722 / 1000
			diowpt={
				'voltage_threshold': (int(f) + round((f - int(f)) * 10) / 10)
			}
		return diowpt


#GSM system




#INIT
gps=g4ngps(2,115200)