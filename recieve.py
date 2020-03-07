import socket
import time
import datetime
from MotorClass import Motor
import threading


import pyowm

owm = pyowm.OWM('3216938eb77dfacd3cf110533bd3adca')


class Data():
	def __init__(self):
		self.Up = 1
		self.AwayFromHome=0
		self.Sunrise = 0
		self.PickTime = 0
		self.UpTime = "None"
		self.DownTime = "None"
		self.TempAbove = "None"
		self.Calibrate = 0
		self._lock = threading.Lock()

	def ToggleCalibrate(self):
		with self._lock:
			self.Calibrate = 1- self.Calibrate
	def getCalibrate(self):
		return self.Calibrate
	def setTempAbove(self,state):
		with self._lock:
			self.TempAbove = int(state)
	def getTempAbove(self):
		with self._lock:
			return self.TempAbove

	def ToggleUp(self):
		with self._lock:
			self.Up = 1-self.Up
	def setUp(self,state):
		with self._lock:
			self.Up = state
	def ToggleAwayFromHome(self):
		with self._lock:
			self.AwayFromHome = 1- self.AwayFromHome
	def toggleSunrise(self):
		with self._lock:
			self.Sunrise = 1-self.Sunrise
	def togglePickTime(self):
		with self._lock:
			self.PickTime = 1-self.PickTime
	def SetUpTime(self,Time):
		with self._lock:
			self.UpTime = Time
	def setDownTime(self,Time):
		with self._lock:
			self.DownTime = Time
	def getUp(self):
		with self._lock:
			return self.Up
	def getAwayFromHome(self):
		with self._lock:
			return self.AwayFromHome
	def getSunrise(self):
		with self._lock:
			return self.Sunrise
	def getPickTime(self):
		with self._lock:
			return self.PickTime
	def getUpTime(self):
		with self._lock:
			return self.UpTime
	def getDownTime(self):
		with self._lock:
			return self.DownTime


datat = Data()

motor = Motor()

def ListenToPort():
	UDP_IP = "192.168.0.38"
	UDP_PORT = 5005
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	SENDIP = "192.168.9.39"
	SENDPORT = 5005
	sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

	while True:
		data, addr = sock.recvfrom(1024)
		#print(data.decode())
		if "." in data.decode():
			SENDIP = data.decode()
		if data.decode() == "toggle":
			datat.ToggleUp()
		if data.decode() == "AwayFromHome":
			datat.ToggleAwayFromHome()
		if data.decode() == "Sunrise":
			datat.toggleSunrise()
		if data.decode() == "PickTime":
			datat.togglePickTime()
		if data.decode().split()[0] == "UpTime":
			datat.SetUpTime(data.decode().split()[1])
		if data.decode().split()[0] == "DownTime":
			datat.setDownTime(data.decode().split()[1])
		if data.decode().split()[0] == "Temp":
			datat.setTempAbove(data.decode().split()[1])
		if data.decode() == "Calibrate":
			datat.ToggleCalibrate()
		tSend = str(datat.getUp()) + " " +str(datat.getAwayFromHome()) + " " + str(datat.getSunrise()) + " " + str(datat.getPickTime()) + " " + datat.getUpTime() + " " + datat.getDownTime() + " " + str(datat.getTempAbove()) + " " + str(datat.getCalibrate())
		print(tSend)
		sock2.sendto(tSend.encode(),(SENDIP,SENDPORT))



x = threading.Thread(target=ListenToPort)
x.start()

Up = 1
AwayFromHome=0
Sunrise = 0
PickTime = 0
UpTime = "None"
DownTime = "None"
numTimes = 10000
lastTime = time.time()
from random import randint
while True:
	time.sleep(0.1)
	if datat.getUp() != Up:
		motor.toggle()
		Up = 1- Up
	if datat.getPickTime() == 1:

		if datat.getUpTime() != "None" and Up == 0:
			now = datetime.datetime.now()
			timer = datat.getUpTime().split(":")
			#print(now.hour,now.minute)
			if int(timer[0]) == now.hour and int(timer[1]) == now.minute:
				motor.toggle()
				Up = 1
				datat.setUp(1)

		if datat.getDownTime() != "None" and Up == 1:
			now = datetime.datetime.now()
			timer = datat.getDownTime().split(":")
			#print(now.hour,now.minute)
			if int(timer[0]) == now.hour and int(timer[1]) == now.minute:
				motor.toggle()
				Up = 0
				datat.setUp(0)
	if datat.getAwayFromHome() == 1:
		if randint(1,100) == 2:
			motor.toggle()
			Up = 1-Up
			datat.ToggleUp()
	if datat.getCalibrate() == 1:
		n = motor.Encoder()
		motor.on()
		while datat.getCalibrate() == 1:
			pass
		n = abs(n-motor.Encoder())
		motor.off()
		Up = 0
		datat.setUp(0)
		print(n)
		motor.numToTurn = n
		print(motor.numToTurn)
	if time.time() - lastTime > 3600 and datat.getSunrise() == 1:
		observation = owm.weather_at_place('Cambridge,GB')
		w = observation.get_weather()
		temp = float(w.get_temperature('celsius')['temp'])
		if temp > datat.getTempAbove():
			if Up = 1:
				motor.toggle()
				Up = 0
				datat.setUp(0)
		lastTime = time.time()
