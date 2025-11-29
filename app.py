from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

# Путь к файлу, который мы будем скачивать
DOWNLOAD_FILE = 'video.mp4'

def download_tiktok_video(url):
    # Если старый файл есть, удаляем его, чтобы не мешал
    if os.path.exists(DOWNLOAD_FILE):
        os.remove(DOWNLOAD_FILE)

    ydl_opts = {
        'outtmpl': DOWNLOAD_FILE,
        'format': 'best',
        'quiet': True,
        # Добавляем маскировку под настоящий браузер Chrome
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Внимание: здесь download=True, мы реально скачиваем файл на диск
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
            return {'status': 'success', 'title': title}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_video():
    data = request.json
    tiktok_url = data.get('url')
    
    if not tiktok_url:
        return jsonify({'status': 'error', 'message': 'Ссылка не найдена'})

    # Сначала скачиваем видео на сервер (ваш компьютер)
    result = download_tiktok_video(tiktok_url)
    
    if result['status'] == 'success':
        # Если скачалось, говорим сайту: "Файл готов, вот ссылка на скачивание с моего ПК"
        return jsonify({
            'status': 'success', 
            'title': result['title'], 
            'download_url': '/download_file' # Ссылка ведет на наш же сервер
        })
    else:
        return jsonify(result)

# Новый маршрут: отдает скачанный файл пользователю
@app.route('/download_file')
def send_video():
    try:
        return send_file(DOWNLOAD_FILE, as_attachment=True, download_name='tiktok_video.mp4')
    except Exception as e:
        return f"Ошибка при отдаче файла: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
