from picamera import PiCamera
import time
import datetime
import os
from parameters import savePath

from PIL import Image

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
			thumb_file_name= currentDT.strftime("%H-%M-%S") + "_thumb.jpg"
			fileId= folder +"/"+ fileName
			thumb_file_id=folder +"/"+ thumb_file_name
			filePath =savePath +"/"+ fileName
			thumb_file_path= savePath +"/"+ thumb_file_name

			self.camera.capture(filePath)

			image = Image.open(filePath)
			MAX_SIZE = (200, 150)
  
			image.thumbnail(MAX_SIZE)
  
			# creating thumbnail
			image.save(thumb_file_path)

			self.camera.stop_preview()

			return fileId ,thumb_file_id

		except Exception as ex:
			if hasattr(ex, 'message'):
				print(e.message)
			else:
				print(ex)
			return None , None

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
