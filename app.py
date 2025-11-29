
from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import time

app = Flask(__name__)

# Имя файла делаем динамическим, чтобы не было конфликтов
DOWNLOAD_FILE = 'video.mp4'

def download_video(url):
    # Опции с маскировкой под браузер Chrome
    ydl_opts = {
        'outtmpl': DOWNLOAD_FILE,
        'format': 'best',
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }
    
    # Удаляем старый файл перед скачиванием
    if os.path.exists(DOWNLOAD_FILE):
        os.remove(DOWNLOAD_FILE)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_route():
    # Получаем ссылку из формы (input name="url")
    tiktok_url = request.form.get('url')
    
    if not tiktok_url:
        return "Ошибка: Ссылка пустая", 400

    # Скачиваем
    success = download_video(tiktok_url)
    
    if success and os.path.exists(DOWNLOAD_FILE):
        # Отдаем файл браузеру напрямую
        # as_attachment=True заставляет браузер сразу начать скачку, а не открывать видео
        return send_file(DOWNLOAD_FILE, as_attachment=True, download_name='tiktok_no_watermark.mp4')
    else:
        return "Не удалось скачать видео. Возможно, приватный профиль или неверная ссылка."

if __name__ == '__main__':
    app.run(debug=True, port=5000)
