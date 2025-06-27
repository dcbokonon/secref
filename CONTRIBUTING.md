# Contributing to SecRef

Thank you for your interest in contributing to SecRef! This project aims to be the most comprehensive cybersecurity resource hub, and we welcome contributions from the community.

## How to Contribute

### 1. Reporting Issues

- **Security Issues**: Please see our [Security Policy](SECURITY.md)
- **Bugs**: Open an issue with a clear description and steps to reproduce
- **Feature Requests**: Open an issue describing the feature and its value

### 2. Adding or Updating Resources

The easiest way to contribute is by adding new cybersecurity resources or updating existing ones.

#### Resource Format

Resources are stored as JSON in `src/data/`. Each resource should include:

```json
{
  "name": "Tool Name",
  "url": "https://example.com",
  "description": "Clear, concise description",
  "type": "free|paid|freemium|enterprise",
  "notation": "(F)†",  // If applicable
  "pricingNote": "Free tier: X, Pro: $Y/month",
  "isCommunityFavorite": false,
  "isIndustryStandard": false,
  "tags": ["category", "use-case"],
  "platforms": ["windows", "linux", "macos"]
}
```

#### Resource Guidelines

- **Accuracy**: Verify all information is current and correct
- **Neutrality**: Use objective descriptions without marketing language
- **Completeness**: Include all relevant fields
- **Categories**: Place resources in appropriate categories
- **Quality**: Only add high-quality, actively maintained resources

### 3. Code Contributions

#### Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/secref.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `npm install`

#### Development Process

1. Make your changes
2. Test thoroughly:
   ```bash
   npm test
   npm run lint
   ```
3. Commit with clear messages:
   ```bash
   git commit -m "Add: New feature description"
   ```
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request

#### Code Standards

- **TypeScript**: Use TypeScript for all new code
- **Testing**: Write tests for new functionality
- **Linting**: Code must pass ESLint checks
- **Security**: Follow secure coding practices
- **Documentation**: Update docs for significant changes

### 4. Documentation Contributions

Help improve our documentation:
- Fix typos or clarify confusing sections
- Add examples or use cases
- Translate documentation
- Improve installation or setup guides

## Pull Request Process

1. **Before Submitting**:
   - Ensure your code follows our style guide
   - All tests pass
   - Update documentation if needed
   - Add yourself to CONTRIBUTORS.md (if not already there)

2. **PR Description**:
   - Clearly describe what changes you made
   - Reference any related issues
   - Include screenshots for UI changes

3. **Review Process**:
   - PRs require at least one review
   - Address reviewer feedback
   - Be patient - reviews may take a few days

## Style Guide

### Git Commit Messages

- Use present tense: "Add feature" not "Added feature"
- Use imperative mood: "Move cursor to..." not "Moves cursor to..."
- Reference issues: "Fix #123: Resolve navigation bug"

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `Add`: New feature or resource
- `Fix`: Bug fix
- `Update`: Update existing functionality
- `Remove`: Remove functionality
- `Refactor`: Code change that doesn't affect behavior
- `Docs`: Documentation only changes
- `Test`: Adding or updating tests

### Code Style

- Use 2 spaces for indentation
- Use meaningful variable names
- Comment complex logic
- Keep functions small and focused

### Resource Naming

- Use official product names
- Include version numbers when relevant
- Be consistent with existing entries

## Community Guidelines

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what's best for the project
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Annual contributor recognition (for significant contributors)

## Questions?

- Check existing issues and discussions
- Join our community chat (when available)
- Email: contribute@secref.org

## License

By contributing to SecRef, you agree that your contributions will be licensed under the MIT License.

Thank you for helping make SecRef better! 🚀