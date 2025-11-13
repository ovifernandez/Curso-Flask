from flask import (
    Flask, render_template, abort, redirect, url_for, request, make_response
)
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from aplicacion import config
from aplicacion.forms import (
    FormCategoria, FormArticulo, FormSINO, LoginForm,
    FormUsuario, FormChangePassword, FormCarrito
)
from werkzeug.utils import secure_filename
from flask_login import (
    LoginManager, login_user, logout_user, login_required,
    current_user
)
import os
import json

# --- 1. INICIALIZACIÓN DE EXTENSIONES (SIN APP) ---
# Creamos las extensiones aquí, pero no las vinculamos a ninguna app
db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()


# --- 2. CREACIÓN DE LA APP ---
app = Flask(__name__)
app.config.from_object(config)


# --- 3. IMPORTACIÓN DE MODELOS ---
# Este es el lugar correcto para importar los modelos.
# Justo después de crear 'app' y ANTES de inicializar 'db'
# ¡Asegúrate de que tienes la clase 'Usuarios' en tu 'models.py'!
from aplicacion.models import Articulos, Categorias, Usuarios


# --- 4. VINCULACIÓN DE EXTENSIONES (CON APP) ---
# Ahora que todo está importado, vinculamos las extensiones a la app
db.init_app(app)
bootstrap.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"


# --- 5. RUTAS Y LÓGICA DE LA APLICACIÓN ---

# Esta función 'load_user' debe estar definida ANTES de cualquier
# ruta que la necesite. La muevo aquí arriba.
@login_manager.user_loader
def load_user(user_id):
    # Ya no necesitas importar 'Usuarios' aquí dentro.
    return Usuarios.query.get(int(user_id))


@app.route('/')
@app.route('/categoria/<id>')
def inicio(id='0'):
    # Ya no necesitas importar 'Articulos' y 'Categorias' aquí dentro.
    categoria = Categorias.query.get(id)
    if id == '0':
        articulos = Articulos.query.all()
    else:
        articulos = Articulos.query.filter_by(CategoriaId=id)
    categorias = Categorias.query.all()
    return render_template("inicio.html", articulos=articulos,
                           categorias=categorias, categoria=categoria)


@app.route('/categorias')
def categorias():
    all_categorias = Categorias.query.all()
    return render_template("categorias.html", categorias=all_categorias)


@app.route('/categorias/new', methods=["get", "post"])
@login_required
def categorias_new():
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    # El formulario se instancia VACÍO. Flask-WTF se encarga de 'request.form'
    form = FormCategoria()
    
    if form.validate_on_submit():
        cat = Categorias(nombre=form.nombre.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for("categorias"))
    else:
        return render_template("categorias_new.html", form=form)

# --- ¡ERROR ARREGLADO! ---
# La función duplicada que tenías aquí ha sido eliminada.


@app.route('/categorias/<id>/edit', methods=["get", "post"])
@login_required
def categorias_edit(id):
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
    cat = Categorias.query.get(id)
    if cat is None:
        abort(404)
        
    # El formulario se carga con el objeto 'cat'
    form = FormCategoria(obj=cat)
    
    if form.validate_on_submit():
        form.populate_obj(cat)
        db.session.commit()
        return redirect(url_for("categorias"))
    return render_template("categorias_new.html", form=form)


@app.route('/categorias/<id>/delete', methods=["get", "post"])
@login_required
def categorias_delete(id):
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
    cat = Categorias.query.get(id)
    if cat is None:
        abort(404)
    form = FormSINO()
    if form.validate_on_submit():
        if form.si.data:
            db.session.delete(cat)
            db.session.commit()
        return redirect(url_for("categorias"))
    return render_template("categorias_delete.html", form=form, cat=cat)


