import RPi.GPIO as GPIO
import json

class on_off_range :
    def __init__(self, on_string , off_string):

        self.on_string= on_string
        self.off_string= off_string


class actuator:
    def __init__(self,name, port):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(port, GPIO.OUT)
        self.name=name
        self.port=port
        self.status="OFF"
        self.on_schedule=False
        self.custom_control=False
        self.on_off_array= []
        self.schedule_off()
    
    def toJSON(self):

        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
            
    def turn_on(self):
        try:
            GPIO.output(self.port, GPIO.LOW)
            self.custom_control=True
            self.status="ON"
            return("ON")
        except Exception as ex:
            return("Err")
    
    def set_on_off(self,on_string , off_string): 
        new_on_off_range=on_off_range(on_string,off_string)
        self.on_off_array.append(new_on_off_range) 
        return new_on_off_range

    def get_on_off_schedules(self):
        return self.on_off_array
    def get_name(self):
        return self.name;

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





    

    


    