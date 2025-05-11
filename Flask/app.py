from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

# You can change 0 to a video stream URL or /dev/videoX
camera = cv2.VideoCapture(1)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # MJPEG streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')  # Serve HTML

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5050)
	app.run()
