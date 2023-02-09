import machine, time

class g4ngps:

# 	def __init__(self, port, speed):
		# self.uart = machine.UART(port, speed)


	def __init__(self, port, speed):
		# self.uart = machine.UART(port, speed)
		# self.uart.init(speed, bits=8, parity=None, stop=1)  #for nonspiram
		#	self.uart =machine.UART(speed, bits=8, parity=None, stop=1,tx=32,rx=35)
				# self.uart =machine.UART(port, speed, bits=8, parity=None, stop=1,tx=26,rx=25) #for this we init with gps=g4ngps.g4ngps(1,115200) #board g
				self.uart =machine.UART(port, speed, bits=8, parity=None, stop=1,tx=32,rx=35) #for this we init with gps=g4ngps.g4ngps(1,115200) #board v
		# self.uart =machine.UART(port, speed, bits=8, parity=None, stop=1,tx=32,rx=35) issue this is how we ini for not spi gps=g4ngps(1,115200)
		
		


	def execute_command(self,command):
		self.uart.write(command)
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			return res
		else:
			print("no UART response")

	def qsysinf(self):
		self.uart.write('QSYSINF//')
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read(73)
			sysinf = {
				'rti': res[7:15],
				'hhmmss': res[15:21],
				'ddmmyyyy': res[23:31],
				'syncage': int(res[31:39],16),
				'psn': res[39:47].decode(),
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
				'uptime': int(res[25:33],16),
				'rtcepoch': int(res[33:51],16),
				'rtclastepoch': int(res[41:49],16),
				'rtcdeltaepoch': int(res[49:57],16),
				'rtcdrift': int(res[57:61],16),
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

#auto-complete parameters commands
	def qacivin(self):
		c = "QACIVIN//"
		res = g4ngps.execute_command(self,c)
		acivin={
			'vin': res[7:-2].decode()
		}
		return acivin

	def qacivrn(self):
		c = "QACIVRN//"
		res = g4ngps.execute_command(self,c)
		acivrn={
			'vrn': res[7:-2].decode()
		}
		return acivrn	

	def qacikfa(self):
		c= "QACIKFA//"
		res = g4ngps.execute_command(self,c)
		acikfa={
			'k_factor': int(res[7:-2],16)
		}
		return acikfa

	def qaciepd(self):
		c= "QACIEPD//"
		res = g4ngps.execute_command(self,c)
		aciepd={
			'drift_epoch': int(res[7:-2],16)
		}
		return aciepd

	def qacioeo(self):
		c= "QACIOEO//"
		res = g4ngps.execute_command(self,c)
		acieoe={
			'engine_on_time': int(res[7:-2],16)
		}
		return acieoe

	def qaciote(self):
		c= "QACIOTE//"
		res = g4ngps.execute_command(self,c)
		aciete={
			'engine_on_time': int(res[7:-2],16)
		}
		return aciete	
#end auto-complete parameters

#main system
	def qsyssts(self):
		c= "QSYSSTS//"
		res = g4ngps.execute_command(self,c)
		syssts={
			'speed_threshold': int(res[7:-2],16)
		}
		return syssts

	def qsysstm(self):
		c="QSYSSTM//"
		res = g4ngps.execute_command(self,c)
		sysstm={
			'time_threshold': int(res[7:-2],16)
		}
		return sysstm
	
	def qsysled(self):
			c="QSYSLED//"
			res = g4ngps.execute_command(self,c)
			result_int = int(res[7:-2],16) #hex to int
			sysled={
				'led': res[7:],
				'led_can':(result_int & 0x8000 != 0),
				'led_wp':(result_int & 0x4000 != 0),
				'led_ignition':(result_int & 0x2000 != 0),
				'led_alarm':(result_int & 0x1000 != 0),
				'led_stationary_vehicle':(result_int & 0x0800 != 0),
				'led_ext_serial_traffic':(result_int & 0x0400 !=0),
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
		c="QSYSRSU//"
		res = g4ngps.execute_command(self,c)
		sysrsu={
			'auto_reset_threshold': int(res[7:-2],16)
		}
		return sysrsu

	def qsysset(self):
		c="QSYSSET//"
		res = g4ngps.execute_command(self,c)
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
		c="QSYSFUS//"
		res = g4ngps.execute_command(self,c)
		sysfus={
			'total_fuel_selector_id': int(res[7:-2],16)
		}
		return sysfus

	def qsysosl(self):
		c= "QSYSOSL//"
		time.sleep_ms(100)
		res = g4ngps.execute_command(self,c)
		sysosl={
			'odometer_selector_id': int(res[7:-2],16)
		}
		return sysosl

	def qsysssl(self):
		c= "QSYSSSL//"
		res = g4ngps.execute_command(self,c)
		sysssl={
			'speed_selector_id': int(res[7:-2],16)
		}
		return sysssl

	def qsystts(self):
		c= "QSYSTTS//"
		res = g4ngps.execute_command(self,c)
		systts={
			'ignition_selector_id': int(res[7:-2],16)
		}
		return systts

#work private system
	def qsyssym(self):
		c="QSYSSYM//"
		res = g4ngps.execute_command(self,c)
		result_int = int(res[7:-2],16) #hex to int
		syssym={
			'work_priv_actv': (result_int & 0x8000 == 0),
			'trig_by_IO': (result_int & 0x4000 != 0),
			'trig_by_IO_neg': (result_int & 0x2000 != 0),
			'trig_by_cal': (result_int & 0x1000 != 0),
			'no_acq_priv': (result_int & 0x0800 != 0),
			'no_trans_priv': (result_int & 0x0400 != 0),
			'no_alarms_priv': (result_int & 0x0200 != 0),
			'use_res_days': (result_int & 0x0100 != 0),
			'set_priv_en_relay': (result_int & 0x0080 != 0),
			'set_priv_dis_relay': (result_int & 0x0040 != 0),
			'set_work_en_relay': (result_int & 0x0020 != 0),
			'set_work_dis_relay': (result_int & 0x0010 != 0)
		}
		return syssym

	#work private defined by calendar
	def qsysca0(self):
		private_intervals = {}
		for j in range(7):
			c= "QSYSSCA0" + str(j + 1) + "//"
			self.uart.write(c)
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
		c="QSYSWPD//"
		self.uart.write(c)
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
		c="QSYSWPF//"
		self.uart.write(c)
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
		c= "QSYSPMG//"
		res = g4ngps.execute_command(self,c)
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
		c="QSYSPMG//"
		res = g4ngps.execute_command(self,c)
		result_int = int(res[7:-2],16) #hex to int
		syswku={
			"wakeup_src_en": (result_int & 0x80000000 == 0),
			"wakeup_src_volt_over": (result_int & 0x40000000 != 0),
			"wakeup_src_hr_mtch": (result_int & 0x20000000 != 0),
			"wakeup_src_cal": (result_int & 0x10000000 != 0),
			"wakeup_src_acq": (result_int & 0x08000000 != 0),
			"wakeup_src_tx": (result_int & 0x04000000 != 0),
			"wakeup_src_back_btn": (result_int & 0x02000000 != 0),
			"wakeup_src_mot_sens": (result_int & 0x01000000 != 0),
			"wakeup_src_volt_IO1_over": (result_int & 0x00800000 != 0),
			"wakeup_src_volt_IO2_over": (result_int & 0x00400000 != 0),
			"wakeup_src_volt_IO3_over": (result_int & 0x00200000 != 0),
			"wakeup_src_volt_IO4_over": (result_int & 0x00100000 != 0),
			"wakeup_src_volt_IO1_under": (result_int & 0x00080000 != 0),
			"wakeup_src_volt_IO2_under": (result_int & 0x00040000 != 0),
			"wakeup_src_volt_IO3_under": (result_int & 0x00020000 != 0),
			"wakeup_src_volt_IO4_under": (result_int & 0x00010000 != 0),
			"wakeup_src_ign_on": (result_int & 0x00008000 != 0),
			"wakeup_src_i_btn_present": (result_int & 0x00004000 != 0),
			"wakeup_src_mov_acc_antithft": (result_int & 0x00002000 != 0),
			"wakeup_src_mov_acc_mov": (result_int & 0x00001000 != 0)
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
		c="QSYSPWM//"
		res = g4ngps.execute_command(self,c)
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
			c = "QSYSWKC0" + str(j + 1) + "//"
			self.uart.write(c)
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
		c= "QSYSPMF//"
		res = g4ngps.execute_command(self,c)
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
		c= "QSYSPMY//"
		res = g4ngps.execute_command(self,c)
		syspmy={
			"fp_power_under_volt": (int(res[7:15], 16) & 0x40000000 != 0),
			"fp_at_hours": (int(res[7:15], 16) & 0x20000000 != 0),
			"fp_at_calendar": (int(res[7:15], 16) & 0x10000000 != 0),
			"fp_for_acquisition": (int(res[7:15], 16) & 0x08000000 != 0),
			"fp_for_transmission": (int(res[7:15], 16) & 0x04000000 != 0),
			"fp_motion_sensor": (int(res[7:15], 16) & 0x01000000 != 0),
			"fp_over_voltage_ain1": (int(res[7:15], 16) & 0x00800000 != 0),
			"fp_over_voltage_ain2": (int(res[7:15], 16) & 0x00400000 != 0),
			"fp_over_voltage_ain3": (int(res[7:15], 16) & 0x00200000 != 0),
			"fp_under_voltage_ain1": (int(res[7:15], 16) & 0x00080000 != 0),
			"fp_under_voltage_ain2": (int(res[7:15], 16) & 0x00040000 != 0),
			"fp_under_voltage_ain3": (int(res[7:15], 16) & 0x00020000 != 0),
			"fp_ignition_on": (int(res[7:15], 16) & 0x00008000 != 0),
			"fp_i_button_present": (int(res[7:15], 16) & 0x00004000 != 0),
			"fp_mov_accl_antitheft": (int(res[7:15], 16) & 0x00002000 != 0),
			"fp_mov_accl_mov_detector": (int(res[7:15], 16) & 0x00001000 != 0),
			"fp_din4_pulled_gnd": (int(res[7:15], 16) & 0x00000800 != 0),
			"fp_din5_pulled_gnd": (int(res[7:15], 16) & 0x00000400 != 0),
			"fp_din6_pulled_gnd": (int(res[7:15], 16) & 0x00000200 != 0),
			"sleep_power_under_volt": (int(res[15:-2], 16) & 0x40000000 != 0),
			"sleep_after_period": (int(res[15:-2], 16) & 0x10000000 != 0),
			"sleep_after_ignition_off": (int(res[15:-2], 16) & 0x08000000 != 0)
		}
		return syspmy

	#power management sleep
	def qsyspms(self):
		c= "QSYSPMS//"
		res = g4ngps.execute_command(self,c)
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
		c= "QSYSSLM//"
		res = g4ngps.execute_command(self,c)
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
		c= "QSYSPDL//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res_str=res.decode()
		syspdl={
			'delay_full_power_to_standby': None
		}	
		if(res_str=='FFFF'):
			syspdl['delay_full_power_to_standby']:None
		else:
			syspdl['delay_full_power_to_standby']:int(res,16)	
		return syspdl

	#power management delay full_power to sleep
	def qsyspds(self):
		c="QSYSPDS//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res_str=res.decode()
		syspds={
			'delay_full_power_to_sleep' : None
		}
		if(res_str=='FFFF'):
			syspds['delay_full_power_to_sleep']: None
		else:
			syspds['delay_full_power_to_sleep']: int(res,16)	
		return syspds	

	#power management full power hour parameters
	def qsysppm(self):
		c="QSYSPPM//"
		res = g4ngps.execute_command(self,c)
		res =res[7:-2]
		qsysppm={
			'fp_hour1': res[:2].decode() +":"+res[2:4].decode(),
			'fp_hour2': res[4:6].decode() +":"+res[6:8].decode(),
			'fp_hour3': res[8:10].decode() +":"+res[10:12].decode(),
			'fp_hour4': res[12:14].decode() +":"+res[14:16].decode(),
			'fp_hour5': res[16:18].decode() +":"+res[18:20].decode(),
			'fp_hour6': res[20:22].decode() +":"+res[22:24].decode(),
			'fp_hour7': res[24:26].decode() +":"+res[26:28].decode(),
			'fp_hour8': res[28:30].decode() +":"+res[30:32].decode(),
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
		c="QSYSPWK//"
		res = g4ngps.execute_command(self,c)
		res =res[7:-2]
		syspwk = {
			'prewakeup_interval':int(res,16)
		}
		return syspwk

	#power management stand by transition period
	def qsyssls(self):
		c="QSYSSLS//"
		res = g4ngps.execute_command(self,c)	
		res =res[7:-2]
		syssls = {
			'stand_by_trasition_period':int(res,16)
		}
		return syssls	

	#power mamangement sleep transition period
	def qsysslc(self):
		c="QSYSSLC//"
		res = g4ngps.execute_command(self,c)
		res =res[7:-2]
		sysslc = {
			'sleep_trasition_period':int(res,16)
		}
		return sysslc

	#power management idle time
	def qsysidt(self):
		c="QSYSIDT//"
		res = g4ngps.execute_command(self,c)
		res =res[7:-2]
		sysslc = {
			'sleep_trasition_period':int(res,16)
		}
		return sysslc	

#Alarm system local network
	def qalmhst(self):
		c="QALMHST//"
		res = g4ngps.execute_command(self,c)
		res =int(res[7:-2],16)
		almhst = {
			"alarm": (res & 0x80000000 == 0),
			"over_speed": (res & 0x40000000 != 0),
			"ign": (res & 0x20000000 != 0),
			"panic_bt": (res & 0x10000000 != 0),
			"relay": (res & 0x08000000 != 0),
			"inp_pwr_uv": (res & 0x04000000 != 0),
			"inp_pwr_ov": (res & 0x02000000 != 0),
			"acc_volt_ut": (res & 0x01000000 != 0),
			"acc_err": (res & 0x00800000 != 0),
			"relay_dc": (res & 0x00400000 != 0),
			"ibtn_dc": (res & 0x00200000 != 0),
			"data_lim": (res & 0x00040000 != 0),
			"dly_traf_ex": (res & 0x00020000 != 0),
			"mthly_traf_ex": (res & 0x00010000 != 0),
			"gps_miss": (res & 0x00008000 != 0),
			"stc_ct_on": (res & 0x00004000 != 0),
			"stc_ct_off": (res & 0x00002000 != 0),
			"spd_ex_ct_ot": (res & 0x00001000 != 0),
			"motion_sen_mv": (res & 0x00000400 != 0),
			"priv_alarm": (res & 0x00000100 != 0),
			"gps_jam": (res & 0x00000040 != 0),
			"gsm_jam": (res & 0x00000020 != 0),
			"accel_antith_alarm": (res & 0x00000008 != 0),
			"dwntime_alarm": (res & 0x00000004 != 0)
		}
		return almhst

#Alarm system roaming network
	def qalmrst(self):
		c="QALMRST//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		almrst = {
			"alarm": (res & 0x80000000 == 0),
			"over_speed": (res & 0x40000000 != 0),
			"ign": (res & 0x20000000 != 0),
			"panic_bt": (res & 0x10000000 != 0),
			"relay": (res & 0x08000000 != 0),
			"inp_pwr_uv": (res & 0x04000000 != 0),
			"inp_pwr_ov": (res & 0x02000000 != 0),
			"acc_volt_ut": (res & 0x01000000 != 0),
			"acc_err": (res & 0x00800000 != 0),
			"relay_dc": (res & 0x00400000 != 0),
			"ibtn_dc": (res & 0x00200000 != 0),
			"data_lim": (res & 0x00040000 != 0),
			"dly_traf_ex": (res & 0x00020000 != 0),
			"mthly_traf_ex": (res & 0x00010000 != 0),
			"gps_miss": (res & 0x00008000 != 0),
			"stc_ct_on": (res & 0x00004000 != 0),
			"stc_ct_off": (res & 0x00002000 != 0),
			"spd_ex_ct_ot": (res & 0x00001000 != 0),
			"motion_sen_mv": (res & 0x00000400 != 0),
			"priv_alarm": (res & 0x00000100 != 0),
			"gps_jam": (res & 0x00000040 != 0),
			"gsm_jam": (res & 0x00000020 != 0),
			"accel_antith_alarm": (res & 0x00000008 != 0),
			"dwntime_alarm": (res & 0x00000004 != 0)
		}
		return almrst	

#Alarm system overspeed speed threashold
	def qalmovs(self):
		c="QALMOVS//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almovs={
			'overspeed_threshold':(res  & 0xffff) / 10
		}
		return almovs

	#Alarm system movement treshold
	def qalmovs(self):
		c="QALMMOV//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almmov={
			'movement_threshold':(res  & 0xffff) / 10
		}
		return almmov

	#Alarm system stationary timer contact on
	def qalmstn(self):
		c="QALMSTN//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almstn={
			'stationary_timer_contact_on':(res  & 0xffff)
		}
		return almstn

	#Alarm system stationary timer contact on
	def qalmstf(self):
		sc="QALMSTF//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almstf={
			'stationary_timer_contact_off':(res  & 0xffff)
		}
		return almstf

	#Alarm system speed threshold contact on
	def qalmssn(self):
		c="QALMSSN//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almssn={
			'speed_threshold_contact_on':(res  & 0xffff) / 10
		}
		return almssn	

	#Alarm system speed threshold contact off
	def qalmssf(self):
		c="QALMSSF//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almssf={
			'speed_threshold_contact_off':(res  & 0xffff) / 10
		}
		return almssf		

	#Alarm system  missing gps treshold
	def qalmgmt(self):
		c="QALMGMT//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almgmt={
			'gps_missing_threshold':(res  & 0xffff)
		}
		return almgmt

	#Alarm system down time timer
	def qalmdta(self):
		c="QALMDTA//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almdta={
			'down_time_timer':(res  & 0xffff)
		}
		return almdta


 	#Alarm system data flash limit
	def qalmdfl(self):
		c="QALMDFL//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almdfl={
			'data_flash_limit':(res  & 0xffff)
		}
		return almdfl

	#Alarm system delay accelerometer movement threhold
	def qalmatd(self):
		c="QALMDFL//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		almatd={
			'delay_acc_movement':(res  & 0xffff)
		}
		return almatd

