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
from actuators.actuator import actuator



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




from parameters import *
from perpetualTimer import *
try:
    from sensors import CameraUtils 
    camera=cameraUtils()
except Exception as ex:
    print("error in camera")

from sensors import SHT1x
shtSensor=SHT1x(shtdataPin, shtClockPin, gpio_mode=GPIO.BCM) 

from sensors import bh1750 
luxSensor= bh1750.bh1750()

stand_lights=actuator("stand light" , lightRelayPort)
roof_lights_sun=actuator("roof light sun" , RoofLightSunRelayPort)
roof_lights_moon=actuator("roof light moon" , RoofLightMoonRelayPort)
humidifier=actuator("humidifier" , humidifierRelayPort)
fans=actuator("fans" , fanRelayPort)
humidifier.schedule_off()
@app.before_first_request
def setup_logging():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

serve_ip="192.168.1.100"
serve_port= "7777"
base_url=serve_ip+":"+serve_port+"/static/saved/"


def get_all_info():
        timestr=time.strftime('%Y-%m-%d %H:%M:%S')
        temprature=shtSensor.read_temperature()
        humidity= shtSensor.read_humidity(temprature)
        lightLevel=luxSensor.readLight()
        img_path = camera.CaptureSingleImage()
        full_path = "" 
        if img_path !=None :
            full_path = base_url+ img_path 
        result={"time":timestr,
                "temprature": temprature,
                "humidity": humidity,
                "light": lightLevel,
                "image" : full_path}

        inset_to_db(result)

        res2= get_last_record()
        pprint(res2)
        print("Data restored")
        return result

Logging_time = perpetualTimer(logInterval,get_all_info)
Logging_time.start()


def background_thread():
    while True:
        socketio.sleep(5)
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
@app.route('/change-env')
def change_env():
 
    return render_template('change.html')



def schedule():
    now = datetime.datetime.now()
    print("Debug timer {}:{}".format(now.hour , now.minute))


    # if now.hour  <21  and now.hour >9:

    #     if now.minute >30 and now.minute <32 :
    #         humidifier.schedule_on()
    #     else:
    #         humidifier.schedule_off()
    
    if now.hour >16:
        stand_lights.schedule_on()
        roof_lights_sun.schedule_on()
        roof_lights_moon.schedule_on()
        fans.schedule_on()
    else:
        stand_lights.schedule_off()
        roof_lights_sun.schedule_off()
        roof_lights_moon.schedule_off()
        fans.schedule_off()

t = perpetualTimer(60,schedule)
t.start()


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
    pprint(request.data)
    status= json.loads(request.data.decode("utf-8"))
    print(status)
    act= actuator("null",0)
 
    if status["name"]== "lights":
        act= stand_lights
    elif status["name"]== "roof_lights_sun":
        act = roof_lights_sun
    elif status["name"]== "roof_lights_moon":
        act = roof_lights_moon
    elif status["name"]== "hummidifier":
        act = humidifier
    elif status["name"]== "fan":
        act = fans
    else:
         return

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
                    U_image_path=  result["image"],U_Desc="_" )
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
                "image":temp_log.U_image_path
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
   socketio.run(app, debug=False,host='0.0.0.0',port=serve_port)
  #  socketio.run(app, debug=False)
    # app.run(debug=False,host='0.0.0.0',port=8888)


