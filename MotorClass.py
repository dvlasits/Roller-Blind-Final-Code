

import RPi.GPIO as IO

import time
import time
import pigpio
import rotary_encoder
class Motor:

	def __init__(self):
		IO.setmode(IO.BCM)
		IO.setup(2,IO.OUT)
		self.p = IO.PWM(2,1000)
		IO.setwarnings(False)
		IO.setup(3,IO.OUT)
		IO.output(3,1)
		IO.setup(4,IO.IN,pull_up_down=IO.PUD_UP)
		self.p.start(0)
		self.Up = 1
		self.speed = 40
		self.numToTurn = 200
		self.pos = 0
		self.pi = pigpio.pi()
		decoder = rotary_encoder.decoder(self.pi, 4, 17, self.callback)


	def callback(self,way):
		self.pos += way


	def Encoder(self):
		return self.pos

	def do(self,n):
		self.p.ChangeDutyCycle(self.speed)
		count = self.Encoder()
		while True:
			if abs(count-self.Encoder()) >= n:
				self.p.ChangeDutyCycle(0)
				break
	def toggle(self):
		if self.Up == 1:
			self.right()
		else:
			self.left()
		self.Up = 1-self.Up
		self.do(self.numToTurn)


	def on(self):
		self.p.ChangeDutyCycle(self.speed)

	def off(self):
		self.p.ChangeDutyCycle(0)

	def left(self):
		IO.output(3,1)
	def right(self):
		IO.output(3,0)