#Transmission system
	#transmission on local network
	def qtrshst(self):
		c="QTRSHST//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshst={
			"tr": (res & 0x80000000 == 0),
			"tr_int_a": (res & 0x40000000 != 0),
			"tr_int_a_cont_on": (res & 0x20000000 != 0),
			"tr_int_a_cont_off": (res & 0x10000000 != 0),
			"tr_int_a_alarms": (res & 0x08000000 != 0),
			"tr_int_b": (res & 0x04000000 != 0),
			"tr_int_b_cont_on": (res & 0x02000000 != 0),
			"tr_int_b_cont_off": (res & 0x01000000 != 0),
			"tr_int_b_alarms": (res & 0x00800000 != 0),
			"tr_alarm": (res & 0x00400000 != 0),
			"tr_data": (res & 0x00200000 != 0),
			"tr_contact": (res & 0x00100000 != 0),
			"tr_hr_match": (res & 0x00080000 != 0),
			"tr_i_button": (res & 0x00040000 != 0),
			"tr_daily_ex": (res & 0x00020000 != 0),
			"tr_monthly_ex": (res & 0x00010000 != 0),
			"tr_gps": (res & 0x00008000 != 0),
			"tr_pwr_on": (res & 0x00004000 != 0),
			"tr_delay": (res & 0x00002000 != 0),
			"tr_clear": (res & 0x00001000 != 0),
			"tr_work_priv": (res & 0x00000800 != 0),
			"tr_ep_int_a_cont_on": (res & 0x00000400 != 0),
			"tr_ep_int_a_cont_off": (res & 0x00000200 != 0),
			"tr_ep_int_b_cont_on": (res & 0x00000100 != 0),
			"tr_ep_int_b_cont_off": (res & 0x00000080 != 0),
			"tr_ep_enabled": (
				(res & 0x00000400) != 0 or (res & 0x00000200) != 0 or
				(res & 0x00000100) != 0 or (res & 0x00000080) != 0),
			"tr_cumulative_dist": (res & 0x00000040 != 0),
			"tr_allow_gen_acq": (res & 0x00000020 != 0),
			"tr_rtc": (res & 0x00000010)
			}
		return trshst

	#transmission on roaming network
	def qtrsrst(self):
		c = "QTRSRST//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshst={
			"tr": (res & 0x80000000 == 0),
			"tr_int_a": (res & 0x40000000 != 0),
			"tr_int_a_cont_on": (res & 0x20000000 != 0),
			"tr_int_a_cont_off": (res & 0x10000000 != 0),
			"tr_int_a_alarms": (res & 0x08000000 != 0),
			"tr_int_b": (res & 0x04000000 != 0),
			"tr_int_b_cont_on": (res & 0x02000000 != 0),
			"tr_int_b_cont_off": (res & 0x01000000 != 0),
			"tr_int_b_alarms": (res & 0x00800000 != 0),
			"tr_alarm": (res & 0x00400000 != 0),
			"tr_data": (res & 0x00200000 != 0),
			"tr_contact": (res & 0x00100000 != 0),
			"tr_hr_match": (res & 0x00080000 != 0),
			"tr_i_button": (res & 0x00040000 != 0),
			"tr_daily_ex": (res & 0x00020000 != 0),
			"tr_monthly_ex": (res & 0x00010000 != 0),
			"tr_gps": (res & 0x00008000 != 0),
			"tr_pwr_on": (res & 0x00004000 != 0),
			"tr_delay": (res & 0x00002000 != 0),
			"tr_clear": (res & 0x00001000 != 0),
			"tr_work_priv": (res & 0x00000800 != 0),
			"tr_ep_int_a_cont_on": (res & 0x00000400 != 0),
			"tr_ep_int_a_cont_off": (res & 0x00000200 != 0),
			"tr_ep_int_b_cont_on": (res & 0x00000100 != 0),
			"tr_ep_int_b_cont_off": (res & 0x00000080 != 0),
			"tr_ep_enabled": (
				(res & 0x00000400) != 0 or (res & 0x00000200) != 0 or
				(res & 0x00000100) != 0 or (res & 0x00000080) != 0),
			"tr_cumulative_dist": (res & 0x00000040 != 0),
			"tr_allow_gen_acq": (res & 0x00000020 != 0),
			"tr_rtc": (res & 0x00000010)
			}
		return trsrst

	#transmission threshold accumulated data for local network
	def qtrshad(self):
		c= "QTRSHAD//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshad={
			"threshold_accumulated_data": ((res & 0xffff) /1024)
		}
		return trshad	

	#transmission threshold accumulated data for roaming network
	def qtrsrad(self):
		c= "QTRSRAD//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trsrad={
			"threshold_accumulated_data": ((res & 0xffff) /1024)
		}
		return trsrad	

	#transmission interval a local network  
	def qtrshia(self):
		c="QTRSHIA//"
		res = g4ngps.execute_command(self,c)
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
		c="QTRSHIB//"
		time.sleep_ms(100)
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshib={
			"interval_b": res & 0xffff
		}	
		return trshib

	#transmission interval b roaming net
	def qtrsrib(self):
		c="QTRSRIB//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trsrib={
			"interval_b": res & 0xffff
		}	
		return trsrib

	#transmission hours roam net
	def qtrsrmt(self):
		c="QTRSRMT//"
		res = g4ngps.execute_command(self,c)
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
		c="QTRSHMT//"
		res = g4ngps.execute_command(self,c)
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
		c= "QTRSHDL//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshdl={
			'daily_traffic_limit_extern_sim': (res & 0xffffffff) / 1024
		}
		return trshdl
	#trasnmission daily traffic ext sim roam net
	def qtrsrdl(self):
		c= "QTRSRDL//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trsrdl={
			'daily_traffic_limit_extern_sim': (res & 0xffffffff) / 1024
		}
		return trsrdl	

	#transmission daily traffic int sim ln
	def qtrshdc(self):
		c="QTRSHDC//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshdc={
			'daily_traffic_limit_int_sim': (res & 0xffffffff) / 1024
		}
		return trshdc
	#trasnmission daily traffic int sim rn
	def qtrsrdc(self):
		c="QTRSRDC//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trsrdc={
			'daily_traffic_limit_int_sim': (res & 0xffffffff) / 1024
		}
		return trsrdc

	#transmission month traffic ext sim local network
	def qtrshml(self):
		c="QTRSHML//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshml={
			'monthly_traffic_limit_extern_sim': (res & 0xffffffff) / 1048576
		}
		return trshml
	#trasnmission month traffic ext sim roaming network
	def qtrsrml(self):
		c="QTRSRML//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trsrml={
			'monthly_traffic_limit_extern_sim': (res & 0xffffffff) / 1048576
		}
		return trsrml	


	#transmission month traffic int sim local network
	def qtrshmc(self):
		c="QTRSHMC//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshmc={
			'monthly_traffic_limit_int_sim': (res & 0xffffffff) / 1048576
		}
		return trshmc
	#trasnmission month traffic int sim roaming network
	def qtrsrmc(self):
		c="QTRSRMC//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trsrmc={
			'monthly_traffic_limit_int_sim': (res & 0xffffffff) / 1048576
		}
		return trsrmc		

	#transmission day of mothly traffic reset
	def qtrstdr(self):
		c="QTRSTDR//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trstdr={
			'day_of_monthly_traffic_reset': (res & 0xff) 
		}
		if trstdr['day_of_monthly_traf_reset'] >= 31:
			trstdr["day_of_monthly_traf_reset"] = None
		return trstdr

	#delay transmision in seconds on local network
	def qtrshdt(self):
		c="QTRSHDT//"	
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshdt={
			'd_trans_sec' : res
		}
		return trshdt
	#delay transmision in seconds on roam network
	def qtrsrdt(self):
		c="QTRSRDT//"	
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trsrdt={
			'd_trans_sec' : res
		}
		return trsrdt

	#transmission at cumulative distance on local network
	def qtrshtd(self):
		c="QTRSHTD//"
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshtd={
			'c_dist_transn' : res /1000
		}
		return trshtd
	#transmission at cumulative distance on roaming network
	def qtrsrtd(self):
		c="QTRSRTD//"
		time.sleep_ms(100)
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		trshtd={
			'c_dist_trans' : res /1000
		}
		return trshtd

