from flask import render_template, request
from flask import current_app as app

@app.route('/')
def home():
    return render_template('homepage.html')

#logic for user registration
@app.route('/signup', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        email=request.form.get('email')
        password = request.form.get('password')









    return render_template()