from flask import render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from applications.database import db
from applications.models import User
from sqlalchemy import desc


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/inf_reg', methods=['GET', 'POST'])
def inf_reg():
    if request.method == 'POST':
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            #checking if email is taken or not
            existing_user = User.query.filter_by(username=username).first()
            existing_email = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Username is already is in use, Please choose a different one.', 'danger')
                return redirect(url_for('signup'))
            if existing_email:
                flash('Email is already in use by a diffrent user', 'danger')
                return redirect(url_for('signup'))


            #creating the new user with hashed password 
            new_user = User(username=username, name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('Your account has been created!', 'success')
            return redirect(url_for('signup'))

    return render_template('inf_reg.html')

@app.route('/sp_reg', methods=['GET', 'POST'])
def sp_reg():
    if request.method == 'POST':
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            #checking if email is taken or not
            existing_user = User.query.filter_by(username=username).first()
            existing_email = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Username is already is in use, Please choose a different one.', 'danger')
                return redirect(url_for('signup'))
            if existing_email:
                flash('Email is already in use by a diffrent user', 'danger')
                return redirect(url_for('signup'))


            #creating the new user with hashed password 
            new_user = User(username=username, name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('Your account has been created!', 'success')
            return redirect(url_for('signup'))

    return render_template('sp_reg.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Assuming User is a model in your database
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            flash('login ho gaya', 'success')
            return render_template('dash.html')
            
        else:
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('home'))

    return render_template('login.html')