#GSM &GPRS system
	#gsm version
	def qgsmfrm(self):
		c='QGSMFRM//'
		res = g4ngps.execute_command(self,c)
		res=res[7:-2]
		gsmfrm={
			'gsm_version':res.decode()
		}
		return gsmfrm	
	#gsm vim - master incoming voice call actions
	def qgsmvim(self):
		c='QGSMVIM//'
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		gsmvim = {}
		if res == 0:
			gsmvim['m_vca'] :"disable"
		elif res == 1:
			gsmvim['m_vca'] : "trig_pre_command"
		elif res == 3:
			gsmvim['m_vca'] : "trig_req_transmission"
		elif res == 4:
			gsmvim['m_vca'] : "voice_answer"
		elif res == 5:
			gsmvim['m_vca'] : "shutdown_gsm"
		elif res == 6:
			gsmvim['m_vca'] : "restart"
		elif res == 7:
			gsmvim['m_vca'] : "enable_relay"
		elif res == 8:
			gsmvim['m_vca'] : "disable_relay"

		return gsmvim
	#gsm viu - user incoming voice call actions
	def qgsmviu(self):
			c='QGSMVIU//'
			res = g4ngps.execute_command(self,c)
			res=int(res[7:-2],16)
			gsmviu = {}
			if res == 0:
				gsmviu['u_vca'] : "disable"
			elif res == 1:
				gsmviu['u_vca'] : "trig_pre_command"
			elif res == 3:
				gsmviu['u_vca'] : "trig_req_transmission"
			elif res == 4:
				gsmviu['u_vca'] : "voice_answer"
			elif res == 5:
				gsmviu['u_vca'] : "shutdown_gsm"
			elif res == 6:
				gsmviu['u_vca'] : "restart"
			elif res == 7:
				gsmviu['u_vca'] : "enable_relay"
			elif res == 8:
				gsmviu['u_vca'] : "disable_relay"
			return gsmviu


	#gsm vin unathentificated user call actions
	def qgsmvin(self):
		c='QGSMVIN//'
		res = g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		gsmvin={
		['u_auth_vca']: None
		}		
		if res == 0:
			gsmvin['u_auth_vca'] : "disable"
		elif res == 1:
			gsmvin['u_auth_vca'] : "trig_pre_command"
		elif res == 3:
			gsmvin['u_auth_vca'] : "trig_req_transmission"
		elif res == 4:
			gsmvin['u_auth_vca'] : "voice_answer"
		elif res == 5:
			gsmvin['u_auth_vca'] : "shutdown_gsm"
		elif res == 6:
			gsmvin['u_auth_vca'] : "restart"
		elif res == 7:
			gsmvin['u_auth_vca'] : "enable_relay"
		elif res == 8:
			gsmvin['u_auth_vca'] : "disable_relay"
		return gsmvin

	def qgsmpdf(self):
		c = "QGSMPDF//"
		result = g4ngps.execute_command(self,c)
		result = result[7:-2]

		gsm = {}
	

		gsm["predefined_command"] = "" if result == "" else result + "//"
		
		res = g4ngps.qsysinf(self)
		psn = res.get('psn')

		if "bd" == psn:
			c = "QGPRDMD//"
			result = g4ngps.execute_command(self,c)
			result = result[7:-2]
			result_int = int(result[:2], 16)
			if result_int == 0x00:
				gsm["gsm_type"] : "automatic"
			elif result_int == 0x20:
				gsm["gsm_type"] : "gsm"
			elif result_int == 0x40:
				gsm["gsm_type"] : "lte"
			elif result_int == 0x60:
				gsm["gsm_type"] : "gsmlte"
			else:
				gsm["gsm_type"] : "automatic"
				
			result_int = int(result[2:4], 16)
			if result_int == 0x00:
				gsm["lte_mode"] : 'catm'
			elif result_int == 0x40:
				gsm["lte_mode"] : 'nbiot'
			elif result_int == 0x80:
				gsm["lte_mode"] : "catmnbiot"
			else:
				gsm["lte_mode"] : "catm"
		else:
			c = "QGPRSIM//"
			res = g4ngps.execute_command(self,c)

			# lic_ch = res[7:-2].decode()
			if "lic" in lic_ch:
				gsm["dual_sim_licensed"] = False
				# return gsm
			else:
				res_int = int(res[7:-2], 16)
				if res_int == 0x00:
					gsm["sim_selector"]:"ext_sim_only"
				elif res_int == 0x20:
					gsm["sim_selector"]:"intern_sim_only"
				elif res_int == 0x40:
					gsm["sim_selector"]:"intern_sim_ext_not_detected"
				elif res_int == 0x60:
					gsm["sim_selector"]:"intern_sim_ext_fails"
				elif result_int == 0x80:
					gsm["sim_selector"]:"ext_sim_home_intern_roaming"
				
					if res_int == 0x60:
						c = "QGPRCTH//"
						result = g4ngps.execute_command(self,c)
						result = result[7:-2]
						gsm["external_sim_timeout"] = int(result, 16)

						c = "QGPRIST//"
						result = g4ngps.execute_command(self,c)
						result = result[7:-2]
						gsm["intern_sim_timeout"] = int(result, 16)	
		return gsm	

	def qgprsim(self):
		c = "QGPRSIM//"
		res = g4ngps.execute_command(self,c)

		lic_ch = res[7:-2].decode()
		gprsim={}
		if "lic" in lic_ch:
			gprsim["dual_sim_licensed"] = False
			# return gprsim
		else:
			res_int = int(res[7:-2], 16)
			if res_int == 0x00:
				gprsim["sim_selector"]:"ext_sim_only"
			elif res_int == 0x20:
				gprsim["sim_selector"]:"intern_sim_only"
			elif res_int == 0x40:
				gprsim["sim_selector"]:"intern_sim_ext_not_detected"
			elif res_int == 0x60:
				gprsim["sim_selector"]:"intern_sim_ext_fails"
			elif res_int == 0x80:
				gprsim["sim_selector"]:"ext_sim_home_intern_roaming"
			
				if res_int == 0x60:
					c = "QGPRCTH//"
					result = g4ngps.execute_command(self,c)
					result = result[7:-2]
					gprsim["external_sim_timeout"] : int(result, 16)

					c = "QGPRIST//"
					result = g4ngps.execute_command(self,c)
					result = result[7:-2]
					gprsim["intern_sim_timeout"] : int(result, 16)	
		return gprsim	
	#read apn info
	def qgprmct(self):
		c="QGPRMCT//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],6)
		res_apn = 0x3000 & res
		qgprmct={
			'apn': None
		}
		if res_apn == 0x0000:
			qgprmct["apn"]: "Main"
		if res_apn == 0x1000:
			qgprmct["apn"]: "List"
		if res_apn == 0x2000: 
			res_apn["apn"]:	"Secondary"	
		return qgprmct
	#read main apn
	def	qgprgma(self):
		c="QGPRGMA//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2].decode()
		gprgma={
			"apn" : res	
		}	
		return gprgma
	#read  main username
	def qgprgmu(self):
		c="QGPRGMU//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2].decode()
		gprgmu={
			"apn_user" : res	
		}
		return gprgmu	
	#read main pass
	def qgprgmp(self):
		c="QGPRGMP//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2].decode()
		gprgmp={
			"apn_pass" : res	
		}
		return gprgmp
	#read secondary user
	def qgprgsu(self):
		c="QGPRGSU//"
		res = g4ngps.execute_command(self,c)
		return res
	
	#def read remote peer type
	def qgprgrs(self):
		c="QGPRGRS//"
		res = g4ngps.execute_command(self,c)
		res= res[7:-2].decode()
		remote_peer={
			'remote_peer': res
		}
		return remote_peer
	
	#def read remote port 
	def qgprgrp(self):
		c="QGPRGRP//"
		res = g4ngps.execute_command(self,c)
		res= res[7:-2].decode()
		remote_port={
			'remote_port': res
		}
		return remote_port
	
	#def read upgrade peer
	def qgprgus(self):
		c="QGPRGUS//"
		res = g4ngps.execute_command(self,c)
		res= res[7:-2].decode()
		gprgus={
			'update_peer': res
		}
		return gprgus
	#def read upgrade port
	def qgprgup(self):
		c="QGPRGUP//"
		res = g4ngps.execute_command(self,c)
		res= res[7:-2].decode()
		gprgup={
			'update_port': res
		}
		return gprgup
	
	#read backup peer
	def qgprgbs(self):
		c="QGPRGBS//"
		res = g4ngps.execute_command(self,c)
		res= res[7:-2].decode()
		gprgbs={
			'backup_peer': res
		}
		return gprgbs
	
		#read backup port
	def qgprgbp(self):
		c="QGPRGBS//"
		res = g4ngps.execute_command(self,c)
		res= res[7:-2].decode()
		gprgbp={
			'backup_port': res
		}
		return gprgbp


	def qgprist(self):
		c = "QGPRIST//"
		result = g4ngps.execute_command(self,c)
		result = result[7:-2].decode()
		gprist={
		"intern_sim_timeout" : int(result, 16)
		}
		return gprist	

	def qgprcth(self):
		c = "QGPRCTH//"
		result = g4ngps.execute_command(self,c)
		result = result[7:-2].decode()
		gprcth={
		"external_sim_timeout" : int(result, 16)
		}
		return gprcth

