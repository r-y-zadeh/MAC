from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moc.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    U_id = db.Column(db.Integer, primary_key=True)
    U_login_name = db.Column(db.String(80), unique=True, nullable=False)
    U_name = db.Column(db.String(80), unique=False, nullable=False)
    U_family = db.Column(db.String(120), unique=False, nullable=False)
    U_email = db.Column(db.String(120), unique=True, nullable=False)
    U_twitter = db.Column(db.String(120), unique=True, nullable=True)

    U_actuator_event = db.relationship("Actuator_Event")

    def __repr__(self):
        return '<User %r>' % self.U_login_name


class Sensor_Type(db.Model):
    __tablename__ = "sensor_types"
    ST_id = db.Column(db.Integer, primary_key=True)
    ST_name = db.Column(db.String(40), unique=True, nullable=False)
    ST_desc = db.Column(db.String(100), unique=True, nullable=False)
    ST_metric = db.Column(db.String(20), unique=True, nullable=True)
    ST_sensor = db.relationship("Sensor")


    def __repr__(self):
        return '<Sensor type %r>' % self.ST_name

class Device_Type(db.Model):
    __tablename__ = "device_types"
    DT_id = db.Column(db.Integer, primary_key=True)
    DT_name = db.Column(db.String(40), unique=True, nullable=False)
    DT_desc = db.Column(db.String(100), unique=True, nullable=False)
    DT_device = db.relationship("Device")


    def __repr__(self):
        return '<Sensor type %r>' % self.ST_name


class Actuator_Type(db.Model):
    __tablename__ = "actuator_types"
    AT_id = db.Column(db.Integer, primary_key=True)
    AT_name = db.Column(db.String(80), unique=True, nullable=False)
    AT_desc = db.Column(db.String(120), unique=True, nullable=False)
    AT_actuator = db.relationship("Actuator")

    def __repr__(self):
        return '<Actuator type %r>' % self.AT_name
        

class Region(db.Model):
    __tablename__ = "regions"
    R_id = db.Column(db.Integer, primary_key=True)
    R_name = db.Column(db.String(80), unique=True, nullable=False)
    R_desc = db.Column(db.String(120), unique=True, nullable=False)
    R_devices = db.relationship("Device")
    R_region_limits = db.relationship("Region_Limits")


    def __repr__(self):
        return '<Region %r>' % self.R_name

class Actuator(db.Model):
    __tablename__ = "actuators"
    A_id = db.Column(db.Integer, primary_key=True)
    A_name = db.Column(db.String(80), unique=True, nullable=False)
    A_desc = db.Column(db.String(120), unique=True, nullable=False)
    A_code = db.Column(db.String(10), unique=True, nullable=False)
    A_GPIO = db.Column(db.Integer,nullable=False)
    A_device = db.Column(db.Integer, db.ForeignKey('devices.D_id'),nullable=False)
    A_Type = db.Column(db.Integer, db.ForeignKey('actuator_types.AT_id'),nullable=False )
    A_actuator_event = db.relationship("Actuator_Event")


    def __repr__(self):
        return '<Actuator \ %r>' % self.A_name

class Device(db.Model):
    __tablename__ = "devices"
    D_id = db.Column(db.Integer, primary_key=True)
    D_name = db.Column(db.String(80), unique=True, nullable=False)
    D_desc = db.Column(db.String(120), unique=True, nullable=False)
    D_code = db.Column(db.String(10), unique=True, nullable=False)
    D_region = db.Column(db.Integer,db.ForeignKey('regions.R_id'),nullable=False )
    D_Type = db.Column(db.Integer,db.ForeignKey('device_types.DT_id') ,nullable=False )
    D_sensors = db.relationship("Sensor")
    D_actuators = db.relationship("Actuator")


    def __repr__(self):
        return '<Sensor \ %r>' % self.S_name

class Sensor(db.Model):
    __tablename__ = "sensors"
    S_id = db.Column(db.Integer, primary_key=True)
    S_name = db.Column(db.String(80), unique=True, nullable=False)
    S_desc = db.Column(db.String(120), unique=True, nullable=False)
    S_code = db.Column(db.String(10), unique=True, nullable=False)
    S_region = db.Column(db.Integer,db.ForeignKey('devices.D_id'),nullable=False )
    S_Type = db.Column(db.Integer,db.ForeignKey('sensor_types.ST_id') ,nullable=False )
    S_sensor_value = db.relationship("Sensor_Values")
    S_region_limits = db.relationship("Region_Limits")


    def __repr__(self):
        return '<Sensor \ %r>' % self.S_name


class Sensor_Values(db.Model):
    __tablename__ = "sensor_values"
    SV_id = db.Column(db.Integer, primary_key=True)
    SV_time = db.Column(db.String(80), unique=True, nullable=False)
    SV_value = db.Column(db.String(120), unique=True, nullable=False)
    Sv_region = db.Column(db.Integer,db.ForeignKey('regions.R_id'),nullable=False )
    SV_Type = db.Column(db.Integer,db.ForeignKey('sensors.S_id') ,nullable=False)


    def __repr__(self):
        return '<Sensor  value\ %r>' % self.SV_value

class Actuator_Event(db.Model):
    __tablename__ = "actuator_events"
    AE_id = db.Column(db.Integer, primary_key=True)
    AE_time = db.Column(db.String(80), unique=True, nullable=False)
    AE_value = db.Column(db.String(120), unique=True, nullable=False)
    AE_user = db.Column(db.Integer,db.ForeignKey('users.U_id'),nullable=False )
    AE_actuator = db.Column(db.Integer,db.ForeignKey('actuators.A_id'),nullable=False )


    def __repr__(self):
        return '<Sensor  value\ %r>' % self.SV_value


class Region_Limits(db.Model):
    __tablename__ = "region_limits"
    RL_id = db.Column(db.Integer, primary_key=True)
    RL_Desc = db.Column(db.String(120), unique=True, nullable=False)
    RL_Max_Value = db.Column(db.String(120), unique=True, nullable=False)
    RL_Min_Value = db.Column(db.String(120), unique=True, nullable=False)
    RL_Region = db.Column(db.Integer,db.ForeignKey('regions.R_id'),nullable=False )
    RL_Sensor = db.Column(db.Integer,db.ForeignKey('sensors.S_id') ,nullable=False)

    def __repr__(self):
        return '<Sensor  value\ %r>' % self.SV_value


# db.create_all()