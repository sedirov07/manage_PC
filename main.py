import pyautogui as pg
from flask import Flask, render_template, request, Response

import pyth

app = Flask(__name__)
app.secret_key = '56987'

menu = [{"name": "Удаленный доступ", "url": "/"},
        {"name": "Управление курсором", "url": "/manage"}]


@app.route('/')
def index():

    return render_template('index.html', title='Удаленный доступ', menu=menu, is_running=pyth.is_running(),
                           volume=pyth.get_volume(), info=pyth.get_system_info())


@app.route('/manage')
def manage():
    return render_template('manage.html', title='Управление курсором', menu=menu)


@app.route('/toggle', methods=['POST'])
def toggle():
    data = request.get_json()
    status = data.get('status')
    return pyth.open_close_app(data, status)


@app.route('/video_feed')
def video_feed():
    return Response(pyth.video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/set_volume', methods=['POST'])
def set_volume():
    volume = request.form.get('volume')
    pyth.volume_set(int(volume))
    return 'OK'


@app.route('/click_coordinates', methods=['POST'])
def click_coordinates():
    x = float(request.form['x'])
    y = float(request.form['y'])
    pg.click(x, y)
    print(f"Clicked coordinates: ({x}, {y})")
    return 'OK'


@app.route('/shutdown', methods=['GET'])
def shutdown():
    pyth.shutdown()
    return 'OK'


@app.route('/restart', methods=['GET'])
def restart():
    pyth.restart()
    return 'OK'


@app.route('/virtual_cb', methods=['GET'])
def virtual_cb():
    pyth.start_virtual_cb()
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
