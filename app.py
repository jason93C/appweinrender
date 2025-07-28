from flask import Flask, request, render_template,redirect,url_for,session, jsonify
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_admin.menu import MenuLink
import os
from flask_admin.form import ImageUploadField
from wtforms.fields import SelectField
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask import request, render_template, redirect, url_for, flash





app = Flask(__name__)
app.secret_key = 'ja593one.'

# Necesario para Flask-Admin
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ja593one.@localhost/app_siembraveci'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static','upload')

db = SQLAlchemy(app)

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

# Vista protegida para cada modelo
class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))
    def render(self, template, **kwargs):
        # Agrega el botón de logout en la esquina superior derecha
        kwargs['logout_button'] = Markup('<a class="btn btn-danger" href="/admin/logout">Cerrar sesión</a>')
        return super().render(template, **kwargs)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    Password = db.Column(db.String(200), nullable=False)
    id_Role = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)


class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    imagen = db.Column(db.String(200), nullable=True)
    precio = db.Column(db.Numeric, nullable=False)
    id_Categoria = db.Column(db.Integer, db.ForeignKey('categoria.id'))  # <- Asegúrate de esto
    




class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    id_Usuario = db.Column(db.String(50), nullable=False, unique=True)

        

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)
    
    
class Categoria(db.Model):
    __tablename__ = 'categoria'   
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Orden(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    id_Cliente = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    id_Producto = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_salida = db.Column(db.DateTime,nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    total = db.Column(db.Float, nullable=False)
    id_pago = db.Column(db.Integer, db.ForeignKey('pagos.id'), nullable=False)
    
    
            
class Pagos(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    metodo = db.Column(db.String(50), nullable=False)
    id_Usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)


class Inventario(db.Model):
    __tablename__ = 'inventarios'
    id = db.Column(db.Integer, primary_key=True)
    id_Producto = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad_existentes = db.Column(db.Integer, nullable=False)
    cantidad_entrada = db.Column(db.Integer, nullable=False)
    cantidad_salida = db.Column(db.Integer, nullable=False)
    fecha_ingreso = db.Column(db.DateTime, nullable=False)
    fecha_salida = db.Column(db.DateTime, nullable=True)
    codigo_producto = db.Column(db.String(100), nullable=False)




    admin = Admin(app, name='panel de administracion', template_mode='bootstrap3')
    admin.add_view(ModelView(Producto, db.session))
    admin.add_view(ModelView(Usuario, db.session))
    admin.add_view(ModelView(Cliente, db.session))
    admin.add_view(ModelView(Categoria, db.session))
    admin.add_view(ModelView(Orden, db.session))
    admin.add_view(ModelView(Pagos, db.session))
    admin.add_link(MenuLink(name='Cerrar sesión', category='', url='/admin/logout'))


class ProductoAdmin(ModelView):
    form_extra_fields = {
        'imagen': ImageUploadField('Imagen',
            base_path=os.path.join(os.path.dirname(__file__), 'static/uploads'),
            relative_path='uploads/',
            allow_overwrite=False)
    }
    form_columns = ['nombre', 'descripcion', 'imagen', 'precio', 'id_Categoria']
    
    form_overrides = {
    "nombre": str,
    "descripcion": str,
    "precio": float,
    "Categoria_id": 1
    }

    form_args = {
        'Categoria_id': {
            'coerce': int,
            'label': 'Categoría'
        }
    }
    
    

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.Categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.all()]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.Categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.all()]
        return form

@app.route("/agregar", methods=["POST"])
def agregar_producto():
    data = request.get_json()
    nuevo = Producto(
        nombre=data["nombre"],
        descripcion=data["descripcion"],
        precio=data["precio"],
        Categoria_id=data["Categoria_id"],
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"message": "Producto agregado correctamente."}), 201


@app.route("/")
def home():
    return render_template("home.html")



@app.route("/iniciosecion/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            return redirect(url_for("home"))
        return "Credenciales incorrectas"
    return render_template("iniciosecion.html")


@app.route("/productos/")
def page():
    return render_template("productos.html")

@app.route('/blog')
def blog():
    return render_template("blog.html")


@app.route('/carrito')
def carrito():
    return render_template("carrito.html")

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        # Validar campos vacíos
        if not all([nombre, apellido, email, password, confirm_password, role]):
            flash("Por favor completa todos los campos.", "danger")
            return "Datos incompletos", 400

        if password != confirm_password:
            flash("Las contraseñas no coinciden", "danger")
            return "Error de contraseña", 400

        # Aquí puedes insertar en tu base de datos con SQLAlchemy
        # nuevo_usuario = Usuario(nombre=nombre, ...)
        # db.session.add(nuevo_usuario)
        # db.session.commit()

        flash("Registro exitoso", "success")
        return redirect(url_for('login'))  # o a donde quieras

    return render_template('registro.html')


@app.route('/ventas')
def ventas():
    productos = Producto.query.all()
    return render_template('ventas.html', productos=productos)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = user.query.filter_by(username=username, password=password).first()

        if user:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            error = 'Usuario o contraseña incorrectos'
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))





if __name__ == "__main__":
    os.makedirs(os.path.join(os.getcwd(), 'static/uploads'), exist_ok=True)
    db.create_all()
    app.run(debug=True)