#GPS
	def qgpsset(self):
		c="QGPSSET//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		gpsset = {
			"sbas_enabled": (res & 0x4000 != 0),
			"gps_updates": (res & 0x2000 != 0),
			"data_filter": (res & 0x1000 == 0),
			"inv_pos": (res & 0x0800 == 0),
			"inv_pos_acc": (res & 0x0400 == 0),
			"inv_pos_priv_mode": (res & 0x0200 != 0)
		}
		return gpsset
		
	#gps number of satelites
	def qgpsefn(self):
		c="QGPSEFN//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		gpsefn={
			"no_sat": res
		}
		return gpsefn

	#gps pdop
	def qgpsefp(self):
		c="QGPSEFP//"
		res=g4ngps.execute_command(self,c) 
		res=res[7:-2]
		pdop1=res[0:2]
		pdop2=res[2:]
		gpsefp={}
		if pdop2 == 0:
			gpsefp["pdop"]:pdop1
		else:
			gpsefp["pdop"]:pdop1+0.1*pdop2
		return gpsefp		

	#gps speed	
	def gpsefs(self):
		c="QGPSEFS//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		gpsefs={
			"gps_speed":res	
		}	
		return gpsefs

	def qgpsact(self):
		c="QGPSACT//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		gpsact={
			"gps_accel_thresh":res	
		}
		return gpsact

	def qgpsdis(self):
		c="QGPSDIS//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		gpsdis={
			"gps_odo":res
		}	
		return gpsdis

