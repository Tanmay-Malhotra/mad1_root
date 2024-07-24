from flask import render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from applications.database import db
from applications.models import Influencer,Sponsor,Campaign
from sqlalchemy import desc


@app.route('/')
def home():
    return render_template('login.html')

# homepage for login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Try to find the user in the Sponsor model
        user = Sponsor.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('sp_home'))
              # Redirect to sponsor homepage
        
        # Try to find the user in the Influencer model
        user = Influencer.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('in_home'))  # Redirect to influencer homepage
        
        # If no matching user found or password incorrect
        flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')







@app.route('/inf_reg', methods=['GET', 'POST'])
def inf_reg():
    if request.method == 'POST':
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            #checking if email is taken or not
            existing_user = Influencer.query.filter_by(username=username).first()
            existing_email = Influencer.query.filter_by(email=email).first()
            if existing_user:
                flash('Username is already is in use, Please choose a different one.', 'danger')
                return redirect(url_for('inf_reg'))
            if existing_email:
                flash('Email is already in use by a diffrent user', 'danger')
                return redirect(url_for('inf_reg'))


            #creating the new user with hashed password 
            new_user = Influencer(username=username, name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))

    return render_template('inf_reg.html')


























#--------------------------------SPONSOR------------------------------------------------

@app.route('/sp_reg', methods=['GET', 'POST'])
def sp_reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        industry = request.form['industry']
        
        # Check if the email or username already exists
        existing_sponsor = Sponsor.query.filter((Sponsor.email == email) | (Sponsor.username == username)).first()
        if existing_sponsor:
            flash('Username or Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('sp_reg'))
        
        # Create new sponsor and add to the database
        new_sponsor = Sponsor(username=username, password=password, email=email, industry=industry)
        db.session.add(new_sponsor)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('sp_home'))
    return render_template('sp_reg.html')

#------------------------------sponsor dashboard---------------------------------------------------------

def get_current_sponsor():
    sponsor_id = session.get('user_id')
    #print(f"Current sponsor ID in session: {sponsor_id}")
    if sponsor_id:
        return Sponsor.query.get(sponsor_id)
    return None

@app.route('/sp_home')
def sp_home():

    sponsor = get_current_sponsor()
    if sponsor:
        return render_template('sp_home.html', sponsor=sponsor)
    return redirect(url_for('login'))

    #sponsor = get_current_sponsor()
    #if sponsor:
    #return render_template('sp_home.html', sponsor=sponsor)
    #return redirect(url_for('login'))
    #return render_template('sp_home.html')
    #return render_template('dashboard.html', active_campaigns=active_campaigns, new_requests=new_requests)


@app.route('/sp_profile')
def sp_profile():
    return render_template('sp_home.html')  # Redirect to dashboard for this example

@app.route('/sp_campaigns')
def sp_campaigns():
    return render_template('create_camp.html')

@app.route('/sp_find')
def sp_find():
    return render_template('sp_find.html')

@app.route('/sp_statistics')
def sp_statistics():
    return render_template('sp_statistics.html')

@app.route('/sp_logout')
def sp_logout():
    return redirect(url_for('login'))


@app.route('/create_camp', methods=['GET', 'POST'])
def create_camp():
    if request.method == 'POST':
        name = request.form['name']
        status = request.form['status']
        budget = request.form['budget']  # Budget should be an integer (whole number)
        user_id = session.get('user_id')
        
        if not user_id:
            flash('You need to log in first.', 'warning')
            return redirect(url_for('login'))
        
        # Fetch the sponsor by ID
        sponsor = Sponsor.query.get(user_id)
        if not sponsor:
            flash('Sponsor not found.', 'danger')
            return redirect(url_for('login'))

        # Create new campaign
        new_campaign = Campaign(name=name, status=status, budget=budget, sponsor_id=sponsor.id)
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('sp_home'))

    return render_template('create_camp.html')

