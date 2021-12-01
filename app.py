import os
from flask import Flask, render_template, request,Response, redirect, url_for, send_from_directory , send_file,jsonify
from werkzeug.utils import secure_filename
import os
import sys
from collections import defaultdict
import fleep
import uuid
import logging
import socket
import RPi.GPIO as GPIO
from pprint import pprint
import json
import datetime
from flask_socketio import SocketIO, emit
from tiny_logger_model import Log_Data ,db
from actuators.actuator import actuator, on_off_range
from actuators.pwm_actuator import *
import paho.mqtt.client as mqtt
from server_configs import *
from parameters import *
from perpetualTimer import *
import schedule

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
async_mode = None
app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
app.config['UPLOAD_FOLDER'] = 'uploads/'
upload_path= app.config['UPLOAD_FOLDER']
app.config['SAVE_PATH']='saved/'
if not os.path.exists(app.config['SAVE_PATH']):
    os.makedirs(app.config['SAVE_PATH'])



# try:
from sensors import CameraUtils 
camera=CameraUtils.cameraUtils()
# except Exception as ex:
#     print("error in camera")

from sensors import SHT1x
shtSensor=SHT1x(shtdataPin, shtClockPin, gpio_mode=GPIO.BCM) 

from sensors import bh1750 
luxSensor= bh1750.bh1750()


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



@app.before_first_request
def setup_logging():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

client = mqtt.Client("raspi")
print (mqtt_host)
client.connect(mqtt_host)
client.subscribe(mqtt_topic)

import time 
def get_all_info():
        timestr=time.strftime('%Y-%m-%d %H:%M:%S')
        temprature=shtSensor.read_temperature()
        humidity= shtSensor.read_humidity(temprature)
        lightLevel=luxSensor.readLight()
        img_path, img_thumb_path =camera.CaptureSingleImage()
        full_path = "" 
        full_thumb_path=""
        if img_path !=None :
            full_path = base_url+ img_path 
            full_thumb_path = base_url+ img_thumb_path 
        
        result={"time":timestr,
                "temprature": temprature,
                "humidity": humidity,
                "light": lightLevel,
                "image" : full_path ,
                "thumb":full_thumb_path }
        pprint(result)
        inset_to_db(result)
        
        mqtt_message = {
            "temperature":temprature,
            "humidity": humidity,
            "light": lightLevel,
            "device_name":"raspi"
        }

        client.publish(mqtt_topic,json.dumps(mqtt_message))
        query_result= get_last_record()        
        pprint(query_result)       
        
        return result

Logging_time = perpetualTimer(logInterval,get_all_info)
Logging_time.start()


def background_thread():
    while True:
        socketio.sleep(Seconds_to_emit_response)
        res=get_last_record()
        
        socketio.emit('my_response',
                      res,
                      namespace='/carpi')


@socketio.on('connect', namespace='/carpi')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)

@socketio.on('recieve', namespace='/carpi')
def recive_command():
   pass

@app.route('/')
def index():
 
    return render_template('index.html' , async_mode=socketio.async_mode)


@app.route('/new')
def index2():
 
    return render_template('index_new.html' , async_mode=socketio.async_mode)


def check_file_type(file_path):
    with open(file_path, "rb") as file:
        info = fleep.get(file.read(128))
        if info.type_matches("raster-image"):
            return file_path
        else :
            return ""

def download_url(file_url):
   
    file_path = os.path.join(upload_path,str(uuid.uuid1()))
    urllib.request.urlretrieve(file_url, file_path)
    return check_file_type(file_path)

@app.route('/change_status', methods=['POST'])
def change_status():

    status= json.loads(request.data.decode("utf-8"))
    print(status)
    act= actuator("null",0)
 
    if status["name"]== "lights":
        act= stand_lights
    elif status["name"]== "roof_lights_sun":
        act = roof_lights_sun
    elif status["name"]== "roof_lights_moon":
        act = roof_lights_moon
    elif status["name"]== "mister":
        act = mister
    elif status["name"]== "home_light":
        act = home_light
    elif status["name"]== "fan":
        act = fans
    elif status["name"]== "dimmer":
        
        pwm_value = int(status["value"])
        dimmer_light.change_duty_cycle(pwm_value)        
        return  Response("{} relay is {} now".format(act.name , act.status))
    elif status["name"]== "refresh":
        get_all_info()
        return  Response("New Data Saved. wait {} seconds to reload".format(Seconds_to_emit_response))

    else:
         return  Response("Invalid request")


    if(status["value"]=="on"):
       response= act.turn_on()

    else:
       response= act.turn_off()

    return  Response("{} relay is {} now".format(act.name , act.status))


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # if file and allowed_file(file.filename):

    filename = secure_filename(str(uuid.uuid1())+"-"+file.filename)
    file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    if check_file_type(file_path) != "" :
       return redirect(url_for('uploaded_file',
                                filename=filename))



def inset_to_db(result):
    dt = Log_Data(D_temprature= result["temprature"], D_hummidity= result["humidity"], 
                    D_Lux= result["light"], D_time= result["time"] ,
                    U_image_path=  result["image"],U_image_thumb_path = result["thumb"], U_Desc="_" )
    db.session.add(dt)
    db.session.commit()

def get_top_records(top_num=100):
    x=Log_Data.query.order_by(Log_Data.D_id.desc()).limit(top_num)
    return x
    
    
def get_last_record():
    temp_log = Log_Data.query.order_by(Log_Data.D_id.desc()).first()
    result={"time":temp_log.D_time,
                "temprature": temp_log.D_temprature,
                "humidity": temp_log.D_hummidity,
                "light": temp_log.D_Lux,
                "image":temp_log.U_image_path,
                "thumb":temp_log.U_image_thumb_path,
                }
    return result



@app.route('/status')
def status():
    try:
        logging.info('Successfully processed')
        result=get_all_info()
        if result:
            data = {
                'status' : 'OK',
                'result' : result
            }
            return jsonify(data)
    except Exception as e: 
        logging.error('Failed to upload to ftp: '+ str(e))
        error = {
			'status' : 'error',
			'msg' : 'unable to process the image'}
        return jsonify(error)
    

if __name__ == '__main__':
   socketio.run(app, debug=False ,host='0.0.0.0',port=serve_port)
  #  socketio.run(app, debug=False)
    # app.run(debug=False,host='0.0.0.0',port=8888)


