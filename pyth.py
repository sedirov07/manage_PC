import numpy as np
import pyautogui as pg
import platform
import socket
import re
import uuid
import psutil
import logging
import openai
import os
import cv2
import GPUtil
import subprocess
from flask import jsonify


def is_running():
    required_processes = ['steam', 'discord', 'browser', 'csgo', 'launcher', 'taskmgr']
    running = {}
    for apps in required_processes:
        running[apps] = any(apps in p.name().lower() for p in psutil.process_iter())
    return running


def open_close_app(data, status=None):
    discord_path = r"C:\Users\Арсен\AppData\Local\Discord\app-1.0.9013\Discord.exe"
    steam_path = r"D:\Steam\steam.exe"
    yandex_browser_path = r"C:\Users\Администратор\AppData\Local\Yandex\YandexBrowser\Application\browser.exe"
    sims4_path = r"D:\Games\The Sims 4\Launcher.exe"
    csgo_path = r"steam://rungameid/730"
    if status is not None:
        if status:
            if data['name'] == "steam":
                os.system("taskkill /f /im Steam.exe")
            elif data['name'] == "discord":
                os.system("taskkill /f /im Discord.exe")
            elif data['name'] == "yandex":
                os.system("taskkill /f /im Browser.exe")
            elif data['name'] == "the sims 4":
                os.system("taskkill /f /im Launcher.exe")
            elif data['name'] == "cs:go":
                os.system("taskkill /f /im csgo.exe")
            elif data['name'] == "taskmgr":
                for proc in psutil.process_iter():
                    if proc.name() == "Taskmgr.exe":
                        proc.kill()
        else:
            if data['name'] == "discord":
                os.startfile(discord_path)
            elif data['name'] == "steam":
                os.startfile(steam_path)
            elif data['name'] == "yandex":
                os.startfile(yandex_browser_path)
            elif data['name'] == "the sims 4":
                pg.sleep(1)
                os.startfile(sims4_path)
                pg.moveTo(700, 475)
                pg.sleep(0.5)
                pg.click()
                pg.sleep(0.5)
                pg.moveTo(900, 595)
                pg.sleep(0.5)
                pg.click()
            elif data['name'] == "cs:go":
                os.startfile(csgo_path)
            elif data['name'] == "taskmgr":
                os.startfile("taskmgr.exe")
        # Отправляем ответ в формате JSON (можно изменить по необходимости)
        return jsonify({'status': 'success'})
    else:
        # Если статус не был передан или не удалось его получить
        return jsonify({'status': 'error', 'message': 'Invalid request'})


def send_to_chatgpt(message):
    openai.api_key = 'api_key'

    def send_message(mess):
        response = openai.Completion.create(
            model="gpt-3.5-turbo-0301",
            prompt=mess,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
        )

        return response.choices[0].text.strip()

    return jsonify({"reply": send_message(message)})


def video_stream():
    while True:
        # Capture the current frame using PyAutoGUI
        img = pg.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)

        # Get the byte representation of the frame
        frame_bytes = buffer.tobytes()

        # Generate the video stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def volume_set(volume):
    command = f'powershell.exe "Set-AudioDevice -PlaybackVolume {volume}"'
    subprocess.run(command, shell=True)


def get_volume():
    command = f'powershell.exe "Get-AudioDevice -PlaybackVolume"'
    output = subprocess.check_output(command, shell=True)
    volume_level = output.decode().strip()
    volume = str(int(float(volume_level[:-1].replace(',', '.')))) + volume_level[-1]
    return volume


def get_system_info():
    try:
        info = dict()
        gpu_info = get_gpu_info()
        info['Операционная система'] = platform.system()
        info['Версия операционной системы'] = platform.release()
        info['Полная версия операционной системы'] = platform.version()
        info['Архитектура'] = platform.machine()
        info['Имя компьютера'] = socket.gethostname()
        info['ip-address'] = socket.gethostbyname(socket.gethostname())
        info['mac-address'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        info['Процессор'] = platform.processor()
        info['Объём оперативной памяти'] = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
        info['Видеокарта'] = f"{gpu_info[0]['Name']}, {int(gpu_info[0]['Memory Total (MB)'])} MB"
        return info
    except Exception as e:
        logging.exception(e)
        return {'error': str(e)}


def get_gpu_info():
    gpu_info = []

    # Получение списка доступных видеокарт
    gpus = GPUtil.getGPUs()

    for gpu in gpus:
        gpu_dict = {}

        # Имя видеокарты
        if gpu.name:
            gpu_dict['Name'] = gpu.name

        # Использование видеопамяти
        if gpu.memoryUsed:
            gpu_dict['Memory Used (MB)'] = gpu.memoryUsed

        # Общий объем видеопамяти
        if gpu.memoryTotal:
            gpu_dict['Memory Total (MB)'] = gpu.memoryTotal

        gpu_info.append(gpu_dict)

    return gpu_info


def shutdown():
    subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(["shutdown", "/s", "/t", "1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def restart():
    subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(["shutdown", "/r", "/t", "1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def start_virtual_cb():
    os.system("osk")
