from actuators.actuator import actuator, on_off_range
from actuators.pwm_actuator import *
from parameters import *
from perpetualTimer import *
import schedule


act_array = []



stand_lights=actuator("stand light" , lightRelayPort)
roof_lights_sun=actuator("roof light sun" , RoofLightSunRelayPort)
roof_lights_moon=actuator("roof light moon" , RoofLightMoonRelayPort)
home_light=actuator("home_light" , home_light_Relay_Port)
fans=actuator("fans" , fanRelayPort)
mister = actuator("mister", MisterRelayPort)

dimmer_light= pwm_actuator("Dimmer_light", DimmerPort,pwm_frequency,pwm_duty_cycle)

home_light.set_on_off("20:00:00" , "22:30:10")
roof_lights_sun.set_on_off("17:30:00" , "22:40:10")
roof_lights_sun.set_on_off("17:30:00" , "22:40:10")
roof_lights_moon.set_on_off("17:30:00" , "22:40:00")
stand_lights.set_on_off("17:00:00" , "22:00:00")

mister.set_on_off("08:00:00" , "08:00:07")
mister.set_on_off("11:00:00" , "11:00:07")
mister.set_on_off("16:00:00" , "16:00:07")
mister.set_on_off("20:00:00" , "20:00:07")


act_array.append(stand_lights)
act_array.append(roof_lights_sun)
act_array.append(roof_lights_moon)
act_array.append(home_light)
act_array.append(fans)
act_array.append(mister)



for act_element in act_array:
    act_schedules= act_element.get_on_off_schedules()
    act_name = act_element.get_name()
    for  act_schedule in act_schedules:
        print ("Set on time {}  and off_time {} for {}".format(act_schedule.on_string ,act_schedule.off_string  ,act_name))
        schedule.every().day.at(act_schedule.on_string).do(act_element.turn_on)
        schedule.every().day.at(act_schedule.off_string ).do(act_element.turn_off)

def schedule_job():
    schedule.run_pending()

schedule_timer = perpetualTimer(1,schedule_job)
schedule_timer.start()

