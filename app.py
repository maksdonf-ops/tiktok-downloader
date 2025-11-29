
from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp
import os
import uuid
import time

app = Flask(__name__)

def download_video(url, filename):
    # Проверяем куки
    cookie_file = 'cookies.txt'
    if not os.path.exists(cookie_file):
        print("!!! ОШИБКА: Файл cookies.txt не найден в папке проекта !!!")

    ydl_opts = {
        'outtmpl': filename,
        'format': 'best',
        'quiet': False, # Включаем логи, чтобы видеть детали в Render
        'verbose': True, # Подробный режим для отладки
        'cookiefile': cookie_file,
        # Убрали impersonate, оставили только обычный заголовок
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }
    
    try:
        print(f"Начинаю скачивание: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            print("Скачивание завершено успешно!")
            return True
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА YT-DLP: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST', 'GET'])
def download_route():
    if request.method == 'GET':
        return redirect(url_for('index'))

    tiktok_url = request.form.get('url')
    if not tiktok_url:
        return "Ошибка: Ссылка пустая", 400

    unique_name = f"{uuid.uuid4()}.mp4"

    success = download_video(tiktok_url, unique_name)
    
    if success and os.path.exists(unique_name):
        try:
            return send_file(unique_name, as_attachment=True, download_name='tiktok_video.mp4')
        except Exception as e:
            return f"Ошибка отправки: {e}"
    else:
        # Теперь эта ошибка будет показываться, только если куки протухли
        return "Не удалось скачать. Проверьте логи Render (возможно, куки не работают).", 500

@app.after_request
def cleanup(response):
    try:
        for file in os.listdir('.'):
            if file.endswith('.mp4'):
                if time.time() - os.path.getmtime(file) > 120:
                    os.remove(file)
    except:
        pass
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