#DLF 
	#read device memory info
	def qdiowpt(self):
		c="QDLFINF//"
		res = g4ngps.execute_command(self,c)
		dlfinf={
			'dlf_records':int(res[7:13],16),
			'dlf_total_records':int(res[13:19],16)
		}
		return dlfinf


#IO system
	# Volt threshold work-private
	def qdiowpt(self):
		c="QDIOWPT//"
		res = g4ngps.execute_command(self,c)
		result_int = int(res[7:-2],16)
		result_int = result_int & 0xffff
		f = result_int * 7.08722 / 1000
		diowpt={
			'voltage_threshold': (int(f) + round((f - int(f)) * 10) / 10)
		}
		return diowpt
	# read accelerometer
	def qdioacp(self):
		c="QDIOACP//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		res1=int(res[0:8],16) 
		res2=int(res[8:16],16)
		qdioacp={
			'enabled':(res1 & 0x80000000 == 0),
            'antitheft_enabled':(res1 & 0x40000000 != 0),
            'motionde_tection':(res1 & 0x20000000 != 0),
            'activate_relay_alarm':(res1 & 0x00800000 != 0),
            'deactivate_relay_alarm':(res1 & 0x00400000 != 0),
            'activate_relay_movement':(res1 & 0x00200000 != 0),
            'deactivate_relay_movement':(res1 & 0x00100000 != 0),
            'arm_ignition_off':(res1 & 0x00008000 != 0),
            'disarm_ignition_on':(res2 & 0x80000000 != 0),
            'disarm_ibutton':(res2 & 0x40000000 != 0),
		}
		return qdioacp



	#arming delay conditions	
	def qdioard(self):
		c="QDIOARD//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		qdioard={
			"arming_delay":res*0.1 
		}
		return qdioard
	#movement lower treshold
	def qdioarh(self):
		c="QDIOARH//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		qdioarh={
			'mov_low_thresh': res
		}
		return qdioarh
	#delay movement lower threshold	
	def qdioart(self):
		c="QDIOART//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		qdioart={
			"arming_delay_mov_low":res*0.1 
		}
		return qdioart
	#movement greater treshold
	def qdioadt(self):
		c="QDIOADT//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		qdioadt={
			"mov_great_thresh":res
		}
		return qdioadt
	#number of acceleration events threshold
	def qdiomdh(self):
		c="QDIOMDH//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		qdiomdh={
			'accel_events_thresh':res
		}
		return qdiomdh
	#event threshold
	def qdiomdh(self):
		c="QDIOMDT//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		qdiomdt={
			'event_thresh':res
		}
		return qdiomdt
	#acceleration decrese rate
	def qdiomdh(self):
		c="QDIOMDR//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		qdiomdr={
			'event_decrese_rate':res
		}
		return qdiomdr
	#time motion detection threshold
	def qdiomdo(self):
		c="QDIOMDO//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		qdiomdo={
			'time_motion_det_thresh':res*0.1
		}
		return qdiomdo
	#dio inf
	def qdioinf(self):
		c="QDIOINF//"	
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioinf={
			"io_contact": res[71:79],
			"io_panic": res[79:87],
			"io_relay": res[87:95],
			"io_status": res[163:165],
			"io_status2": res[165:167],
			"ain1": res[167:171],
			"ain2": res[171:175],
			"ain3": res[175:179],
			"power_in_voltage": res[191:195],
			"temperature": res[199:203]
		}
		return qdioinf
	#DIOAI read device config
	def qdioai1(self):	
		c="QDIOAI1//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai1={
			'IO1':g4ngps.setEntity(self,res)
		}
		return qdioai1
	

	def qdioai2(self):	
		c="QDIOAI2//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai2={
			'IO2':g4ngps.setEntity(self,res)
		}
		return qdioai2
	
	def qdioai3(self):	
		c="QDIOAI13//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai3={
			'IO3':g4ngps.setEntity(self,res)
		}
		return qdioai3
	
	def qdioai4(self):	
		c="QDIOAI4//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai4={
			'IO4':g4ngps.setEntity(self,res)
		}
		return qdioai4
	
	def qdioai5(self):	
		c="QDIOAI5//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai5={
			'IO5':g4ngps.setEntity(self,res)
		}
		return qdioai5
	
	def qdioai6(self):
		c="QDIOAI6//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai6={
			'IO6':g4ngps.setEntity(self,res)
		}
		return qdioai6

	def qdioai7(self):
		c="QDIOAI7//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai7={
			'IO7':g4ngps.setEntity(self,res)
		}
		return qdioai7


	def qdioai8(self):
		c="QDIOAI8//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai8={
			'IO8':g4ngps.setEntity(self,res)
		}
		return qdioai8
	
	def qdioai9(self):
		c="QDIOAI9//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioai9={
			'IO9':g4ngps.setEntity(self,res)
		}
		return qdioai9
	
	def qdioaia(self):
		c="QDIOAIA//"
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		qdioaia={
			'IOA':g4ngps.setEntity(self,res)
		}
		return qdioaia

	def setEntity(self,data):
		data=data[0:2].decode()
		if data == "01":
			return "CONTACT"
		elif data == "02":
			return "PANIC BUTTON"
		elif data == "03":
			return "WORK PRIVATE DETECTOR"
		elif data == "04":
			return "RELAY"
		elif data == "05":
			return "EVENT COUNTER1"
		elif data == "06":
			return "EVENT COUNTER2"
		elif data == "07":
			return "STATE COUNTER1"
		elif data == "08":
			return "state couter2"
		elif data == "09":
			return "event generator1"
		elif data == "0A":
			return "event generator2"
		elif data == "0B":
			return "event ibuttonA"
		elif data == "0D":
			return "MotionSensor"
		elif data == "10":
			return "ACCELEROMETERSIREN"
		elif data == "11":
			return "KLINEINTERFACE"
		elif data == "12":
			return "KLINEFUELSENSOR"
		elif data =="13":
			return "ARMINGPOSITIVEACCELEROMETER"
		elif data == "14":
			return "ARMINGNEGATIVEACCELEROMETER"
		elif data == "15":
			return "DISARMINGPOSITIVEACCELEROMETER"
		elif data =="16":
			return "DISARMINGNEGATIVEACCELEROMETER"
		elif data =="17":
			return "IBUTTONB"
		elif data =="18":
			return "BUZZERSIREN"
		elif data =="19":
			return "LATCHINGRELAYCOILA"
		elif data =="1A":
			return "LATCHINGRELAYCOILB"
		elif data == "1B":
			return "TACHO_SIEMENS_DTO1381"
		elif data =="1C":
			return "TACHO_SIEMENS_MTCO1324"
		elif data == "1D":
			return "TACHO_STONERIDGE_SE5000"
		elif data == "1E":
			return "TACHO_STONERIDGE_2400_4800"
		elif data =="1F":
			return "TACHO_ACTIA_L2000"
		elif data == "20":
			return "WORKPRIVATELED"
	#dioEntities
	#read ignition io entity
	def qdiopco(self):
		c = "QDIOPCO//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res = res[0:4]
		ig={}
		if res:
			result_int = int(res, 16)
			ig["enabled"] = (result_int & 0x8000) == 0
			ig["io"] = "todo"
			ig["sog_derived"] = (result_int & 0x4000) != 0
			ig["motion_sensor_derived"] = (result_int & 0x2000) != 0
			ig["accelerometer_movement"] = (result_int & 0x0800) != 0
			ig["polarity"] = (result_int & 0x0400) != 0

		c = "QDIOPCT//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		if res:
			result_int = int(res, 16)
			result_int = result_int & 0xffff
			f = result_int * 7.08722 / 1000
			f = int(f) + round((f - int(f)) * 10) / 10
			ig["threshold"] = f

		c = "QDIOCSS//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		ig["speed_threshold"] = int(res)

		c = "QDIOCST//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		result_int = int(res, 16)
		ig["time_threshold"] = result_int & 0xffff

		c = "QDIOPCF//"
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		i = int(res, 16)
		f = float(i)
		ig["filter_threshold"] = f

		return ig
	#read panic button io entity
	def qdiopal(self):
		resInt = 0
		resLong = 0

		c = "QDIOPAL//"

		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		resLong = int(res, 16)

		pb = {}
		pb['io'] = "todo"
		pb['polarity'] = (resLong & 0x20000000) != 0
		pb['monostable'] = (resLong & 0x10000000) != 0
		pb['disableRelay'] = (resLong & 0x00800000) != 0
		pb['stateIgnition'] = (resLong & 0x08000000) != 0
		pb['panicTimeFilter'] = (resLong & 0x02000000) != 0

		c = "QDIOPAT//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		resInt = int(res, 16)
		resInt = resInt & 0xffff
		f = resInt * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		pb['threshold'] = f

		c = "QDIOPDR//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		resInt = int(res, 16)

		pb['duration'] = resInt & 0xffff

		c = "QDIOPAF//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		resInt = int(res, 16)

		pb['thresholdTimeFilter'] = resInt & 0xffff

		return pb
	#read relay io entity
	def qdioprt(self):
		c="QDIOPRT//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		rl={}
		rl['enabled'] = res & 0x80000000 == 0
		rl['io'] =res #get IO entity
		rl['polarity'] =res & 0x20000000 != 0
		rl['mono'] =res & 0x10000000 != 0
		rl['act_contact_off'] =res & 0x08000000 != 0
		rl['inact_contact_off'] =res & 0x02000000 != 0
		rl['act_contact_on'] =res & 0x04000000 != 0
		rl['inact_contact_on'] =res & 0x01000000 != 0
		c="QDIOPRP//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)

		C="QDIOPRP//"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		res=res & 0xffff
		if res == 65535:
			rl['relayPulse'] = None
		else:
			rl['relayPulse'] = res
		return rl
	#ibu io entity
	def qibuast(self):
		c="QIBUAST//"

		res = g4ngps.execute_command(self,c)
		res = int (res[7:-2],16)
		ibutton = {}
		ibutton["io"] = None #get_io_of_entity(ENTITY45.IBUTTONA)
		ibutton["deac_contact_off"] = (res & 0x20000000) != 0
		ibutton["deac_contact_on"] = (res & 0x10000000) != 0
		ibutton["deac_panic_alarm"] = (res & 0x08000000) != 0
		ibutton["light_on_auth_success"] = (res & 0x04000000) != 0
		ibutton["light_off_auth_failed"] = (res & 0x02000000) != 0
		ibutton["led_on_relay_enabled"] = (res & 0x01000000) != 0
		ibutton["led_off_relay_disabled"] = (res & 0x00800000) != 0
		ibutton["ignition_ok"] = (res & 0x00008000) != 0
		ibutton["ignition_failed"] = (res & 0x00004000) != 0
		ibutton["ignition_ok_timer"] = (res & 0x00002000) != 0
		ibutton["ignition_failed_timer"] = (res & 0x00001000) != 0
		ibutton["ok_reset_enable_relay"] = (res & 0x00000800) != 0
		ibutton["ok_reset_disable_relay"] = (res & 0x00000400) != 0
		ibutton["fail_reset_enable_relay"] = (res & 0x00000200) != 0
		ibutton["fail_reset_disable_relay"] = (res & 0x00000100) != 0
		ibutton["ignition_ok"] = (re & 0x00000080) != 0
		ibutton["ibu_recog"] = (res & 0x00000040) != 0
		ibutton["ibu_not_recog"] = (res & 0x00000020) != 0

		c = "QIBULND//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)

		duration = res & 0xffff
		if duration == 255:
			ibutton["time_light_on_success_auth"] = None
		else:
			ibutton["time_light_on_success_auth"] = duration
		
		c="QIBULFD//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		duration = res & 0xffff
		if duration == 255:
			ibutton["time_light_on_failed_auth"] = None
		else:
			ibutton["time_light_on_failed_auth"] = duration

		c="QIBUAOT//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		ibutton["auth_ok_timer"] =res & 0xffff
		c="QIBUAFT//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		ibutton["auth_fail_timer"] =res & 0xffff

		return ibutton
	
	#read input power
	def qdiovlt(self):
		c="QDIOVLT//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		res = res & 0xffff
		f=	res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		diovolt={}
		diovolt["un_volt_thresh"] = f
		c="QDIOVHT//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		res = res & 0xffff
		f=	res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		diovolt["ov_volt_thresh"] =f
		return diovolt
	#read event counter 1 dio entity
	def qdioeco1(self):
		c="QDIOECO//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res = int(res[0:4],16)

		ev_count1={}
		ev_count1["set_io"] = None #implement this
		ev_count1["edge_trigg"] = res & 0x4000 != 0
		ev_count1["edge_filter"] = res & 0x2000 != 0
		c="QDIOE1F//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		ev_count1["filter_thresh"] = (res & 0xffff) / 100
		c="QDIOE1L//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		res = res & 0xffff
		f= res* 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		ev_count1["level_thresh"] =f

		return ev_count1
	#read event counter 2 dio entity
	def qdioeco2(self):
		c="QDIOECO//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res = int(res[4:8],16)

		ev_count2={}
		ev_count2["set_io"] = None #implement this
		ev_count2["edge_trigg"] = res & 0x4000 != 0
		ev_count2["edge_filter"] = res & 0x2000 != 0
		c="QDIOE2F//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		ev_count2["filter_thresh"] = (res & 0xffff) / 100
		c="QDIOE2L//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		res = res & 0xffff
		f= res* 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		ev_count2["level_thresh"] =f

		return ev_count2
	#read state counter 1 dio entity
	def qdiosco1(self):
		c="QDIOSCO//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res = int(res[0:4],16)
		state_count1={}
		state_count1["set_io"]= None #todo
		state_count1["edge_trigg"] = res & 0x4000 != 0
		c="QDIOS1L//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		res = res & 0xffff
		f= res* 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		state_count1["level_thresh"] =f
	
		return state_count1
	#read state counter2 dio entity
	def qdiosco2(self):
		c="QDIOSCO//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res = int(res[0:4],16)
		state_count2={}
		state_count2["set_io"]= None #todo
		state_count2["edge_trig"] = res & 0x4000 != 0
		c="QDIOS2L//"
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		res = res & 0xffff
		f= res* 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		state_count2["level_thresh"] =f
	
		return state_count2
	#read event generator2
	def qdioego1(self):
		c="QDIOEGO//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res = int(res[0:4],16)
		qev_gen1=[]
		qev_gen1["set_io"]=None
		qev_gen1["edge_trig"]=(res & 0x4000) != 0
		return qev_gen1
	
	def qdioego2(self):
		c="QDIOEGO//"
		res = g4ngps.execute_command(self,c)
		res = res[7:-2]
		res = int(res[4:8],16)
		qev_gen2=[]
		qev_gen2["set_io"]=None
		qev_gen2["edge_trig"]=(res & 0x4000) != 0
		return qev_gen2
	
	def qdiomts(self):
		result_int = 0
		result_long = 0
		ms = {}
	
		commands = ["QDIOMTS//", "QDIOMTT//", "QDIOMIT//", "QDIOMFT//", "QDIOMFC//"]
		results = [g4ngps.execute_command(self,cmd) for cmd in commands]
		results = [res[7:-2] for res in results]
		
		result_long = int(results[0], 16)
		ms['io'] = None #"todo"
		ms['relay'] = (result_long & 0x40000000) != 0
		
		result_int = int(results[1], 16) & 0xffff
		f = result_int * 7.08722 / 1000
		ms['threshold'] = int(f) + round((f - int(f)) * 10) / 10

		result_int = int(results[2], 16) & 0xffff
		ms['idle_timer'] = result_int / 100

		result_int = int(results[3], 16) & 0xffff
		ms['filter_timer'] = result_int / 100

		result_int = int(results[4], 16) & 0xffff
		ms['threshold_filter_counter'] = result_int & 0xffff
	
		return ms

