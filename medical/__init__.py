from flask import Flask
from urllib.parse import quote
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
import cloudinary

app = Flask(__name__)

app.secret_key = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()0123456789'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/medicaldb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 10

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ami5692643@gmail.com'
app.config['MAIL_PASSWORD'] = 'rhadhawgpeqmivyr'  # App password từ Google
app.config['MAIL_DEFAULT_SENDER'] = ('MSSO_N10', 'ami5692643@gmail.com')

db = SQLAlchemy(app)
login = LoginManager(app)
mail = Mail(app)

scheduler = BackgroundScheduler()

# Configuration
cloudinary.config(
    cloud_name="dvn6qzq9o",
    api_key="438998175576659",
    api_secret="2PhCeDJfEWebcAPrYZSHM3fHweI",  # Click 'View API Keys' above to copy your API secret
    secure=True
)
