from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moc-tiny.db'
db = SQLAlchemy(app)


class Log_Data(db.Model):
    __tablename__ = "data"
    D_id = db.Column(db.Integer, primary_key=True)
    D_temprature = db.Column(db.Float, unique=False, nullable=False)
    D_hummidity = db.Column(db.Float, unique=False, nullable=False)
    D_Lux = db.Column(db.Float, unique=False, nullable=False)
    D_time = db.Column(db.String(40), unique=False, nullable=False)
    U_image_path = db.Column(db.String(80), unique=False, nullable=True)
    U_image_thumb_path = db.Column(db.String(80), unique=False, nullable=True)
    U_Desc = db.Column(db.String(120), unique=False, nullable=True)
   

    def __repr__(self):
        return '<Data %d>' % self.D_id

db.create_all()

