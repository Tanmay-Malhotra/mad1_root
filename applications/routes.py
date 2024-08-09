from flask import render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from datetime import date
from applications.database import db
from applications.models import influencer,sponsor,campaign,adrequest
from sqlalchemy import desc

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check for admin login
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_home'))

        # Try to find the user in the Sponsor model
        user = sponsor.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('sp_home'))  # Redirect to sponsor homepage
        
        # Try to find the user in the Influencer model
        user = influencer.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('inf_home'))  # Redirect to influencer homepage
        
        # If no matching user found or password incorrect
        flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/admin_home')
def admin_home():
    if not session.get('admin_logged_in'):
        flash('You need to be logged in as admin to access this page.', 'danger')
        return redirect(url_for('login'))
    total_users = sponsor.query.count() + influencer.query.count()
    number_of_sponsors = sponsor.query.count()
    number_of_influencers = influencer.query.count()
    number_of_campaigns = campaign.query.count()
    active_ad_requests = adrequest.query.filter_by(status='Request Accepted').count()
    
    return render_template('admin_home.html', total_users=total_users, 
                           number_of_sponsors=number_of_sponsors,
                           number_of_influencers=number_of_influencers,
                           number_of_campaigns=number_of_campaigns,
                           active_ad_requests=active_ad_requests)
    

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
    
@app.route('/admin/find/sponsors')
def admin_sponsors():
    sponsors = sponsor.query.all()  # Fetch all sponsors
    return render_template('admin_sponsors.html', sponsors=sponsors)



@app.route('/admin/sponsor/flag/<int:sponsor_id>', methods=['POST'])
def flag_sponsor(sponsor_id):
    sponsor_to_flag = sponsor.query.get_or_404(sponsor_id)
    sponsor_to_flag.flagged = 'yes' if sponsor_to_flag.flagged == 'no' else 'no'
    db.session.commit()
    flash('Sponsor has been flagged.', 'success')
    return redirect(url_for('admin_sponsors'))


@app.route('/admin/sponsor/delete/<int:sponsor_id>', methods=['POST'])
def delete_sponsor(sponsor_id):
    sponsor_to_delete = sponsor.query.get_or_404(sponsor_id)
    
    # Delete associated ad requests
    ad_requests = adrequest.query.join(campaign).filter(campaign.sponsor_id == sponsor_id).all()
    for ad_request in ad_requests:
        db.session.delete(ad_request)
    
    # Delete associated campaigns
    campaigns = campaign.query.filter_by(sponsor_id=sponsor_id).all()
    for campaign_to_delete in campaigns:
        db.session.delete(campaign_to_delete)
    
    # Delete the sponsor
    db.session.delete(sponsor_to_delete)
    db.session.commit()
    
    flash('Sponsor and all associated data have been deleted.', 'success')
    return redirect(url_for('admin_sponsors'))


@app.route('/admin/campaigns')
def admin_campaigns():
    # Retrieve all campaigns
    all_campaigns = campaign.query.all()
    return render_template('admin_campaigns.html', campaigns=all_campaigns)


