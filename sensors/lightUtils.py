from . import bh1750 
class lightUtils():

	def __init__(self):

		self.lightStatus=False
		self. luxSensor= bh1750.bh1750()
		

	def readLux(self):
		str(self.luxSensor.readLight())

	def returnLightStatus(self):
		if  self.lightStatus ==True:
			return "ON"
		else:
			return "OFF"
