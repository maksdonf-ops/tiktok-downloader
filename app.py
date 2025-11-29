
from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp
import os
import uuid
import time

app = Flask(__name__)

def download_video(url, filename):
    ydl_opts = {
        'outtmpl': filename,
        'format': 'best',
        'quiet': True,
        # Включаем продвинутую маскировку (теперь у нас есть curl_cffi)
        'impersonate': 'chrome', 
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            return True
    except Exception as e:
        print(f"ERROR LOG: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

# Разрешаем И POST (скачивание), И GET (если браузер тупит)
@app.route('/download', methods=['POST', 'GET'])
def download_route():
    # Если кто-то зашел сюда просто так (GET) - кидаем на главную
    if request.method == 'GET':
        return redirect(url_for('index'))

    # Логика для POST (нажатие кнопки)
    tiktok_url = request.form.get('url')
    
    if not tiktok_url:
        return "Ошибка: Пустая ссылка", 400

    unique_name = f"{uuid.uuid4()}.mp4"

    success = download_video(tiktok_url, unique_name)
    
    if success and os.path.exists(unique_name):
        try:
            return send_file(unique_name, as_attachment=True, download_name='tiktok_video.mp4')
        except Exception as e:
            return f"Ошибка отправки файла: {e}"
    else:
        return "Ошибка: ТикТок не отдал видео (возможно, оно 18+ или приватное)", 500

@app.after_request
def cleanup(response):
    try:
        for file in os.listdir('.'):
            if file.endswith('.mp4'):
                # Удаляем файлы старше 2 минут
                if time.time() - os.path.getmtime(file) > 120:
                    os.remove(file)
    except:
        pass
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
