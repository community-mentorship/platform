from app import db
from datetime import datetime
import enum

class ViewerScope(enum.Enum):
    ALL_USERS = "all_users"
    MENTORS_ONLY = "mentors_only"
    MENTEES_ONLY = "mentees_only"
    ADMINS_ONLY = "admins_only"
    MATCHED_PAIR = "matched_pair"
    MENTOR_OF = "mentor_of"
    MENTEE_OF = "mentee_of"
    SELF_ONLY = "self_only"

class UserRole(enum.Enum):
    MENTOR = "mentor"
    MENTEE = "mentee"
    BOTH = "both"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.MENTEE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    mentor_matches = db.relationship('Match', foreign_keys='Match.mentor_id', backref='mentor', lazy='dynamic')
    mentee_matches = db.relationship('Match', foreign_keys='Match.mentee_id', backref='mentee', lazy='dynamic')
    change_logs = db.relationship('UserChangeLog', foreign_keys='UserChangeLog.user_id', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def name(self):
        """Alias for full_name to match requirements"""
        return self.full_name
    
    def can_view_page(self, page):
        """Check if user can view a specific page based on viewer scope"""
        if page.viewer_scope == ViewerScope.ALL_USERS:
            return True
        elif page.viewer_scope == ViewerScope.ADMINS_ONLY:
            return self.is_admin
        elif page.viewer_scope == ViewerScope.MENTORS_ONLY:
            return self.role in [UserRole.MENTOR, UserRole.BOTH]
        elif page.viewer_scope == ViewerScope.MENTEES_ONLY:
            return self.role in [UserRole.MENTEE, UserRole.BOTH]
        elif page.viewer_scope == ViewerScope.SELF_ONLY:
            # For user-specific content - requires additional context
            return False
        elif page.viewer_scope in [ViewerScope.MATCHED_PAIR, ViewerScope.MENTOR_OF, ViewerScope.MENTEE_OF]:
            # These require match context - will be handled at route level
            return False
        return False
    
    def get_active_matches_as_mentor(self):
        """Get active matches where this user is the mentor"""
        return self.mentor_matches.all()
    
    def get_active_matches_as_mentee(self):
        """Get active matches where this user is the mentee"""
        return self.mentee_matches.all()
    
    def is_matched_with(self, other_user):
        """Check if this user is matched with another user"""
        return Match.query.filter(
            ((Match.mentor_id == self.id) & (Match.mentee_id == other_user.id)) |
            ((Match.mentor_id == other_user.id) & (Match.mentee_id == self.id))
        ).first() is not None

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    viewer_scope = db.Column(db.Enum(ViewerScope), default=ViewerScope.ALL_USERS, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    created_by = db.relationship('User', backref=db.backref('pages', lazy=True))
    
    def __repr__(self):
        return f'<Page {self.title}>'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    matched_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<Match mentor:{self.mentor_id} mentee:{self.mentee_id}>'

class UserChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    field_changed = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    updated_by_user = db.relationship('User', foreign_keys=[updated_by], backref='changes_made')
    
    def __repr__(self):
        return f'<UserChangeLog {self.field_changed} for user:{self.user_id}>'


class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    fields = db.Column(db.JSON, nullable=False)  # Store form field definitions as JSON
    viewer_scope = db.Column(db.Enum(ViewerScope), default=ViewerScope.ALL_USERS, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    created_by = db.relationship('User', backref=db.backref('forms', lazy=True))
    submissions = db.relationship('Submission', backref='form', lazy='dynamic')
    
    def __repr__(self):
        return f'<Form {self.title}>'


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)
    responses = db.Column(db.JSON, nullable=False)  # Store user responses as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref=db.backref('submissions', lazy=True))
    
    # Ensure one submission per user per form
    __table_args__ = (db.UniqueConstraint('user_id', 'form_id', name='_user_form_uc'),)
    
    def __repr__(self):
        return f'<Submission {self.user.username} -> {self.form.title}>'