@app.route('/admin/campaign/flag/<int:campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    campaign_to_flag = campaign.query.get_or_404(campaign_id)
    campaign_to_flag.flagged = 'yes' if campaign_to_flag.flagged == 'no' else 'no'
    db.session.commit()
    flash('Campaign has been flagged.', 'success')
    return redirect(url_for('admin_campaigns'))

@app.route('/admin/campaign/delete/<int:campaign_id>', methods=['POST'])
def admin_delete_campaign(campaign_id):
    campaign_to_delete = campaign.query.get_or_404(campaign_id)
    
    # Delete associated ad requests
    ad_requests = adrequest.query.filter_by(campaign_id=campaign_id).all()
    for ad_request in ad_requests:
        db.session.delete(ad_request)
    
    # Delete the campaign
    db.session.delete(campaign_to_delete)
    db.session.commit()
    
    flash('Campaign and all associated data have been deleted.', 'success')
    return redirect(url_for('admin_campaigns'))


@app.route('/admin/influencers', methods=['GET'])
def admin_influencers():
    influencers = influencer.query.all()
    return render_template('admin_influencers.html', influencers=influencers)

@app.route('/admin/influencers/flag/<int:influencer_id>', methods=['POST'])
def flag_influencer(influencer_id):
    influencer_to_flag = influencer.query.get_or_404(influencer_id)
    influencer_to_flag.flagged = 'yes' if influencer_to_flag.flagged == 'no' else 'no'
    db.session.commit()
    flash('Influencer has been flagged.', 'success')
    return redirect(url_for('admin_influencers'))

@app.route('/admin/influencers/delete/<int:influencer_id>', methods=['POST'])
def delete_influencer(influencer_id):
    influencer_to_delete = influencer.query.get_or_404(influencer_id)
    
    # First, delete all associated ad requests
    adrequests = adrequest.query.filter_by(influencer_id=influencer_to_delete.id).all()
    for adrequest_to_delete in adrequests:
        db.session.delete(adrequest_to_delete)

    # Then, delete the influencer
    db.session.delete(influencer_to_delete)
    db.session.commit()
    
    flash('Influencer and their associated ad requests have been deleted.', 'success')
    return redirect(url_for('admin_influencers'))









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
    search_query = request.args.get('search', None)

    query = campaign.query.join(sponsor)


    # Filter by search query if provided
    if search_query:
        search_filter = (campaign.name.ilike(f'%{search_query}%') | 
                         sponsor.username.ilike(f'%{search_query}%') |
                         campaign.budget.like(f'%{search_query}%')
                         )
        query = query.filter(search_filter)

    campaigns = query.all()

    return render_template('inf_find.html', campaigns=campaigns, selected_industry=selected_industry, search_query=search_query)


@app.route('/ad_management')
def ad_management():
    influencer_id = session.get('user_id')
    if not influencer_id:
        return redirect(url_for('login'))

    inf = influencer.query.get(influencer_id)
    if inf is None:
        return redirect(url_for('login'))

    ad_requests = adrequest.query.filter_by(influencer_id=influencer_id).all()

    new_negotiations = [req for req in ad_requests if req.status == 'Request Negotiated']
    pending_requests = [req for req in ad_requests if req.status == 'Request Sent']
    active_requests = [req for req in ad_requests if req.status == 'Request Accepted']
    rejected_requests = [req for req in ad_requests if req.status == 'Request Rejected']

    return render_template('ad_management.html', influencer=inf, new_negotiations=new_negotiations, pending_requests=pending_requests, active_requests=active_requests, rejected_requests=rejected_requests)


@app.route('/ad_request/<int:ad_request_id>/accept', methods=['POST'])
def accept_ad_request(ad_request_id):
    ad_request = adrequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Request Accepted'
    db.session.commit()
    flash('Ad request accepted.', 'success')
    return redirect(url_for('ad_management'))


@app.route('/ad_request/<int:ad_request_id>/reject', methods=['POST'])
def reject_ad_request(ad_request_id):
    ad_request = adrequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Request Rejected'
    db.session.commit()
    flash('Ad request rejected.', 'success')
    return redirect(url_for('ad_management'))


@app.route('/inf_request_ad/<int:campaign_id>', methods=['GET', 'POST'])
def inf_request_ad(campaign_id):
    inf = influencer.query.get(session['user_id'])
    cmp = campaign.query.get_or_404(campaign_id)
    
    if request.method == 'POST':
        requirements = request.form['requirements']
        payment_amount = float(request.form['payment_amount'])
        
        new_ad_request = adrequest(
            campaign_id=campaign_id,
            influencer_id=inf.id,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Request Sent'
        )
        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad request sent successfully!', 'success')
        return redirect(url_for('ad_management'))
    
    return render_template('inf_request_ad.html', campaign=cmp)




@app.route('/influencer/<int:influencer_id>/negotiate_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def negotiate_ad_request(influencer_id, ad_request_id):
    inf = influencer.query.get_or_404(influencer_id)
    ad_req = adrequest.query.get_or_404(ad_request_id)

    if request.method == 'POST':
        new_requirements = request.form.get('new_requirements')
        new_payment_amount = request.form.get('new_payment_amount')

        # Update the ad request with new details and change status to 'Request Negotiated'
        ad_req.requirements = new_requirements
        ad_req.payment_amount = new_payment_amount
        ad_req.status = 'Request Negotiated'
        db.session.commit()
        flash('Ad request updated and sent for negotiation', 'success')
        return redirect(url_for('ad_management', influencer_id=influencer_id))

    return render_template('negotiate_ad_request.html', influencer=inf, ad_request=ad_req)






















#--------------------------------SPONSOR------------------------------------------------

""" @app.route('/sp_reg', methods=['GET', 'POST'])
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
    return render_template('sp_reg.html') """

@app.route('/sp_reg', methods=['GET', 'POST'])
def sp_reg():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        industry = request.form.get('industry')

        # Check if username or email already exists
        existing_user_influencer = influencer.query.filter_by(username=username).first()
        existing_user_sponsor = sponsor.query.filter_by(username=username).first()
        existing_email_influencer = influencer.query.filter_by(email=email).first()
        existing_email_sponsor = sponsor.query.filter_by(email=email).first()

        if existing_user_influencer or existing_user_sponsor:
            flash('Username is already in use, please choose a different one.', 'danger')
            return redirect(url_for('sp_reg'))
        if existing_email_influencer or existing_email_sponsor:
            flash('Email is already in use by a different user.', 'danger')
            return redirect(url_for('sp_reg'))

        # Create new sponsor
        new_sponsor = sponsor(name=name, username=username, password=password, email=email, industry=industry)
        db.session.add(new_sponsor)
        db.session.commit()
        flash('Your account has been created!', 'success')
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

    
@app.route('/sp_profile')
def sp_profile():
    return render_template('sp_home.html')  # Redirect to dashboard for this example



@app.route('/ad_request/<int:influencer_id>', methods=['GET', 'POST'])
def ad_request(influencer_id):
    inf = influencer.query.get_or_404(influencer_id)
    current_sponsor = get_current_sponsor()
    if not current_sponsor:
        flash('You need to be logged in to send an ad request.', 'danger')
        return redirect(url_for('login'))  # Assuming you have a login route

    campaigns = campaign.query.filter_by(sponsor_id=current_sponsor.id).all()  # Fetch only campaigns created by the current sponsor

    if not campaigns:
        flash('You need to create a campaign before sending an ad request.', 'warning')
        return redirect(url_for('create_camp'))  # Assuming you have a route to create a campaign

    if request.method == 'POST':
        campaign_id = request.form['campaign_id']
        requirements = request.form['requirements']
        payment_amount = float(request.form['payment_amount'])

        new_ad_request = adrequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Request Sent'
        )
        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad request sent successfully!', 'success')
        return redirect(url_for('sp_find'))

    return render_template('ad_request.html', influencer=inf, campaigns=campaigns)







@app.route('/campaign/<int:campaign_id>/ad_requests', methods=['GET'])
def view_ad_request(campaign_id):
    cmp = campaign.query.get_or_404(campaign_id)
    ad_requests = adrequest.query.filter_by(campaign_id=campaign_id).all()

    new_negotiations = [req for req in ad_requests if req.status == 'Request Negotiated']
    pending_requests = [req for req in ad_requests if req.status == 'Request Sent']
    active_requests = [req for req in ad_requests if req.status == 'Request Accepted']
    rejected_requests = [req for req in ad_requests if req.status == 'Request Rejected']

    return render_template('view_ad_request.html', campaign=cmp, new_negotiations=new_negotiations, pending_requests=pending_requests, active_requests=active_requests, rejected_requests=rejected_requests)

@app.route('/ad_request/<int:ad_request_id>/edit', methods=['GET', 'POST'])
def edit_ad_request(ad_request_id):
    ad_req = adrequest.query.get_or_404(ad_request_id)
    if request.method == 'POST':
        ad_req.requirements = request.form['requirements']
        ad_req.payment_amount = request.form['payment_amount']
        db.session.commit()
        flash('Ad request updated successfully!', 'success')
        return redirect(url_for('view_ad_request', campaign_id=ad_req.campaign_id))

    return render_template('edit_ad_request.html', ad_request=ad_req)

@app.route('/ad_request/<int:ad_request_id>/delete', methods=['POST'])
def delete_ad_request(ad_request_id):
    ad_req = adrequest.query.get_or_404(ad_request_id)
    campaign_id = ad_req.campaign_id
    db.session.delete(ad_req)
    db.session.commit()
    flash('Ad request deleted successfully!', 'success')
    return redirect(url_for('view_ad_request', campaign_id=campaign_id))



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
    
    # Find all related adrequests and delete them
    related_adrequests = adrequest.query.filter_by(campaign_id=campaign_id).all()
    for adreq in related_adrequests:
        db.session.delete(adreq)
    
    db.session.delete(cmp)
    db.session.commit()
    
    flash('Campaign and related ad requests deleted successfully!', 'success')
    return redirect(url_for('campaigns'))




@app.route('/sp_find', methods=['GET'])
def sp_find():
    selected_industry = request.args.get('industry', None)
    search_query = request.args.get('search', None)

    query = influencer.query


    # Filter by search query if provided
    if search_query:
        search_filter = (influencer.name.ilike(f'%{search_query}%') | 
                         influencer.username.ilike(f'%{search_query}%') | 
                         influencer.email.ilike(f'%{search_query}%'))
        query = query.filter(search_filter)

    # Execute query to fetch all influencers
    influencers = query.all()

    return render_template('sp_find.html', influencers=influencers, selected_industry=selected_industry, search_query=search_query)







@app.route('/accept_negotiation/<int:ad_request_id>', methods=['POST'])
def accept_negotiation(ad_request_id):
    ad_request = adrequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Request Accepted'
    db.session.commit()
    flash('Negotiated request accepted!', 'success')
    return redirect(url_for('view_ad_request', campaign_id=ad_request.campaign_id))

@app.route('/reject_negotiation/<int:ad_request_id>', methods=['POST'])
def reject_negotiation(ad_request_id):
    ad_request = adrequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Request Rejected'
    db.session.commit()
    flash('Negotiated request rejected!', 'danger')
    return redirect(url_for('view_ad_request', campaign_id=ad_request.campaign_id))