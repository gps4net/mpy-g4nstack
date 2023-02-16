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

	# SYS subsystem: main system

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

	# set esp32 real time clock from qsysinf
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

	# sim selector
	def qgprsim(self):
		res = self.execute_command('QGPRSIM//')
		sr = res[7:-2]
		gprsim = {}
		if len(sr) == 2:
			si = int(sr, 16)
			if si == 0x00:
				gprsim['sim_sel'] = 'ext_sim'
			elif si == 0x20:
				gprsim['sim_sel'] = 'int_sim'
			elif si == 0x40:
				gprsim['sim_sel'] = 'ext_sim_fb_int'
			elif si == 0x60:
				gprsim['sim_sel'] = 'ext_sim_to_int'
			elif si == 0x80:
				gprsim['sim_sel'] = 'ext_sim_h_int_r'
		elif len(sr) == 3 and sr == b'LIC':
			gprsim = { 'lic': True }
		return gprsim

	# apn selector
	def qgprmct(self):
		res = self.execute_command('QGPRMCT//')
		av = 0x3000 & int(res[7:11], 16)
		qgprmct = {}
		if av == 0x0000:
			qgprmct['apn'] = 'pri'
		if av == 0x1000:
			qgprmct['apn'] = 'lst'
		if av == 0x2000:
			qgprmct['apn'] = 'sec'
		return qgprmct

	# primary apn
	def qgprgma(self):
		res = self.execute_command('QGPRGMA//')
		gprgma = { 'pri_apn': res[7:-2].decode() }
		return gprgma

	# primary apn username
	def qgprgmu(self):
		res = self.execute_command('QGPRGMU//')
		gprgmu = {' pri_apn_usr': res[7:-2].decode() }
		return gprgmu

	# primary apn password
	def qgprgmp(self):
		res = self.execute_command('QGPRGMP//')
		gprgmp = { 'pri_apn_pwd': res[7:-2].decode() }
		return gprgmp

	# secondary apn
	def qgprgsa(self):
		res = self.execute_command('QGPRGSA//')
		gprgsa = { 'sec_apn': res[7:-2].decode() }
		return gprgsa

	# secondary apn user
	def qgprgsu(self):
		res = self.execute_command('QGPRGSU//')
		gprgsu = { 'sec_apn_usr': res[7:-2].decode() }
		return gprgsu

	# secondary apn passowrd
	def qgprgsp(self):
		res = self.execute_command('QGPRGSP//')
		gprgsp = { 'sec_apn_pwd': res[7:-2].decode() }
		return gprgsp

	# apn params
	def qgprgms(self):
		res = self.execute_command('QGPRGMS//')
		gms = res[7:-2].decode().split(',')
		gprgms = {
			'pri_apn': gms[0],
			'pri_apn_usr': gms[1],
			'pri_apn_pwd': gms[2],
			'sec_apn': gms[3],
			'sec_apn_usr': gms[4],
			'sec_apn_pwd': gms[5]
		}
		return gprgms

	# remote server name
	def qgprgrs(self):
		res = self.execute_command('QGPRGRS//')
		gprgrs = { 'rem_srv': res[7:-2].decode() }
		return gprgrs

	# remote server port
	def qgprgrp(self):
		res = self.execute_command('QGPRGRP//')
		gprgrp = { 'rem_srv_prt': res[7:-2].decode() }
		return gprgrp

	# upgrade server name
	def qgprgus(self):
		res = self.execute_command('QGPRGUS//')
		gprgus = { 'upg_srv': res[7:-2].decode() }
		return gprgus

	# upgrade server port
	def qgprgup(self):
		res = self.execute_command('QGPRGUP//')
		gprgup = { 'upg_srv_prt': res[7:-2].decode() }
		return gprgup

	# backup server name
	def qgprgbs(self):
		res = self.execute_command('QGPRGBS//')
		gprgbs = { 'bkp_srv': res[7:-2].decode() }
		return gprgbs

	# backup server port
	def qgprgbp(self):
		res = self.execute_command('QGPRGBP//')
		gprgbp = { 'bkp_srv_prt': res[7:-2].decode() }
		return gprgbp

	# sim manager internal sim timeout [min]
	def qgprist(self):
		res = self.execute_command('QGPRIST//')
		gprist = { 'int_sim_to': int(res[7:-2], 16) }
		return gprist

	# sim manager external sim timeout [min]
	def qgprcth(self):
		res = self.execute_command('QGPRCTH//')
		gprcth = { 'ext_sim_to': int(res[7:-2], 16) }
		return gprcth

	# external sim traffic limit
	def qgprxtt(self):
		res = self.execute_command('QGPRXTT//')
		gprxtt = { 'ext_sim_tfc_lim': int(res[7:15], 16) }
		return gprxtt

	# internal sim traffic limit
	def qgprctt(self):
		res = self.execute_command('QGPRCTT//')
		gprctt = { 'int_sim_tfc_lim': int(res[7:15], 16) }
		return gprctt

	# query gprs traffic counters
	def qgprtrc(self):
		res = self.execute_command('QGPRTRC//')
		gprtrc = {
			'ext_sim_tot_tfc': int(res[7:11], 16),
			'int_sim_tot_tfc': int(res[11:15], 16),
			'ext_sim_mth_tfc': int(res[15:19], 16),
			'int_sim_mth_tfc': int(res[19:23], 16),
			'ext_sim_dly_tfc': int(res[23:27], 16),
			'int_sim_dly_tfc': int(res[27:31], 16),
			'ext_sim_tot_att': int(res[31:33], 16),
			'int_sim_tot_att': int(res[33:35], 16),
			'ext_sim_tot_conn': int(res[35:38], 16),
			'int_sim_tot_conn': int(res[38:41], 16),
		}
		return gprtrc

	# gprs waiting threshold for sending data
	def qgprthw(self):
		res = self.execute_command('QGPRTHW//')
		gprthw = { 'gprs_dla_th': int(res[7:11], 16) }
		return gprthw

	# reset traffic counters
	def cgprtcs(self, id):
		if (not re.match('^[a-fA-F0-9]+$', id)):
			return None
		res = self.execute_command('CGPRTCS{:04d}//'.format(int(id, 16)))
		return res[7:10]

	# use primary apn
	def cgprupa(self):
		res = self.execute_command('CGPRUPA//')
		return res[7:10]

	# use ceondary apn
	def cgprusa(self):
		res = self.execute_command('CGPRUSA//')
		return res[7:10]

	# GPS subsystem

	# gps information
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
				'gps_dst': int(res[73:81], 16),
				'gps_trp_dst': int(res[81:89], 16)
			}
			inavstat = int(gpsinf['navstat'], 16)
			gpsinf['alt'] *= inavstat & 0x80 >> 7
			gpsinf['lat'] *= inavstat & 0x40 >> 6
			gpsinf['lon'] *= inavstat & 0x20 >> 5
			gpsinf['nst'] = inavstat & 0x10 >> 4
			gpsinf['navst'] = inavstat & 0x0f
			return gpsinf

	# gps settings
	def qgpsset(self):
		res = self.execute_command('QGPSSET//')
		ri = int(res[7:11], 16)
		gpsset = {
			'pwr_save': (ri & 0x8000 != 0),
			'sbas_ena': (ri & 0x4000 != 0),
			'gps_upd': (ri & 0x2000 != 0),
			'gps_fltr': (ri & 0x1000 == 0),
			'trans_vld': (ri & 0x0800 == 0),
			'acc_vld': (ri & 0x0400 == 0),
			'inv_pos_pvt': (ri & 0x0200 != 0),
			'vld_pos_prot ': (ri & 0x0100 != 0)
		}
		return gpsset

	# exhaustive filter space vehicle threshold
	def qgpsefn(self):
		res = self.execute_command('QGPSEFN//')
		gpsefn = { 'gus_th': int(res[7:-2], 16) }
		return gpsefn

	# exhaustive filter pdop threshold
	def qgpsefp(self):
		res = self.execute_command('QGPSEFP//')
		gpsefp = { 'pdop_th': int(res[7:9], 16) + 0.1*int(res[9:11], 16) }
		return gpsefp

	# exhaustive filter speed threshold [km/h]
	def qgpsefs(self):
		res = self.execute_command('QGPSEFS//')
		gpsefs = { 'spd_th': int(res[7:11]) }
		return gpsefs

	# acceleration threshold [km/h/s]
	def qgpsact(self):
		res = self.execute_command('QGPSACT//')
		gpsact = { 'acc_th': int(res[7:11]) }
		return gpsact

	# minimum speed threshold [km/h]
	def qgpssgt(self):
		res = self.execute_command('QGPSSGT//')
		gpssgt = { 'spd_min_th': int(res[7:11]) }
		return gpssgt

	# odometer and trip distance value
	def qgpsdis(self):
		res = self.execute_command('QGPSDIS//')
		gpsdis = {
			'gps_dst': int(res[7:15], 16),
			'gps_trp_dst': int(res[15:23])
		}
		return gpsdis

	def qgpspdc(self):
		res = self.execute_command('QGPSPDC//')
		gpspdc = {
			'pvt_dst': int(res[7:15], 16),
		}
		return gpspdc

	# gps restart time threshold [sec]
	def qgpsttr(self):
		res = self.execute_command('QGPSTTR//')
		gpsttr = {
			'gps_rst_th': int(res[7:11], 16),
		}
		return gpsttr

	# reset distance counters
	def cgpsdrs(self, id):
		if (not re.match('^[a-fA-F0-9]+$', id)):
			return None
		res = self.execute_command('CGPSDRS{:04d}//'.format(int(id, 16)))
		return res[7:10]

	# DFL subsystem: dataflash

	# dataflash info
	def qdflinf(self):
		res = self.execute_command('QDFLINF//')
		dlfinf = {
			'dlf_rec': int(res[7:13], 16),
			'dlf_tot_rec': int(res[13:19], 16)
		}
		return dlfinf

	# clear dirty bit
	def cdfledb(self):
		res = self.execute_command('CDFLEDB//')
		return res[7:10]

	# clear erase bit
	def cdfleeb(self):
		res = self.execute_command('CDFLEEB//')
		return res[7:10]

	# insert record in dataflash
	def cdflwrc(self, data):
		if (len(data) != 64 and not re.match('^[a-fA-F0-9]+$', data)):
			return None
		res = self.execute_command('CDFLWRC{:s}//'.format(data))
		return res[7:10]

	# DIO subsystem: data I/O

	# data io information
	def qdioinf(self):
		res = self.execute_command('QDIOINF//')
		qdioinf = {
			'io_alloc': res[7:71],
			'ign_opt': res[71:79],
			'panic_opt': res[79:87],
			'rly_opt': res[87:95],
			'ext_opt': res[95:99],
			'ec_opt': res[99:107],
			'sc_opt': res[107:115],
			'eg_opt': res[115:123],
			'ms_opt': res[123:131],
			'wrk_prv_opt': res[131:139],
			'acc_opt': res[139:155],
			'ibu_set': res[155:163],
			'io_sts1': res[163:165],
			'io_sts2': res[165:167],
			'ain1': res[167:171],
			'ain2': res[171:175],
			'ain3': res[175:179],
			'asp1': res[179:183],
			'asp2': res[183:187],
			'asp3': res[187:191],
			'avin': res[191:195],
			'asp4': res[195:199],
			'atmp': res[199:203],
			'acc_x': res[203:205],
			'acc_y': res[205:207],
			'acc_z': res[207:209]
		}
		return qdioinf


	# data io counters
	def qdiocnt(self):
		res = self.execute_command('QDIOCNT//')
		diocnt = {
			'lst_ign_on': res[7:15],
			'last_ign_off': res[15:23],
			'tot_ign_on': res[23:31],
			'tot_ign_off': res[31:39],
			'ec1_trp_evt': res[39:47],
			'ec1_tot_evt': res[47:55],
			'ec2_trp_evt': res[55:63],
			'ec2_tot_evt': res[63:71],
			'sc1_trp_on': res[71:79],
			'sc1_trp_off': res[79:87],
			'sc1_tot_on': res[87:95],
			'sc1_tot_off': res[95:103],
			'sc2_trp_on': res[103:111],
			'sc2_trp_off': res[111:119],
			'sc2_trp_on': res[119:127],
			'sc2_tot_off': res[127:135],
		}
		return diocnt

	# work private options
	def qdiowpo(self):
		res = self.execute_command('QDIOWPO//')
		wi = int(res[7:15], 16)
		diowpo = { 'wp_ena': ((wi & 0x80000000) >> 31 == 0) }
		return diowpo

	# voltage threshold for work private
	def qdiowpt(self):
		res = self.execute_command('QDIOWPT//')
		fn = int(res[7:11], 16) * 7.08722 / 1000
		diowpt = { 'vin_th': (int(f) + round((fn - int(fn)) * 10) / 10) }
		return diowpt

	# accelerometer settings
	def qdioacp(self):
		res = self.execute_command('QDIOACP//')
		ai = int(res[7:15], 16)
		aj = int(res[15:23], 16)
		dioacp = {
			'acc_ena': (ai & 0x80000000 == 0),
			'at_ena': (ai & 0x40000000 != 0),
			'md_ena': (ai & 0x20000000 != 0),
			'rly_act_alm': (ai & 0x00800000 != 0),
			'rly_deact_alm': (ai & 0x00400000 != 0),
			'rly_act_mvmt': (ai & 0x00200000 != 0),
			'rly_deact_mvmt': (ai & 0x00100000 != 0),
			'arm_ign_off': (ai & 0x00008000 != 0),
			'disarm_ign_on': (aj & 0x80000000 != 0),
			'disarm_ibu': (aj & 0x40000000 != 0),
		}
		return dioacp

	# accelerometer anti-theft arming lower time threshold [sec/10]
	def qdioard(self):
		res = self.execute_command('QDIOARD//')
		dioard = { 'acc_tm_lo_th': int(res[7:11], 16) * 0.1 }
		return dioard

	# accelerometer anti-theft arming lower movement treshold [sec/10]
	def qdioarh(self):
		res = self.execute_command('QDIOARH//')
		dioarh = { 'acc_mvmt_lo_th': int(res[7:-2], 16) }
		return dioarh

	# accelerometer anti-theft arming higher time threshold [sec/10]
	def qdioart(self):
		res = self.execute_command('QDIOART//')
		dioart = { 'acc_tm_hi_th': int(res[7:-2], 16) * 0.1}
		return dioart

	# accelerometer anti-theft arming higher movement treshold [sec/10]
	def qdioadt(self):
		res = self.execute_command('QDIOADT//')
		dioadt = { 'acc_mvmt_hi_th': int(res[7:-2], 16) }
		return dioadt

	# accelerometer anti-theft period during which events must occur to trigger alarm [sec/10]
	def dioaep(self):
		res = self.execute_command('QDIOAEP//')
		dioaep = { 'acc_at_evt_per': int(res[7:-2], 16) * 0.1 }
		return dioaep

	# accelerometer anti-theft number of events to trigger alarm [sec/10]
	def dioaet(self):
		res = self.execute_command('QDIOAET//')
		dioaet = { 'acc_at_evt_num': int(res[7:-2], 16) * 0.1 }
		return dioaet

	# accelerometer motion detector acceleration threshold
	def qdiomdh(self):
		res = self.execute_command('QDIOMDH//')
		diomdh = { 'acc_md_acc_th': int(res[7:-2], 16) }
		return diomdh

	# accelerometer motion detector event threshold
	def qdiomdh(self):
		res = self.execute_command('QDIOMDT//')
		diomdt = { 'acc_md_evt_th': int(res[7:-2], 16) }
		return diomdt

	# accelerometer motion detector decrease rate [events/sec]
	def qdiomdr(self):
		res = self.execute_command('QDIOMDR//')
		diomdr = { 'acc_md_evt_dr': int(res[7:-2], 16) }
		return diomdr

	# accelerometer motion detector on/off transition duration [sec/10]
	def qdiomdo(self):
		res = self.execute_command('QDIOMDO//')
		diomdo = { 'acc_md_trans': int(res[7:11], 16) * 0.1 }
		return diomdo

	# refresh period for acceleration locked values [sec/10]
	def dioalu(self):
		res = self.execute_command('QDIOALU//')
		dioalu = { 'acc_lv_ref': int(res[7:11], 16) * 0.1 }
		return dioalu

	# arm accelerometer anti-theft
	def cdioate(self):
		res = self.execute_command('CDIOATE//')
		return res[7:10]

	# disarm accelerometer anti-theft
	def cdiodte(self):
		res = self.execute_command('CDIODTE//')
		return res[7:10]

	# pin allocation for io1
	def qdioai1(self):
		res = self.execute_command('QDIOAI1//')
		qdioai1 = { 'io1_alloc': self.__dioai_(res[7:11]) }
		return qdioai1

	# pin allocation for io2
	def qdioai2(self):
		res = self.execute_command('QDIOAI2//')
		qdioai2 = { 'io2_alloc': self.__dioai_(res[7:11]) }
		return qdioai2

	# pin allocation for io3
	def qdioai3(self):
		res = self.execute_command('QDIOAI3//')
		qdioai3 = { 'io3_alloc': self.__dioai_(res[7:11]) }
		return qdioai3

	# pin allocation for io4
	def qdioai4(self):
		res = self.execute_command('QDIOAI4//')
		qdioai4 = { 'io4_alloc': self.__dioai_(res[7:11]) }
		return qdioai4

	# pin allocation for io5
	def qdioai5(self):
		res = self.execute_command('QDIOAI5//')
		qdioai5 = { 'io5_alloc': self.__dioai_(res[7:11]) }
		return qdioai5

	# pin allocation for io6
	def qdioai6(self):
		res = self.execute_command('QDIOAI6//')
		qdioai6 = { 'io6_alloc': self.__dioai_(res[7:11]) }
		return qdioai6

	# pin allocation for io7
	def qdioai7(self):
		res = self.execute_command('QDIOAI7//')
		qdioai7 = { 'io7_alloc': self.__dioai_(res[7:11]) }
		return qdioai7

	# pin allocation for io8
	def qdioai8(self):
		res = self.execute_command('QDIOAI8//')
		qdioai8 = { 'io8_alloc': self.__dioai_(res[7:11]) }
		return qdioai8

	# pin allocation for io9
	def qdioai9(self):
		res = self.execute_command('QDIOAI9//')
		qdioai9 = { 'io9_alloc': self.__dioai_(res[7:11]) }
		return qdioai9

	# pin allocation for ioa
	def qdioaia(self):
		res = self.execute_command('QDIOAIA//')
		qdioaia = { 'ioa_alloc': self.__dioai_(res[7:11]) }
		return qdioaia

	# pin allocation for vin
	def qdioaiv(self):
		res = self.execute_command('QDIOAIV//')
		qdioaia = { 'vin_alloc': self.__dioai_(res[7:11]) }
		return qdioaia

	# pin allocation for uart
	def qdioaiu(self):
		res = self.execute_command('QDIOAIU//')
		qdioaiu = { 'uart_alloc': self.__dioai_(res[7:11]) }
		return qdioaiu

	# decode io allocation
	def __dioai_(self, apr):
		ai = int(apr[0:2], 16)
		if ai == 0x01:
			return 'ign'
		elif ai == 0x02:
			return 'panic'
		elif ai == 0x03:
			return 'wrk_pvt_det'
		elif ai == 0x04:
			return 'rly'
		elif ai == 0x05:
			return 'ec1'
		elif ai == 0x06:
			return 'ec2'
		elif ai == 0x07:
			return 'sc1'
		elif ai == 0x08:
			return 'sc2'
		elif ai == 0x09:
			return 'eg1'
		elif ai == 0x0a:
			return 'eg2'
		elif ai == 0x0b:
			return 'ibu_a'
		elif ai == 0x0c:
			return 'exp'
		elif ai == 0x0d:
			return 'ms'
		elif ai == 0x10:
			return 'acc_siren'
		elif ai == 0x11:
			return 'kline'
		elif ai == 0x12:
			return 'kline_fuel'
		elif ai == 0x13:
			return 'acc_arm_pos'
		elif ai == 0x14:
			return 'acc_arm_neg'
		elif ai == 0x15:
			return 'acc_disarm_pos'
		elif ai == 0x16:
			return 'acc_disarm_neg'
		elif ai == 0x17:
			return 'ibu_b'
		elif ai == 0x18:
			return 'buzzer_siren'
		elif ai == 0x19:
			return 'lrly_coil_a'
		elif ai == 0x1a:
			return 'lrly_coil_b'
		elif ai == 0x1b:
			return 'dtco_vdo_1381'
		elif ai == 0x1c:
			return 'mtco_vdo_1324'
		elif ai == 0x1d:
			return 'dtco_sr_se5000'
		elif ai == 0x1e:
			return 'dtco_sr_2400_4800'
		elif ai == 0x1f:
			return 'dtco_actia_l2000'
		elif ai == 0x20:
			return 'wrk_pvt_led'
		elif ai == 0x21:
			return 'ibu_a_auth'
		elif ai == 0x22:
			return 'ibu_b_deauth'
		elif ai == 0x23:
			return 'mode_sw'
		elif ai == 0x24:
			return 'rgb_led'
		elif ai == 0x25:
			return 'rs232_par'
		elif ai == 0x26:
			return 'rs232_clg'
		elif ai == 0x27:
			return 'tco_sog_fo'

	# ignition options
	def qdiopco(self):
		res = self.execute_command('QDIOPCO//')
		if len(res) == 8:
			ci = int(res[7:11], 16)
			qdiopco = {
				'ign_ena': (ci & 0x8000) == 0,
				'sog': (ci & 0x4000) != 0,
				'ms': (ci & 0x2000) != 0,
				'exp': (ci & 0x1000) != 0,
				'acc_md': (ci & 0x800) != 0,
				'pol': (ci & 0x400) != 0,
				'no_ipt': (ci & 0x200) != 0,
				'can': (ci & 0x100) != 0,
				'tco': (ci & 0x80) != 0,
			}
			return qdiopco
	
	# ignition voltage threshold [v*141]
	def qdiopct(self):
		res = self.execute_command('QDIOPCT//')
		if len(res) == 4:
			fn = int(res[7:11], 16) * 7.08722 / 1000
			qdiopct = { 'ign_th' : int(f) + round((fn - int(fn)) * 10) / 10 }
			return qdiopct

	# ignition filter threshold [sec]
	def qdiopcf(self):
		res = self.execute_command('QDIOPCF//')
		if len(res) == 2:
			qdiopcf = { 'ign_fltr_th' : int(res[7:-2], 16) }
			return qdiopcf

	# speed threshold for sog ignition [km/h]
	def qdiocss(self):
		res = self.execute_command('QDIOCSS//')
		qdiocss = { 'ign_sog_th': int(res[7:11]) }
		return diocss

	# time threshold for sog ignition [sec]
	def qdiocst(self):
		res = self.execute_command('QDIOCST//')
		diocst = { 'ign_sog_tm_th': int(res[7:11], 16) }	
		return diocst

	# ignition on timer
	def qdiotoo(self):
		res = self.execute_command('QDIOTOO//')
		diotoo = { 'ign_on_tmr': int(res[7:15], 16) }	
		return diotoo

	# ignition off timer
	def qdiotof(self):
		res = self.execute_command('QDIOTOF//')
		diotof = { 'ign_off_tmr': int(res[7:15], 16) }	
		return diotof

	# enable ignition
	def cdioect(self):
		res = self.execute_command('CDIOECT//')
		return res[7:10]

	# disable ignition
	def cdiodct(self):
		res = self.execute_command('CDIODCT//')
		return res[7:10]

	# panic button options
	def qdiopal(self):
		res = self.execute_command('QDIOPAL//')
		if len(res[7:15]) == 8:
			oi = int(res[7:11], 16)
			qdiopal = {
				'panic_ena': (oi & 0x8000) == 0,
				'exp': (oi & 0x4000) != 0,
				'pol': (oi & 0x2000) != 0,
				'monost': (oi& 0x1000) != 0,
				'rly_disa': (oi & 0x800) != 0,
				'ign_on_disa': (oi & 0x400) != 0,
				'ipt_fltr': (oi & 0x0200) != 0,
				'rly_ena_on': (oi & 0x80) != 0,
				'rly_ena_off': (oi & 0x40) != 0,
				'rly_disa_on': (oi & 0x20) != 0,
				'rly_disa_off': (oi & 0x10) != 0,
			}
			return qdiopal
	
	# panic button voltage threshold [v*141]
	def qdiopat(self):
		res = self.execute_command('QDIOPAT//')
		if len(res[7:11]) == 4:
			fn = int(res[7:11], 16) * 7.08722 / 1000
			qdiopat = { 'panic_th' : int(fn) + round((fn - int(fn)) * 10) / 10 }
			return qdiopat

	# duration for keeping panic signal active [sec]
	def qdiopdr(self):
		res = self.execute_command('QDIOPDR//')
		if len(res[7:11]) == 4:
			qdiopdr = { 'panic_dur': int(res[7:11], 16) }
			return qdiopdr
	
	# panic button time filter [sec/10]
	def qdiopaf(self):
		res = self.execute_command('QDIOPAF//')
		if len(res[7:-2]) == 2:
			qdiopaf = { 'panic_tm_fltr': int(res[7:-2], 16) }
			return qdiopaf

	# enable panic state
	def cdioect(self):
		res = self.execute_command('CDIOEPA//')
		return res[7:10]

	# disable panic state
	def cdiodct(self):
		res = self.execute_command('CDIODPA//')
		return res[7:10]

	# relay options
	def qdioprt(self):
		res = self.execute_command('QDIOPRT//')
		if len(res[7:15]) == 8:
			ri = int(res[7:11], 16)
			qdioprt = {
				'rly_ena': ri & 0x8000 == 0,
				'int_rly_ena': ri & 0x4000 == 0,
				'pol': ri & 0x2000 != 0,
				'monost': ri & 0x1000 != 0,
				'rly_ena_ign_on': ri & 0x800 != 0,
				'rly_ena_ign_off': ri & 0x200 != 0,
				'rly_disa_ign_on': ri & 0x400 != 0,
				'rly_disa_ign_on': ri & 0x100 != 0
			}
			return qdioprt

	# relay pulse duration [sec]
	def qdioprp(self):
		res = self.execute_command('QDIOPRP//')
		if len(res[7:11]) == 4:
			qdioprp = { 'rly_pls_dur': int(res[7:11], 16) }
			return qdioprp

	# enable relay
	def cdioerl(self):
		res = self.execute_command('CDIOERL//')
		return res[7:10]

	# disable relay
	def cdiodrl(self):
		res = self.execute_command('CDIODRL//')
		return res[7:10]

	# ibuutton io entity
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
		canset={}
		if res.decode() =="LIC" or res.decode()=="UNK" or res.decode()=="ERR":
			canset['can_log.enabled'] = "No license"
			return canset
		else:
			res=int(res[:4],16)
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
	def read_fuel_measurement(self):
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
	def read_record10_local_net(self):
		rec10 = {}
		rec10['qacqhgp'] = self.qacqhgp()
		rec10['qacqhti'] = self.qacqhti()
		rec10['qacqhtx'] = self.qacqhtx()
		rec10['qacqhss'] = self.qacqhss()
		rec10['qacqhgi'] = self.qacqhgi()
		return rec10

	def read_record10_roam_net(self):
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
	def read_record11_local_net(self):
		rec11={}
		rec11['qacqhsp'] = self.qacqhsp()
		rec11['qacqhsi'] = self.qacqhsi()

		return rec11
	def read_record11_roam_net(self):
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
	def read_record12_local_net(self):
		rec12={}
		rec12['qacqhcp'] = self.qacqhcp()
		rec12['qacqhci'] = self.qacqhci()

		return rec12
	def read_record12_roam_net(self):
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
	def read_record13_local_net(self):
		rec13={}
		rec13['qacqhrp'] = self.qacqhrp()
		return rec13
	def read_record13_roam_net(self):
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
	def read_record14_local_net(self):
		rec14={}
		rec14['qacqmrp'] = self.qacqhmp()
		return rec14
	def read_record14_roam_net(self):
		rec14={}
		rec14['qacqmrp'] = self.qacqrmp()
		return rec14
	#record 0x15 commands
	def qacqhdp(self):
		return self.acq_rec15_dp("QACQHDP//")
	def qacqrdp(self):
		return self.acq_rec15_dp("QACQRDP//")
	def qacqhip(self):
		return self.acq_rep15_ip("QACQHIP//")
	def qacqrip(self):
		return self.acq_rep15_ip("QACQRIP//")
	def acq_rec15_dp(self,c):
		res=int(self.execute_command(c)[7:-2],16)
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
		res=int(self.execute_command(c)[7:-2],16)
		acq_dp={
			"acq_interval": res 
		}
		return acq_dp
	def read_record15_local_net(self):
		rec15={}
		rec15['qacqhdp'] = self.qacqhdp()
		rec15['qacqhip'] = self.qacqhip()
		return rec15
	def read_record15_roam_net(self):
		rec15={}
		rec15['qacqrdp'] = self.qacqrdp()
		rec15['qacqrip'] = self.qacqrip()
		return rec15
	#record 0x16 commands
	def qacqhia(self):
		return self.acq_rec16_ia("QACQHIA//")
	def qacqria(self):
		return self.acq_rec16_ia("QACQRIA//")
	def acq_rec16_ia(self, c):
		res=self.execute_command(c)
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
	def read_record16_local_net(self):
		rec16={}
		rec16["qacqhia"] = self.qacqhia()
		return rec16
	def read_record16_roam_net(self):
		rec16={}
		rec16["qacqria"] = self.qacqria()
		return rec16
	#record 0x17 commands
	def qacqhib(self):
		return self.acq_rec17_ib("QACQHIB//")
	def qacqrib(self):
		return self.acq_rec17_ib("QACQRIB//")
	def acq_rec17_ib(self, c):
		res=self.execute_command(c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res =int(res[7:-2],16)
			acq_ib = {
			"acq_enable": (res & 0x80000000) == 0,
			}
			return acq_ib
	def read_record17_local_net(self):
		rec17={}
		rec17["qacqhib"] = self.qacqhib()
		return rec17
	def read_record17_roam_net(self):
		rec17={}
		rec17["qacqrib"] = self.qacqrib()
		return rec17
	#record 0x18 commands
	
	def qacqhio(self):
		return self.acq_rec18_io("QACQHIO//")
	
	def qacqrio(self):
		return self.acq_rec18_io("QACQRIO//")
	
	def acq_rec18_io(self,c):
		res = self.execute_command(c)
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
		return self.acq_rec18_oa("QACQHOA//")

	def qacqroa(self):
		return self.acq_rec18_oa("QACQROA//")

	def acq_rec18_oa(self,c):
		res = int(self.execute_command(c)[7:-2],16)
		acq_oa={
			"acq_interval_A": res / 10
		}	
		return acq_oa
	
	def qacqhob(self):
		return self.acq_rec18_ob("QACQHOB//")

	def qacqrob(self):
		return self.acq_rec18_ob("QACQROB//")
	
	def acq_rec18_ob(self,c):
		res = int(self.execute_command(c)[7:-2],16)
		acq_ob={
			"acq_interval_B":res  /10
		}	
		return acq_ob	

	def qacqit1(self):
		res=int(self.execute_command("QACQIT1//")[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_it1={
		"acq_io1_threshold": f
		}
		return acq_it1
	
	def qacqit2(self):
		res=int(self.execute_command("QACQIT2//")[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_it2={
		"acq_io2_threshold": f
		}
		return acq_it2
	
	def qacqit3(self):
		res=int(self.execute_command("QACQIT3//")[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_it3={
		"acq_io3_threshold": f
		}
		return acq_it3
	
	def qacqit4(self):
		res=int(self.execute_command("QACQIT4//")[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_it4={
		"acq_io4_threshold": f
		}
		return acq_it4
	def qacqitv(self):
		res=int(self.execute_command("QACQITV//")[7:-2],16)
		f = res * 7.08722 / 1000
		f = int(f) + round((f - int(f)) * 10) / 10
		acq_itv={
		"acq_volt_in_threshold": f
		}
		return acq_itv
	
	def qacqitt(self):
		res=int(self.execute_command("QACQITT//")[7:-2],16)
		acq_itt={
		"acq_time_filter_threshold": res /10
		}
		return acq_itt

	def read_record18_local_net(self):
		record18={}
		record18["acq_io"] = self.qacqhio()
		record18["acq_oa"] = self.qacqhoa()
		record18["acq_ob"] = self.qacqhob()
		record18["acqit1"] = self.qacqit1()
		record18["acqit2"] = self.qacqit2()
		record18["acqit3"] = self.qacqit3()
		record18["acqit4"] = self.qacqit4()
		record18["acqitv"] = self.qacqitv()
		record18["acqitt"] = self.qacqitt()
		return record18

	def read_record18_roam_net(self):
		record18={}
		record18["acq_io"] = self.qacqrio()
		record18["acq_oa"] = self.qacqroa()
		record18["acq_ob"] = self.qacqrob()
		record18["acqit1"] = self.qacqit1()
		record18["acqit2"] = self.qacqit2()
		record18["acqit3"] = self.qacqit3()
		record18["acqit4"] = self.qacqit4()
		record18["acqitv"] = self.qacqitv()
		record18["acqitt"] = self.qacqitt()
		return record18
		#_iorecord 0x19 commands
	
	def qacqhpr(self):
		return self.acq_rec19_pr("QACQHPR//")

	def qacqrpr(self):
		return self.acq_rec19_pr("QACQRPR//")

	def acq_rec19_pr(self, c):
		res=self.execute_command(c)
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

	def read_record19_local_net(self):
		rec19={}
		rec19["qacqhpr"] = self.qacqhpr()
		return rec19
	def read_record19_roam_net(self):
		rec19={}
		rec19["qacqrpr"] = self.qacqrpr()
		return rec19
		#record 0x1A commands
	def qacqhev(self):
		return self.acq_rec1A_ev("QACQHEV//")
	def qacqrev(self):
		return self.acq_rec1A_ev("QACQREV//")
	def acq_rec1A_ev(self, c):
		res=int(self.execute_command(c)[7:-2],16)
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
		return self.acq_rec1A_eb("QACQHEB//")
	def qacqreb(self):
		return self.acq_rec1A_eb("QACQREB//")
	
	def acq_rec1A_eb(self,c):
		res=int(self.execute_command(c)[7:-2],16)
		acq_eb={
			"interval_B" :res
		}
		return acq_eb
	
	def qacqhea(self):
		return self.acq_rec1A_ea("QACQHEB//")
	def qacqrea(self):
		return self.acq_rec1A_ea("QACQREB//")
	
	def acq_rec1A_ea(self,c):
		res=int(self.execute_command(self,c)[7:-2],16)
		acq_ea={
			"interval_A" :res
		}
		return acq_ea
	def read_record1A_local_net(self):
		rec1A={}
		rec1A["qacqhev"] = self.qacqhev()
		rec1A["qacqheb"] = self.qacqheb()
		rec1A["qacqhea"] = self.qacqhea()
		return rec1A
	
	def read_record1A_roam_net(self):
		rec1A={}
		rec1A["qacqrev"] = self.qacqrev()
		rec1A["qacqreb"] = self.qacqreb()
		rec1A["qacqrea"] = self.qacqrea()
		return rec1A
	
	#record 0x1B commands
	def qacqhs1(self):
		return self.acq_rec1B_s1("QACQHS1//")
	def qacqrs1(self):
		return self.acq_rec1B_s1("QACQRS1//")
	def acq_rec1B_s1(self,c):
		res=int(self.execute_command(c)[7:-2],16)
		acq_s1 = {
			"acq_enable": (res & 0x80000000) == 0,
			"ignition": (res & 0x40000000) != 0,
			"state_counter_1": (res & 0x20000000) != 0,
			"gen_trans_after_acq": (res & 0x10000000) != 0
		}
		return acq_s1
	def read_record1B_local_net(self):
		rec1b={}
		rec1b["qacqhs1"] = self.qacqhs1()
		return rec1b
	def read_record1B_roam_net(self):
		rec1b={}
		rec1b["qacqrs1"] = self.qacqrs1()
		return rec1b
	#record 0x1C commands
	def qacqhs2(self):
		return self.acq_rec1C_s2("QACQHS2//")
	def qacqrs2(self):
		return self.acq_rec1C_s2("QACQRS2//")
	def acq_rec1C_s2(self,c):
		res=self.execute_command(c)
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
	def read_record1C_local_net(self):
		rec1c={}
		rec1c["qacqhs2"] = self.qacqhs2()
		return rec1c
	def read_record1C_roam_net(self):
		rec1c={}
		rec1c["qacqrs2"] = self.qacqrs2()
		return rec1c
	
	#record 0x1D commands
	def qacqhsf(self):
		return self.acq_rec1D_sf("QACQHSF//")
	def qacqrsf(self):
		return self.acq_rec1D_sf("QACQRSF//")
	def acq_rec1D_sf(self,c):
		res=self.execute_command(c)
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
	def read_record1D_local_net(self):
		rec1d={}
		rec1d["qacqhsf"] = self.qacqhsf()
		return rec1d
	def read_record1D_roam_net(self):
		rec1d={}
		rec1d["qacqrsf"] = self.qacqrsf()
		return rec1d
	#record 0X1E commands
	def qacqhwp(self):
		return self.acq_rec1E_wp("QACQHWP//")
	def qacqrwp(self):
		return self.acq_rec1E_wp("QACQRWP//")
	def acq_rec1E_wp(self,c):
		res=self.execute_command(c)
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
		return self.acq_rec1E_wi("QACQHWI//")
	def qacqrwi(self):
		return self.acq_rec1E_wi("QACQRWI//")

	def acq_rec1E_wi(self,c):
		res=self.execute_command(c)
		if res[7:-2].decode()=="LIC":
			return "No License"
		else:
			res=int(res[7:-2],16)
			acq_wi={
				"acq_interval": res
			}
			return acq_wi

	def read_record1E_local_net(self):
		rec1e={}
		rec1e["qacqhwp"] = self.qacqhwp()
		rec1e["qacqhwi"] = self.qacqhwi()
		return rec1e
	def read_record1E_roam_net(self):
		rec1e={}
		rec1e["qacqrwp"] = self.qacqrwp()
		rec1e["qacqrwi"] = self.qacqrwi()
		return rec1e
#record 0X1F commands
	def qacqhdw(self):
		return self.acq_rec1F_dw("QACQHDW//")
	def qacqrdw(self):
		return self.acq_rec1F_dw("QACQRDW//")
	def acq_rec1F_dw(self,c):
		res=self.execute_command(c)
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
	def read_record1F_local_net(self):
		rec1e={}
		rec1e["qacqhdw"] = self.qacqhdw()
		return rec1e
	def read_record1F_roam_net(self):
		rec1e={}
		rec1e["qacqrdw"] = self.qacqrdw()
		return rec1e
#record 0x20 commands
	def qacqhdb(self):
		return self.acq_rec20_db("QACQHDB//")
	def qacqrdb(self):
		return self.acq_rec20_db("QACQRDB//")

	def acq_rec20_db(self,c):
		res=self.execute_command(c)
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
	def read_record20_local_net(self):
		rec20={}
		rec20["qacqhdb"] = self.qacqhdb()
		return rec20
	def read_record20_roam_net(self):
		rec20={}
		rec20["qacqrdb"] = self.qacqrdb()
		return rec20
#record 0x21 commands
	def qacqhfu(self):
		return self.acq_rec21_fu("QACQHFU//")
	def qacqrfu(self):
		return self.acq_rec21_fu("QACQRFU//")
	def acq_rec21_fu(self,c):
		res=self.execute_command(c)
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
	def read_record21_local_net(self):
		rec21={}
		rec21["qacqhfu"] = self.qacqhfu()
		return rec21
	def read_record21_roam_net(self):
		rec21={}
		rec21["qacqrfu"] = self.qacqrfu()
		return rec21
#record 0x23and0x24
	def qacqhdb(self):
		return self.acq_rec23and24_db("QACQHDB//")
	def qacqhdb(self):
		return self.acq_rec23and24_db("QACQRDB//")
	def acq_rec23and24_db(self,c):
		res=self.execute_command(c)
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
	def read_record23and24_local_net(self):
		rec23and24={}
		rec23and24["qacqhdb"] = self.qacqhdb()
		return rec23and24
	def read_record23and24_roam_net(self):
		rec23and24={}
		rec23and24["qacqrdb"] = self.qacqrdb()
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
	def read_record25(self):
		rec25={}
		rec25["record_25"] = self.qacqetr()
		return rec25
#record0x40and0x41	
	def qacqtco(self):
		res=self.execute_command("QACQTCO//")
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
		res=self.execute_command("QACQTCI//")
		if res[7:-2].decode()=="LIC":
			return "No License"
		elif res[7:-2].decode()=="":
			return None
		else:
			res=int(res[7:-2],16)
			acqtci={}
			acqtci["acq_interval"] = res
	def read_record40and41(self):
		rec40and41={}
		rec40and41["qacqtco"] = self.qacqtco()
		rec40and41["qacqtci"] = self.qacqtci()
		return rec40and41