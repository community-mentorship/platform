from app import db
from datetime import datetime
import enum

class ViewerScope(enum.Enum):
    ALL = "all"
    MENTOR = "mentor"
    MENTEE = "mentee"
    ADMIN = "admin"
    PERSONAL = "personal"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # user, mentor, mentee, both
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def can_view_page(self, page):
        """Check if user can view a specific page based on viewer scope"""
        if page.viewer_scope == ViewerScope.ALL:
            return True
        elif page.viewer_scope == ViewerScope.ADMIN:
            return self.is_admin
        elif page.viewer_scope == ViewerScope.MENTOR:
            return self.role in ['mentor', 'both']
        elif page.viewer_scope == ViewerScope.MENTEE:
            return self.role in ['mentee', 'both']
        elif page.viewer_scope == ViewerScope.PERSONAL:
            # For future use with user-specific pages
            return False
        return False

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    viewer_scope = db.Column(db.Enum(ViewerScope), default=ViewerScope.ALL, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    created_by = db.relationship('User', backref=db.backref('pages', lazy=True))
    
    def __repr__(self):
        return f'<Page {self.title}>'
