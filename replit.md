# Mentorship Platform

## Overview

A comprehensive mentorship program management platform built for Lenny's Slack community. This Flask-based web application enables members to apply as mentors/mentees, view match results, track session progress, and manage administrative tasks through a "Backstage" interface.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL (configured but can use SQLite for development)
- **Session Management**: Flask's built-in session-based authentication
- **Forms**: WTForms with enhanced validation and CSRF protection
- **Templates**: Jinja2 with server-side rendering

### Frontend Architecture
- **Styling**: Bootstrap 5 with Replit-themed dark mode
- **Icons**: Feather Icons
- **JavaScript**: Minimal client-side JavaScript, primarily server-side rendered
- **Responsive Design**: Mobile-first Bootstrap grid system

### Database Schema
- **Users**: Core user management with roles (Mentor, Mentee, Both)
- **Matches**: Mentor-mentee relationship tracking
- **Pages**: Static content management with markdown support
- **Forms**: Dynamic form builder with rich field types
- **Submissions**: Form response storage
- **UserChangeLog**: Audit trail for user modifications

## Key Components

### Authentication & Authorization
- **Login System**: Simple username/email-based authentication that creates users on-the-fly
- **Role-Based Access**: UserRole enum (MENTOR, MENTEE, BOTH)
- **Admin System**: Boolean flag for administrative privileges
- **Scoped Access Control**: ViewerScope enum for granular content permissions

### Form Builder (Enhanced)
- **Rich Text Formatting**: Bold, italic, and hyperlink support in form labels
- **Multiple Field Types**: Text, textarea, email, URL, dropdown, radio buttons, checkboxes
- **Advanced Validation**: Character limits, email validation, URL validation
- **Live Preview**: Real-time form preview with formatted labels
- **Selection Limits**: Configurable maximum selections for checkbox fields

### Content Management
- **Static Pages**: Markdown-supported page creation with HTML rendering
- **Access Control**: Page-level permissions based on user roles and relationships
- **Admin Interface**: Complete "Backstage" administrative dashboard

### User Management
- **Profile Management**: Edit user details, roles, and admin status
- **Change Tracking**: Complete audit log via UserChangeLog model
- **Mentor-Mentee Matching**: Track active mentorship relationships through Match model

## Data Flow

1. **User Registration/Login**: Users authenticate via simple form, creating accounts automatically
2. **Role Assignment**: Admins can modify user roles and permissions through admin interface
3. **Form Creation**: Admins create dynamic forms with rich formatting and validation
4. **Form Submission**: Users complete forms with client-side and server-side validation
5. **Content Access**: Scoped access control determines content visibility based on roles and relationships
6. **Change Tracking**: All administrative changes are logged for audit purposes

## External Dependencies

### Python Packages
- `flask>=3.1.1`: Web framework
- `flask-sqlalchemy>=3.1.1`: Database ORM
- `flask-wtf>=1.2.2`: Form handling and CSRF protection
- `wtforms>=3.2.1`: Form validation
- `psycopg2-binary>=2.9.10`: PostgreSQL adapter
- `gunicorn>=23.0.0`: WSGI server for production
- `email-validator>=2.2.0`: Email validation
- `markdown>=3.8`: Markdown processing
- `werkzeug>=3.1.3`: WSGI utilities

### External Services
- **Bootstrap CDN**: Replit-themed Bootstrap CSS
- **Feather Icons**: Icon library via CDN
- **PostgreSQL**: Database service (configurable)

## Deployment Strategy

### Development Environment
- **Local Development**: Flask development server with SQLite fallback
- **Hot Reload**: Gunicorn with `--reload` flag for development
- **Environment Variables**: `SESSION_SECRET` and `DATABASE_URL` configuration

### Production Environment
- **WSGI Server**: Gunicorn with autoscaling deployment target
- **Database**: PostgreSQL 16 with connection pooling
- **Proxy**: ProxyFix middleware for proper HTTPS URL generation
- **Modules**: Python 3.11 with PostgreSQL 16 via Nix

### Configuration
- **Database Connection**: Automatic fallback from PostgreSQL to SQLite
- **Session Security**: Configurable session secret key
- **Pool Settings**: Connection pool with 300-second recycle and pre-ping

## Open Source Security

### Repository Status
- **Public Repository**: https://github.com/community-mentorship/platform
- **Security Files**: Comprehensive .gitignore, SECURITY.md, and .env.example
- **Sensitive Data**: All environment variables and secrets properly protected
- **Cache Directory**: .cache/ excluded from repository

### Security Measures Implemented
- Environment variable template (.env.example) for safe deployment
- Comprehensive security documentation in SECURITY.md
- Protected sensitive files via .gitignore (secrets, logs, cache, personal data)
- No hardcoded credentials or personal information in codebase

## Recent Changes

### June 15, 2025 - Open Source Security Implementation
- Connected to community-mentorship organization repository
- Created comprehensive .gitignore protecting sensitive data
- Added SECURITY.md with deployment and privacy guidelines
- Created .env.example template for safe environment setup
- Verified no personal information or credentials in codebase
- Repository ready for public open-source distribution

### June 15, 2025 - Cycle 5 Completion
- Enhanced form builder with rich text formatting (bold, italic, links)
- Advanced field validation with character limits and format checking
- Live preview functionality showing formatted labels and validation hints
- Multiple field types: text, textarea, email, URL, dropdown, radio, checkbox
- Comprehensive end-to-end test suite validating all enhanced features

## Changelog
- June 15, 2025: Cycle 5 enhanced form builder completed
- June 15, 2025: Open source security implementation
- June 15, 2025: Repository connected to community-mentorship organization

## User Preferences

Preferred communication style: Simple, everyday language.