@app.route('/articulos/new', methods=["get", "post"])
@login_required
def articulos_new():
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
    form = FormArticulo()
    
    # Consejo de optimización: filtra en la BD, no en Python.
    categorias = [(c.id, c.nombre) for c in Categorias.query.filter(Categorias.id > 1).all()]
    
    form.CategoriaId.choices = categorias
    if form.validate_on_submit():
        nombre_fichero = "" # Inicializa por si 'try' falla
        try:
            f = form.photo.data
            if f: # Comprueba si se subió un archivo
                nombre_fichero = secure_filename(f.filename)
                f.save(os.path.join(app.root_path, "static/upload", nombre_fichero))
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            nombre_fichero = "" # Asegura que sea "" si falla
            
        art = Articulos()
        form.populate_obj(art)
        art.image = nombre_fichero
        db.session.add(art)
        db.session.commit()
        return redirect(url_for("inicio"))
    else:
        return render_template("articulos_new.html", form=form)


@app.route('/articulos/<id>/edit', methods=["get", "post"])
@login_required
def articulos_edit(id):
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
    art = Articulos.query.get(id)
    if art is None:
        abort(404)
    form = FormArticulo(obj=art)
    
    # Mismo consejo de optimización aquí
    categorias = [(c.id, c.nombre) for c in Categorias.query.filter(Categorias.id > 1).all()]
    
    form.CategoriaId.choices = categorias
    if form.validate_on_submit():
        nombre_fichero = art.image # Por defecto, mantiene la imagen antigua
        # Borramos la imagen anterior si hemos subido una nueva
        if form.photo.data:
            if art.image: # Asegúrate que 'art.image' no esté vacío
                try:
                    os.remove(os.path.join(app.root_path, "static/upload", art.image))
                except FileNotFoundError:
                    pass # El archivo no existía, no pasa nada
            try:
                f = form.photo.data
                nombre_fichero = secure_filename(f.filename)
                f.save(os.path.join(app.root_path, "static/upload", nombre_fichero))
            except Exception as e:
                print(f"Error al guardar nueva imagen: {e}")
                nombre_fichero = "" # Si falla, no asigna imagen
        
        form.populate_obj(art)
        art.image = nombre_fichero
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("articulos_new.html", form=form)


@app.route('/articulos/<id>/delete', methods=["get", "post"])
@login_required
def articulos_delete(id):
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
    art = Articulos.query.get(id)
    if art is None:
        abort(404)
    form = FormSINO()
    if form.validate_on_submit():
        if form.si.data:
            if art.image: # Asegúrate que 'art.image' no esté vacío
                try:
                    os.remove(os.path.join(app.root_path, "static/upload", art.image))
                except FileNotFoundError:
                    pass
            db.session.delete(art)
            db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("articulos_delete.html", form=form, art=art)


@app.route('/login', methods=['get', 'post'])
def login():
    # Control de permisos
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('inicio'))
        form.username.errors.append("Usuario o contraseña incorrectas.")
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required # Buena práctica: solo quien está logueado puede desloguearse
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/registro", methods=["get", "post"])
def registro():
    # Control de permisos
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))
    form = FormUsuario()
    if form.validate_on_submit():
        existe_usuario = Usuarios.query.filter_by(username=form.username.data).first()
        if existe_usuario is None:
            user = Usuarios()
            form.populate_obj(user)
            user.admin = False
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("inicio"))
        form.username.errors.append("Nombre de usuario ya existe.")
    return render_template("usuarios_new.html", form=form)


@app.route('/perfil/<username>', methods=["get", "post"])
@login_required
def perfil(username):
    # Control de permisos
    if current_user.username != username:
        abort(403) # Error 'Forbidden', no puedes editar perfiles ajenos
        
    user = Usuarios.query.filter_by(username=username).first()
    if user is None:
        abort(404)
        
    # 'request.form' no es necesario aquí, 'obj=user' es para cargar datos
    form = FormUsuario(obj=user)
    del form.password # Buena idea eliminar el campo de contraseña
    
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("usuarios_new.html", form=form, perfil=True)


@app.route('/changepassword/<username>', methods=["get", "post"])
@login_required
def changepassword(username):
    # Control de permisos
    if current_user.username != username:
        abort(403) # Error 'Forbidden'
        
    user = Usuarios.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    form = FormChangePassword()
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("changepassword.html", form=form)


