#!/usr/bin/env python3
"""
Demo Script for Enhanced Form Builder (Cycle 5)

Creates a comprehensive demonstration form showcasing all enhanced features:
- Rich text formatting in labels
- Character limits and validation
- Multiple field types
- Advanced validation rules
"""

import sys
import json
from app import app, db
from models import User, Form, ViewerScope, UserRole


def create_demo_form():
    """Create a comprehensive demo form showcasing all enhanced features"""
    
    with app.app_context():
        # Ensure admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@mentorship.com',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                role=UserRole.BOTH
            )
            db.session.add(admin)
            db.session.commit()
        
        # Check if demo form already exists
        existing_form = Form.query.filter_by(slug='enhanced-demo').first()
        if existing_form:
            print("Demo form already exists. Deleting and recreating...")
            db.session.delete(existing_form)
            db.session.commit()
        
        # Enhanced form fields showcasing all features
        demo_fields = [
            {
                'id': 'field_1',
                'type': 'text',
                'label': '**Full Name** *(required)*\nPlease enter your complete legal name',
                'name': 'full_name',
                'placeholder': 'John Doe',
                'required': True,
                'min_length': 3,
                'max_length': 50
            },
            {
                'id': 'field_2',
                'type': 'email',
                'label': '**Email Address**\nWe\'ll use this for program communications',
                'name': 'email',
                'placeholder': 'your.email@example.com',
                'required': True
            },
            {
                'id': 'field_3',
                'type': 'textarea',
                'label': '**Professional Background**\nDescribe your experience and expertise\n*Read our [privacy policy](https://example.com/privacy) for data handling info*',
                'name': 'background',
                'placeholder': 'Tell us about your professional journey, key skills, and what you bring to the mentorship program...',
                'required': True,
                'min_length': 100,
                'max_length': 800
            },
            {
                'id': 'field_4',
                'type': 'select',
                'label': '**Primary Role Interest**\nWhat role are you most interested in?',
                'name': 'primary_role',
                'required': True,
                'options': [
                    'Mentor - I want to guide others',
                    'Mentee - I want to learn and grow',
                    'Both - I want to mentor and be mentored'
                ]
            },
            {
                'id': 'field_5',
                'type': 'radio',
                'label': '**Experience Level**\nSelect your overall professional experience',
                'name': 'experience_level',
                'required': True,
                'options': [
                    'Entry Level (0-2 years)',
                    'Mid Level (3-7 years)',
                    'Senior Level (8-15 years)',
                    'Executive Level (15+ years)'
                ]
            },
            {
                'id': 'field_6',
                'type': 'checkbox',
                'label': '**Areas of Expertise** *(select up to 4)*\nWhat areas can you contribute to or want to learn about?',
                'name': 'expertise_areas',
                'required': False,
                'max_selections': 4,
                'options': [
                    'Software Engineering',
                    'Product Management',
                    'Data Science & Analytics',
                    'UX/UI Design',
                    'Digital Marketing',
                    'Business Strategy',
                    'Leadership & Management',
                    'Entrepreneurship',
                    'Sales & Business Development',
                    'Finance & Operations'
                ]
            },
            {
                'id': 'field_7',
                'type': 'url',
                'label': '**LinkedIn Profile** *(optional)*\nShare your LinkedIn profile for better matching',
                'name': 'linkedin_url',
                'placeholder': 'https://linkedin.com/in/yourprofile',
                'required': False
            },
            {
                'id': 'field_8',
                'type': 'text',
                'label': '**Company/Organization**\nWhere do you currently work?',
                'name': 'company',
                'placeholder': 'Your current employer',
                'required': False,
                'max_length': 100
            },
            {
                'id': 'field_9',
                'type': 'textarea',
                'label': '**Goals & Expectations**\nWhat do you hope to achieve through this mentorship program?\n*Be specific about your objectives*',
                'name': 'goals',
                'placeholder': 'Describe your learning goals, what you hope to contribute, and what success looks like for you...',
                'required': True,
                'min_length': 50,
                'max_length': 400
            },
            {
                'id': 'field_10',
                'type': 'select',
                'label': '**Time Commitment**\nHow much time can you dedicate monthly?',
                'name': 'time_commitment',
                'required': True,
                'options': [
                    '2-4 hours per month',
                    '4-6 hours per month',
                    '6-8 hours per month',
                    '8+ hours per month'
                ]
            },
            {
                'id': 'field_11',
                'type': 'checkbox',
                'label': '**Preferred Communication** *(select all that apply)*\nHow do you prefer to connect with your mentor/mentee?',
                'name': 'communication_preferences',
                'required': True,
                'max_selections': 5,
                'options': [
                    'Video calls (Zoom, Meet)',
                    'Phone calls',
                    'Slack messaging',
                    'Email exchanges',
                    'In-person meetings (if local)',
                    'Group mentorship sessions'
                ]
            }
        ]
        
        # Create the enhanced demo form
        demo_form = Form(
            title='Enhanced Mentorship Program Application',
            slug='enhanced-demo',
            fields=demo_fields,
            viewer_scope=ViewerScope.ALL_USERS,
            is_active=True,
            created_by_id=admin.id
        )
        
        db.session.add(demo_form)
        db.session.commit()
        
        print("✅ Enhanced demo form created successfully!")
        print(f"📋 Form Title: {demo_form.title}")
        print(f"🔗 URL Slug: {demo_form.slug}")
        print(f"📝 Total Fields: {len(demo_form.fields)}")
        print("\n🎯 Featured Enhancements:")
        print("   • Rich text formatting in labels (bold, italic, links)")
        print("   • Character length validation (min/max limits)")
        print("   • Multiple field types (text, email, textarea, select, radio, checkbox, url)")
        print("   • Advanced validation rules")
        print("   • Selection limits for checkbox fields")
        print("   • Placeholder text and help information")
        print("   • Required/optional field configurations")
        
        print(f"\n🌐 Access the form at: /form/{demo_form.slug}")
        print(f"⚙️  Edit in admin at: /admin/forms/{demo_form.id}/edit")
        
        return demo_form


def print_form_structure(form):
    """Print detailed form structure for verification"""
    print("\n" + "="*60)
    print("FORM STRUCTURE ANALYSIS")
    print("="*60)
    
    for i, field in enumerate(form.fields, 1):
        print(f"\nField {i}: {field['name']}")
        print(f"  Type: {field['type']}")
        print(f"  Label: {repr(field['label'])}")
        print(f"  Required: {field.get('required', False)}")
        
        if field.get('min_length'):
            print(f"  Min Length: {field['min_length']}")
        if field.get('max_length'):
            print(f"  Max Length: {field['max_length']}")
        if field.get('options'):
            print(f"  Options: {field['options']}")
        if field.get('max_selections'):
            print(f"  Max Selections: {field['max_selections']}")
        if field.get('placeholder'):
            print(f"  Placeholder: {field['placeholder']}")


if __name__ == '__main__':
    print("Creating Enhanced Form Builder Demo...")
    print("="*50)
    
    try:
        demo_form = create_demo_form()
        print_form_structure(demo_form)
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("The enhanced form builder demo is ready!")
        print("Visit the admin interface to see the live preview and editing features.")
        
    except Exception as e:
        print(f"❌ Error creating demo form: {e}")
        import traceback
        traceback.print_exc()