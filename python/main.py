from flask import Flask, render_template, Response
from flask.ext.cors import CORS, cross_origin
from camera import VideoCamera

app = Flask(__name__)
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/load_ajax', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def load_ajax():
    vars = request.data
    return ', '.join([str(i) for i in vars])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
