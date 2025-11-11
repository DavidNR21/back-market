from flask import *
import datetime
from models.models import *
from routes.routes import user_bp


app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

version = "v1"

#################################################
app.register_blueprint(user_bp, url_prefix = f"/api/{version}/user") # v1


#################################################



@app.route('/')
def index():

    return 'No Ar...'


if __name__ == '__main__':
    app.run(debug=True)