#read buzzer
	def qdiobuz(self):

		buzzer2 = {}
		cmd = ["QALMOVB//", "QIBUNAB//", "QIBUAST//", "QIBAKAB//", "QIBAFAB//"]
		res = [g4ngps.execute_command(self, c)[7:-2] for c in cmd]
		if res[0].upper() == "C1A0":
			buzzer2["activ_over_speed_alm"] = True
		if res[1].upper() == "C3AA" and int(res[2], 16) & int("00000080", 16) != 0:
			buzzer2["activ_ign_on_ibut_notauth"] = True
		if res[3].upper() == "81AA" and int(res[2], 16) & int("00000040", 16) != 0:
			buzzer2["activ_ibut_auth"] = True
		if res[4].upper() == "82F8" and int(res[2], 16) & int("00000020", 16) != 0:
			buzzer2["activ_ibut_notrec"] = True
		else:
			buzzer2["activ_ibut_notrec"] = False

		buzzer2["use_use_int_buz"] = (int(res[2], 16) & 0x4000) != 0
		return buzzer2
#read dvb behavior
	def qdvbset(self):
		command = "QDVBSET//"
		result = g4ngps.execute_command(self,command)
		result = result[7: -2]
		d_b = {}

		result_int = int(result[0:4], 16)
		d_b["enabled"] = (result_int & 0x8000) == 0

		acc_brake_ds = result_int & 0x0070
		d_b["acc_brake_data_source"] = acc_brake_ds == 0 and 1 or None

		analysis_interval = result_int & 0x0007
		d_b["analysis_interval"] = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8}.get(analysis_interval, None)

		result_int = int(result[4:8], 16)
		harsh_cornering = result_int & 0x7000
		d_b["cornering_data_source"] = harsh_cornering == 0 and 1 or None

		commands = [("QDVBIAB//", "interval_ab_speed_threshold"),
					("QDVBIBC//", "interval_bc_speed_threshold"),
					("QDVBICD//", "interval_cd_speed_threshold"),
					("QDVBGAA//", "interval_a_accel_threshold"),
					("QDVBGAB//", "interval_b_accel_threshold"),
					("QDVBGAC//", "interval_c_accel_threshold"),
					("QDVBGAD//", "interval_d_accel_threshold"),
					("QDVBGBA//", "interval_ab_brake_threshold"),
					("QDVBGBB//", "interval_bc_brake_threshold"),
					("QDVBGBC//", "interval_cd_brake_threshold")]

		for cmd, attr in commands:
			result = g4ngps.execute_command(self,cmd)
			result = result[7: -2]
			result_int = int(result, 16)
			value = result_int % 10 >= 5 and (result_int / 10 + 1) or (result_int / 10)
			d_b[attr] = value

		return d_b

	#readtcoinfo
	def qtcoins(self):
		tco = {}
		commands = ["QTCOINS//", "QTCOIVH//", "QTCORTC//"]
		results = [g4ngps.execute_command(self, command) for command in commands]

		result = results[0][7:-2][:2]
		if result:
			result_int = int(result, 16)
			tco["enabled"] = True if (result_int & 0x80) == 0 else False

		result = results[1][7:-2]
		if result and result != "ERR":
			vehicle_settings = result.split(",")
			try:
				tco["VIN"] = vehicle_settings[0]
				tco["VRN"] = vehicle_settings[1].strip()
				tco["KFactor"] = str(int(vehicle_settings[2], 16))
			except Exception:
				pass

		result = results[2][7:-2]
		if result:
			try:
				result_drift_epoch = int(result[:4], 16)
				tco["TCODriftEpoch"] = result_drift_epoch
			except Exception:
				pass

			try:
				result_total_offset = int(result[4:8], 16)
				tco["TCOTotalOffset"] = result_total_offset
			except Exception:
				pass

			try:
				result_tco_panel = int(result[8:16], 16)
				tco["TCOPanelEpoch"] = result_tco_panel

				TCOType = bin(int(result[-4:], 16))[2:]
				tco["TCOType"] = TCOType[8:12]
				ControlBits = TCOType[12:16]

				tco["TcoIgnitionBit0"] = True if ControlBits[0] == "1" else False
				tco["EngineRPMBit1"] = True if ControlBits[1] == "1" else False
				tco["TcoCalibrationErrorBit2"] = True if ControlBits[2] == "1" else False
				tco["TcoTimeErrorBit3"] = True if ControlBits[3] == "1" else False
			except Exception:
				pass

		return tco

	#read Led panel
	def qpaninf(self):
		cmds = ["QPANINF//", "QPANSET//", "QPANOVS//", "QPANHBA//", "QPANGPI//", "QPANSEO//", "QPANFCI//"]
		led = {}
		for cmd in cmds:
			result = g4ngps.execute_command(self, cmd)
			if cmd == "QPANINF//":
				led_number = int(result[31:33][1:2])
				led["total_led"] = led_number
				led_panel_enabled = int(result[7:9], 16)
				led["enabled"] = (bin(led_panel_enabled)[2:].zfill(8)[0] != "1")
			elif cmd == "QPANSET//":
				result_long = int(result[7:-2][:8], 16)
				led["enabled"] = (result_long & 0x80000000) == 0
				led["led_off_when_ignition_off"] = (result_long & 0x40000000) != 0
				led["adaptive_light_intensity"] = (result_long & 0x20000000) != 0
				led["io1_pull_up"] = (result_long & 0x00800000) != 0
				led["io3_pull_down"] = (result_long & 0x00400000) != 0
				led["io2_pull_down"] = (result_long & 0x00200000) != 0
				led["uart_enable"] = (result_long & 0x00100000) != 0
				led["bit3"] = (result_long & 0x0008000) != 0
				led["bit2"] = (result_long & 0x0004000) != 0
				led["bit1"] = (result_long & 0x0002000) != 0
				led["bit0"] = (result_long & 0x0001000) != 0
				led["light_level_threshold2"] = (result_long & 0x0000080) != 0
				led["light_level_threshold1"] = (result_long & 0x00000010) != 0
			else:
				result = int(result[7:-2], 16)
				if result != 0 and result <= led["total_led"]:
					if cmd == "QPANOVS//":
						led["overspeed"] = True
						led["overspeed_number"] = result
					elif cmd == "QPANHBA//":
						led["harsh_breaking"] = True
						led["harsh_breaking_number"] = result
					elif cmd == "QPANGPI//":
						led["gps_indicator"] = True
						led["gps_indicator_number"] = result
					elif cmd == "QPANSEO//":
						led["stationary_engine_on"] = True
						led["stationary_engine_on_number"] = result
					elif cmd == "QPANFCI//":
						led["first_crash_indicator"] = True
						led["first_crash_indicator_number"] = result
		return led

	#read canlog
	def qclgset(self):
		cmd = "QCLGSET//"
		result = g4ngps.execute_command(self,cmd)
		result = result[7:-2]

		canlog={}
		result_int = int(result[:4], 16)
		canlog["can_log.enabled"] = (result_int & 0x8000 == 0)

		cmd = "QCLGPFN//"
		result = g4ngps.execute_command(self,cmd)
		canlog["can_log.profile_name"] = result[7:-2].decode()

		try:
			cmd = "QCLGSCP//"
			result = g4ngps.execute_command(self,cmd)
			if result == "":
				return canlog
			result = result[7:-2]
			if result.decode() != "ERR":
				result = result[6:8] + result[4:6] + result[2:4] + result[0:2]
				canlog["can_log.profile_code"] = int(result, 16)
		except ( IOError) as e:
			#no profile installed
			pass

		return canlog
	#read fuel measurement
	def fuelmeasurement(self):
		fuel_m={}
		fuel_m['qfueset'] = g4ngps.qfueset(self)
		fuel_m['qfuetac'] = g4ngps.qfuetac(self)
		fuel_m['qfuespi'] = g4ngps.qfuespi(self)
		fuel_m['qfuefrt'] = g4ngps.qfuefrt(self)
		fuel_m['qfuefrv'] = g4ngps.qfuefrv(self)
		return fuel_m

	def qfueset(self):
		cmd = "QFUESET//"
		result = g4ngps.execute_command(self, cmd)
		result = result[7:-2]
		result_int = int(result[:4], 16)
		enabled = (result_int & 0x8000) == 0
		return {"enabled": enabled}

	def qfuetac(self):
		cmd = "QFUETAC//"
		result = g4ngps.execute_command(self, cmd)
		result = result[7:-2]
		if result:
			tank_volume = int(result, 16) / 10
			return {"tank_volume": tank_volume}
		return {}

	def qfuespi(self):
		cmd = "QFUESPI//"
		result = g4ngps.execute_command(self, cmd)
		result = result[7:-2]
		if result:
			speed_int_A_limit = int(result[:4], 16) / 10
			speed_int_B_limit = int(result[4:8], 16) / 10
			speed_int_C_limit = int(result[8:12], 16) / 10
			return {
				"speed_int_A_limit": speed_int_A_limit,
				"speed_int_B_limit": speed_int_B_limit,
				"speed_int_C_limit": speed_int_C_limit
			}
		return {}

	def qfuefrt(self):
		cmd = "QFUEFRT//"
		result = g4ngps.execute_command(self, cmd)
		result = result[7:-2]
		if result:
			fuel_rates = {}
			if result[:4].upper().decode() != "FFFF":
				fuel_rates["idle_fuel_rate"] = int(result[:4], 16) / 1820.4
			if result[4:8].upper().decode() != "FFFF":
				fuel_rates["int_A_fuel_rate"] = int(result[4:8], 16) / 65.536
			if result[8:12].upper().decode() != "FFFF":
				fuel_rates["int_B_fuel_rate"] = int(result[8:12], 16) / 65.536
			if result[12:16].upper().decode() != "FFFF":
				fuel_rates["int_C_fuel_rate"] = int(result[12:16], 16) / 65.536
			return fuel_rates
		return fuel_rates

	def qfuefrv(self):
		cmd = "QFUEFRV//"
		result = g4ngps.execute_command(self, cmd)
		result = result[7:-2]
		if result:
			fuel_counters = {}
			if result[:8].upper().decode() != "FFFFFFFF":
				fuel_counters["fuel_counter_total"] = int(result[:8], 16) / 100
		return fuel_counters
