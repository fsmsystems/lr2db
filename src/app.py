# app.py - a minimal flask api using flask_restful
import os,time, datetime
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_influxdb import InfluxDB

app = Flask(__name__)


INFLUXDB_HOST = 'influxdb'
INFLUXDB_DATABASE = 'lr2db'
INFLUXDB_PORT = '8086'


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['INFLUXDB_HOST'] = INFLUXDB_HOST
app.config['INFLUXDB_DATABASE'] = INFLUXDB_DATABASE
app.config['INFLUXDB_PORT'] = INFLUXDB_PORT

influx_db = InfluxDB(app=app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#@app.route('/')
#def hello_world():
#    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            #changed to be static
            filename = 'upload.csv'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
# clock_time,time_stamp,val,metric,region,location_name,script,transaction,error_message,emulation,source,unit,total_duration
     influx_db.database.create(INFLUXDB_DATABASE)
     influx_db.database.switch(INFLUXDB_DATABASE)
     with open(UPLOAD_FOLDER+'/'+filename, "r") as file:
         for line in file.readlines()[1:]: #Skiping the first line (headers): clock_time,time_stamp,val,metric,region,location_name,script,transaction,error_message,emulation,source,unit,total_duration
            rline = line.split(',')
            print('Data')
            timedata=str(rline[0])           
            print(timedata)
            print(rline)
            if rline[2]:
               try: #Per algun motiu, hi ha algun camp que no ho agafa bé
                 value=float(rline[2])
               except ValueError:
                 print("error")
               #datetime.strptime(timedata('"'), '%Y-%m-%dT%H:%M:%S.%f')
               line_object = [{ "measurement":"http_request",
                           "tags": {
                            'location_name':rline[5],
                            'script':rline[6],
                            'transaction':rline[7],
                            'metric':rline[3],
                              },
                            "time":timedata,   # 2020-05-15T07:25:51Z
                            #"time":"2020-05-15T07:25:46Z",
                            "fields": {
                              'time_stamp':rline[1],
                              'val':value,
                              'metric':rline[3],
                              'region':rline[4],
                              'location_name':rline[5],
                              'script':rline[6],
                              'error_message':rline[8],
                              'emulation':rline[9],
                              'source':rline[10],
                              'unit':rline[11],
                              'total_duration':rline[12]
                           }
               }]
               print(value)
               print(timedata)
               print(line_object)
               influx_db.write_points(line_object,time_precision='ms') 


     os.remove(UPLOAD_FOLDER+'/'+filename)
     return 'Done! '
#       return render_template('upload.html')
          

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
    influx_db = InfluxDB(app=app)
