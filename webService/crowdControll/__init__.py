from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from crowdControll.trainedModel.models import vgg19
import torch

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['GOOGLEMAPS_KEY'] = "5791628bb0b13ce0c676dfde2680ba245"

model_path = "crowdControll/trainedModel/model_qnrf.pth"
device = torch.device('cpu')  # device can be "cpu" or "gpu"

model = vgg19()
model.to(device)
model.load_state_dict(torch.load(model_path, device))
model.eval()

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from crowdControll import routes
