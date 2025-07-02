# Security Policy

## Supported Versions

SecRef is actively maintained. Security updates are provided for:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

SecRef takes security seriously. We appreciate your efforts to responsibly disclose your findings.

### Where to Report

Please report security vulnerabilities via one of these channels:

1. **Email**: security@secref.org
2. **GitHub Security Advisory**: [Create a security advisory](https://github.com/mikedilalo/secref/security/advisories/new)

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if available)
- Your contact information (for follow-up)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Within 30 days for critical issues

### What to Expect

1. **Acknowledgment**: We'll confirm receipt of your report
2. **Assessment**: We'll investigate and validate the issue
3. **Resolution**: We'll work on a fix and coordinate disclosure
4. **Credit**: With your permission, we'll acknowledge your contribution

## Security Measures

SecRef implements the following security measures:

### Application Security
- Authentication required for admin access
- CSRF protection on all forms
- Input validation and sanitization
- SQL injection prevention via parameterized queries
- XSS protection through content sanitization
- Rate limiting on sensitive endpoints

### Infrastructure Security
- HTTPS enforcement in production
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Regular dependency updates
- Automated security scanning in CI/CD

### Data Protection
- No user tracking or analytics
- Minimal data collection
- Secure session management
- Encrypted data transmission

## Disclosure Policy

- We follow responsible disclosure practices
- Security issues are fixed before public disclosure
- We coordinate with reporters on disclosure timing
- Critical vulnerabilities may trigger immediate patches

## Hall of Fame

We gratefully acknowledge security researchers who have helped improve SecRef:

- [Your name could be here!]

## Contact

- Security: security@secref.org
- General: info@secref.org
- GitHub: https://github.com/dcbokonon/secref

Thank you for helping keep SecRef secure!
