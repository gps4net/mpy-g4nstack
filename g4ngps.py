import machine, time, re

class g4ngps:

	def __init__(self, port=2, speed=115200, bits=8, parity=None, stop=1, tx=17, rx=16):
		self.uart = machine.UART(port, speed, bits=bits, parity=parity, stop=stop, tx=tx, rx=rx)

	def execute_command(self, command):
		self.uart.write(command)
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
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
				'syncage': int(res[31:39], 16),
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
				'uptime': int(res[25:33], 16),
				'rtcepoch': int(res[33:51], 16),
				'rtclastepoch': int(res[41:49], 16),
				'rtcdeltaepoch': int(res[49:57], 16),
				'rtcdrift': int(res[57:61], 16),
				'rtcstatus': res[61:63],
			}
			return sysrtc

	def setrtc(self):
		rtc = machine.RTC()
		sysrtc = self.qsysrtc()
		# initialize rtc (year, month, day, weekday, hours, minutes, seconds, usec)
		rtc.init(
			tuple([
			int(sysrtc['ddmmyyyy'][4:8]),
			int(sysrtc['ddmmyyyy'][2:4]),
			int(sysrtc['ddmmyyyy'][0:2]),
			int(sysrtc['dow'][0:2]) - 1,
			int(sysrtc['hhmmss'][0:2]),
			int(sysrtc['hhmmss'][2:4]),
			int(sysrtc['hhmmss'][4:6]),
			int(sysrtc['us'][0:2])
			]))

	def qgpsinf(self):
		self.uart.write('QGPSINF//')
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read(91)
			gpsinf = {
				'hhmmss': res[7:13],
				'ddmmyyyy': res[13:21],
				'hour': int(res[7:9]),
				'min': int(res[9:11]),
				'sec': int(res[11:13]),
				'day': int(res[13:15]),
				'mon': int(res[15:17]),
				'year': int(res[17:21]),
				'lat': int(res[21:29]) / 1000000,
				'lon': int(res[29:39]) / 1000000,
				'alt': int(res[39:45]) / 100,
				'navstat': res[45:47],
				'sog': int(res[47:53], 16),
				'cog': int(res[53:59], 16) / 100,
				'gus': int(res[59:61]),
				'pdop': int(res[61:65], 16) / 100,
				'hdop': int(res[65:69], 16) / 100,
				'vdop': int(res[69:73], 16) / 100,
				'gps_dist': int(res[73:81], 16),
				'gps_trp_dist': int(res[81:89], 16)
			}
			inavstat = int(gpsinf['navstat'], 16)
			gpsinf['alt'] *= inavstat & 0x80 >> 7
			gpsinf['lat'] *= inavstat & 0x40 >> 6
			gpsinf['lon'] *= inavstat & 0x20 >> 5
			gpsinf['nst'] = inavstat & 0x10 >> 4
			gpsinf['navst'] = inavstat & 0x0f
			return gpsinf

	# SYS subsystem: main system

	def qsyssts(self):
		res = self.execute_command('QSYSSTS//')
		syssts = { 'spd_th': int(res[7:11], 16) }
		return syssts

	def qsysstm(self):
		res = self.execute_command('QSYSSTM//')
		sysstm = { 'tm_th': int(res[7:11], 16) }
		return sysstm

	def qsysled(self):
		res = self.execute_command('QSYSLED//')
		result_int = int(res[7:11], 16)
		sysled = {
			'led': res[7:-1],
			'led_can': (result_int & 0x8000 != 0),
			'led_wp': (result_int & 0x4000 != 0),
			'led_ign': (result_int & 0x2000 != 0),
			'led_alm': (result_int & 0x1000 != 0),
			'led_staty_veh': (result_int & 0x0800 != 0),
			'led_ext_tfc': (result_int & 0x0400 != 0),
			'led_sim_sel': (result_int & 0x0200 != 0),
			'led_ftp_ind': (result_int & 0x0100 != 0),
			'led_acc_at': (result_int & 0x0080 != 0),
			'led_acc_mov': (result_int & 0x0040 != 0),
			'led_fuel_snsr': (result_int & 0x0020 != 0),
			'led_eng_run': (result_int & 0x0010 != 0),
			'led_ibu_auth': (result_int & 0x0008 != 0),
			'led_data_mode': (result_int & 0x0004 != 0)
		}
		return sysled

	def qsysrsu(self):
		res = self.execute_command('QSYSRSU//')
		sysrsu = { 'auto_rst_th': int(res[7:15], 16) }
		return sysrsu

	def qsysset(self):
		res = self.execute_command('QSYSSET//')
		if res:
			result_int = int(res[7:15], 16)
			## TODO: recheck these flags
			sysset = {
				'ers_upg_req': (result_int & 0x80000000 != 0),
				'trs_sys_chg': (result_int & 0x40000000 == 0),
				'chg_upg_srv': (result_int & 0x20000000 == 0),
				'chg_cnf_srv': (result_int & 0x10000000 != 0)
			}
			return sysset

	# selectors in main system

	def qsysfus(self):
		res = self.execute_command('QSYSFUS//')
		sysfus = { 'tot_fuel_sel': int(res[7:-2], 16) }
		return sysfus

	def qsysosl(self):
		res = self.execute_command('QSYSOSL//')
		sysosl = { 'odo_sel': int(res[7:-2], 16) }
		return sysosl

	def qsysssl(self):
		res = self.execute_command('QSYSSSL//')
		sysssl = { 'spd_sel': int(res[7:-2], 16) }
		return sysssl

	def qsystts(self):
		res = self.execute_command('QSYSTTS//')
		systts = { 'ign_sel': int(res[7:-2], 16) }
		return systts

	# work private
	def qsyssym(self):
		res = self.execute_command('QSYSSYM//')
		result_int = int(res[7:11], 16)
		syssym = {
			'wrk_pvt_actv': (result_int & 0x8000 == 0),
			'trg_io': (result_int & 0x4000 != 0),
			'trg_io_neg': (result_int & 0x2000 != 0),
			'trg_cal': (result_int & 0x1000 != 0),
			'no_acq_pvt': (result_int & 0x0800 != 0),
			'no_trs_pvt': (result_int & 0x0400 != 0),
			'no_alm_pvt': (result_int & 0x0200 != 0),
			'use_res_days': (result_int & 0x0100 != 0),
			'pvt_ena_rly': (result_int & 0x0080 != 0),
			'pvt_dis_rly': (result_int & 0x0040 != 0),
			'wrk_ena_rly': (result_int & 0x0020 != 0),
			'wrk_dis_rly': (result_int & 0x0010 != 0)
		}
		return syssym

	# calendar day 01..07
	def qsyssca(self, id):
		if int(id) < 1 or int(id) > 7:
			return None
		res = self.execute_command('QSYSSCA{:02d}//'.format(id))
		syssca = {
			'day': int(res[7:9]),
			'tm_int': res[9:45],
		}
		return syssca

	# reserved private days
	def qsyswpd(self):
		self.uart.write('QSYSWPD//')
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			res = res[7:-2]
			reserved_days = bytearray(65)
			try:
				for i in range(65):
					if res[i*2:(i + 1)*2].decode() == 'FF':
						break
					reserved_days[i] = int(res[i*2:(i + 1)*2], 16)
					print(reserved_days)
			except Exception as e:
				print('Error: ', e)

	def qsyswpf(self):
		self.uart.write('QSYSWPF//')
		time.sleep_ms(100)
		if self.uart.any():
			res = self.uart.read()
			syswpf = { 'wp_tm_fltr': int(res[7:-2], 16) }
			return syswpf

	# power management swv >= 30
	def qsyspmg(self):
		res = self.execute_command('QSYSPMG//')
		result_int = int(res[7:15], 16)
		syspmg = {
			'pmg_ena': (result_int & 0x80000000 == 0),
			'pmg_leds_off': (result_int & 0x40000000 != 0),
			'pdn_mode_lvl': (result_int & 0x20000000 != 0),
			'pdn_led_ind': (result_int & 0x10000000 != 0),
			'acc_chg_pdn': (result_int & 0x08000000 != 0),
		}
		return syspmg

	# power saving wakeup sources
	def qsyswku(self):
		res = self.execute_command('QSYSWKU//')
		result_int = int(res[7:15], 16)
		syswku = {
			'wku_ena': (result_int & 0x80000000 == 0),
			'wku_ov': (result_int & 0x40000000 != 0),
			'wku_hr_mtch': (result_int & 0x20000000 != 0),
			'wku_cal': (result_int & 0x10000000 != 0),
			'wku_acq': (result_int & 0x08000000 != 0),
			'wku_tx': (result_int & 0x04000000 != 0),
			'wku_back_btn': (result_int & 0x02000000 != 0),
			'wku_ms': (result_int & 0x01000000 != 0),
			'wku_io1_ov': (result_int & 0x00800000 != 0),
			'wku_io2_ov': (result_int & 0x00400000 != 0),
			'wku_io3_ov': (result_int & 0x00200000 != 0),
			'wku_io4_ov': (result_int & 0x00100000 != 0),
			'wku_io1_uv': (result_int & 0x00080000 != 0),
			'wku_io2_uv': (result_int & 0x00040000 != 0),
			'wku_io3_uv': (result_int & 0x00020000 != 0),
			'wku_io4_uv': (result_int & 0x00010000 != 0),
			'wku_ign_on': (result_int & 0x00008000 != 0),
			'wku_ibu': (result_int & 0x00004000 != 0),
			'wku_acc_at': (result_int & 0x00002000 != 0),
			'wku_acc_mov': (result_int & 0x00001000 != 0)
		}
		return syswku

	# wake up hour match
	def qsyspwm(self):
		res = self.execute_command('QSYSPWM//')
		qsyspwm = {
			'wku_hr_01': res[7:11].decode(),
			'wku_hr_02': res[11:15].decode(),
			'wku_hr_03': res[15:19].decode(),
			'wku_hr_04': res[19:23].decode(),
			'wku_hr_05': res[23:27].decode(),
			'wku_hr_06': res[27:31].decode(),
			'wku_hr_07': res[31:35].decode(),
			'wku_hr_08': res[35:39].decode(),
			'wku_hr_09': res[39:43].decode(),
			'wku_hr_10': res[43:47].decode(),
			'wku_hr_11': res[47:51].decode(),
			'wku_hr_12': res[51:55].decode(),
		}
		return qsyspwm

	# wake up calendar 01..07
	def qsyswkc(self, id):
		if int(id) < 1 or int(id) > 7:
			return None
		res = self.execute_command('QSYSWKC{:02d}//'.format(id))
		syswkc = {
			'day': int(res[7:9]),
			'tm_int': res[9:45],
		}
		return syswkc

	# power management full power
	def qsyspmf(self):
		res = self.execute_command('QSYSPMF//')
		sby_res = int(res[7:15], 16)
		zzz_res = int(res[15:23], 16)
		syspmf = {
			'sby_pwr_uv': (sby_res & 0x40000000 != 0),
			'sby_hrs': (sby_res & 0x20000000 != 0),
			'sby_idle': (sby_res & 0x10000000 != 0),
			'sby_acq': (sby_res & 0x08000000 != 0),
			'sby_trs': (sby_res & 0x04000000 != 0),
			'sby_cal': (sby_res & 0x02000000 != 0),
			'sby_ign_off': (sby_res & 0x01000000 != 0),
			'zzz_pwr_uv': (zzz_res & 0x40000000 != 0),
			'zzz_hrs': (zzz_res & 0x20000000 != 0),
			'zzz_idle': (zzz_res & 0x10000000 != 0),
			'zzz_acq': (zzz_res & 0x08000000 != 0),
			'zzz_trs': (zzz_res & 0x04000000 != 0),
			'zzz_cal': (zzz_res & 0x02000000 != 0),
			'zzz_ign_off': (zzz_res & 0x01000000 != 0)
		}
		return syspmf

	# power management standby
	def qsyspmy(self):
		res = self.execute_command('QSYSPMY//')
		fp_res = int(res[7:15], 16)
		zzz_res = int(res[15:23], 16)
		syspmy = {
			'fp_pwr_uv': (fp_res & 0x40000000 != 0),
			'fp_hrs': (fp_res & 0x20000000 != 0),
			'fp_cal': (fp_res & 0x10000000 != 0),
			'fp_acq': (fp_res & 0x08000000 != 0),
			'fp_trs': (fp_res & 0x04000000 != 0),
			'fp_ms': (fp_res & 0x01000000 != 0),
			'fp_ov_ain1': (fp_res & 0x00800000 != 0),
			'fp_ov_ain2': (fp_res & 0x00400000 != 0),
			'fp_ov_ain3': (fp_res & 0x00200000 != 0),
			'fp_uv_ain1': (fp_res & 0x00080000 != 0),
			'fp_uv_ain2': (fp_res & 0x00040000 != 0),
			'fp_uv_ain3': (fp_res & 0x00020000 != 0),
			'fp_ign_on': (fp_res & 0x00008000 != 0),
			'fp_ibu': (fp_res & 0x00004000 != 0),
			'fp_acc_at': (fp_res & 0x00002000 != 0),
			'fp_acc_mov': (fp_res & 0x00001000 != 0),
			'fp_gnd_din4': (fp_res & 0x00000800 != 0),
			'fp_gnd_din5': (fp_res & 0x00000400 != 0),
			'fp_gnd_din6': (fp_res & 0x00000200 != 0),
			'zzz_pwr_uv': (zzz_res & 0x40000000 != 0),
			'zzz_dla': (zzz_res & 0x10000000 != 0),
			'zzz_ign_off': (zzz_res & 0x08000000 != 0)
		}
		return syspmy

	# power management sleep
	def qsyspms(self):
		res = self.execute_command('QSYSPMS//')
		fp_res = int(res[7:15], 16)
		sby_res = int(res[15:23], 16)
		syspms = {
			'fp_bat_low': (fp_res & 0x40000000 != 0),
			'fp_dla': (fp_res & 0x20000000 != 0),
			'fp_ign_on': (fp_res & 0x08000000 != 0),
			'fp_ibu': (fp_res & 0x04000000 != 0),
			'fp_min': (fp_res & 0x00800000 != 0),
			'fp_hr': (fp_res & 0x00400000 != 0),
			'fp_wdy': (fp_res & 0x00200000 != 0),
			'fp_day': (fp_res & 0x00100000 != 0),
			'sby_bat_low': (sby_res & 0x40000000 != 0),
			'sby_dla': (sby_res & 0x20000000 != 0),
			'sby_ign_on': (sby_res & 0x08000000 != 0),
			'sby_ibu': (sby_res & 0x04000000 != 0),
			'sby_min': (sby_res & 0x00800000 != 0),
			'sby_hr': (sby_res & 0x00400000 != 0),
			'sby_wdy': (sby_res & 0x00200000 != 0),
			'sby_day': (sby_res & 0x00100000 != 0)
		}
		return syspms

	# power management sleep control week day
	def qsysslm(self):
		res = self.execute_command('QSYSSLM//')
		res_str = res.decode()
		sysslm = {
			'zzz_hr': int(res[7:9], 16), 
			'zzz_min': int(res[9:11], 16),
			'zzz__day': int(res[11:13], 16),
			'zzz_wdy': int(res[13:15], 16),
		}
		return sysslm

	# power management full power to stanby delay
	def qsyspdl(self):
		res = self.execute_command('QSYSPDL//')
		syspdl = { 'fp_sby_dla': int(res[7:11], 16) }
		return syspdl

	# power management full power to sleep delay
	def qsyspds(self):
		res = self.execute_command('QSYSPDS//')
		syspds = { 'fp_zzz_dla': int(res[7:11], 16) }
		return syspds

	#power management full power hour parameters
	def qsysppm(self):
		res = self.execute_command('QSYSPPM//')
		qsysppm = {
			'fp_hr_01': res[7:11].decode(),
			'fp_hr_02': res[11:15].decode(),
			'fp_hr_03': res[15:19].decode(),
			'fp_hr_04': res[19:23].decode(),
			'fp_hr_05': res[23:27].decode(),
			'fp_hr_06': res[27:31].decode(),
			'fp_hr_07': res[31:35].decode(),
			'fp_hr_08': res[35:39].decode(),
			'fp_hr_09': res[39:43].decode(),
			'fp_hr_10': res[43:47].decode(),
			'fp_hr_11': res[47:51].decode(),
			'fp_hr_12': res[51:55].decode(),
		}
		return qsysppm

	# power management pre-wakeup delay
	def qsyspwk(self):
		res = self.execute_command('QSYSPWK//')
		syspwk = { 'pwku_dla': int(res[7:11], 16) }
		return syspwk

	# power management stand by transition delay
	def qsyssls(self):
		res = self.execute_command('QSYSSLS//')
		syssls = {'sby_trsn_dla': int(res[7:11], 16) }
		return syssls

	# power mamangement sleep transition delay
	def qsysslc(self):
		res = self.execute_command('QSYSSLC//')
		sysslc = { 'zzz_trsn_dla': int(res[7:-2], 16) }
		return sysslc

	# power management idle time
	def qsysidt(self):
		res = self.execute_command('QSYSIDT//')
		sysslc = { 'idle_tm': int(res[7:11], 16) }
		return sysslc

	# ACI subsystem: autocompleted information 

	def qacivin(self):
		res = self.execute_command('QACIVIN//')
		acivin = { 'vin': res[7:-2].decode() }
		return acivin

	def qacivrn(self):
		res = self.execute_command('QACIVRN//')
		acivrn = { 'vrn': res[7:-2].decode() }
		return acivrn

	def qacikfa(self):
		res = self.execute_command('QACIKFA//')
		acikfa = { 'k_fact': int(res[7:11], 16) }
		return acikfa

	def qaciepd(self):
		res = self.execute_command('QACIEPD//')
		aciepd = { 'drft_epoch': int(res[7:11], 16) }
		return aciepd

	def qacioeo(self):
		res = self.execute_command('QACIOEO//')
		acieoe = { 'ign_on_tm': int(res[7:15], 16) }
		return acieoe

	def qaciote(self):
		res = self.execute_command('QACIOTE//')
		aciete = { 'ign_on_tm': int(res[7:15], 16) }
		return aciete

	# ALM subsys: alarm system
	
	# alarms in home network
	def qalmhst(self):
		res = self.execute_command('QALMHST//')
		almhst = g4ngps.qalm_st(self, int(res[7:16], 16))
		return almhst

	# alarms in roaming
	def qalmrst(self):
		res = self.execute_command('QALMRST//')
		almrst = g4ngps.qalm_st(self, int(res[7:16], 16))
		return almrst

	# decode alarm dict
	def qalm_st(self, av):
		return {
			'alm_ena': (av & 0x80000000 == 0),
			'ovs': (av & 0x40000000 != 0),
			'ign': (av & 0x20000000 != 0),
			'panic_btn': (av & 0x10000000 != 0),
			'rly': (av & 0x08000000 != 0),
			'inp_pwr_uv': (av & 0x04000000 != 0),
			'inp_pwr_ov': (av & 0x02000000 != 0),
			'accu_uv': (av & 0x01000000 != 0),
			'accu_err': (av & 0x00800000 != 0),
			'rly_dc': (av & 0x00400000 != 0),
			'ibu_dc': (av & 0x00200000 != 0),
			'ibu_sp': (av & 0x00100000 != 0),
			'ibu_grp': (av & 0x00080000 != 0),
			'dlog_lim': (av & 0x00040000 != 0),
			'dly_tfc_exc': (av & 0x00020000 != 0),
			'mth_tfc_exc': (av & 0x00010000 != 0),
			'no_gps_sig': (av & 0x00008000 != 0),
			'staty_ign_on': (av & 0x00004000 != 0),
			'staty_ign_off': (av & 0x00002000 != 0),
			'mvmt_ign_off': (av & 0x00001000 != 0),
			'can': (av & 0x00000800 != 0),
			'mvmt_ms': (av & 0x00000400 != 0),
			'ibu_auth': (av & 0x00000200 != 0),
			'pvt_mode': (av & 0x00000100 != 0),
			'gar_pnd_dc': (av & 0x00000080 != 0),
			'gps_jam': (av & 0x00000040 != 0),
			'gsm_jam': (av & 0x00000020 != 0),
			'fuel': (av & 0x00000020 != 0),
			'acc_at': (av & 0x00000008 != 0),
			'dwntm': (av & 0x00000004 != 0)
		}

	# overspeed alarm speed threshold [km/h*10]
	def qalmovs(self):
		res = self.execute_command('QALMOVS//')
		almovs = { 'ovs_th': (int(res[7:11], 16) & 0xffff) / 10 }
		return almovs

	# movement motion sensor alarm treshold [km/h*10]
	def qalmovs(self):
		res = self.execute_command('QALMMOV//')
		almmov = { 'mvmt_ms_th': (int(res[7:11], 16) & 0xffff) / 10}
		return almmov

	# stationary w/ ignition on alarm timer [sec]
	def qalmstn(self):
		res = self.execute_command('QALMSTN//')
		res = int(res[7:11], 16)
		almstn = { 'staty_ign_on_tmr': (res & 0xffff) }
		return almstn

	# stationary w/ ignition off alarm timer [sec]
	def qalmstf(self):
		res = self.execute_command('QALMSTF//')
		almstf = { 'staty_ign_off_tmr': (int(res[7:11], 16) & 0xffff) }
		return almstf

	# stationary alarm speed threshold [km/h*10]
	def qalmssn(self):
		res = self.execute_command('QALMSSN//')
		almssn = { 'staty_spd_th': (int(res[7:11], 16) & 0xffff) / 10 }
		return almssn

	# stationary w/ ignition off speed threshold [km/h*10]
	def qalmssf(self):
		res = self.execute_command('QALMSSF//')
		almssf = { 'staty_ign_off_spd_th': (int(res[7:11], 16) & 0xffff) / 10 }
		return almssf

	# no gps signal alarm timer [sec]
	def qalmgmt(self):
		res = self.execute_command('QALMGMT//')
		almgmt = { 'no_gps_sig_tmr': (int(res[7:11], 16) & 0xffff) }
		return almgmt

	# downtime alarm timer [min]
	def qalmdta(self):
		res = self.execute_command('QALMDTA//')
		almdta = { 'dwtm_tmr': (int(res[7:11], 16) & 0xffff) }
		return almdta

	# datalog alarm limit [records]
	def qalmdfl(self):
		res = self.execute_command('QALMDFL//')
		almdfl = { 'dlog_lim': (int(res[7:11], 16) & 0xffff) }
		return almdfl

	# accelerometer anti-theft delay [sec]
	def qalmatd(self):
		res = self.execute_command('QALMATD//')
		almatd = { 'acc_at_dla': (int(res[7:11], 16) & 0xffff) }
		return almatd

	# accelerometer anti-theft siren activation time [sec]
	def qalmatt(self):
		res = self.execute_command('QALMATT//')
		almatt = { 'acc_at_srn_on_tmr': (int(res[7:-2], 16) & 0xffff) }
		return almatt

	# event counter 1 total events [events]
	def qalme1t(self):
		res = self.execute_command('QALME1T//')
		alme1t = { 'ec1_evt_tot': (int(res[7:11], 16) & 0xffff) }
		return alme1t

	# event counter 1 trip events [events]
	def qalme1r(self):
		res = self.execute_command('QALME1R//')
		alme1r = { 'ec1_evt_trp': (int(res[7:11], 16) & 0xffff) }
		return alme1r

	# event counter 2 total events [events]
	def qalme2t(self):
		res = self.execute_command('QALME2T//')
		alme2t = { 'ec2_evt_tot': (int(res[7:11], 16) & 0xffff) }
		return alme2t

	# event counter 2 trip events [events]
	def qalme2r(self):
		res = self.execute_command('QALME2R//')
		alme2r = { 'ec2_evt_trp': (int(res[7:11], 16) & 0xffff) }
		return alme2r

	# TRS sybsystem: transmission
	
	# transmission in home network
	def qtrshst(self):
		res = self.execute_command('QTRSHST//')
		trshst = self.__qtrs_st(int(res[7:15], 16))
		return trshst

	# transmission in roaming
	def qtrsrst(self):
		c = 'QTRSRST//'
		res = self.execute_command(c)
		trsrst = self.__qtrs_st(int(res[7:15], 16))
		return trsrst

	# decode transmission dict
	def __qtrs_st(self, tv):
		return {
			'trs_ena': (tv & 0x80000000 == 0),
			'int_a': (tv & 0x40000000 != 0),
			'int_a_ign_on': (tv & 0x20000000 != 0),
			'int_a_ign_off': (tv & 0x10000000 != 0),
			'int_a_alm': (tv & 0x08000000 != 0),
			'int_b': (tv & 0x04000000 != 0),
			'int_b_ign_on': (tv & 0x02000000 != 0),
			'int_b_ign_off': (tv & 0x01000000 != 0),
			'int_b_alm': (tv & 0x00800000 != 0),
			'alm': (tv & 0x00400000 != 0),
			'data_th': (tv & 0x00200000 != 0),
			'ign': (tv & 0x00100000 != 0),
			'hrs_mtch': (tv & 0x00080000 != 0),
			'ibu': (tv & 0x00040000 != 0),
			'dly_tfc_ex': (tv & 0x00020000 != 0),
			'mth_tfc_ex': (tv & 0x00010000 != 0),
			'no_gps': (tv & 0x00008000 != 0),
			'pwr_on': (tv & 0x00004000 != 0),
			'trs_dla': (tv & 0x00002000 != 0),
			'trs_clr_su': (tv & 0x00001000 != 0),
			'wrk_pvt': (tv & 0x00000800 != 0),
			'ep_int_a_ign_on': (tv & 0x00000400 != 0),
			'ep_int_a_ign_off': (tv & 0x00000200 != 0),
			'ep_int_b_ign_on': (tv & 0x00000100 != 0),
			'ep_int_b_ign_off': (tv & 0x00000080 != 0),
			'dist_th': (tv & 0x00000040 != 0),
			'acq_trg': (tv & 0x00000020 != 0),
			'no_rtc': (tv & 0x00000010 != 0)
		}

	# transmission threshold on accumulated data on home network [bytes]
	def qtrshad(self):
		res = self.execute_command('QTRSHAD//')
		trshad = { 'h_data_th': ((int(res[7:11], 16) & 0xffff) / 1024) }
		return trshad

	# transmission threshold on accumulated data in roaming
	def qtrsrad(self):
		res = self.execute_command('QTRSRAD//')
		trsrad = { 'r_data_th': ((int(res[7:11], 16) & 0xffff) / 1024) }
		return trsrad

	# transmission interval a on home network
	def qtrshia(self):
		res = self.execute_command('QTRSHIA//')
		trshia = { 'h_int_a': int(res[7:11], 16) & 0xffff }
		return trshia

	# transmission interval a in roaming
	def qtrshia(self):
		res = self.execute_command('QTRSRIA//')
		trsria = { 'r_int_a': int(res[7:11], 16) & 0xffff }
		return trsria

	# transmission interval b on home network
	def qtrshib(self):
		res = self.execute_command('QTRSHIB//')
		trsrib = { 'h_int_b': int(res[7:11], 16) & 0xffff }
		return trshib

	# transmission interval b roaming net
	def qtrsrib(self):
		res = self.execute_command('QTRSRIB//')
		trsrib = { 'r_int_b': int(res[7:11], 16) & 0xffff }
		return trsrib

	# transmission hours on home network
	def qtrshmt(self):
		res = self.execute_command('QTRSHMT//')
		trshmt = self.__qtrs_mt(res)
		return trshmt

	# transmission hours in roaming
	def qtrsrmt(self):
		res = self.execute_command('QTRSRMT//')
		trsrmt = self.__qtrs_mt(res)
		return trsrmt

	# decode transmission hours dict
	def __qtrs_mt(self, tv):
		return {
			'trs_hr_01': tv[7:13].decode(),
			'trs_hr_02': tv[13:19].decode(),
			'trs_hr_03': tv[19:25].decode(),
			'trs_hr_04': tv[25:31].decode(),
			'trs_hr_05': tv[31:37].decode(),
			'trs_hr_06': tv[37:43].decode(),
			'trs_hr_07': tv[43:49].decode(),
			'trs_hr_08': tv[49:55].decode(),
		}

	# transmission daily traffic limit for external sim on home network [bytes]
	def qtrshdl(self):
		res = self.execute_command('QTRSHDL//')
		trshdl = { 'h_dly_tfc_ext_sim_th': int(res[7:15], 16) / 1024 }
		return trshdl

	# transmission daily traffic limit for external sim in roaming [bytes]
	def qtrsrdl(self):
		res = self.execute_command('QTRSRDL//')
		trsrdl = { 'r_dly_tfc_ext_sim_th': int(res[7:15], 16) / 1024 }
		return trsrdl

	# transmission daily traffic limit for internal sim on home network [bytes]
	def qtrshdc(self):
		res = self.execute_command('QTRSHDC//')
		trshdc = { 'h_dly_tfc_int_sim_th': int(res[7:15], 16) / 1024 }
		return trshdc

	# transmission daily traffic limit for internal sim in roaming [bytes]
	def qtrsrdc(self):
		res = self.execute_command('QTRSRDC//')
		trsrdc = { 'h_dly_tfc_int_sim_th': int(res[7:15], 16) / 1024 }
		return trsrdc
		
	# transmission monthly traffic limit for external sim in home network [kbytes]
	def qtrshml(self):
		res = self.execute_command('QTRSHML//')
		trshml = { 'h_mth_tfc_ext_sim_th': int(res[7:15], 16) / 1048576 }
		return trshml

	# transmission monthly traffic limit for external sim in roaming [kbytes]
	def qtrsrml(self):
		res = self.execute_command('QTRSRML//')
		trsrml = { 'r_mth_tfc_ext_sim_th': int(res[7:15], 16) / 1048576 }
		return trsrml

	# transmission monthly traffic limit for external sim in home network [kbytes]
	def qtrshmc(self):
		res = self.execute_command('QTRSHMC//')
		trshmc = { 'h_mth_tfc_int_sim_th': int(res[7:15], 16) / 1048576 }
		return trshmc

	# transmission monthly traffic limit for external sim in roaming [kbytes]
	def qtrsrmc(self):
		res = self.execute_command('QTRSRMC//')
		trsrmc = { 'r_mth_tfc_int_sim_th': int(res[7:15], 16) / 1048576 }
		return trsrmc

	# transmission mothly traffic reset [day of month]
	def qtrstdr(self):
		res = self.execute_command('QTRSTDR//')
		trstdr = { 'mth_trf_rst': int(res[7:-2], 16) }
		return trstdr

	# delay transmission delay on home network [sec]
	def qtrshdt(self):
		res = self.execute_command('QTRSHDT//')
		trshdt = { 'h_trs_dla': int(res[7:11], 16) }
		return trshdt

	# delay transmission delay in roaming [sec]
	def qtrsrdt(self):
		res = self.execute_command('QTRSRDT//')
		trsrdt = { 'r_trs_dla': int(res[7:11], 16) }
		return trsrdt

	# transmission at cumulative distance on home network [m]
	def qtrshtd(self):
		res = self.execute_command('QTRSHTD//')
		trshtd = { 'h_trs_dist': int(res[7:15], 16) / 1000 }
		return trshtd

	# transmission at cumulative distance on home network [m]
	def qtrsrtd(self):
		res = self.execute_command('QTRSRTD//')
		trsrtd = { 'r_trs_dist': int(res[7:15], 16) / 1000 }
		return trsrtd

	def ctrsreq(self):
		res = self.execute_command('CTRSREQ//')
		return res[7:10]

	def ctrsltr(self):
		res = self.execute_command('CTRSLTR//')
		return res[7:10]

	def ctrsutr(self):
		res = self.execute_command('CTRSUTR//')
		return res[7:10]

	def ctrsctr(self):
		res = self.execute_command('CTRSCTR//')
		return res[7:10]

	# GSM subsystem

	def qgsminf(self):
		res = self.execute_command('QGSMINF//')
		gsminf = {
			'gsm_sts': res[7:9],
			'int_sim_mcc_mnc': res[9:15].decode(),
			'ext_sim_mcc_mnc': res[15:21].decode(),
			'sim_imsi': res[21:36].decode(),
			'gsm_auth_crt_sts': res[36:38],
			'gsm_auth_req_sts': res[38:40],
		}
		return gsminf

	def qgsmfrm(self):
		res = self.execute_command('QGSMFRM//')
		gsmfrm = { 'gsm_frmw': res[7:-2].decode() }
		return gsmfrm

	# incoming voice call master actions
	def qgsmvim(self):
		res = self.execute_command('QGSMVIM//')
		gsmvim = { 'mas_vca': self.__qgsmvi(int(res[7:-2], 16)) }
		return gsmvim

	# incoming voice call user actions
	def qgsmviu(self):
		res = self.execute_command('QGSMVIU//')
		gsmviu = { 'usr_vca': self.__qgsmvi(int(res[7:-2], 16)) }
		return gsmviu

	# incoming voice call unauthorised actions
	def qgsmvin(self):
		res = self.execute_command('QGSMVIN//')
		gsmviu = { 'ua_vca': self.__qgsmvi(int(res[7:-2], 16)) }
		return gsmviu

	def __qgsmvi(self, vi):
		if vi == 0:
			return 'vca_dis'
		elif vi == 1:
			return 'trg_pdef_cmd'
		elif vi == 3:
			return 'trg_req_trs'
		elif vi == 4:
			return 'vca_ans'
		elif vi == 5:
			return 'sd_gsm'
		elif vi == 6:
			return 'rst'
		elif vi == 7:
			return 'rly_ena'
		elif vi == 8:
			return 'rly_dis'

	# predefined command
	def qgsmpdf(self):
		res = self.execute_command('QGSMPDF//')
		gsmpdf = { 'pdef_cmd': res[7:-2].decode() }
		return gsmpdf

	# authorized number 01..12
	def qgsma(self, id):
		if int(id) < 1 or int(id) > 12:
			return None
		res = self.execute_command('QGSMA{:02d}//'.format(id))
		gsma = { 'num_{:02d}'.format(id): res[7:-2].decode() }
		return gsma

	# all authorized numbers
	def qgsmall(self):
		res = self.execute_command('QGSMALL//')
		gsmall = {
			'num_01': res[7:23].decode(),
			'num_02': res[23:39].decode(),
			'num_03': res[39:55].decode(),
			'num_04': res[55:71].decode(),
			'num_05': res[71:87].decode(),
			'num_06': res[87:103].decode(),
			'num_07': res[103:119].decode(),
			'num_08': res[119:135].decode(),
			'num_09': res[135:151].decode(),
			'num_10': res[151:167].decode(),
			'num_11': res[167:183].decode(),
			'num_12': res[183:199].decode(),
		}
		return gsmall

	# sms alert destination 1..8
	def qgsmal(self, id):
		if int(id) < 1 or int(id) > 8:
			return None
		res = self.execute_command('QGSMAL{:01d}//'.format(id))
		gsma = { 'num_{:02d}'.format(id): res[7:-2].decode() }
		return gsma
	
	# location information
	def qgsmloc(self):
		res = self.execute_command('QGSMLOC//')
		gsmloc = {
			'gsm_sts': res[7:9],
			'mcc_mnc': res[9:15].decode(),
			'lac': res[15:19],
			'lac_age': int(res[19:23], 16),
			'cid': res[23:27],
			'cid_age': int(res[27:31], 16)
		}
		return gsmloc

	# trigger predefined command from gsmpdf as being executed from phone number
	def cgsmssm(self, tel):
		if (len(tel) < 6 or not re.match('^\+\d+$', tel)):
			return None
		res = self.execute_command('CGSMSSM{:s}//'.format(tel))
		return res[7:10]

	# switch to external sim
	def cgsmuxs(self):
		res = self.execute_command('CGSMUXS//')
		return res[7:10]

	# switch to internal sim
	def cgsmuxs(self):
		res = self.execute_command('CGSMUOS//')
		return res[7:10]

	## GPR subsystem: mobile data

	def qgprsim(self):
		res = self.execute_command('QGPRSIM//')
		lic_ch = res[7:-2].decode()
		gprsim = {}
		if 'lic' in lic_ch:
			gprsim['dual_sim_licensed'] = False
			# return gprsim
		else:
			res_int = int(res[7:-2], 16)
			if res_int == 0x00:
				gprsim['sim_selector']: 'ext_sim_only'
			elif res_int == 0x20:
				gprsim['sim_selector']: 'intern_sim_only'
			elif res_int == 0x40:
				gprsim['sim_selector']: 'intern_sim_ext_not_detected'
			elif res_int == 0x60:
				gprsim['sim_selector']: 'intern_sim_ext_fails'
			elif res_int == 0x80:
				gprsim['sim_selector']: 'ext_sim_home_intern_roaming'
				if res_int == 0x60:
					c = 'QGPRCTH//'
					result = g4ngps.execute_command(self, c)
					result = result[7:-2]
					gprsim['external_sim_timeout']: int(result, 16)

					c = 'QGPRIST//'
					result = g4ngps.execute_command(self, c)
					result = result[7:-2]
					gprsim['intern_sim_timeout']: int(result, 16)
		return gprsim

	# read apn info
	def qgprmct(self):
		c = 'QGPRMCT//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 6)
		res_apn = 0x3000 & res
		qgprmct = {'apn': None}
		if res_apn == 0x0000:
			qgprmct['apn']: 'Main'
		if res_apn == 0x1000:
			qgprmct['apn']: 'List'
		if res_apn == 0x2000:
			res_apn['apn']: 'Secondary'
		return qgprmct

	#read main apn
	def qgprgma(self):
		c = 'QGPRGMA//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		gprgma = {'apn': res}
		return gprgma

	#read  main username
	def qgprgmu(self):
		c = 'QGPRGMU//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		gprgmu = {'apn_user': res}
		return gprgmu

	#read main pass
	def qgprgmp(self):
		c = 'QGPRGMP//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		gprgmp = {'apn_pass': res}
		return gprgmp

	#read secondary user
	def qgprgsu(self):
		c = 'QGPRGSU//'
		res = g4ngps.execute_command(self, c)
		return res

	#def read remote peer type
	def qgprgrs(self):
		c = 'QGPRGRS//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		remote_peer = {'remote_peer': res}
		return remote_peer

	#def read remote port
	def qgprgrp(self):
		c = 'QGPRGRP//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		remote_port = {'remote_port': res}
		return remote_port

	#def read upgrade peer
	def qgprgus(self):
		c = 'QGPRGUS//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		gprgus = {'update_peer': res}
		return gprgus

	#def read upgrade port
	def qgprgup(self):
		c = 'QGPRGUP//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		gprgup = {'update_port': res}
		return gprgup

	#read backup peer
	def qgprgbs(self):
		c = 'QGPRGBS//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		gprgbs = {'backup_peer': res}
		return gprgbs

		#read backup port
	def qgprgbp(self):
		c = 'QGPRGBS//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2].decode()
		gprgbp = {'backup_port': res}
		return gprgbp

	def qgprist(self):
		c = 'QGPRIST//'
		result = g4ngps.execute_command(self, c)
		result = result[7:-2].decode()
		gprist = {'intern_sim_timeout': int(result, 16)}
		return gprist

	def qgprcth(self):
		c = 'QGPRCTH//'
		result = g4ngps.execute_command(self, c)
		result = result[7:-2].decode()
		gprcth = {'external_sim_timeout': int(result, 16)}
		return gprcth