#record 10x
	def qacqhgp(self):
		c="QACQHGP//"
		return g4ngps.qacq_rec10_gp(self,c)
	def qacqrgp(self):
		c="QACQRGP//"
		return g4ngps.qacq_rec10_gp(self,c)
	def qacqhti(self):
		c="QACQHTI//"
		return g4ngps.qacq_rec10_ti(self,c)
	def qacqrti(self):
		c="QACQRTI//"
		return g4ngps.qacq_rec10_ti(self,c)
	def qacqhtx(self):
		c="QACQHTX//"
		return g4ngps.qacq_rec10_tx(self,c)
	def qacqrtx(self):
		c="QACQRTX//"
		return g4ngps.qacq_rec10_tx(self,c)
	def qacqhss(self):
		c="QACQHSS//"
		return g4ngps.qacq_rec10_hs(self,c)
	def qacqrss(self):
		c="QACQRSS//"
		return g4ngps.qacq_rec10_hs(self,c)
	def qacqhgi(self):
		c="QACQHGI//"
		return g4ngps.qacq_rec10_gi(self,c)
	def qacqrgi(self):
		c="QACQRGI//"
		return g4ngps.qacq_rec10_gi(self,c)

	#generates the record 10 by calling its relevant methods
	def record10_local_net(self):
		rec10={}
		rec10['qacqhgp'] = g4ngps.qacqhgp(self)
		rec10['qacqhti'] = g4ngps.qacqhti(self)
		rec10['qacqhtx'] = g4ngps.qacqhtx(self)
		rec10['qacqhss'] = g4ngps.qacqhss(self)
		rec10['qacqhgi'] = g4ngps.qacqhgi(self)
		return rec10
	
	def qacq_rec10_gp(self, c):
		res= g4ngps.execute_command(self,c)
		res= int(res[7:-2],16)

		acq_rec10_gp={
			"acq": (res & 0x80000000) == 0,
			"cog_acq": (res & 0x40000000) != 0,
			"cog_acq_cnt_on": (res & 0x20000000) != 0,
			"cog_acq_ovrspd": (res & 0x10000000) != 0,
			"cnt_acq": (res & 0x08000000) != 0,
			"acq_int_a": (res & 0x04000000) != 0,
			"acq_int_a_cnt_on": (res & 0x02000000) != 0,
			"acq_int_a_ovrspd": (res & 0x01000000) != 0,
			"alarm_acq": (res & 0x00800000) != 0,
			"gps_val_acq": (res & 0x00400000) != 0,
			"acq_int_b_cnt_on": (res & 0x00200000) != 0,
			"acq_int_b_cnt_off": (res & 0x00100000) != 0,
			"rec_reset": (res & 0x00080000) != 0,
			"gen_trn_aft_acq": (res & 0x00040000) != 0
		}
		return acq_rec10_gp

	def qacq_rec10_ti(self, c):
		res= g4ngps.execute_command(self,c)
		res= int(res[7:-2],16)
		acq_rec10_ti={
			"acq_cog_min_time": (res & 0xffff) / 10,
		}
		return acq_rec10_ti
	
	def qacq_rec10_tx(self,c):
		res= g4ngps.execute_command(self,c)
		res= int(res[7:-2],16)
		acq_rec10_tx={
			"acq_cog_max_time": (res & 0xffff) / 10,	
		}
		return acq_rec10_tx
	
	def qacq_rec10_hs(self,c):
		res= g4ngps.execute_command(self,c)
		res= int(res[7:-2],16)
		acq_rec10_hs={
			"acq_cog_min_sog": (res & 0xffff) / 10,	
		}
		return acq_rec10_hs

	def qacq_rec10_gi(self,c):
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		acq_rec10_gi={
			"acq_int_A" : (res & 0xffff) /10
		}
		return acq_rec10_gi
	
	def qacq_rec10_gb(self,c):
		res=g4ngps.execute_command(self,c)
		res=res[7:-2]
		acq_rec10_gi={}
		if res[:3].decode == "UNK":
			acq_rec10_gi["acq_int_B"] : False
		else:	
			res=int(res,16)
			acq_rec10_gi["acq_int_B"] : (res & 0xffff) /10
		
		return acq_rec10_gi
	
	def qacqhsp(self):
		c="QACQHSP//"
		return g4ngps.acq_rec11_sp(self,c)
	def qacqrsp(self):
		c="QACQRSP//"
		return g4ngps.acq_rec11_sp(self,c)


	def acq_rec11_sp(self, c):
		res= g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)

		acqhsp={
			"acquisition": (res & 0x80000000) == 0,
			"contact_state": (res & 0x40000000) != 0,
			"preset_interval": (res & 0x20000000) != 0,
			"contact_on": (res & 0x10000000) != 0,
			"alarm_on": (res & 0x08000000) != 0,
			"alarm_changing": (res & 0x04000000) != 0,
			"gen_trans_after_acq": (res & 0x02000000) != 0
		}
		return acqhsp



# #INIT for no spi
# gps=g4ngps(2,115200)
# INIT for wrover nightly build
# gps=g4ngps.g4ngps(1,115200