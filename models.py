from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Token(db.Model):
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)
    token_type = db.Column(db.String)
    scope = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    expires_at = db.Column(db.DateTime)
    refresh_token = db.Column(db.String)
    
    def is_expired(self):
        """Check if the token is expired"""
        if not self.expires_at:
            return True
        return datetime.datetime.now() > self.expires_at
    
    @classmethod
    def get_valid_token(cls, username):
        """Get a valid token for a user"""
        token = cls.query.filter_by(username=username).order_by(cls.created_at.desc()).first()
        if token and not token.is_expired():
            return token
        return None