#GPS

	def qgpsset(self):
		c = 'QGPSSET//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		gpsset = {
			'sbas_enabled': (res & 0x4000 != 0),
			'gps_updates': (res & 0x2000 != 0),
			'data_filter': (res & 0x1000 == 0),
			'inv_pos': (res & 0x0800 == 0),
			'inv_pos_acc': (res & 0x0400 == 0),
			'inv_pos_priv_mode': (res & 0x0200 != 0)
		}
		return gpsset

	#gps number of satelites
	def qgpsefn(self):
		c = 'QGPSEFN//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		gpsefn = {'no_sat': res}
		return gpsefn

	#gps pdop
	def qgpsefp(self):
		c = 'QGPSEFP//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		pdop1 = res[0:2]
		pdop2 = res[2:]
		gpsefp = {}
		if pdop2 == 0:
			gpsefp['pdop']: pdop1
		else:
			gpsefp['pdop']: pdop1 + 0.1 * pdop2
		return gpsefp

	#gps speed
	def gpsefs(self):
		c = 'QGPSEFS//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		gpsefs = {'gps_speed': res}
		return gpsefs

	def qgpsact(self):
		c = 'QGPSACT//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		gpsact = {'gps_accel_thresh': res}
		return gpsact

	def qgpsdis(self):
		c = 'QGPSDIS//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		gpsdis = {'gps_odo': res}
		return gpsdis

