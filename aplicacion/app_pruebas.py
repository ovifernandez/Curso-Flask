from jinja2 import Template
from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
    abort,
)
from flask import SQLAlchemy
from aplicacion.forms import formcalculadora 
from config import config
app = Flask(__name__)

app.config.from_object(config)
db = SQLAlchemy(app)

form = formcalculadora(request.form)

@app.route("/calculadora_post", methods=["get","post"])
def calculadora_post():
	if request.method=="POST":
		num1=request.form.get("num1")
		num2=request.form.get("num2")
		operador=request.form.get("operador")
	
		try:
			resultado=eval(num1+operador+num2)
		except:
			return render_template("error.html",error="No puedo realizar la operación")
		
		return render_template("resultado.html",num1=num1,num2=num2,operador=operador,resultado=resultado)	
	else:
		return render_template("calculadora_post.html")

@app.route('/info', methods=['GET', 'POST'])
def info():
    cad = ""
    cad += "\nURL:" + request.url + "\n"
    cad += "\n\\n\n\nMetodo:" + request.method + "\n"

    cad += "header:\n"
    for item, value in request.headers.items():
        cad +="{}:{}\n".format(item, value)

    cad+="informacion en formularios (POST):\n"
    for item, value in request.form.items():
        cad +="{}:{}\n".format(item, value)

    cad += "informacion en URL (GET): \n"
    for item, value in request.args.items():
        cad +="{}:{}\n".format(item, value)

    cad += "Ficheros:\n"
    for item, value in request.files.items():
        cad +="{}:{}\n".format(item, value)

    return cad

@app.route('/')
def inicio():
    temp5='Hola '
    print(Template(temp5).render(nombre="   pepe  "))	

    temp6="los datos son {{ lista|join(', ') }}"
    print(Template(temp6).render(lista=["amarillo","verde","rojo"]))	

    temp6="El ultimo elemento tiene  caracteres"
    print(Template(temp6).render(lista=["amarillo","verde","rojo"]))

    temp7='''
    <ul>
    {% for elem in elems -%}
    <li>{{loop.index}} - {{ elem }}</li>
    {% endfor -%}
    </ul>
    '''
    print(Template(temp7).render(elems=["amarillo","verde","rojo"]))
    temp9='''
    {% if elems %}
    <ul>
    {% for elem in elems -%}
        {% if elem is divisibleby 2 -%}
            <li>{{elem}} es divisible por 2.</li>
        {% else -%}
            <li>{{elem}} no es divisible por 2.</li>
        {% endif -%}
    {% endfor -%}
    </ul>
    {% endif %}
    '''
    print(Template(temp9).render(elems=[1,2,3,4]))
    return '<img src="'+url_for('static', filename='img/tux.png')+'"/>'

@app.route('/articulos/')
def articulos():
    return 'Listado de Articulos'

@app.route("/articulos/<int:id>")
def mostrar_ariculo(id):
	return 'Vamos a mostrar el artículo con id:{}'.format(id)

@app.route('/articulos/new',methods=["POST"])
def articulos_new():
	return 'Está URL recibe información de un formulario con el método POST'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return 'Hemos accedido con POST'
    else:
        return 'Hemos accedido con GET'

@app.route('/sumar', methods=['GET', 'POST'])
def sumar():
     if request.method == 'POST':
        num1 = int(request.form.get('num1', 0))
        num2 = int(request.form.get('num2', 0))
        return 'La suma es: {}'.format(num1 + num2)
     else:
        return '''
            <form method="post">
                Num1: <input type="text" name="num1"><br>
                Num2: <input type="text" name="num2"><br>
                <input type="submit" value="Sumar">
            </form>
        '''        
@app.route('/acercade')
def acercade():
    return 'Pagina de Acerca de Nosotros'

@app.route('/string/')
def string():
    return 'Hello world!'

@app.route('/object/')
def return_object():
    headers = {'Content-Type': 'text/plain'}
    return make_response('Hello World!', 200, headers)
    
@app.route('/tuple/')
def return_tuple():
    return 'Hello World!', 200, {'Content-Type': 'text/plain'}

@app.route('/error')
def error():
    abort(401)

#@app.errorhandler(404)
#def page_not_found(error):
#    return 'Página no encontrada...', 404

@app.route('/redirect')
def index():
    return redirect(url_for('acercade'))

@app.route('/hola/')
@app.route('/hola/<nombre>')
def saluda(nombre = None):
    return render_template("tample1.html", nombre=nombre)

@app.route('/suma/<num1>/<num2>')
def suma(num1, num2):
    try:
        resultado = int(num1) + int(num2)
    except:
        abort(404)

    return render_template("template2.html",num1=num1, num2=num2, resultado=resultado)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error=error), 404

@app.route('/tabla/<numero>')
def tabla(numero):
    try:
        numero = int(numero)
    except:
        abort(404)
    return render_template("template3.html", num=numero)

@app.route('/enlaces')
def enlaces():
	enlaces=[{"url":"http://www.google.es","texto":"Google"},
			{"url":"http://www.twitter.com","texto":"Twitter"},
			{"url":"http://www.facbook.com","texto":"Facebook"},
			]
	return render_template("template4.html",enlaces=enlaces)















if __name__ == '__main__':
    app.run('0.0.0.0',8080, debug=True)