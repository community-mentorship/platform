#!/usr/bin/env python3
"""
End-to-End Test for Enhanced Form Builder (Cycle 5)

This test validates the complete form builder workflow including:
- Rich text formatting in labels
- Character limits and validation
- Live preview functionality  
- Form submission with enhanced validation
- Admin form management features
"""

import unittest
import json
import re
from app import app, db
from models import User, Form, Submission, UserRole, ViewerScope
from routes import process_form_label


class FormBuilderE2ETest(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create admin user
            self.admin_user = User(
                username='admin_test',
                email='admin@test.com',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                role=UserRole.BOTH
            )
            db.session.add(self.admin_user)
            
            # Create regular user
            self.regular_user = User(
                username='user_test',
                email='user@test.com',
                first_name='Test',
                last_name='User',
                is_admin=False,
                role=UserRole.MENTEE
            )
            db.session.add(self.regular_user)
            db.session.commit()
    
    def tearDown(self):
        """Clean up test environment"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login_admin(self):
        """Helper to login as admin"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.admin_user.id
            sess['username'] = self.admin_user.username
            sess['first_name'] = self.admin_user.first_name
            sess['is_admin'] = True
    
    def login_user(self):
        """Helper to login as regular user"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.regular_user.id
            sess['username'] = self.regular_user.username
            sess['first_name'] = self.regular_user.first_name
            sess['is_admin'] = False
    
    def test_rich_text_label_processing(self):
        """Test rich text formatting in form labels"""
        test_cases = [
            ("**Bold text**", "<strong>Bold text</strong>"),
            ("*Italic text*", "<em>Italic text</em>"),
            ("[Link text](https://example.com)", '<a href="https://example.com" target="_blank" rel="noopener">Link text</a>'),
            ("**Bold** and *italic* text", "<strong>Bold</strong> and <em>italic</em> text"),
            ("Visit [our website](https://test.com) for more info", 'Visit <a href="https://test.com" target="_blank" rel="noopener">our website</a> for more info'),
            ("Line 1\nLine 2", "Line 1<br>Line 2")
        ]
        
        for input_text, expected_output in test_cases:
            with self.subTest(input_text=input_text):
                result = process_form_label(input_text)
                self.assertEqual(result, expected_output)
    
    def test_create_enhanced_form(self):
        """Test creating a form with enhanced features through admin interface"""
        self.login_admin()
        
        # Advanced form configuration with rich formatting and validation
        form_fields = [
            {
                'id': 'field_1',
                'type': 'text',
                'label': '**Full Name** (Required)',
                'name': 'full_name',
                'placeholder': 'Enter your full name',
                'required': True,
                'min_length': 2,
                'max_length': 50
            },
            {
                'id': 'field_2',
                'type': 'email',
                'label': '*Email Address*',
                'name': 'email',
                'placeholder': 'your.email@example.com',
                'required': True
            },
            {
                'id': 'field_3',
                'type': 'textarea',
                'label': 'Tell us about your experience\nVisit [our guide](https://help.example.com) for tips',
                'name': 'experience',
                'placeholder': 'Describe your background...',
                'required': True,
                'min_length': 50,
                'max_length': 500
            },
            {
                'id': 'field_4',
                'type': 'select',
                'label': '**Preferred Role**',
                'name': 'preferred_role',
                'required': True,
                'options': ['Mentor', 'Mentee', 'Both']
            },
            {
                'id': 'field_5',
                'type': 'checkbox',
                'label': 'Areas of Interest',
                'name': 'interests',
                'required': False,
                'max_selections': 3,
                'options': ['Technology', 'Business', 'Design', 'Marketing', 'Product']
            },
            {
                'id': 'field_6',
                'type': 'url',
                'label': 'LinkedIn Profile (Optional)',
                'name': 'linkedin_url',
                'placeholder': 'https://linkedin.com/in/yourprofile',
                'required': False
            }
        ]
        
        # Create form via POST request
        response = self.client.post('/admin/forms/new', data={
            'title': 'Enhanced Mentorship Application',
            'slug': 'enhanced-application',
            'viewer_scope': ViewerScope.ALL_USERS.value,
            'is_active': True,
            'fields_json': json.dumps(form_fields)
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Verify form was created with correct fields
        with app.app_context():
            form = Form.query.filter_by(slug='enhanced-application').first()
            self.assertIsNotNone(form)
            self.assertEqual(form.title, 'Enhanced Mentorship Application')
            self.assertEqual(len(form.fields), 6)
            
            # Check specific field configurations
            name_field = form.fields[0]
            self.assertEqual(name_field['min_length'], 2)
            self.assertEqual(name_field['max_length'], 50)
            
            experience_field = form.fields[2]
            self.assertEqual(experience_field['min_length'], 50)
            self.assertEqual(experience_field['max_length'], 500)
            
            checkbox_field = form.fields[4]
            self.assertEqual(checkbox_field['max_selections'], 3)
    
    def test_form_preview_functionality(self):
        """Test form preview modal functionality"""
        self.login_admin()
        
        # Create a test form first
        with app.app_context():
            test_form = Form(
                title='Test Preview Form',
                slug='test-preview',
                fields=[
                    {
                        'type': 'text',
                        'label': '**Name**',
                        'name': 'name',
                        'required': True,
                        'min_length': 2,
                        'max_length': 30
                    }
                ],
                viewer_scope=ViewerScope.ALL_USERS,
                is_active=True,
                created_by_id=self.admin_user.id
            )
            db.session.add(test_form)
            db.session.commit()
            
            # Test forms list page (contains preview functionality)
            response = self.client.get('/admin/forms')
            self.assertEqual(response.status_code, 200)
            
            # Check that preview button and modal are present
            self.assertIn('Preview', response.data.decode())
            self.assertIn('previewModal', response.data.decode())
            self.assertIn('showFormPreview', response.data.decode())
    
    def test_form_submission_with_validation(self):
        """Test form submission with enhanced validation"""
        self.login_user()
        
        with app.app_context():
            # Create form with validation rules
            test_form = Form(
                title='Validation Test Form',
                slug='validation-test',
                fields=[
                    {
                        'type': 'text',
                        'label': 'Short Name',
                        'name': 'short_name',
                        'required': True,
                        'min_length': 5,
                        'max_length': 10
                    },
                    {
                        'type': 'textarea',
                        'label': 'Description',
                        'name': 'description',
                        'required': True,
                        'min_length': 20,
                        'max_length': 100
                    },
                    {
                        'type': 'email',
                        'label': 'Email',
                        'name': 'email',
                        'required': True
                    },
                    {
                        'type': 'url',
                        'label': 'Website',
                        'name': 'website',
                        'required': False
                    },
                    {
                        'type': 'checkbox',
                        'label': 'Skills',
                        'name': 'skills',
                        'max_selections': 2,
                        'options': ['Python', 'JavaScript', 'Design', 'Marketing']
                    }
                ],
                viewer_scope=ViewerScope.ALL_USERS,
                is_active=True,
                created_by_id=self.admin_user.id
            )
            db.session.add(test_form)
            db.session.commit()
            
            # Test 1: Valid submission
            response = self.client.post('/form/validation-test/submit', data={
                'short_name': 'TestName',  # 8 chars, within 5-10 limit
                'description': 'This is a valid description that meets the minimum length requirement.',  # > 20 chars
                'email': 'test@example.com',
                'website': 'https://example.com',
                'skills': ['Python', 'JavaScript']  # 2 selections, within limit
            })
            self.assertEqual(response.status_code, 302)  # Redirect to success page
            
            # Verify submission was saved
            submission = Submission.query.filter_by(
                user_id=self.regular_user.id,
                form_id=test_form.id
            ).first()
            self.assertIsNotNone(submission)
            
            # Test 2: Invalid submission - name too short
            # Create new user for another submission
            new_user = User(
                username='user2',
                email='user2@test.com',
                first_name='User2',
                last_name='Test',
                role=UserRole.MENTEE
            )
            db.session.add(new_user)
            db.session.commit()
            
            with self.client.session_transaction() as sess:
                sess['user_id'] = new_user.id
                sess['username'] = new_user.username
                sess['first_name'] = new_user.first_name
                sess['is_admin'] = False
            
            response = self.client.post('/form/validation-test/submit', data={
                'short_name': 'Hi',  # Too short (< 5 chars)
                'description': 'Valid description that is long enough to pass validation.',
                'email': 'test@example.com',
                'website': 'https://example.com'
            })
            self.assertEqual(response.status_code, 200)  # Returns to form with error
            self.assertIn('Must be at least 5 characters', response.data.decode())
            
            # Test 3: Invalid email format
            response = self.client.post('/form/validation-test/submit', data={
                'short_name': 'ValidName',
                'description': 'Valid description that is long enough to pass validation.',
                'email': 'invalid-email',  # Invalid email format
                'website': 'https://example.com'
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn('valid email address', response.data.decode())
            
            # Test 4: Invalid URL format
            response = self.client.post('/form/validation-test/submit', data={
                'short_name': 'ValidName',
                'description': 'Valid description that is long enough to pass validation.',
                'email': 'test@example.com',
                'website': 'not-a-url'  # Invalid URL format
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn('valid URL', response.data.decode())
    
    def test_form_rendering_with_formatting(self):
        """Test that forms render with proper formatting and validation hints"""
        self.login_user()
        
        with app.app_context():
            # Create form with rich formatting
            test_form = Form(
                title='Formatting Test Form',
                slug='formatting-test',
                fields=[
                    {
                        'type': 'text',
                        'label': '**Full Name** - Please enter your *complete* name',
                        'name': 'full_name',
                        'required': True,
                        'min_length': 3,
                        'max_length': 50,
                        'placeholder': 'John Doe'
                    },
                    {
                        'type': 'textarea',
                        'label': 'About You\nRead our [privacy policy](https://example.com/privacy)',
                        'name': 'about',
                        'required': True,
                        'min_length': 10,
                        'max_length': 200
                    }
                ],
                viewer_scope=ViewerScope.ALL_USERS,
                is_active=True,
                created_by_id=self.admin_user.id
            )
            db.session.add(test_form)
            db.session.commit()
            
            # Get form rendering
            response = self.client.get('/form/formatting-test')
            self.assertEqual(response.status_code, 200)
            content = response.data.decode()
            
            # Check that rich text formatting is rendered
            self.assertIn('<strong>Full Name</strong>', content)
            self.assertIn('<em>complete</em>', content)
            self.assertIn('<br>', content)  # Line break
            self.assertIn('<a href="https://example.com/privacy"', content)  # Link
            
            # Check that validation hints are shown
            self.assertIn('3-50 characters', content)
            self.assertIn('10-200 characters', content)
            
            # Check that HTML attributes for validation are present
            self.assertIn('minlength="3"', content)
            self.assertIn('maxlength="50"', content)
            self.assertIn('minlength="10"', content)
            self.assertIn('maxlength="200"', content)
    
    def test_admin_form_edit_with_existing_formatting(self):
        """Test editing forms preserves rich formatting and validation"""
        self.login_admin()
        
        with app.app_context():
            # Create form with rich content
            original_form = Form(
                title='Original Form',
                slug='original-form',
                fields=[
                    {
                        'type': 'text',
                        'label': '**Original Label** with *formatting*',
                        'name': 'original_field',
                        'required': True,
                        'min_length': 5,
                        'max_length': 25
                    }
                ],
                viewer_scope=ViewerScope.ALL_USERS,
                is_active=True,
                created_by_id=self.admin_user.id
            )
            db.session.add(original_form)
            db.session.commit()
            
            # Test form edit page loads with existing data
            response = self.client.get(f'/admin/forms/{original_form.id}/edit')
            self.assertEqual(response.status_code, 200)
            content = response.data.decode()
            
            # Check that form builder loads existing formatting
            self.assertIn('Original Label', content)
            self.assertIn('form-builder', content)
            self.assertIn('updateField', content)
            
            # Test updating the form
            updated_fields = [
                {
                    'type': 'text',
                    'label': '**Updated Label** with [link](https://example.com)',
                    'name': 'updated_field',
                    'required': True,
                    'min_length': 3,
                    'max_length': 30
                }
            ]
            
            response = self.client.post(f'/admin/forms/{original_form.id}/edit', data={
                'title': 'Updated Form Title',
                'slug': 'updated-form',
                'viewer_scope': ViewerScope.ALL_USERS.value,
                'is_active': True,
                'fields_json': json.dumps(updated_fields)
            })
            
            self.assertEqual(response.status_code, 302)  # Redirect after update
            
            # Verify form was updated
            updated_form = Form.query.get(original_form.id)
            self.assertEqual(updated_form.title, 'Updated Form Title')
            self.assertEqual(updated_form.slug, 'updated-form')
            self.assertEqual(updated_form.fields[0]['label'], '**Updated Label** with [link](https://example.com)')
            self.assertEqual(updated_form.fields[0]['min_length'], 3)
            self.assertEqual(updated_form.fields[0]['max_length'], 30)
    
    def test_complete_workflow(self):
        """Test complete end-to-end workflow from form creation to submission"""
        # Step 1: Admin creates enhanced form
        self.login_admin()
        
        workflow_fields = [
            {
                'type': 'text',
                'label': '**Project Name** - Choose a *memorable* name',
                'name': 'project_name',
                'required': True,
                'min_length': 5,
                'max_length': 30,
                'placeholder': 'My Awesome Project'
            },
            {
                'type': 'textarea',
                'label': 'Project Description\nSee our [guidelines](https://example.com/guide)',
                'name': 'description',
                'required': True,
                'min_length': 50,
                'max_length': 300
            },
            {
                'type': 'select',
                'label': '**Category**',
                'name': 'category',
                'required': True,
                'options': ['Web Development', 'Mobile App', 'Data Science', 'Design']
            },
            {
                'type': 'checkbox',
                'label': 'Technologies Used',
                'name': 'technologies',
                'max_selections': 3,
                'options': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Docker']
            }
        ]
        
        # Create form
        response = self.client.post('/admin/forms/new', data={
            'title': 'Project Submission Form',
            'slug': 'project-submission',
            'viewer_scope': ViewerScope.ALL_USERS.value,
            'is_active': True,
            'fields_json': json.dumps(workflow_fields)
        })
        self.assertEqual(response.status_code, 302)
        
        # Step 2: Verify form appears in admin list
        response = self.client.get('/admin/forms')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Project Submission Form', response.data.decode())
        
        # Step 3: User submits form with valid data
        self.login_user()
        
        response = self.client.post('/form/project-submission/submit', data={
            'project_name': 'Amazing Web App',
            'description': 'This is a comprehensive web application that provides users with an intuitive interface for managing their projects and collaborating with team members.',
            'category': 'Web Development',
            'technologies': ['JavaScript', 'React', 'Node.js']
        })
        self.assertEqual(response.status_code, 302)
        
        # Step 4: Verify submission was saved correctly
        with app.app_context():
            form = Form.query.filter_by(slug='project-submission').first()
            submission = Submission.query.filter_by(
                user_id=self.regular_user.id,
                form_id=form.id
            ).first()
            
            self.assertIsNotNone(submission)
            responses = submission.responses
            self.assertEqual(responses['project_name'], 'Amazing Web App')
            self.assertEqual(responses['category'], 'Web Development')
            self.assertEqual(len(responses['technologies']), 3)
            self.assertIn('JavaScript', responses['technologies'])
        
        # Step 5: User tries to submit again (should be prevented)
        response = self.client.get('/form/project-submission')
        self.assertEqual(response.status_code, 200)
        # Should show "already submitted" page
        self.assertIn('submitted', response.data.decode().lower())


def run_tests():
    """Run the end-to-end test suite"""
    print("Running Enhanced Form Builder End-to-End Tests...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(FormBuilderE2ETest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nTest Result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == '__main__':
    run_tests()