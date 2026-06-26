from flask import Flask, render_template
from routes.measurement_routes import meas_bp

app = Flask(__name__)

app.secret_key = "key"
app.register_blueprint(meas_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)