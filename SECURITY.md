# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to security@yourcompany.com. All security vulnerabilities will be promptly addressed.

Please include the following information:
- Type of vulnerability
- Full paths of affected files
- Location of the issue
- Step-by-step instructions to reproduce
- Proof-of-concept or exploit code (if possible)
- Impact assessment

## Security Measures

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Manager, Employee)
- Secure password hashing with bcrypt
- Token expiration and refresh

### Data Protection
- Face encodings stored as binary (not raw images)
- Input validation on all endpoints
- SQL injection prevention via ORM
- XSS protection in frontend

### Face Recognition Security
- Identity verification (face must match logged-in user)
- Quality checks before face enrollment
- Limited retry attempts
- Admin/Manager-only enrollment

### Infrastructure
- CORS protection
- HTTPS enforcement (production)
- Rate limiting (recommended for production)
- Environment variable isolation

## Best Practices

### For Developers
1. Never commit `.env` files
2. Use strong SECRET_KEY (32+ characters)
3. Rotate keys regularly
4. Keep dependencies updated
5. Review code for security issues

### For Deployment
1. Use HTTPS for all connections
2. Enable rate limiting
3. Set up monitoring and alerts
4. Regular security audits
5. Database backups
6. Restrict CORS to specific domains

## Known Limitations

1. Face recognition accuracy varies with lighting
2. SQLite not suitable for high-concurrency production
3. Uploaded face images accumulate (implement cleanup)
4. No built-in rate limiting (add middleware)

## Updates

Security updates will be released as needed and announced in release notes.
