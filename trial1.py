import cv2
from flask import Flask, Response, render_template, request
app = Flask(__name__)

camera1 = None  
camera2 = None  

def generate_frames1():
    while True:
        if camera1 is not None:
            success, frame = camera1.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_frames2():
    while True:
        url = 'http://192.168.29.216:4747/video'
        cap = cv2.VideoCapture(url)
        while True:
            success, frame = cap.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global camera1, camera2
    if camera1 is None:
        camera1 = cv2.VideoCapture(0)
    if camera2 is None:
        camera2 = cv2.VideoCapture(1)
    return 'Video streams started'

@app.route('/stop', methods=['POST'])
def stop():
    global camera1, camera2
    if camera1 is not None:
        camera1.release()
        camera1 = None
    if camera2 is not None:
        camera2.release()
        camera2 = None
    return 'Video streams stopped'
@app.route('/video_stream1')
def video_stream1():
    return Response(generate_frames1(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_stream2')
def video_stream2():
    return Response(generate_frames2(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
