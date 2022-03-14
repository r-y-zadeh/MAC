

from tiny_logger_model import Log_Data ,db


def inset_to_db(result):
    dt = Log_Data(D_temprature= result["temprature"], D_hummidity= result["humidity"], 
                    D_Lux= result["light"], D_time= result["time"] ,
                    U_image_path=  result["image"],U_image_thumb_path = result["thumb"], U_Desc="_" )
    db.session.add(dt)
    db.session.commit()

def get_top_records(top_num=10):

    x= Log_Data.query.order_by(Log_Data.D_id.desc()).limit(top_num)
    for y in x :
        print (y.D_temprature)
    return y
    
    
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
