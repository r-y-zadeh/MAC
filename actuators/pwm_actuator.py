
import RPi.GPIO as GPIO
import json
class pwm_actuator:

    def __init__(self,name, port , frequency , duty_cycle):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(port, GPIO.OUT)

        self.pwm_act = GPIO.PWM(port, frequency)
        self.pwm_act.start(0)

        self.name=name
        self.port=port
        self.frequency=frequency
        self.duty_cycle=duty_cycle;
        
        self.status="OFF"
        self.on_schedule=False
        self.custom_control=False
        self.on_off_array= []
       
        
    def change_duty_cycle(self,duty_cycle):
        print(self.port , self.frequency , duty_cycle)
        self.duty_cycle= duty_cycle
        self.pwm_act.ChangeDutyCycle(duty_cycle)