import machine, time, struct, binascii, gc

class g4ngps:

	def __init__(self, port, speed):
		self.uart = machine.UART(port, speed)
		self.uart.init(speed, bits=8, parity=None, stop=1)

	def execute_command(self,command):
		self.uart.write(command)
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			print(res)
			return res

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
				gsm["lte_mode"] : "catm"
			elif result_int == 0x40:
				gsm["lte_mode"] : "nbiot"
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

	def qgprist(self):
		c = "QGPRIST//"
		result = g4ngps.execute_command(self,c)
		result = result[7:-2]
		gprist={
		"intern_sim_timeout" : int(result, 16)
		}
		return gprist	

	def qgprcth(self):
		c = "QGPRCTH//"
		result = g4ngps.execute_command(self,c)
		result = result[7:-2]
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
			"sbas_enabled": (result & 0x4000 != 0),
			"gps_updates": (result & 0x2000 != 0),
			"data_filter": (result & 0x1000 == 0),
			"inv_pos": (result & 0x0800 == 0),
			"inv_pos_acc": (result & 0x0400 == 0),
			"inv_pos_priv_mode": (result & 0x0200 != 0)
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
		c="QGPSDIS"
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		gpsdis={
			"gps_odo":res
		}	
		return gpsdis



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







#INIT
gps=g4ngps(2,115200)