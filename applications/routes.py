from flask import render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from datetime import date
from applications.database import db
from applications.models import influencer,sponsor,campaign
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
        user = sponsor.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('sp_home'))
              # Redirect to sponsor homepage
        
        # Try to find the user in the Influencer model
        user = influencer.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('inf_home'))  # Redirect to influencer homepage
        
        # If no matching user found or password incorrect
        flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')



#-----------------------------------------------INFLUENCER--------------------------------------------------------------



@app.route('/inf_reg', methods=['GET', 'POST'])
def inf_reg():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        industry = request.form.get('industry')  # Ensure this is captured
        email = request.form.get('email')
        platform = request.form.get('platform')
        followers = request.form.get('followers')

        #checking if email is taken or not
        existing_user_influencer = influencer.query.filter_by(username=username).first()
        existing_user_sponsor = sponsor.query.filter_by(username=username).first()

        # Check for existing email in both tables
        existing_email_influencer = influencer.query.filter_by(email=email).first()
        existing_email_sponsor = sponsor.query.filter_by(email=email).first()
        if existing_user_influencer or existing_user_sponsor:
            flash('Username is already is in use, Please choose a different one.', 'danger')
            return redirect(url_for('inf_reg'))
        if existing_email_sponsor or existing_email_influencer:
            flash('Email is already in use by a diffrent user', 'danger')
            return redirect(url_for('inf_reg'))


        #creating the new user with hashed password 
        new_user = influencer(username=username, name=name, email=email, password=password, industry=industry, platform=platform, followers = followers)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('inf_reg.html')




def get_current_influencer():
    influencer_id = session.get('user_id')
    #print(f"Current sponsor ID in session: {sponsor_id}")
    if influencer_id:
        return influencer.query.get(influencer_id)
    return None

@app.route('/inf_home')
def inf_home():

    inf = get_current_influencer()
    if inf:
        return render_template('inf_home.html', influencer=inf)
    return redirect(url_for('login'))

@app.route('/inf_find', methods=['GET'])
def inf_find():
    selected_industry = request.args.get('industry', None)
    
    # If an industry is selected, filter campaigns by that industry
    if selected_industry:
        campaigns = campaign.query.join(sponsor).filter(sponsor.industry == selected_industry).order_by(
            db.case(
                (sponsor.industry == selected_industry, 0),  # Selected industry at the top
                (sponsor.industry != selected_industry, 1),  # Others follow
                else_=2
            )
        ).all()
    else:
        campaigns = campaign.query.all()  # Get all campaigns if no industry is selected

    return render_template('inf_find.html', campaigns=campaigns, selected_industry=selected_industry)


























#--------------------------------SPONSOR------------------------------------------------

