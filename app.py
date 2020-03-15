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
from flask_socketio import SocketIO, emit
from tiny_logger_model import Log_Data ,db




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

def init_GPOIO():
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fanRelayPort, GPIO.OUT)
    GPIO.setup(humidifierRelayPort, GPIO.OUT)
    GPIO.setup(lightRelayPort, GPIO.OUT)
    GPIO.setup(motionDetectorPin, GPIO.IN)
    GPIO.setup(RoofLightRelayPort, GPIO.OUT)
    GPIO.output(fanRelayPort, GPIO.HIGH)
    GPIO.output(humidifierRelayPort, GPIO.HIGH)
    GPIO.output(lightRelayPort, GPIO.HIGH)
    GPIO.output(RoofLightRelayPort, GPIO.HIGH)



from parameters import *
from perpetualTimer import *
try:
    from CameraUtils import * 
    camera=cameraUtils()
except Exception as ex:
    print("error in camera")

from pi_sht1x import SHT1x
shtSensor=SHT1x(shtdataPin, shtClockPin, gpio_mode=GPIO.BCM) 

import bh1750 
luxSensor= bh1750.bh1750()

init_GPOIO()

def get_all_info():
        timestr=time.strftime('%Y-%m-%d %H:%M:%S')
        temprature=shtSensor.read_temperature()
        humidity= shtSensor.read_humidity(temprature)
        lightLevel=luxSensor.readLight()
        image_path =camera.CaptureSingleImage()
        result={"time":timestr,
                "temprature": temprature,
                "humidity": humidity,
                "light": lightLevel,
                "image":"http://ryz.ddns.net:8888/static/saved/"+image_path}

        inset_to_db(result)
        
        print("Data stored")

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
    if status["name"]== "lights":
        out_port = lightRelayPort
    elif status["name"]== "roof_lights":
        out_port = RoofLightRelayPort
    elif status["name"]== "hummidifier":
        out_port = humidifierRelayPort
    elif status["name"]== "fan":
        out_port = fanRelayPort
    else:
         return


    GPIO.setup(out_port, GPIO.OUT)
    if(status["value"]=="on"):
        GPIO.output(out_port, GPIO.LOW)

    else:
        GPIO.output(out_port, GPIO.HIGH)


    return  Response("{} relay is {} now".format(status["name"] , status["value"]))


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
    socketio.run(app, debug=False,host='0.0.0.0',port=8888)
    # app.run(debug=False,host='0.0.0.0',port=8888)

