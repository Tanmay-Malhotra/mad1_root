from applications.database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    industry = db.Column(db.String(100))
    #making changes from here 
    campaigns = db.relationship('campaign', backref='sponsor', lazy=True)

class campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False,default="active")
    category = db.Column(db.String(50), nullable=False)  
    budget = db.Column(db.Integer, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    
    ad_requests = db.relationship('adrequest', backref='campaign', lazy=True)

class influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    platform = db.Column(db.String(100))  
    followers = db.Column(db.Integer, nullable=False)
    ad_requests = db.relationship('adrequest', backref='influencer', lazy=True)

class adrequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    requirements = db.Column(db.String(500), nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Request Sent')




#class admanagement(db.Model):
    #id = db.Column(db.Integer, primary_key=True)