@app.route('/sp_reg', methods=['GET', 'POST'])
def sp_reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        industry = request.form['industry']
        
        # Check if the email or username already exists
        existing_sponsor = sponsor.query.filter((sponsor.email == email) | (sponsor.username == username)).first()
        if existing_sponsor:
            flash('Username or Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('sp_reg'))
        
        # Create new sponsor and add to the database
        new_sponsor = sponsor(username=username, password=password, email=email, industry=industry)
        db.session.add(new_sponsor)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('sp_reg.html')

#------------------------------sponsor dashboard---------------------------------------------------------

def get_current_sponsor():
    sponsor_id = session.get('user_id')
    #print(f"Current sponsor ID in session: {sponsor_id}")
    if sponsor_id:
        return sponsor.query.get(sponsor_id)
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

""" @app.route('/sp_campaigns')
def sp_campaigns():
    sponsor_id = session.get('user_id')
    if not sponsor_id:
        return redirect(url_for('login'))

    sponsor = Sponsor.query.get(sponsor_id)
    if sponsor is None:
        return redirect(url_for('login'))

    campaigns = sponsor.campaigns  # This accesses the campaigns associated with the sponsor
    return render_template('campaigns.html', campaigns=campaigns) """
    



@app.route('/sp_statistics')
def sp_statistics():
    return render_template('sp_statistics.html')

@app.route('/sp_logout')
def sp_logout():
    return redirect(url_for('login'))


@app.route('/campaigns')
def campaigns():
    sponsor_id = session.get('user_id')
    if not sponsor_id:
        return redirect(url_for('login'))

    spnsr = sponsor.query.get(sponsor_id)
    if sponsor is None:
        return redirect(url_for('login'))

    campaigns = spnsr.campaigns  # This accesses the campaigns associated with the sponsor
    return render_template('campaigns.html', campaigns=campaigns)

""" def campaigns():
    sponsor_id = session.get('user_id')
    if not sponsor_id:
        return redirect(url_for('login'))

    sponsor = Sponsor.query.get(sponsor_id)  # Fetch the Sponsor, not Campaign
    if sponsor is None:
        return redirect(url_for('login'))

    campaigns = sponsor.campaigns  # Access the sponsor's campaigns via the relationship
    return render_template('campaigns.html', campaigns=campaigns) """

""" def campaigns():
    sponsor_id = session.get('user_id')
    if not sponsor_id:
        return redirect(url_for('login'))

    sponsor = Campaign.query.get(sponsor_id)
    campaigns = sponsor.campaigns  # Access the sponsor's campaigns via the relationship

    return render_template('campaigns.html', campaigns=campaigns) """


@app.route('/create_camp', methods=['GET', 'POST'])
def create_camp():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        budget = int(request.form['budget'])  # Budget should be an integer (whole number)
        start_date = request.form.get('start_date')  # Get the start date from the form
        end_date = request.form.get('end_date')  # Get the end date from the form
        user_id = session.get('user_id')

        if not user_id:
            flash('You need to log in first.', 'warning')
            return redirect(url_for('login'))

        # Fetch the sponsor by ID
        spnsr = sponsor.query.get(user_id)
        if not spnsr:
            flash('Sponsor not found.', 'danger')
            return redirect(url_for('login'))

        # Convert the start_date and end_date to date objects if provided
        start_date = date.fromisoformat(start_date) if start_date else None
        end_date = date.fromisoformat(end_date) if end_date else None

        # Create new campaign
        new_campaign = campaign(
            name=name,
            category=category,
            budget=budget,
            sponsor_id=spnsr.id,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaigns'))

    return render_template('create_camp.html')

@app.route('/campaign_mgmt/<int:campaign_id>')
def campaign_mgmt(campaign_id):
    cmp = campaign.query.get_or_404(campaign_id)
    return render_template('campaign_mgmt.html', campaign=cmp)

@app.route('/update_campaign/<int:campaign_id>', methods=['POST'])
def update_campaign(campaign_id):
    cmp = campaign.query.get_or_404(campaign_id)
    
    # Update campaign details from form data
    cmp.name = request.form['name']
    cmp.status = request.form['status']
    cmp.category = request.form['category']
    cmp.budget = int(request.form['budget'])
    cmp.start_date = date.fromisoformat(request.form['start_date']) if request.form['start_date'] else None
    cmp.end_date = date.fromisoformat(request.form['end_date']) if request.form['end_date'] else None

    db.session.commit()
    flash('Campaign updated successfully!', 'success')
    return redirect(url_for('campaigns'))

#### Delete Campaign Route

@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    cmp = campaign.query.get_or_404(campaign_id)
    db.session.delete(cmp)
    db.session.commit()
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('campaigns'))



@app.route('/sp_find', methods=['GET'])
def sp_find():
    selected_industry = request.args.get('industry', None)
    if selected_industry:
        influencers = influencer.query.order_by(
            db.case(
                (influencer.industry == selected_industry, 0),  # Selected industry at the top
                (influencer.industry != selected_industry, 1),  # Others follow
                else_=2
            ),
        ).all()
    else:
        influencers = influencer.query.all()
    return render_template('sp_find.html', influencers=influencers, selected_industry=selected_industry)


""" @app.route('/create_camp', methods=['GET', 'POST'])
def create_camp():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        budget = request.form['budget']  # Budget should be an integer (whole number)
        user_id = session.get('user_id')
        
        if not user_id:
            flash('You need to log in first.', 'warning')
            return redirect(url_for('login'))
        
        # Fetch the sponsor by ID
        spnsr = sponsor.query.get(user_id)
        if not spnsr:
            flash('Sponsor not found.', 'danger')
            return redirect(url_for('login'))

        # Create new campaign
        new_campaign = campaign(name=name, category=category, budget=budget, sponsor_id=spnsr.id)
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaigns'))

    return render_template('create_camp.html')
 """
