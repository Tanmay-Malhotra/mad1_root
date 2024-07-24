from applications.database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    industry = db.Column(db.String(100))

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)  
    budget = db.Column(db.Integer, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True))

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  
    email = db.Column(db.String(100), unique=True, nullable=False)
    platform = db.Column(db.String(100))  


