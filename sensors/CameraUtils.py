from picamera import PiCamera
import time
import datetime
import os
from parameters import savePath


class cameraUtils():

	def __init__(self):

		self.camera = PiCamera() 
		#self.camera.resolution = (1920,1080)
		self.camera.resolution = (800,600)
		self.camera.rotation=180
		self.savePath=savePath

	def CaptureSingleImage(self):
		try:	
			self.camera.start_preview()
			#time.sleep(0.1)
			currentDT = datetime.datetime.now()

			folder = currentDT.strftime("%Y-%m-%d")
			savePath=self.savePath+folder
			if not os.path.exists(savePath) :
				os.makedirs(savePath)
			fileName= currentDT.strftime("%H-%M-%S") + ".jpg"
			fileId= folder +"/"+ fileName
			filePath =savePath +"/"+ fileName

			self.camera.capture(filePath)

			self.camera.stop_preview()
			return fileId
		except Exception as ex:
			return None

	def setRes(self,resolutionValue):
		if resolutionValue=='high':
			self.camera.resolution = (3280 ,2464)
		else:
			self.camera.resolution = (800,600)
	def CaptureStream(self, duration):

		self.camera.start_preview()
		#time.sleep(0.1)
		currentDT = datetime.datetime.now()

		folder = currentDT.strftime("%Y-%m-%d")
		savePath=self.savePath+folder
		if not os.path.exists(savePath) :
			os.makedirs(savePath)
		fileName= currentDT.strftime("%H-%M-%S") + ".mp4"
		fileId= folder +"/"+ fileName
		filePath =savePath +"/"+ fileName
		
		self.camera.start_recording(filePath)
		time.sleep(duration)
		self.camera.stop_recording()
		self.camera.stop_preview()

		return fileId
