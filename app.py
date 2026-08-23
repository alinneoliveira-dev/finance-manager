from flask import Flask, render_template

from routes.dashboard import dashboard_bp
from routes.transacoes import transacoes_bp
from routes.categorias import categorias_bp
from routes.limites import limites_bp

app = Flask(__name__)

app.register_blueprint(dashboard_bp)
app.register_blueprint(transacoes_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(limites_bp)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
