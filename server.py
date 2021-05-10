# -*- coding: iso-8859-15 -*-

from flask import render_template
from flask import Flask, request
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/home', methods=['GET'])
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")



@app.route('/signup', methods=['GET'])
def signup():
    return render_template("signup.html")


@app.route('/processLogin', methods=['GET', 'POST'])
def processLogin():
       missing = []
       fields = ['email', 'passwd', 'login_submit']
       for field in fields:
              value = request.form.get(field, None)
              if value is None:
                  missing.append(field)
       if missing:
              return "Warning: Some fields are missing"


       return render_template("login.html")


@app.route('/processSignup', methods=['GET', 'POST'])
def processSignup():
       missing = []
       fields = ['nickname', 'email', 'passwd','confirm', 'signup_submit']
       for field in fields:
              value = request.form.get(field, None)
              if value is None:
                     missing.append(field)
       if missing:
              return "Warning: Some fields are missing"

       return render_template("signup.html")


@app.route('/processHome', methods=['GET', 'POST'])
def processHome():
	missing = []
	fields = ['message', 'last', 'post_submit']
	for field in fields:
		value = request.form.get(field, None)
		if value is None:
			missing.append(field)
	if missing:
		return "Warning: Some fields are missing"

	return render_template("home.html")



#app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, port=55555)