@app.route('/carrito/add/<id>', methods=["get", "post"])
@login_required
def carrito_add(id):
    art = Articulos.query.get(id)
    if art is None:
        abort(404)
        
    form = FormCarrito()
    form.id.data = id
    
    if form.validate_on_submit():
        cantidad = int(form.cantidad.data)
        if art.stock >= cantidad:
            try:
                datos = json.loads(request.cookies.get(str(current_user.id)))
            except:
                datos = []
            
            actualizar = False
            for dato in datos:
                if dato["id"] == id:
                    dato["cantidad"] = cantidad
                    actualizar = True
            
            if not actualizar:
                datos.append({"id": form.id.data,
                              "cantidad": cantidad})
                              
            resp = make_response(redirect(url_for('inicio')))
            resp.set_cookie(str(current_user.id), json.dumps(datos))
            return resp
            
        form.cantidad.errors.append("No hay artículos suficientes.")
    return render_template("carrito_add.html", form=form, art=art)


@app.route('/carrito')
@login_required
def carrito():
    try:
        datos = json.loads(request.cookies.get(str(current_user.id)))
    except:
        datos = []
        
    articulos = []
    cantidades = []
    total = 0
    for articulo in datos:
        art = Articulos.query.get(articulo["id"])
        if art: # Comprueba que el artículo todavía existe
            cantidad_art = int(articulo["cantidad"])
            articulos.append(art)
            cantidades.append(cantidad_art)
            total += art.precio_final() * cantidad_art
            
    articulos_con_cantidad = zip(articulos, cantidades)
    return render_template("carrito.html", articulos=articulos_con_cantidad, total=total)


@app.route('/carrito_delete/<id>')
@login_required
def carrito_delete(id):
    try:
        datos = json.loads(request.cookies.get(str(current_user.id)))
    except:
        datos = []
        
    new_datos = []
    for dato in datos:
        if dato["id"] != id:
            new_datos.append(dato)
            
    resp = make_response(redirect(url_for('carrito')))
    resp.set_cookie(str(current_user.id), json.dumps(new_datos))
    return resp


@app.context_processor
def contar_carrito():
    if not current_user.is_authenticated:
        return {'num_articulos': 0}
    
    cookie_data = request.cookies.get(str(current_user.id))
    if not cookie_data:
        return {'num_articulos': 0}
    
    try:
        datos = json.loads(cookie_data)
        return {'num_articulos': len(datos)}
    except:
        return {'num_articulos': 0}


@app.route('/pedido')
@login_required
def pedido():
    try:
        datos = json.loads(request.cookies.get(str(current_user.id)))
    except:
        datos = []
        
    if not datos: # Si el carrito está vacío, redirige
        return redirect(url_for('inicio'))
        
    total = 0
    
    # ¡CUIDADO! Esto debe ser una transacción.
    # Si algo falla a la mitad, la base de datos quedará inconsistente.
    try:
        for articulo in datos:
            art = Articulos.query.get(articulo["id"])
            if art is None:
                continue # El artículo fue borrado
                
            cantidad_pedida = int(articulo["cantidad"])
            
            if art.stock < cantidad_pedida:
                # Aquí deberías manejar el error (ej. redirigir al carrito)
                # Por ahora, solo saltamos este artículo y no lo cobramos
                continue 
                
            total += art.precio_final() * cantidad_pedida
            
            # --- Advertencia de Lógica de Negocio ---
            # Esto es una "race condition". 
            # Es mejor usar una actualización atómica, pero para este curso es OK.
            art.stock -= cantidad_pedida
            
        db.session.commit() # Confirma todos los cambios al stock
        
        resp = make_response(render_template("pedido.html", total=total))
        resp.set_cookie(str(current_user.id), "", expires=0) # Borra la cookie
        return resp

    except Exception as e:
        db.session.rollback() # Deshace los cambios si algo falló
        print(f"Error durante el pedido: {e}")
        # Idealmente, aquí registras el error 'e'
        return redirect(url_for('carrito')) # Envía al usuario de vuelta


@app.errorhandler(404)
def pague_not_found(error):
    return render_template("error.html", error="Página no encontrada..."), 404