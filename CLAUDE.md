# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask-based mentorship platform with sophisticated form building, role-based access control, and dynamic content management. Uses modular architecture with SQLAlchemy ORM and session-based authentication.

## Common Development Commands

```bash
# Install dependencies (uses uv package manager)
cd platform && uv pip install -e .

# Run development server
cd platform && python main.py

# Run tests
cd platform && python test_form_builder_e2e.py
cd platform && python test_form_features.py

# Create demo content
cd platform && python demo_enhanced_form.py

# Production deployment
cd platform && gunicorn --bind 0.0.0.0:5000 --reload main:app
```

## Architecture Overview

**Core Components:**
- `app.py` - Flask factory with automatic database initialization
- `models.py` - SQLAlchemy models with enum-based role/scope system
- `routes.py` - Route handlers with decorator-based authorization
- `forms.py` - WTForms with custom validation logic
- `main.py` - Application entry point

**Key Architectural Patterns:**
- **Auto-Database Setup**: Tables created automatically on first run via `db.create_all()` in app.py:34
- **Role-Based Authorization**: Uses `@admin_required` and `@login_required` decorators with `ViewerScope` enum for fine-grained access control
- **Dynamic Content System**: Pages and forms use JSON fields for flexible content structure
- **Audit Logging**: All admin user changes tracked in `UserChangeLog` model
- **Session Context Injection**: `inject_user()` function makes current user available to all templates

## Database Architecture

**No formal migration system** - uses `db.create_all()` for schema management. Tables are automatically created on app startup.

**Key Model Relationships:**
- `User` → `Match` (mentor/mentee relationships via foreign keys)
- `User` → `Page`/`Form` (content ownership via created_by_id)
- `Form` → `Submission` (one-to-many with unique constraint per user)
- `User` → `UserChangeLog` (audit trail for admin changes)

**ViewerScope System**: Critical enum controlling access to pages/forms:
- `ALL_USERS`, `MENTORS_ONLY`, `MENTEES_ONLY`, `ADMINS_ONLY`
- `MATCHED_PAIR`, `MENTOR_OF`, `MENTEE_OF`, `SELF_ONLY`

## Form Builder System

Advanced dynamic form creation with:
- **JSON Field Storage**: Form structure stored as JSON in `Form.fields`
- **Rich Text Processing**: Custom markdown-to-HTML conversion in forms.py
- **Live Preview**: JavaScript-based form builder with real-time updates
- **Validation Engine**: Custom validators for length, format, and selection limits

**Form Field Types**: text, textarea, email, url, number, date, select, radio, checkbox, rich_text

## Authentication & Authorization

**Demo-Style Login**: Users created automatically on first login attempt (no password validation)
- Login flow: `routes.py:login()` → auto-creates user if not exists
- Session management: Flask sessions with `session['user_id']`
- Context injection: `inject_user()` decorator provides user to all templates

**Authorization Decorators**:
- `@login_required` - Basic authentication check
- `@admin_required` - Admin role verification
- Page-level access via `user.can_view_page(page)` method

## Template System

**Bootstrap-based responsive design** with dark theme:
- `base.html` - Master template with Feather icons and global navigation
- `admin/` - Admin interface templates with form builders and user management
- Dynamic content rendering via Jinja2 with markdown processing

## Testing Approach

**Two-tier testing strategy**:
- `test_form_features.py` - Unit tests for form validation, rich text processing
- `test_form_builder_e2e.py` - Full workflow tests (create form → submit → verify)

**Test Coverage**: Form builder functionality, user workflows, admin operations, rich text formatting

## Environment Configuration

**Required Environment Variables**:
- `DATABASE_URL` - PostgreSQL connection string (defaults to SQLite for dev)
- `SESSION_SECRET` - Flask session encryption key

**Development vs Production**:
- Dev: SQLite database in `instance/mentorship.db`
- Prod: PostgreSQL with connection pooling and health checks configured