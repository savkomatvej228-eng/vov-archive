from flask import Flask, render_template, abort, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ---------- Настройка базы данных ----------
# Приоритет: переменная окружения DATABASE_URL (для PostgreSQL)
# Если её нет, используем SQLite для локальной разработки
POSTGRES_URL = os.environ.get("DATABASE_URL")
if POSTGRES_URL and POSTGRES_URL.startswith("postgres://"):
    # Render иногда даёт строку postgres://, но SQLAlchemy требует postgresql://
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

if POSTGRES_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ww2_archive.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----- МОДЕЛИ -----
class Topic(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    text = db.Column(db.Text)
    audio = db.Column(db.String(100))
    video = db.Column(db.String(100))
    images = db.relationship('Image', backref='topic', lazy=True, cascade='all, delete-orphan')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200))
    topic_id = db.Column(db.String(50), db.ForeignKey('topic.id'), nullable=False)

class Hero(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    text = db.Column(db.Text)
    image = db.Column(db.String(100))
    audio = db.Column(db.String(100))
    video = db.Column(db.String(100))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

class Report(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)

# ----- КОНТЕКСТНЫЙ ПРОЦЕССОР -----
@app.context_processor
def inject_current_page():
    return dict(current_page=request.path)

# ----- МАРШРУТЫ -----
@app.route('/')
def home():
    operations_count = Topic.query.count()
    heroes_count = Hero.query.count()
    return render_template('index.html',
                           operations_count=operations_count,
                           heroes_count=heroes_count)

@app.route('/operations')
def operations_list():
    topics = Topic.query.all()
    return render_template('operations.html', topics=topics)

@app.route('/topic/<topic_id>')
def topic_detail(topic_id):
    topic = Topic.query.get(topic_id)
    if not topic:
        abort(404)
    return render_template('operation_detail.html', topic=topic)

@app.route('/heroes')
def heroes_list():
    heroes = Hero.query.all()
    return render_template('heroes.html', heroes=heroes)

@app.route('/hero/<hero_id>')
def hero_detail(hero_id):
    hero = Hero.query.get(hero_id)
    if not hero:
        abort(404)
    return render_template('hero_detail.html', hero=hero)

@app.route('/reports')
def reports_list():
    reports = Report.query.all()
    return render_template('reports.html', reports=reports)

@app.route('/report/<report_id>')
def report_detail(report_id):
    report = Report.query.get(report_id)
    if not report:
        abort(404)
    return render_template('report_detail.html', report=report)

# ----- ЭНДПОИНТ ДЛЯ UPTIMEROBOT (НЕ ДАЁМ САЙТУ ЗАСНУТЬ) -----
@app.route('/health')
def health_check():
    return 'OK', 200

# ----- КЭШИРОВАНИЕ СТАТИКИ (ОПЦИОНАЛЬНО, ДЛЯ УСКОРЕНИЯ) -----
@app.route('/static/<path:filename>')
def custom_static(filename):
    response = send_from_directory(app.static_folder, filename)
    # Кэшировать на 1 час
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

# ----- ЗАПУСК ПРИЛОЖЕНИЯ -----
if __name__ == '__main__':
    with app.app_context():
        db.create_all()          # создаём таблицы, если их нет
    # Render передаёт порт в переменной окружения PORT
    port = int(os.environ.get('PORT', 5000))
    # Обязательно host='0.0.0.0' для доступа извне
    app.run(host='0.0.0.0', port=port)