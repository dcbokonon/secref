# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of SecRef - comprehensive cybersecurity resource directory
- 892+ security tools organized by category
- 1,247+ learning resources
- Community directory with physical and online groups
- Flask-based admin panel for resource management
- SQLite database with import/export functionality
- Comprehensive security hardening
- Docker deployment support
- GitHub Actions CI/CD pipeline

### Security
- Implemented authentication system with secure password hashing
- Added CSRF protection to all forms
- Configured security headers in Caddy
- Added rate limiting to prevent abuse
- Input validation and sanitization
- SQL injection prevention with parameterized queries

## [1.0.0] - 2025-06-26

### Added
- Initial public release

[Unreleased]: https://github.com/dcbokonon/secref/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/dcbokonon/secref/releases/tag/v1.0.0