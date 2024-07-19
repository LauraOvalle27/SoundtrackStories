from flask import Flask
from routes import init_routes
from flask_session import Session
import os

app = Flask(__name__)

app.config['DATABASE'] = os.path.join(app.root_path, 'site.db')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = "mirrorball"

init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)