#DLF
#read device memory info

	def qdiowpt(self):
		c = 'QDLFINF//'
		res = g4ngps.execute_command(self, c)
		dlfinf = {'dlf_records': int(res[7:13], 16), 'dlf_total_records': int(res[13:19], 16)}
		return dlfinf

#IO system
# Volt threshold work-private

	def qdiowpt(self):
		c = 'QDIOWPT//'
		res = g4ngps.execute_command(self, c)
		result_int = int(res[7:-2], 16)
		result_int = result_int & 0xffff
		f = result_int * 7.08722 / 1000
		diowpt = {'voltage_threshold': (int(f) + round((f - int(f)) * 10) / 10)}
		return diowpt

	# read accelerometer
	def qdioacp(self):
		c = 'QDIOACP//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		res1 = int(res[0:8], 16)
		res2 = int(res[8:16], 16)
		qdioacp = {
			'enabled': (res1 & 0x80000000 == 0),
			'antitheft_enabled': (res1 & 0x40000000 != 0),
			'motionde_tection': (res1 & 0x20000000 != 0),
			'activate_relay_alarm': (res1 & 0x00800000 != 0),
			'deactivate_relay_alarm': (res1 & 0x00400000 != 0),
			'activate_relay_movement': (res1 & 0x00200000 != 0),
			'deactivate_relay_movement': (res1 & 0x00100000 != 0),
			'arm_ignition_off': (res1 & 0x00008000 != 0),
			'disarm_ignition_on': (res2 & 0x80000000 != 0),
			'disarm_ibutton': (res2 & 0x40000000 != 0),
		}
		return qdioacp

	#arming delay conditions
	def qdioard(self):
		c = 'QDIOARD//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		qdioard = {'arming_delay': res * 0.1}
		return qdioard

	#movement lower treshold
	def qdioarh(self):
		c = 'QDIOARH//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		qdioarh = {'mov_low_thresh': res}
		return qdioarh

	#delay movement lower threshold
	def qdioart(self):
		c = 'QDIOART//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		qdioart = {'arming_delay_mov_low': res * 0.1}
		return qdioart

	#movement greater treshold
	def qdioadt(self):
		c = 'QDIOADT//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		qdioadt = {'mov_great_thresh': res}
		return qdioadt

	#number of acceleration events threshold
	def qdiomdh(self):
		c = 'QDIOMDH//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		qdiomdh = {'accel_events_thresh': res}
		return qdiomdh

	#event threshold
	def qdiomdh(self):
		c = 'QDIOMDT//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		qdiomdt = {'event_thresh': res}
		return qdiomdt

	#acceleration decrese rate
	def qdiomdh(self):
		c = 'QDIOMDR//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		qdiomdr = {'event_decrese_rate': res}
		return qdiomdr

	#time motion detection threshold
	def qdiomdo(self):
		c = 'QDIOMDO//'
		res = g4ngps.execute_command(self, c)
		res = int(res[7:-2], 16)
		qdiomdo = {'time_motion_det_thresh': res * 0.1}
		return qdiomdo

	#dio inf
	def qdioinf(self):
		c = 'QDIOINF//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioinf = {
			'io_contact': res[71:79],
			'io_panic': res[79:87],
			'io_relay': res[87:95],
			'io_status': res[163:165],
			'io_status2': res[165:167],
			'ain1': res[167:171],
			'ain2': res[171:175],
			'ain3': res[175:179],
			'power_in_voltage': res[191:195],
			'temperature': res[199:203]
		}
		return qdioinf

	#DIOAI read device config
	def qdioai1(self):
		c = 'QDIOAI1//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai1 = {'IO1': g4ngps.setEntity(self, res)}
		return qdioai1

	def qdioai2(self):
		c = 'QDIOAI2//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai2 = {'IO2': g4ngps.setEntity(self, res)}
		return qdioai2

	def qdioai3(self):
		c = 'QDIOAI13//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai3 = {'IO3': g4ngps.setEntity(self, res)}
		return qdioai3

	def qdioai4(self):
		c = 'QDIOAI4//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai4 = {'IO4': g4ngps.setEntity(self, res)}
		return qdioai4

	def qdioai5(self):
		c = 'QDIOAI5//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai5 = {'IO5': g4ngps.setEntity(self, res)}
		return qdioai5

	def qdioai6(self):
		c = 'QDIOAI6//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai6 = {'IO6': g4ngps.setEntity(self, res)}
		return qdioai6

	def qdioai7(self):
		c = 'QDIOAI7//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai7 = {'IO7': g4ngps.setEntity(self, res)}
		return qdioai7

	def qdioai8(self):
		c = 'QDIOAI8//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai8 = {'IO8': g4ngps.setEntity(self, res)}
		return qdioai8

	def qdioai9(self):
		c = 'QDIOAI9//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioai9 = {'IO9': g4ngps.setEntity(self, res)}
		return qdioai9

	def qdioaia(self):
		c = 'QDIOAIA//'
		res = g4ngps.execute_command(self, c)
		res = res[7:-2]
		qdioaia = {'IOA': g4ngps.setEntity(self, res)}
		return qdioaia

	def setEntity(self, data):
		data = data[0:2].decode()
		if data == '01':
			return 'CONTACT'
		elif data == '02':
			return 'PANIC BUTTON'
		elif data == '03':
			return 'WORK PRIVATE DETECTOR'
		elif data == '04':
			return 'RELAY'
		elif data == '05':
			return 'EVENT COUNTER1'
		elif data == '06':
			return 'EVENT COUNTER2'
		elif data == '07':
			return 'STATE COUNTER1'
		elif data == '08':
			return 'state couter2'
		elif data == '09':
			return 'event generator1'
		elif data == '0A':
			return 'event generator2'
		elif data == '0B':
			return 'event ibuttonA'
		elif data == '0D':
			return 'MotionSensor'
		elif data == '10':
			return 'ACCELEROMETERSIREN'
		elif data == '11':
			return 'KLINEINTERFACE'
		elif data == '12':
			return 'KLINEFUELSENSOR'
		elif data == '13':
			return 'ARMINGPOSITIVEACCELEROMETER'
		elif data == '14':
			return 'ARMINGNEGATIVEACCELEROMETER'
		elif data == '15':
			return 'DISARMINGPOSITIVEACCELEROMETER'
		elif data == '16':
			return 'DISARMINGNEGATIVEACCELEROMETER'
		elif data == '17':
			return 'IBUTTONB'
		elif data == '18':
			return 'BUZZERSIREN'
		elif data == '19':
			return 'LATCHINGRELAYCOILA'
		elif data == '1A':
			return 'LATCHINGRELAYCOILB'
		elif data == '1B':
			return 'TACHO_SIEMENS_DTO1381'
		elif data == '1C':
			return 'TACHO_SIEMENS_MTCO1324'
		elif data == '1D':
			return 'TACHO_STONERIDGE_SE5000'
		elif data == '1E':
			return 'TACHO_STONERIDGE_2400_4800'
		elif data == '1F':
			return 'TACHO_ACTIA_L2000'
		elif data == '20':
			return 'WORKPRIVATELED'

	#dioEntities
	#read ignition io entity
	def qdiopco(self):
		res = self.execute_command('QDIOPCO//')
		res = res[7:-2]
		res = res[0:4]
		diopco = {}
		if res:
			result_int = int(res, 16)
			diopco['enabled'] = (result_int & 0x8000) == 0
			diopco['io'] = 'todo'
			diopco['sog_derived'] = (result_int & 0x4000) != 0
			diopco['motion_sensor_derived'] = (result_int & 0x2000) != 0
			diopco['accelerometer_movement'] = (result_int & 0x0800) != 0
			diopco['polarity'] = (result_int & 0x0400) != 0
		return diopco
	
	def qdiopct(self):
		res = self.execute_command("QDIOPCT//")
		if res:
			res = int(res[7:-2], 16)
			f = res * 7.08722 / 1000
			f = int(f) + round((f - int(f)) * 10) / 10
			diopct = {'threshold' : f}
			return diopct
		else:
			return None	
	def qdiocss(self):
		res=self.execute_command("QDIOCSS//")[7:-2]
		diocss={
			'speed_thresh': int(res)
		}
		return diocss

	def qdiocst(self):
		res=self.execute_command("QDIOCST//")[7:-2]
		diocst ={
			'time_threshold': int(res,16)
		}	
		return diocst

	def qdiopcf(self):
		res=int(self.execute_command("QDIOPCF//")[7:-2],16)
		diopcf={
			'filter_thresh' : float(res)
		}
		return diopcf
	def read_ignition_entity(self):
		ig_ent_io ={
			'diopco': self.qdiopco(),
			'diopct': self.qdiopct(),
			'diocss': self.qdiocss(),
			'diocst': self.qdiocst(),
			'diopcf': self.qdiopcf()
		}	
		return ig_ent_io

	#read panic button io entity
	def read_panic_button_entity(self):
		pan_ent_io={
			'diopal': self.qdiopal(),
			'diopat': self.qdiopat(),
			'diopdr': self.qdiopdr(),
			'diopaf': self.qdiopaf()
		}
		return pan_ent_io
	
	
	def qdiopal(self):
		res = int(self.execute_command('QDIOPAL//')[7:-2],16)
		diopal = {
		'io': 'todo',
		'polarity' : (res & 0x20000000) != 0,
		'monostable' : (res& 0x10000000) != 0,
		'disableRelay' : (res & 0x00800000) != 0,
		'stateIgnition' : (res & 0x08000000) != 0,
		'panicTimeFilter' : (res & 0x02000000) != 0
		}
		return diopal
	
	def qdiopat(self):
		res = int(self.execute_command('QDIOPAT//')[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		diopat={'threshold' : f}
		return diopat

	def qdiopdr(self):
		res = int(self.execute_command('QDIOPDR//')[7:-2],16)
		diopdr={'duration':  res}
		return diopdr
	
	def qdiopaf(self):
		res = int(self.execute_command('QDIOPAF//')[7:-2],16)
		diopaf={'thresholdTimeFilter':res}
		return diopaf

	#read relay io entity
	def read_relay_entity(self):
		relay_ent_io={

		}
		return relay_ent_io
	def qdioprt(self):
		res = int(self.execute_command("QDIOPRT")[7:-2],16)
		dioprt = {
		'enabled': res & 0x80000000 == 0,
		'io' :  res,  #get IO entity
		'polarity' : res & 0x20000000 != 0,
		'mono' : res & 0x10000000 != 0,
		'act_contact_off' : res & 0x08000000 != 0,
		'inact_contact_off' : res & 0x02000000 != 0,
		'act_contact_on' : res & 0x04000000 != 0,
		'inact_contact_on' : res & 0x01000000 != 0
		}
		return dioprt

	def qdioprp(self):
		res = int(self.execute_command("QDIOPRP//")[7:-2],16)
		dioprp={}
		if res == 65535:
			dioprp['relayPulse'] = None
		else:
			dioprp['relayPulse'] = res
		return dioprp

	#ibu io entity
	def qibuast(self):
		res = int(self.execute_command("QIBUAST//")[7:-2],16)
		ibutton = {
		'io': None, 
		'deac_contact_off': (res & 0x20000000) != 0,
		'deac_contact_on': (res & 0x10000000) != 0,
		'deac_panic_alarm': (res & 0x08000000) != 0,
		'light_on_auth_success': (res & 0x04000000) != 0,
		'light_off_auth_failed': (res & 0x02000000) != 0,
		'led_on_relay_enabled' : (res & 0x01000000) != 0,
		'led_off_relay_disabled' : (res & 0x00800000) != 0,
		'ignition_ok' : (res & 0x00008000) != 0,
		'ignition_failed' : (res & 0x00004000) != 0,
		'ignition_ok_timer' : (res & 0x00002000) != 0,
		'ignition_failed_timer' : (res & 0x00001000) != 0,
		'ok_reset_enable_relay' : (res & 0x00000800) != 0,
		'ok_reset_disable_relay' : (res & 0x00000400) != 0,
		'fail_reset_enable_relay' : (res & 0x00000200) != 0,
		'fail_reset_disable_relay' : (res & 0x00000100) != 0,
		'ignition_ok' : (res & 0x00000080) != 0,
		'ibu_recog' : (res & 0x00000040) != 0,
		'ibu_not_recog' : (res & 0x00000020) != 0
		}
		return ibutton
	def qibulnd(self):
		res = int(self.execute_command('QIBULND//')[7:-2],16)
		ibulnd = {}
		if res== 255:
			ibulnd['time_light_on_success_auth'] = None
		else:
			ibulnd['time_light_on_success_auth'] = res
		return ibulnd	
	def qibulfd(self):
		res = int(self.execute_command("QIBULFD//")[7:-2],16)
		ibulfd={}
		if res == 255:
			ibulfd['time_light_on_failed_auth'] = None
		else:
			ibulfd['time_light_on_failed_auth'] = res
		return ibulfd
	def qibuaot(self):
		res = int(self.execute_command("QIBUAOT//")[7:-2],16)
		ibuaot={
		'auth_ok_timer': res}
		return ibuaot
	def qibuaft(self):
		res = int(self.execute_command('QIBUAFT//')[7:-2],16)
		ibuaft = {
		'auth_fail_timer' : res 
		}
		return ibuaft
	def read_ibutton_entity(self):
		ibu_ent_io={
			'ibuast': self.qibuast(),
			'ibulnd': self.qibulnd(),
			'ibulfd': self.qibulfd(),
			'ibuaot': self.qibuaot(),
			'ibuaft': self.qibuaft()
		}
		return ibu_ent_io

	#read input power
	def qdiovlt(self):
		res = int(self.execute_command('QDIOVLT//')[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		diovolt = {}
		diovolt['un_volt_thresh'] = f
		return diovolt
	def qdiovht(self):
		res = int(self.execute_command('QDIOVHT//')[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		diovolt = {}
		diovolt['ov_volt_thresh'] = f
		return diovolt
	
	def read_input_power(self):
		input_power={
			'diovlt':self.qdiovlt(),
			'diovht':self.qdiovht()
		}
		return input_power

	#read event counter 1 dio entity
	def qdioeco1(self):
		res = self.execute_command('QDIOECO//')[7:-2]
		res = res[7:-2]
		res = int(res[0:4], 16)

		dioeco1 = {}
		dioeco1['set_io'] : None  #implement this
		dioeco1['edge_trigg'] : res & 0x4000 != 0
		dioeco1['edge_filter'] : res & 0x2000 != 0
		return dioeco1

	def qdioe1f(self):
		res = int(self.execute_command('QDIOE1F//')[7:-2],16)
		dioelf={}
		dioelf['filter_thresh'] : res / 100
		return dioelf
	
	def qdioe1l(self):
		res = int(self.execute_command('QDIOE1L//')[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		dioe1l={'level_thresh' : f}
		return dioe1l
	
	def read_event_count1(self):
		ev_count_1={
		'dioeco1':self.qdioeco1(),
		'dioel1f':self.qdioe1f(),
		'dioel1l':self.qdioe1l()
		}
		return ev_count_1

	#read event counter 2 dio entity
	def qdioeco2(self):
		res = self.execute_command("QDIOECO//")[7:-2]
		res = int(res[4:8], 16)
		dioeco2 = {}
		dioeco2['set_io'] = None  #implement this
		dioeco2['edge_trigg'] = res & 0x4000 != 0
		dioeco2['edge_filter'] = res & 0x2000 != 0
		return dioeco2
	
	def qdioe2f(self):
		res = int(self.execute_command("QDIOE2F//")[7:-2],16)
		dioe2f={'filter_thresh': res / 10}
		return dioe2f
	
	def qdioe2l(self):
		res = int(self.execute_command("QDIOE2L//")[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		dioe2l={'level_thresh' : f}
		return dioe2l
	def read_event_counter2(self):
		ev_counter2={
		'dioeco2':self.qdioeco2(),
		'dioe2f':self.qdioe2f(),
		'dioe2l':self.qdioe2l()	
		}	
		return ev_counter2


	#read state counter 1 dio entity
	def qdiosco1(self):
		res = self.execute_command("QDIOSCO//")[7:-2]
		res = int(res[0:4], 16)
		diosco1= {}
		diosco1['set_io'] = None  #todo
		diosco1['edge_trigg'] = res & 0x4000 != 0
		return 

	def qdios1l(self):	
		res = int(self.execute_command("QDIOS1L//")[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		dios1l={'level_thresh' : f}
		return dios1l
	
	def read_state_count1(self):
		state_count1={
			'diosco1': self.qdiosco1(),
			'dios1l':self.qdios1l()
		}
		return state_count1
	
	#read state counter2 dio entity
	def qdiosco2(self):
		res = self.execute_command('QDIOSCO//')[7:-2]
		res = int(res[0:4], 16)
		state_count2 = {
		'set_io' : None,  #todo
		'edge_trig': res & 0x4000 != 0
		}
		return state_count2

	def qdios2l(self):
		res = int(self.execute_command("QDIOS2L//")[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		dios2l={'level_thresh': f}
		return dios2l
	
	def read_state_count2(self):
		state_count2={
			'diosco2': self.qdiosco2(),
			'dios2l': self.qdios2l()
		}
		return state_count2

	#read event generator2
	def qdioego1(self):
		res = self.execute_command('QDIOEGO//')[7:-2]
		res = int(res[0:4], 16)
		qev_gen1 = {
		'set_io' : None,
		'edge_trig' : (res & 0x4000) != 0
		}
		return qev_gen1

	def qdioego2(self):
		res = self.execute_command('QDIOEGO//')[7:-2]
		res = int(res[4:8], 16)
		qev_gen2 = {
		'set_io' : None,
		'edge_trig' : (res & 0x4000) != 0
		}
		return qev_gen2

	def qdiomts(self):
		res =self.execute_command('QDIOMTS//')[7:-2]
		diomts={
		'io_assigned':None, #todo	
		'relay' :(res & 0x40000000) !=0
		}
		return diomts

	def qdiomtt(self):
		res = int(self.execute_command('QDIOMTT//')[7:-2], 16) 
		f = res * 7.08722 / 1000
		diomtt={
			'threshold':int(f) + round((f - int(f)) * 10) / 10
		}
		return diomtt
	def qdiomit(self):
		res = int(self.execute_command('QDIOMIT//')[7:-2], 16) 
		diomit={
			'idle_timer': res
		}
		return diomit
	def qdiomft(self):
		res= int(self.execute_command('QDIOMFT//')[7:-2], 16)
		diomft={
			'filter_timer':res
		}
		return diomft
	def qdiomts(self):
		res= int(self.execute_command('QDIOMFC//')[7:-2], 16)
		diomfc={
			'threshold_fil_counter':res
		}
		return diomfc
	def read_event_gen2(self):
		eg2={
			'dioego':self.qdioego2(),
			'diomts':self.qdiomts(),
			'diomtt':self.qdiomtt(),
			'diomit':self.qdiomit(),
			'diomtf':self.qdiomft(),
			'diomts':self.qdiomts()
		}
		return eg2

#read buzzer

	def read_buzzer_entity(self):
		res=self.execute_command("QIBUAST//")[7:-2]
		res=int(res[2])
		buzzer2 = {
		'use_use_int_buz':res & 0x4000 != 0,
		'almovb':self.qalmovb(),
		'ibunab':self.qibunab(),
		'ibukab':self.qibakab(),
		'ibafab':self.qibafab()
		}
		return buzzer2
	def qalmovb(self):
		res=self.execute_command("QALMOVB//")[7:-2]
		almovb={}
		if res.decode() == 'C1A0':
			almovb['activ_over_speed_alm'] = True
		else:
			almovb['activ_over_speed_alm'] = False
		return almovb
	def qibunab(self):
		res=self.execute_command("QIBUNAB//")[7:-2]
		ibunab={}
		if res.decode() == 'C3AA' and int(res, 16) & int('00000080', 16) != 0:
			ibunab['activ_ign_on_ibut_notauth'] = True
		else: 
			ibunab['activ_ign_on_ibut_notauth'] = False
		return ibunab
	def qibakab(self):
		res=self.execute_command("QIBAKAB//")[7:-2]
		ibakab={}
		if res.decode() == '81AA' and int(res, 16) & int('00000040', 16) != 0:
			ibakab['activ_ibut_auth'] = True
		else:
			ibakab['activ_ibut_auth'] = False
		return ibakab
	def qibafab(self):
		res=self.execute_command("QIBAFAB//")[7:-2]
		ibafab={}
		if res.decode() == '82F8' and int(res, 16) & int('00000020', 16) != 0:
			ibafab['activ_ibut_notrec']=True
		else:
			ibafab['activ_ibut_notrec']=False
		return ibafab	
	
#read dvb behavior

	def read_driver_behavior(self):
		result = self.execute_command('QDVBSET//')
		result = result[7:-2]
		d_b = {}

		result_int = int(result[0:4], 16)
		d_b['enabled'] = (result_int & 0x8000) == 0

		acc_brake_ds = result_int & 0x0070
		d_b['acc_brake_data_source'] = acc_brake_ds == 0 and 1 or None

		analysis_interval = result_int & 0x0007
		d_b['analysis_interval'] = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8}.get(analysis_interval, None)

		result_int = int(result[4:8], 16)
		harsh_cornering = result_int & 0x7000
		d_b['cornering_data_source'] = harsh_cornering == 0 and 1 or None

		commands = [('QDVBIAB//', 'interval_ab_speed_threshold'), ('QDVBIBC//', 'interval_bc_speed_threshold'),
			('QDVBICD//', 'interval_cd_speed_threshold'), ('QDVBGAA//', 'interval_a_accel_threshold'),
			('QDVBGAB//', 'interval_b_accel_threshold'), ('QDVBGAC//', 'interval_c_accel_threshold'),
			('QDVBGAD//', 'interval_d_accel_threshold'), ('QDVBGBA//', 'interval_ab_brake_threshold'),
			('QDVBGBB//', 'interval_bc_brake_threshold'), ('QDVBGBC//', 'interval_cd_brake_threshold')]

		for cmd, attr in commands:
			result = self.execute_command( cmd)
			result = result[7:-2]
			result_int = int(result, 16)
			value = result_int % 10 >= 5 and (result_int / 10 + 1) or (result_int / 10)
			d_b[attr] = value

		return d_b

	#readtcoinfo
	def read_tco_info(self):
		tco = {
		'tcoins': self.qtcoins(),
		'tcoivh': self.qtcoivh(),
		'tcortc': self.qtcortc()
		}
		return tco
	
	def qtcoins(self):
		res= self.execute_command("QTCOINS//")[7:-2][0:2]
		tcoins={}
		if res:
			res = int(res, 16)
			tcoins['enabled'] = True if (res & 0x80) == 0 else False
		return tcoins	

	def qtcoivh(self):
		res=self.execute_command("QTCOIVH//")[7:-2]
		tcoivh={}
		if res and res != 'ERR':
			vehicle_settings = res.decode().split(',')
			try:
				tcoivh['VIN'] = vehicle_settings[0]
				tcoivh['VRN'] = vehicle_settings[1].strip()
				tcoivh['KFactor'] = str(int(vehicle_settings[2], 16))
			except Exception:
				pass
		return tcoivh	
	
	def qtcortc(self):
		res=self.execute_command("QTCORTC//")[7:-2]
		tcortc={}
		if res:
			try:
				result_drift_epoch = int(res[:4], 16)
				tcortc['TCODriftEpoch'] = result_drift_epoch
			except Exception:
				pass

			try:
				result_total_offset = int(res[4:8], 16)
				tcortc['TCOTotalOffset'] = result_total_offset
			except Exception:
				pass

			try:
				result_tco_panel = int(res[8:16], 16)
				tcortc['TCOPanelEpoch'] = result_tco_panel

				TCOType = bin(int(res[-4:], 16))[2:]
				tcortc['TCOType'] = TCOType[8:12]
				control_bits = TCOType[12:16]

				tcortc['TcoIgnitionBit0'] = True if control_bits[0] == '1' else False
				tcortc['EngineRPMBit1'] = True if control_bits[1] == '1' else False
				tcortc['TcoCalibrationErrorBit2'] = True if control_bits[2] == '1' else False
				tcortc['TcoTimeErrorBit3'] = True if control_bits[3] == '1' else False
			except Exception:
				pass

		return tcortc
	



	#read Led panel
	def read_led_panel(self):
		cmds = ['QPANINF//', 'QPANSET//', 'QPANOVS//', 'QPANHBA//', 'QPANGPI//', 'QPANSEO//', 'QPANFCI//']
		led = {}
		for cmd in cmds:
			result = self.execute_command(cmd)
			if cmd == 'QPANINF//':
				led_number = int(result[31:33][1:2])
				led['total_led'] = led_number
				led_panel_enabled = int(result[7:9], 16)
				led['enabled'] = (bin(led_panel_enabled)[2:].zfill(8)[0] != '1')
			elif cmd == 'QPANSET//':
				result_long = int(result[7:-2][:8], 16)
				led['enabled'] = (result_long & 0x80000000) == 0
				led['led_off_when_ignition_off'] = (result_long & 0x40000000) != 0
				led['adaptive_light_intensity'] = (result_long & 0x20000000) != 0
				led['io1_pull_up'] = (result_long & 0x00800000) != 0
				led['io3_pull_down'] = (result_long & 0x00400000) != 0
				led['io2_pull_down'] = (result_long & 0x00200000) != 0
				led['uart_enable'] = (result_long & 0x00100000) != 0
				led['bit3'] = (result_long & 0x0008000) != 0
				led['bit2'] = (result_long & 0x0004000) != 0
				led['bit1'] = (result_long & 0x0002000) != 0
				led['bit0'] = (result_long & 0x0001000) != 0
				led['light_level_threshold2'] = (result_long & 0x0000080) != 0
				led['light_level_threshold1'] = (result_long & 0x00000010) != 0
			else:
				result = int(result[7:-2], 16)
				if result != 0 and result <= led['total_led']:
					if cmd == 'QPANOVS//':
						led['overspeed'] = True
						led['overspeed_number'] = result
					elif cmd == 'QPANHBA//':
						led['harsh_breaking'] = True
						led['harsh_breaking_number'] = result
					elif cmd == 'QPANGPI//':
						led['gps_indicator'] = True
						led['gps_indicator_number'] = result
					elif cmd == 'QPANSEO//':
						led['stationary_engine_on'] = True
						led['stationary_engine_on_number'] = result
					elif cmd == 'QPANFCI//':
						led['first_crash_indicator'] = True
						led['first_crash_indicator_number'] = result
		return led

	#read canlog
	def read_canlog(self):
		canlog={
		'clgset':self.qclgset(),
		'clgpfn':self.qclgpfn(),
		'clfscp':self.qclfscp()	
		}
		return canlog

	def qclgset(self):
		res = self.execute_command("QCLGSET//")[7:-2]
		res=int(res[:4],16)
		canset={}
		canset['can_log.enabled'] = (res & 0x8000 == 0)
		return canset

	
	def qclgpfn(self):
		res = self.execute_command("QCLGPFN//")[7:-2].decode()
		clgpfn={
		'can_log.profile_name': res
		}
		return clgpfn

	def qclfscp(self):
		clgscp={}
		try:
			res= self.execute_command("QCLGSCP//")
			if res == '':
				return clgscp
			res = res[7:-2]
			if res.decode() != 'ERR':
				res = res[6:8] + res[4:6] + res[2:4] + res[0:2]
				clgscp['can_log.profile_code'] = int(res, 16)
		except (IOError) as e:
			#no profile installed
			pass



	#read fuel measurement
	def fuelmeasurement(self):
		fuel_m = {}
		fuel_m['qfueset'] = self.qfueset()
		fuel_m['qfuetac'] = self.qfuetac()
		fuel_m['qfuespi'] = self.qfuespi()
		fuel_m['qfuefrt'] = self.qfuefrt()
		fuel_m['qfuefrv'] = self.qfuefrv()
		return fuel_m

	def qfueset(self):

		res = self.execute_command('QFUESET//')[7:-2]
		res = int(res[:4], 16)
		qfueset =  {'enabled': (res & 0x8000) == 0}
		return qfueset

	def qfuetac(self):
		res = self.execute_command('QFUETAC//')[7:-2]
		qfuetac={
			'tank_volume': int(res, 16) / 10
		}
		return qfuetac

	def qfuespi(self):
		res = self.execute_command('QFUESPI//')[7:-2]
		if res:
			qfuespi = {
			'speed_int_A_limit':int(res[:4], 16) / 10,
			'speed_int_B_limit':int(res[4:8], 16) / 10,
			'speed_int_C_limit':int(res[8:12], 16) / 10
			}
		return qfuespi

	def qfuefrt(self):
		res = self.execute_command('QFUEFRT//')[7:-2]
		if res:
			fuel_rates = {}
			if res[:4].decode() != 'FFFF':
				fuel_rates['idle_fuel_rate'] = int(res[:4], 16) / 1820.4
			if res[4:8].decode() != 'FFFF':
				fuel_rates['int_A_fuel_rate'] = int(res[4:8], 16) / 65.536
			if res[8:12].decode() != 'FFFF':
				fuel_rates['int_B_fuel_rate'] = int(res[8:12], 16) / 65.536
			if res[12:16].decode() != 'FFFF':
				fuel_rates['int_C_fuel_rate'] = int(res[12:16], 16) / 65.536
		return fuel_rates

	def qfuefrv(self):
		res = self.execute_command('QFUEFRV//')
		res = res[7:-2]
		if res:
			fuel_counters = {}
			if res[:8].decode() != 'FFFFFFFF':
				fuel_counters['fuel_counter_total'] = int(res[:8], 16) / 100
		return fuel_counters

	# record 10x

	def qacqhgp(self):
		return self.qacq_rec10_gp('QACQHGP//')

	def qacqrgp(self):
		return self.qacq_rec10_gp('QACQRGP//')

	def qacqhti(self):
		return self.qacq_rec10_ti('QACQHTI//')

	def qacqrti(self):
		return self.qacq_rec10_ti('QACQRTI//')

	def qacqhtx(self):
		return self.qacq_rec10_tx('QACQHTX//')

	def qacqrtx(self):
		return self.qacq_rec10_tx('QACQRTX//')

	def qacqhss(self):
		return self.qacq_rec10_hs('QACQHSS//')

	def qacqrss(self):
		return self.qacq_rec10_hs('QACQRSS//')

	def qacqhgi(self):
		return self.qacq_rec10_gi('QACQHGI//')

	def qacqrgi(self):
		return self.qacq_rec10_gi('QACQRGI//')

	#generates the record 0x10 by calling its relevant methods
	def record10_local_net(self):
		rec10 = {}
		rec10['qacqhgp'] = self.qacqhgp()
		rec10['qacqhti'] = self.qacqhti()
		rec10['qacqhtx'] = self.qacqhtx()
		rec10['qacqhss'] = self.qacqhss()
		rec10['qacqhgi'] = self.qacqhgi()
		return rec10

	def record10_roam_net(self):
		rec10={}
		rec10['qacqrgp'] = self.qacqrgp()
		rec10['qacqrti'] = self.qacqrti()
		rec10['qacqrtx'] = self.qacqrtx()
		rec10['qacqrss'] = self.qacqrss()
		rec10['qacqrgi'] = self.qacqrgi()
		return rec10
	
	def qacq_rec10_gp(self, c):
		res = int(self.execute_command(c)[7:-2],16)
		acq_rec10_gp = {
			'acq': (res & 0x80000000) == 0,
			'cog_acq': (res & 0x40000000) != 0,
			'cog_acq_cnt_on': (res & 0x20000000) != 0,
			'cog_acq_ovrspd': (res & 0x10000000) != 0,
			'cnt_acq': (res & 0x08000000) != 0,
			'acq_int_a': (res & 0x04000000) != 0,
			'acq_int_a_cnt_on': (res & 0x02000000) != 0,
			'acq_int_a_ovrspd': (res & 0x01000000) != 0,
			'alarm_acq': (res & 0x00800000) != 0,
			'gps_val_acq': (res & 0x00400000) != 0,
			'acq_int_b_cnt_on': (res & 0x00200000) != 0,
			'acq_int_b_cnt_off': (res & 0x00100000) != 0,
			'rec_reset': (res & 0x00080000) != 0,
			'gen_trn_aft_acq': (res & 0x00040000) != 0
		}
		return acq_rec10_gp

	def qacq_rec10_ti(self, c):
		res = int(self.execute_command(c)[7:-2],16)
		acq_rec10_ti = {
			'acq_cog_min_time': res / 10,
		}
		return acq_rec10_ti

	def qacq_rec10_tx(self, c):
		res = int(self.execute_command(c)[7:-2],16)
		acq_rec10_tx = {
			'acq_cog_max_time': res / 10,
		}
		return acq_rec10_tx

	def qacq_rec10_hs(self, c):
		res = int(self.execute_command(c)[7:-2],16)
		acq_rec10_hs = {
			'acq_cog_min_sog': res / 10,
		}
		return acq_rec10_hs
	def qacq_rec10_gi(self, c):
		res = int(self.execute_command(c)[7:-2],16)
		acq_rec10_gi = {'acq_int_A': res / 10}
		return acq_rec10_gi
	def qacq_rec10_gb(self, c):
		res =self.execute_command(c)[7:-2]
		acq_rec10_gi = {}
		if res[:3].decode() == 'UNK':
			acq_rec10_gi['acq_int_B']: False
		else:
			res = int(res, 16)
			acq_rec10_gi['acq_int_B']: res / 10
		return acq_rec10_gi
	#record 0x11_commands
	def qacqhsp(self):
		return self.acq_rec11_sp('QACQHSP//')

	def qacqrsp(self):
		return self.acq_rec11_sp("QACQRSP//")
	
	def qacqhsi(self):
		return self.acq_rec11_si("QACQHSI//")
	
	def qacqrsi(self):
		return self.acq_rec11_si("QACQRSI//")
	
	#read the settings for record 0x11 by calling the relevant methods
	def record11_local_net(self):
		rec11={}
		rec11['qacqhsp'] = self.qacqhsp()
		rec11['qacqhsi'] = self.qacqhsi()

		return rec11
	def record11_roam_net(self):
		rec11={}
		rec11['qacqrsp'] = self.qacqrsp()
		rec11['qacqrsi'] = self.qacqrsi()

		return rec11

	def acq_rec11_si(self,c):
		res=int(self.execute_command(c)[7:-2],16)
		acq_si={
			"acq_interval": res / 10
		}
		return acq_si

	def acq_rec11_sp(self, c):
		res = int(self.execute_command(c)[7:-2],16)
		acq_sp = {
			'acq_enable': (res & 0x80000000) == 0,
			'contact_state': (res & 0x40000000) != 0,
			'preset_interval': (res & 0x20000000) != 0,
			'contact_on': (res & 0x10000000) != 0,
			'alarm_on': (res & 0x08000000) != 0,
			'alarm_changing': (res & 0x04000000) != 0,
			'gen_trans_after_acq': (res & 0x02000000) != 0
		}
		return acq_sp
	#record 0x12 commands

	def qacqhcp(self):
		return self.acq_rec12_cp("QACQHCP//")
	def qacqrcp(self):
		return self.acq_rec12_cp("QACQRCP//")
	def qacqhci(self):
		return self.acq_rec12_ci("QACQHCI//")
	def qacqrci(self):
		return self.acq_rec12_ci("QACQRCI//")
	
	#read the settings for record 0x12 by calling the relevant methods
	def record12_local_net(self):
		rec12={}
		rec12['qacqhcp'] = self.qacqhcp()
		rec12['qacqhci'] = self.qacqhci()

		return rec12
	def record12_roam_net(self):
		rec12={}
		rec12['qacqrcp'] = self.qacqrcp()
		rec12['qacqrci'] = self.qacqrci()

		return rec12

	def acq_rec12_ci(self,c):
		res=int(self.execute_command(c)[7:-2],16)
		acq_ci={
			"acq_interval": res
		}
		return acq_ci

	def acq_rec12_cp(self,c):
		res= int(self.execute_command(c)[7:-2],16)
		acq_cp={
			"acq_enable": ((res & 0x80000000) == 0),
			"contact_state": ((res & 0x40000000) != 0),
			"interval_acquisition": ((res & 0x20000000) != 0),
			"contact_on": ((res & 0x10000000) != 0),
			"contact_off": ((res & 0x08000000) != 0),
			"work_private": ((res & 0x04000000) != 0),
			"gen_trans_after_acq": ((res & 0x02000000) != 0)
		}
		return acq_cp
	#record 0x13 commands
	def qacqhrp(self):
		return self.acq_rec13_rp("QACQHRP//")

	def qacqrrp(self):	
		return self.acq_rec13_rp("QACQHRP//")
	

	def acq_rec13_rp(self,c):
		res=int(self.execute_command(c)[7:-2],16)
		acq_rp = {
		'acq_enable': (res & 0x80000000) == 0,
		'daily_acq': (res & 0x40000000) != 0,
		'monthly_acq': (res & 0x20000000) != 0,
		'gen_trans_after_acq': (res & 0x10000000) != 0
		}
		return acq_rp
	def record13_local_net(self):
		rec13={}
		rec13['qacqhrp'] = self.qacqhrp()
		return rec13
	def record13_roam_net(self):
		rec13={}
		rec13['qacqrrp'] = self.qacqrrp()
		return rec13
	#record 0x14 commands
	def qacqhmp(self):
		return self.acq_rec14_mp("QACQHMP//")

	def qacqrmp(self):	
		return self.acq_rec14_mp("QACQHMP//")
	

	def acq_rec14_mp(self,c):
		res=self.execute_command(c)
		res=int(res[7:-2],16)
		acq_mp = {
			"ignition_change": (res & 0x40000000) != 0,
			"mccmnc_change": (res & 0x20000000) != 0,
			"lac_change": (res & 0x10000000) != 0,
			"cid_change": (res & 0x08000000) != 0,
			"gsm_registered_change": (res & 0x04000000) != 0,
			"roaming_status_change": (res & 0x02000000) != 0,
			"gen_trans_after_acq": (res & 0x01000000) != 0,
		}
		return acq_mp
	def record14_local_net(self):
		rec14={}
		rec14['qacqmrp'] = g4ngps.qacqhmp(self)
		return rec14
	def record14_roam_net(self):
		rec14={}
		rec14['qacqmrp'] = g4ngps.qacqrmp(self)
		return rec14
	#record 0x15 commands
	def qacqhdp(self):
		c="QACQHDP//"
		return g4ngps.acq_rec15_dp(self,c)
	def qacqrdp(self):
		c="QACQRDP//"
		return g4ngps.acq_rec15_dp(self,c)
	def qacqhip(self):
		c="QACQHIP//"
		return g4ngps.acq_rep15_ip(self,c)
	def qacqrip(self):
		c="QACQRIP//"
		return g4ngps.acq_rep15_ip(self,c)
	def acq_rec15_dp(self,c):
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		acq_dp = {
		'acq_enabled': (res & 0x80000000) == 0,
		'contact_state': (res & 0x40000000) != 0,
		'work_private': (res & 0x20000000) != 0,
		'interval_acquisition': (res & 0x10000000) != 0,
		'contact_on': (res & 0x08000000) != 0,
		'contact_off': (res & 0x04000000) != 0,
		'gen_trans_after_acq': (res & 0x02000000) != 0
		}
		return acq_dp
	def acq_rep15_ip(self,c):
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		acq_dp={
			"acq_interval": (res & 0xffff)
		}
		return acq_dp
	def record15_local_net(self):
		rec15={}
		rec15['qacqhdp'] = g4ngps.qacqhdp(self)
		rec15['qacqhip'] = g4ngps.qacqhip(self)
		return rec15
	def record15_roam_net(self):
		rec15={}
		rec15['qacqrdp'] = g4ngps.qacqrdp(self)
		rec15['qacqrip'] = g4ngps.qacqrip(self)
		return rec15
	#record 0x16 commands
	def qacqhia(self):
		c="QACQHIA//"
		return g4ngps.acq_rec16_ia(self,c)
	def qacqria(self):
		c="QACQRIA//"
		return g4ngps.acq_rec16_ia(self,c)
	def acq_rec16_ia(self, c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_ia = {
			"acq_enable": (res & 0x80000000) == 0,
			"contact": (res & 0x40000000) != 0,
			"gen_trans_after_acq": (res & 0x20000000) != 0
			}
			return acq_ia
	def record16_local_net(self):
		rec16={}
		rec16["qacqhia"] = g4ngps.qacqhia(self)
		return rec16
	def record16_roam_net(self):
		rec16={}
		rec16["qacqria"] = g4ngps.qacqria(self)
		return rec16
	#record 0x17 commands
	def qacqhib(self):
		c="QACQHIB//"
		return g4ngps.acq_rec17_ib(self,c)
	def qacqrib(self):
		c="QACQRIB//"
		return g4ngps.acq_rec17_ib(self,c)
	def acq_rec17_ib(self, c):
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		acq_ib = {
		"acq_enable": (res & 0x80000000) == 0,
		}
		return acq_ib
	def record17_local_net(self):
		rec17={}
		rec17["qacqhib"] = g4ngps.qacqhib(self)
		return rec17
	def record17_roam_net(self):
		rec17={}
		rec17["qacqrib"] = g4ngps.qacqrib(self)
		return rec17
	#record 0x18 commands
	
	def qacqhio(self):
		return g4ngps.acq_rec18_io(self,"QACQHIO//")
	
	def qacqrio(self):
		return g4ngps.acq_rec18_io(self,"QACQRIO//")
	
	def acq_rec18_io(self,c):
		res = g4ngps.execute_command(self,c)
		print(res)
		if res[7:-2].decode()=="LIC":
			print("no lic")
			return "No License"
		else:
			res = int(res[7:-2], 16)	
			acq_io={
				'acq' : res & 0x80000000 == 0,
				'tmr_filt' : res & 0x40000000 != 0,
				'gen_trans_after_acq' : res & 0x20000000 != 0,
				'int_a_acq' : res & 0x00800000 != 0,
				'int_a_w_contact_on_acq' : res & 0x00400000 != 0,
				'int_a_w_contact_off_acq' : res & 0x00200000 != 0,
				'int_b_acq' : res & 0x00100000 != 0,
				'int_b_w_contact_on_acq' : res & 0x00080000 != 0,
				'int_b_w_contact_off_acq' : res & 0x00040000 != 0,
				'contact_acq_off_on' : res & 0x00020000 != 0,
				'contact_acq_on_off' : res & 0x00010000 != 0,
				'over_io1_threshold' : res & 0x00008000 != 0,
				'under_io1_threshold' : res & 0x00004000 != 0,
				'over_io2_threshold' : res & 0x00002000 != 0,
				'under_io2_threshold' : res & 0x00001000 != 0,
				'over_io3_threshold' : res & 0x00000800 != 0,
				'under_io3_threshold' : res & 0x00000400 != 0,
				'over_io4_threshold' : res & 0x00000200 != 0,
				'under_io4_threshold' : res & 0x00000100 != 0,
				'over_vin_threshold' : res & 0x00000080 != 0,
				'under_vin_threshold' : res & 0x00000040 != 0
			}
			return acq_io
	def	qacqhoa(self):
		return g4ngps.acq_rec18_oa(self,"QACQHOA//")

	def qacqroa(self):
		return g4ngps.acq_rec18_oa(self,"QACQROA//")

	def acq_rec18_oa(self,c):
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		acq_oa={
			"acq_interval_A": (res & 0xffff) /10
		}	
		return acq_oa
	
	def qacqhob(self):
		return g4ngps.acq_rec18_ob(self,"QACQHOB//")

	def qacqrob(self):
		return g4ngps.acq_rec18_ob(self,"QACQROB//")
	
	def acq_rec18_ob(self,c):
		res = g4ngps.execute_command(self,c)
		res = int(res[7:-2],16)
		acq_ob={
			"acq_interval_B": (res & 0xffff) /10
		}	
		return acq_ob	

	def qacqit1(self):
		res=g4ngps.execute_command(self,"QACQIT1//")
		res=int(res[7:-2],16) &0xffff
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_it1={
		"acq_io1_threshold": f
		}
		return acq_it1
	
	def qacqit2(self):
		res=g4ngps.execute_command(self,"QACQIT2//")
		res=int(res[7:-2],16) &0xffff
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_it2={
		"acq_io2_threshold": f
		}
		return acq_it2
	
	def qacqit3(self):
		res=g4ngps.execute_command(self,"QACQIT3//")
		res=int(res[7:-2],16) &0xffff
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_it3={
		"acq_io3_threshold": f
		}
		return acq_it3
	
	def qacqit4(self):
		res=g4ngps.execute_command(self,"QACQIT4//")
		res=int(res[7:-2],16) &0xffff
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_it4={
		"acq_io4_threshold": f
		}
		return acq_it4
	def qacqitv(self):
		res=g4ngps.execute_command(self,"QACQITV//")
		res=int(res[7:-2],16) &0xffff
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_itv={
		"acq_volt_in_threshold": f
		}
		return acq_itv
	
	def qacqitt(self):
		res=g4ngps.execute_command(self,"QACQITT//")
		res=int(res[7:-2],16) &0xffff /10
		acq_itt={
		"acq_time_filter_threshold": res
		}
		return acq_itt

	def record18_local_net(self):
		record18={}
		record18["acq_io"] = g4ngps.qacqhio(self)
		record18["acq_oa"] = g4ngps.qacqhoa(self)
		record18["acq_ob"] = g4ngps.qacqhob(self)
		record18["acqit1"] = g4ngps.qacqit1(self)
		record18["acqit2"] = g4ngps.qacqit2(self)
		record18["acqit3"] = g4ngps.qacqit3(self)
		record18["acqit4"] = g4ngps.qacqit4(self)
		record18["acqitv"] = g4ngps.qacqitv(self)
		record18["acqitt"] = g4ngps.qacqitt(self)
		return record18

	def record18_roam_net(self):
		record18={}
		record18["acq_io"] = g4ngps.qacqrio(self)
		record18["acq_oa"] = g4ngps.qacqroa(self)
		record18["acq_ob"] = g4ngps.qacqrob(self)
		record18["acqit1"] = g4ngps.qacqit1(self)
		record18["acqit2"] = g4ngps.qacqit2(self)
		record18["acqit3"] = g4ngps.qacqit3(self)
		record18["acqit4"] = g4ngps.qacqit4(self)
		record18["acqitv"] = g4ngps.qacqitv(self)
		record18["acqitt"] = g4ngps.qacqitt(self)
		return record18
		#_iorecord 0x19 commands
	
	def qacqhpr(self):
		c="QACQHPR//"
		return g4ngps.acq_rec19_pr(self,c)

	def qacqrpr(self):
		c="QACQRPR//"
		return g4ngps.acq_rec19_pr(self,c)

	def acq_rec19_pr(self, c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_pr = {
				"acq_enable": ((res & 0x80000000) == 0),
				"param_changed": ((res & 0x40000000) != 0),
				"param_interrogated": ((res & 0x20000000) != 0),
				"command_issued": ((res & 0x10000000) != 0),
				"gen_trans_after_acq": ((res & 0x08000000) != 0)
			}
			return acq_pr

	def record19_local_net(self):
		rec19={}
		rec19["qacqhpr"] = g4ngps.qacqhpr(self)
		return rec19
	def record19_roam_net(self):
		rec19={}
		rec19["qacqrpr"] = g4ngps.qacqrpr(self)
		return rec19
		#record 0x1A commands
	def qacqhev(self):
		c="QACQHEV//"
		return g4ngps.acq_rec1A_ev(self,c)
	def qacqrev(self):
		c="QACQREV//"
		return g4ngps.acq_rec1A_ev(self,c)
	def acq_rec1A_ev(self, c):
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		acq_ev = {
			"acq_enable": (res & 0x80000000) == 0,
			"ignition": (res & 0x40000000) != 0,
			"event_c1": (res & 0x20000000) != 0,
			"event_c2": (res & 0x10000000) != 0,
			"gen_trans_after_acq": (res & 0x08000000) != 0,
			"int_a_when_contact_on_acq": (res & 0x00800000) != 0,
			"int_a_when_contact_off_acq": (res & 0x00400000) != 0,
			"int_b_when_contact_on_acq": (res & 0x00200000) != 0,
			"int_b_when_contact_off_acq": (res & 0x00100000) != 0
		}	
		return acq_ev
	def qacqheb(self):
		return g4ngps.acq_rec1A_eb(self,"QACQHEB//")
	def qacqreb(self):
		return g4ngps.acq_rec1A_eb(self,"QACQREB//")
	
	def acq_rec1A_eb(self,c):
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		acq_eb={
			"interval_B" :res & 0xffff
		}
		return acq_eb
	
	def qacqhea(self):
		return g4ngps.acq_rec1A_ea(self,"QACQHEB//")
	def qacqrea(self):
		return g4ngps.acq_rec1A_ea(self,"QACQREB//")
	
	def acq_rec1A_ea(self,c):
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		acq_ea={
			"interval_A" :res & 0xffff
		}
		return acq_ea
	def record1A_local_net(self):
		rec1A={}
		rec1A["qacqhev"] = g4ngps.qacqhev(self)
		rec1A["qacqheb"] = g4ngps.qacqheb(self)
		rec1A["qacqhea"] = g4ngps.qacqhea(self)
		return rec1A
	
	def record1A_roam_net(self):
		rec1A={}
		rec1A["qacqrev"] = g4ngps.qacqrev(self)
		rec1A["qacqreb"] = g4ngps.qacqreb(self)
		rec1A["qacqrea"] = g4ngps.qacqrea(self)
		return rec1A
	
	#record 0x1B commands
	def qacqhs1(self):
		return g4ngps.acq_rec1B_s1(self,"QACQHS1//")
	def qacqrs1(self):
		return g4ngps.acq_rec1B_s1(self,"QACQRS1//")
	def acq_rec1B_s1(self,c):
		res=g4ngps.execute_command(self,c)
		res=int(res[7:-2],16)
		acq_s1 = {
			"acq_enable": (res & 0x80000000) == 0,
			"ignition": (res & 0x40000000) != 0,
			"state_counter_1": (res & 0x20000000) != 0,
			"gen_trans_after_acq": (res & 0x10000000) != 0
		}
		return acq_s1
	def record1B_local_net(self):
		rec1b={}
		rec1b["qacqhs1"] = g4ngps.qacqhs1(self)
		return rec1b
	def record1B_roam_net(self):
		rec1b={}
		rec1b["qacqrs1"] = g4ngps.qacqrs1(self)
		return rec1b
	#record 0x1C commands
	def qacqhs2(self):
		return g4ngps.acq_rec1C_s2(self,"QACQHS2//")
	def qacqrs2(self):
		return g4ngps.acq_rec1C_s2(self,"QACQRS2//")
	def acq_rec1C_s2(self,c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_s2 = {
				"acq_enable": (res & 0x80000000) == 0,
				"ignition": (res & 0x40000000) != 0,
				"state_counter_2": (res & 0x20000000) != 0,
				"gen_trans_after_acq": (res & 0x10000000) != 0
			}
			return acq_s2
	def record1C_local_net(self):
		rec1c={}
		rec1c["qacqhs2"] = g4ngps.qacqhs2(self)
		return rec1c
	def record1C_roam_net(self):
		rec1c={}
		rec1c["qacqrs2"] = g4ngps.qacqrs2(self)
		return rec1c
	
	#record 0x1D commands
	def qacqhsf(self):
		return g4ngps.acq_rec1D_sf(self,"QACQHSF//")
	def qacqrsf(self):
		return g4ngps.acq_rec1D_sf(self,"QACQRSF//")
	def acq_rec1D_sf(self,c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_sf = {
				"acq_enable": (res & 0x80000000) == 0,
				"ignition": (res & 0x40000000) != 0,
				"state_work_private_mode": (res & 0x20000000) != 0,
				"gen_trans_after_acq": (res & 0x10000000) != 0
			}
			return acq_sf
	def record1D_local_net(self):
		rec1d={}
		rec1d["qacqhsf"] = g4ngps.qacqhsf(self)
		return rec1d
	def record1D_roam_net(self):
		rec1d={}
		rec1d["qacqrsf"] = g4ngps.qacqrsf(self)
		return rec1d
	#record 0X1E commands
	def qacqhwp(self):
		return g4ngps.acq_rec1E_wp(self,"QACQHWP//")
	def qacqrwp(self):
		return g4ngps.acq_rec1E_wp(self,"QACQRWP//")
	def acq_rec1E_wp(self,c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_wp = {
			"acq": (res & 0x80000000) == 0,
			"ignition_state": (res & 0x40000000) != 0,
			"work_private": (res & 0x20000000) != 0,
			"interval_acq_ignition_on": (res & 0x10000000) != 0,
			"interval_acq_ignition_off": (res & 0x08000000) != 0,
			"interval_acq_work": (res & 0x04000000) != 0,
			"interval_acq_private": (res & 0x02000000) != 0,
			"gen_trans_after_acq": (res & 0x01000000) != 0,
			}
			return acq_wp
	def qacqhwi(self):
		return g4ngps.acq_rec1E_wi(self,"QACQHWI//")
	def qacqrwi(self):
		return g4ngps.acq_rec1E_wi(self,"QACQRWI//")

	def acq_rec1E_wi(self,c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_wi={
				"acq_interval": res & 0xffff
			}
			return acq_wi

	def record1E_local_net(self):
		rec1e={}
		rec1e["qacqhwp"] = g4ngps.qacqhwp(self)
		rec1e["qacqhwi"] = g4ngps.qacqhwi(self)
		return rec1e
	def record1E_roam_net(self):
		rec1e={}
		rec1e["qacqrwp"] = g4ngps.qacqrwp(self)
		rec1e["qacqrwi"] = g4ngps.qacqrwi(self)
		return rec1e
#record 0X1F commands
	def qacqhdw(self):
		return g4ngps.acq_rec1F_dw(self,"QACQHDW//")
	def qacqrdw(self):
		return g4ngps.acq_rec1F_dw(self,"QACQRDW//")
	def acq_rec1F_dw(self,c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_dw = {
				"acq_enable": (res & 0x80000000) == 0,
				"acq_rtcgps_synch_reset": (res & 0x40000000) != 0,
				"acq_rtcgps_synch": (res & 0x20000000) != 0,
				"acq_reset": (res & 0x10000000) != 0
			}
			return acq_dw	
	def record1F_local_net(self):
		rec1e={}
		rec1e["qacqhdw"] = g4ngps.qacqhdw(self)
		return rec1e
	def record1F_roam_net(self):
		rec1e={}
		rec1e["qacqrdw"] = g4ngps.qacqrdw(self)
		return rec1e
#record 0x20 commands
	def qacqhdb(self):
		return g4ngps.acq_rec20_db(self,"QACQHDB//")
	def qacqrdb(self):
		return g4ngps.acq_rec20_db(self,"QACQRDB//")

	def acq_rec20_db(self,c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_db={
			"acq_enable": (res & 0x80000000) == 0,
			"acq_ign_chg": (res & 0x40000000) != 0,
			"acq_evt_chg": (res & 0x20000000) != 0
			}
			return acq_db
	def record20_local_net(self):
		rec20={}
		rec20["qacqhdb"] = g4ngps.qacqhdb(self)
		return rec20
	def record20_roam_net(self):
		rec20={}
		rec20["qacqrdb"] = g4ngps.qacqrdb(self)
		return rec20
#record 0x21 commands
	def qacqhfu(self):
		return g4ngps.acq_rec21_fu(self, "QACQHFU//")
	def qacqrfu(self):
		return g4ngps.acq_rec21_fu(self, "QACQRFU//")
	def acq_rec21_fu(self,c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_rec21={
				"acq": (res & 0x80000000) == 0,
				"ign_change": (res & 0x40000000) != 0,
				"epoch_int_on": (res & 0x20000000) != 0,
				"epoch_int_off": (res & 0x10000000) != 0,
				"work_priv_acq": (res & 0x0800000) != 0,
				"acq_after_reset": (res & 0x04000000) != 0,
				"gen_trans_acq": (res & 0x02000000) != 0,
				"acq_ibutton_auth": (res & 0x01000000) != 0,
				"acq_delta_sens_change": (res & 0x00800000) != 0
			}
			return acq_rec21
	def record21_local_net(self):
		rec21={}
		rec21["qacqhfu"] = g4ngps.qacqhfu(self)
		return rec21
	def record21_roam_net(self):
		rec21={}
		rec21["qacqrfu"] = g4ngps.qacqrfu(self)
		return rec21
#record 0x23and0x24
	def qacqhdb(self):
		return g4ngps.acq_rec23and24_db(self,"QACQHDB//")
	def qacqhdb(self):
		return g4ngps.acq_rec23and24_db(self,"QACQRDB//")
	def acq_rec23and24_db(self,c):
		res=g4ngps.execute_command(self,c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_rec23and24={
				"acq": (res & 0x80000000) == 0,
				"acq_ign_chg": (res & 0x40000000) != 0,
				"acq_evt_chg": (res & 0x20000000) != 0,
				"acq_eco_drv_rec_en": (res & 0x00008000) == 0,
				"acq_overbrk_det_evt": (res & 0x00004000) != 0,
				"acq_fuel_rate_det_evt": (res & 0x00002000) != 0,
				"acq_eng_overload_det_evt": (res & 0x00001000) != 0
			}
			return acq_rec23and24
	def record23and24_local_net(self):
		rec23and24={}
		rec23and24["qacqhdb"] = g4ngps.qacqhdb(self)
		return rec23and24
	def record23and24_roam_net(self):
		rec23and24={}
		rec23and24["qacqrdb"] = g4ngps.qacqrdb(self)
		return rec23and24	
#record 0x25		
	def qacqetr(self):
		res=self.execute_command("QACQETR//")
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_rec25={
				"event_tracer_enabled": (res & 0x80000000) == 0,
				"acq_enable":res & 0x80000000 == 0,
				"acquisition_at_driver_behavior_event_change": (res & 0x40000000) != 0,
			}
			return acq_rec25
	def record25(self):
		rec25={}
		rec25["record_25"] = g4ngps.qacqetr(self)
		return rec25
#record0x40and0x41	
	def qacqtco(self):
		res=g4ngps.execute_command(self,"QACQTCO//")
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=res[7:-2]
			res_1st=int(res[0:8],16)
			acqtco={
				"acq": ((res_1st & 0x80000000) == 0),
				"dis_acq_not_perf": ((res_1st & 0x40000000) != 0),
				"trig_drvreq_drv1_ws": ((res_1st & 0x00800000) != 0),
				"trig_drvreq_drv2_ws": ((res_1st & 0x00400000) != 0),
				"trig_drvreq_recog_state": ((res_1st & 0x00200000) != 0),
				"trig_drvreq_ignition": ((res_1st & 0x00100000) != 0),
				"trig_vehreq_drv1_ws": ((res_1st & 0x00080000) != 0),
				"trig_vehreq_drv2_ws": ((res_1st & 0x00040000) != 0),
				"trig_vehreq_recog_state": ((res_1st & 0x00020000) != 0),
				"trig_vehreq_ignition": ((res_1st & 0x00010000) != 0),
				"trig_drvreq_drv1_timestate": ((res_1st & 0x00008000) != 0),
				"trig_drvreq_drv1_cardstate": ((res_1st & 0x00004000) != 0),
				"trig_drvreq_drv1_overspeed_state": ((res_1st & 0x00002000) != 0),
				"trig_drvreq_drv2_timestate": ((res_1st & 0x00001000) != 0),
				"trig_drvreq_drv2_cardstate": ((res_1st & 0x00000800) != 0),
				"trig_drvreq_motor_state": ((res_1st & 0x00000400) != 0),
				"trig_drvreq_tco_perf_state": ((res_1st & 0x00000200) != 0),
				"trig_drvreq_tco_dir_state": ((res_1st & 0x00000100) != 0),
				"trig_vehreq_drv1_time_state": ((res_1st & 0x00000080) != 0),
				"trig_vehreq_drv1_card_state": ((res_1st & 0x00000040) != 0),
				"trig_vehreq_drv1_overspeed_state": ((res_1st & 0x00000020) != 0),
				"trig_vehreq_drv2_time_state": ((res_1st & 0x00000010) != 0),
				"trig_vehreq_drv2_card_state": ((res_1st & 0x00000008) != 0),
				"trig_vehreq_motorstate": ((res_1st & 0x00000004) != 0),
				"trig_vehreq_tco_perf_state": ((res_1st & 0x00000002) != 0),
				"trig_vehreq_tco_dir_state":((res_1st & 0x00000001) != 0)
			}
			if res[8:16].decode()!="":
				res_2nd=int(res[8:16],16)
				acqtco["drvEpochIgnOnAcq"] = (res_2nd & 0x80000000) != 0
				acqtco["vehEpochIgnOnAcq"] = (res_2nd & 0x40000000) != 0
			return acqtco
	def qacqtci(self):
		res=g4ngps.execute_command(self,"QACQTCI//")
		if res[7:-2].decode()=="LIC":
			return "No License"
		elif res[7:-2].decode()=="":
			return None
		else:
			res=int(res[7:-2],16)
			acqtci={}
			acqtci["acq_interval"] = res & 0xffff
	def record40and41(self):
		rec40and41={}
		rec40and41["qacqtco"] = g4ngps.qacqtco(self)
		rec40and41["qacqtci"] = g4ngps.qacqtci(self)
		return rec40and41