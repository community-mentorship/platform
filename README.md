# Mentorship Platform

A comprehensive mentorship program management platform built for Lenny's Slack community. This web application enables members to apply as mentors/mentees, view match results, track session progress, with full administrative capabilities for managing applications and monitoring program health.

## Features

### Core Functionality
- **User Authentication**: Simple session-based login system
- **Role Management**: Support for Mentors, Mentees, and Both roles
- **Admin Dashboard**: Complete "Backstage" administrative interface
- **Dynamic Form Builder**: Create custom application forms with rich formatting

### Enhanced Form Builder (Cycle 5)
- **Rich Text Formatting**: Bold, italic, and hyperlink support in form labels
- **Advanced Validation**: Character limits, email validation, URL validation
- **Multiple Field Types**: Text, textarea, email, URL, dropdown, radio buttons, checkboxes
- **Live Preview**: Real-time form preview with formatted labels
- **Selection Limits**: Configurable maximum selections for checkbox fields
- **Validation Hints**: User-friendly character count and format guidance

### User Management
- **Profile Management**: Edit user details, roles, and admin status
- **Change Tracking**: Complete audit log of user modifications
- **Mentor-Mentee Matching**: Track active mentorship relationships
- **Scoped Access Control**: Granular permissions for different user types

### Content Management
- **Static Pages**: Create and manage informational pages
- **Markdown Support**: Rich content formatting with HTML rendering
- **Access Control**: Page-level permissions based on user roles and relationships

## Technology Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL with full migration support
- **Frontend**: Server-side rendered templates with Bootstrap 5
- **Styling**: Replit-themed dark mode Bootstrap CSS
- **Forms**: WTForms with enhanced validation
- **Testing**: Comprehensive end-to-end test suite

## Project Structure

```
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── models.py           # Database models and relationships
├── routes.py           # URL routing and view logic
├── forms.py            # Form definitions and validation
├── templates/          # Jinja2 templates
│   ├── admin/         # Administrative interface templates
│   └── *.html         # User-facing templates
├── static/            # CSS, JavaScript, and assets
├── test_*.py          # Comprehensive test suites
└── demo_*.py          # Demonstration scripts
```

## Development Approach

This project follows a **cycle-based development methodology** with 6-hour weekly cycles:

- **Cycle 1**: Flask foundation and basic authentication
- **Cycle 2**: Admin dashboard and user management
- **Cycle 3**: Role-based permissions and access control
- **Cycle 4**: Complete form system with submissions
- **Cycle 5**: Enhanced form builder with rich formatting ✅

Each cycle delivers a complete, tested, and deployable feature set.

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/community-mentorship/mentorship-platform.git
cd mentorship-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export DATABASE_URL="postgresql://user:password@localhost/mentorship"
export SESSION_SECRET="your-secret-key-here"
```

4. Initialize the database:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

5. Run the application:
```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

### Creating Demo Content

Run the demo script to create sample forms:
```bash
python demo_enhanced_form.py
```

### Running Tests

Execute the comprehensive test suite:
```bash
python test_form_features.py
python test_form_builder_e2e.py
```

## Usage

### For Administrators
1. Access the admin dashboard at `/admin`
2. Create and manage application forms with the enhanced form builder
3. View and edit user profiles and roles
4. Monitor form submissions and program activity

### For Users
1. Complete the registration process
2. Fill out application forms
3. View mentorship matches and relationships
4. Access role-specific content and resources

## Key Features in Detail

### Enhanced Form Builder
The form builder supports sophisticated form creation with:
- **Rich labels**: `**Bold text**`, `*italic text*`, `[links](URL)`
- **Validation rules**: Character limits, format checking
- **Field types**: Text, email, URL, textarea, select, radio, checkbox
- **User guidance**: Placeholder text, validation hints, character counters

### Access Control System
Granular permission system supporting:
- All users, mentors only, mentees only, admins only
- Matched pairs, specific mentor-mentee relationships
- Self-only access for personal content

### Audit Trail
Complete change tracking for:
- User profile modifications
- Role changes
- Administrative actions
- Form submissions and updates

## Contributing

This project is part of Lenny's Slack community mentorship program. Contributions should align with the community guidelines and project roadmap.

## License

This project is proprietary software developed for Lenny's Slack community mentorship program.

## Support

For technical issues or feature requests, please contact the development team through the community Slack workspace.