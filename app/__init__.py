from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Message, Mail
from flask_bcrypt import Bcrypt
from flask_login import login_required
import os

from dotenv import load_dotenv
load_dotenv('.env')

#-----#-----#-----#-----#-----#-----#

app = Flask(__name__)

mail = Mail(app)
mail.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FILES'] = r'static/img/'
#Funfou


#app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
#app.config['MAIL_PORT'] = 2525
#app.config['MAIL_USERNAME'] = 'e515ff873718d1'
#app.config['MAIL_PASSWORD'] = '********ee19'
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = False
#
#@app.route('/sendemailteste/')
#def indextestePage():  
#    message = Message(
#        subject = 'lalala teste',
#        recipients = ['mateuspansteingorges@gmail.com'],
#        sender = 'celestialkaffe@gmail.com',
#        body = 'e  trabalho escolar ignorar bla bla bla deu certo porra vamo'
#    )
#    mail.send(message)
#    return render_template('sendemailteste.html', message=message)


db = SQLAlchemy(app)
migrate = Migrate(app,db,render_as_batch=True)

bcrypt = Bcrypt(app)

#login_manager = LoginManager(app)
#login_manager.init_app(app)

#-----#-----#-----#-----#-----#-----#

from app.views import IndexPage # aqui é para mudar dps para HomePage
from app.models import Itens, Usuario