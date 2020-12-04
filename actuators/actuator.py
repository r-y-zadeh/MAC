import RPi.GPIO as GPIO


class actuator:
    def __init__(self,name, port):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(port, GPIO.OUT)
        self.name=name
        self.port=port
        self.status="OFF"
        self.on_schedule=False
        self.custom_control=False

    def turn_on(self):
        try:
            GPIO.output(self.port, GPIO.LOW)
            self.custom_control=True
            self.status="ON"
            return("ON")
        except Exception as ex:
            return("Err")
        

    def turn_off(self):
        try:
            GPIO.output(self.port, GPIO.HIGH)
            self.custom_control=False
            self.status="OFF"
            return("OFF")
        except Exception as ex:
            return("Err")
        

    def get_status(self):
        return self.status

    def schedule_on(self):
        temp=self.custom_control
        self.on_schedule=True
        self.turn_on()
        self.custom_control=temp
        
    def schedule_off(self):
        if self.custom_control == False:
            self.turn_off()





    

    


    