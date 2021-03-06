# -*- coding: iso-8859-15 -*-

from flask import Flask, request, render_template, session, redirect, url_for
import os.path
from os import listdir
import json
from time import time
import sys
import datetime
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')
    #return render_template("index.html")

@app.route('/home', methods=['GET'])
def home():
    return app.send_static_file('home.html')
    #return render_template("home.html")

@app.route('/login', methods=['GET'])
def login():
    return app.send_static_file('login.html')
    #return render_template("login.html")


@app.route('/signup', methods=['GET'])
def signup():
    return app.send_static_file('signup.html')
    #return render_template("signup.html")

@app.route('/cuenta', methods=['GET'])
def cuenta():
    if not 'email' in session:
        return app.send_static_file('login.html')
    else:
        return render_template('micuenta.html', user_name = session['user_name'], email = session['email'], )

@app.route('/processLogin', methods=['GET', 'POST'])
def processLogin():
       missing = []
       fields = ['email', 'passwd', 'login_submit']
       for field in fields:
              value = request.form.get(field, None)
              if value is None:
                  missing.append(field)
       if missing:
             return process_missingFields(missing, "/login")
       else:
            return load_user(request.form['email'], request.form['passwd'])


@app.route('/processSignup', methods=['GET', 'POST'])
def processSignup():
       missing = []
       fields = ['nickname', 'email', 'passwd','confirm', 'signup_submit']
       for field in fields:
              value = request.form.get(field, None)
              if value is None:
                     missing.append(field)
       if missing:
              return process_missingFields(missing, "/signup")
       else:
           return create_user_file(request.form['nickname'], request.form['email'], request.form['passwd'],request.form['confirm'])


@app.route('/processHome', methods=['GET', 'POST'])
def processHome():
	missing = []
	fields = ['message', 'last', 'post_submit']
	for field in fields:
		value = request.form.get(field, None)
		if value is None:
			missing.append(field)
	if missing:
		return process_missingFields(missing, "/home")

	return guardarMensajes(request.form['message'])

@app.route('/processMicuenta', methods=['GET', 'POST'])
def processMicuenta():
    if request.form.get('passwd_submit'):
        email = session['email']
        if email == "":
            return process_error('Error: Primero debes acceder a tu cuenta.', url_for("signup")) 
        else:
            return render_template('newPasswd.html')
    if request.form.get('logout_submit'):
        session['user_name'] = ""
        session['messages'] = ""
        session['password'] = ""
        session['email'] = ""
        session['friends'] = ""
        return render_template('index.html')



@app.route('/processChangepasswd', methods=['GET', 'POST'])
def processChangepasswd():
    missing = []
    fields = ['oldPasswd', 'newPasswd', 'confirmNewpasswd']
    for field in fields:
        value = request.form.get(field, None)
        if value is None:
            missing.append(field)
        if missing:
            return process_missingFields(missing, render_template('micuenta.html'))
    return newPassword(session['password'])
     
#este m??todo define el comportamiento del formulario de cambio de contrase??a
def newPassword(sessionPasswd):
    if sessionPasswd != request.form['oldPasswd']:
        return process_error("Error: tu actual contrase??a es incorrecta.", url_for('cuenta'))
    elif request.form['newPasswd'] != request.form['confirmNewpasswd']:
        return process_error("Se ha producido un error al confirmar la nueva contrase??a", url_for('cuenta'))
    else:
        session['password'] = request.form['newPasswd']
        save_current_user()
        return render_template('home.html')

# este codigo controla los errores de campos ausentes
def process_missingFields(campos, next_page):
    """
    :param campos: Lista de Campos que faltan
    :param next_page: ruta al pulsar bot??n continuar
    :return: plantilla generada
    """
    return render_template("missingFields.html", inputs=campos, next=next_page)

def load_user(email, passwd):
    """
    Carga datos usuario (identified by email) del directorio data.
    Busca un archivo de nombre el email del usuario
    :param email: user id
    :param passwd: password 
    :return: pagina home si existe el usuario y es correcto el pass
    """
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(SITE_ROOT, "data/", email)
   
    if not os.path.isfile(file_path):
        return process_error("User not found / No existe un usuario con ese nombre", url_for("login"))
    with open(file_path, 'r') as f:
        data = json.load(f)
    if data['password'] != passwd:
        return process_error("Incorrect password / la clave no es correcta", url_for("login"))
    session['user_name'] = data['user_name']
    session['messages'] = data['messages']
    session['password'] = passwd
    session['email'] = email
    session['friends'] = data['friends']
    return redirect(url_for("home"))

def save_current_user():
    datos = {
        "user_name": session["user_name"],
        "password": session['password'],
        "messages": session['messages'], # lista de tuplas (time_stamp, mensaje)
        "email": session['email'],
        "friends": session['friends']
    }
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(SITE_ROOT, "data/", session['email'])
    with open(file_path, 'w') as f:
        json.dump(datos, f)

def guardarMensajes(mensaje):
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(SITE_ROOT, "data/", session['email'])
    with open(file_path, 'r') as f:
        data = json.load(f)
    fechaHora = datetime.datetime.now()
    fechaHora = fechaHora.strftime("%m/%d/%Y, %H:%M:%S")
    paqMensaje = []
    paqMensaje.append(fechaHora)
    paqMensaje.append(mensaje)
    session['messages'] = data['messages']
    session['messages'].append(paqMensaje)
    save_current_user()
    return render_template("home.html", last = request.form['last'], message = request.form['message'])


def create_user_file(name, email, passwd, passwd_confirmation):
    """
    Crea el fichero (en directorio /data). El nombre ser?? el email.
    Si el fichero ya existe, error.
    Si no coincide el pass con la confirmaci??n, error.
    :param name: Nombre o apodo del usuario
    :param email: correo
    :param passwd: password 
    :param passwd_confirmation: debe coincidir con pass
    :return: Si no hay errores, direcci??n al usuario a home.
    """
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    directory = os.path.join(SITE_ROOT, "data")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(SITE_ROOT, "data/", email)
    if os.path.isfile(file_path):
       return process_error("The email is already used, you must select a different email / Ya existe un usuario con ese nombre", url_for("signup"))
    if passwd != passwd_confirmation:
       return process_error("Your password and confirmation password do not match / Las claves no coinciden", url_for("signup"))
    datos = {
        "user_name": name,
        "password": passwd,
        "messages": [],
        "friends": []
    }
    with open(file_path, 'w') as f:
        json.dump(datos, f)
    session['user_name'] = name
    session['password'] = passwd
    session['messages'] = []
    session['friends'] = []
    session['email'] = email
    save_current_user()
    return redirect(url_for("home"))

def process_error(message, next_page):
    """
    M??todo que carga pagina de error
    :param message: mensaje de error para el usuario
    :param next_page: p??gina siguiente
    :return: template error.html
    """
    return render_template("error.html", error_message=message, next=next_page)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, port=55555)