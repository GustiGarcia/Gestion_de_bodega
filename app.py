# Importamos librerias, rutas y modelos
from flask import Flask, render_template, request, redirect, url_for, flash
from config.config import Config 
from models.db import db
from routes.variedadUva_routes import variedadUva_bp
from routes.loteVino_routes import loteVino_bp
from routes.recepcionUva_routes import recepcionUva_bp
from routes.fermentacionAlcoholica_routes import fermentacion_bp
from routes.crianza_almacenamiento_routes import crianza_bp
from routes.embotellado_routes import embotellado_bp

# Importaciones para Flask-Login
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user 

# Creamos la app
app = Flask(__name__)

# Configuración de Flask-Login
login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuración de la clave secreta (usa la de tu .env en producción)
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_segura_y_larga_para_tu_proyecto_de_bodega'

# Cargar configuración desde Config
app.config.from_object(Config)

# Inicializar base de datos
db.init_app(app)

# Clase de Usuario para Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id
    def get_id(self):
        return str(self.id)

# Usuario de prueba
USERS = {
    "admin": {"password": "1234"}
}

# Función para recargar el usuario desde la sesión
@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None

# ===== REGISTRAR BLUEPRINTS =====
app.register_blueprint(variedadUva_bp, url_prefix="/variedades")
app.register_blueprint(loteVino_bp, url_prefix="/lotes")
app.register_blueprint(recepcionUva_bp, url_prefix="/recepcion")
app.register_blueprint(fermentacion_bp, url_prefix="/fermentacion")
app.register_blueprint(crianza_bp, url_prefix="/crianza")
app.register_blueprint(embotellado_bp, url_prefix="/embotellado")

# ===== RUTAS PRINCIPALES =====
@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

# Rutas de Login y Logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            next_page = request.args.get('next') 
            return redirect(next_page or url_for('index'))
        else:
            flash('Credenciales inválidas. Inténtalo de nuevo.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

# ===== INICIALIZAR BASE DE DATOS =====
with app.app_context():
    db.create_all()

# ===== EJECUCIÓN LOCAL =====
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)