# Contributing to Reddit Scraper

Thank you for your interest in contributing to Reddit Scraper! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Standards](#development-standards)

## Code of Conduct

This project follows a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Respect Reddit's Terms of Service and API guidelines

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Reddit API credentials (for testing)

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/pixelbrow720/reddit-scraper.git
   cd reddit-scraper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Setup configuration**
   ```bash
   cp config/settings.example.yaml config/settings.yaml
   # Edit config/settings.yaml with your Reddit API credentials
   ```

5. **Run tests**
   ```bash
   python -m pytest tests/  # If tests are available
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes** - Fix issues and improve stability
- **Feature enhancements** - Add new functionality
- **Documentation** - Improve docs, examples, and guides
- **Performance improvements** - Optimize code and algorithms
- **Testing** - Add or improve test coverage
- **Examples** - Create usage examples and tutorials

### Before You Start

1. **Check existing issues** - Look for related issues or feature requests
2. **Create an issue** - Discuss your idea before implementing large changes
3. **Follow the roadmap** - Check if your contribution aligns with project goals

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "Add: New filtering option for post categories"
git commit -m "Fix: Rate limiting issue with concurrent requests"
git commit -m "Docs: Update installation instructions"
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Reference to related issues** (if applicable)
- **Screenshots** (if UI changes)

### 5. Code Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

```markdown
**Bug Description**
A clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should have happened

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- Reddit Scraper version: [e.g., 1.0.0]

**Additional Context**
- Log files (if relevant)
- Configuration settings (remove sensitive data)
- Screenshots (if applicable)
```

### Feature Requests

For feature requests, please include:

- **Use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives considered** - Other approaches you've thought about
- **Additional context** - Any other relevant information

## Development Standards

### Code Style

- **PEP 8** compliance for Python code
- **Type hints** for function parameters and return values
- **Docstrings** for all public functions and classes
- **Clear variable names** that describe their purpose

### Code Structure

```python
def function_name(param1: str, param2: int = 10) -> Dict[str, Any]:
    """Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2 with default value
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
    """
    # Implementation here
    pass
```

### Testing

- Write tests for new functionality
- Ensure existing tests still pass
- Aim for good test coverage
- Use descriptive test names

### Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions/classes
- Update configuration examples if needed
- Include usage examples for new features

### Performance Considerations

- **Rate limiting** - Respect Reddit's API limits
- **Memory usage** - Handle large datasets efficiently
- **Error handling** - Graceful failure and recovery
- **Logging** - Appropriate log levels and messages

## Project Structure

```
reddit-scraper/
├── src/
│   ├── core/           # Core scraping functionality
│   ├── processors/     # Data processing and filtering
│   ├── exporters/      # Export functionality
│   └── cli/           # Command line interface
├── tests/             # Test files
├── docs/              # Documentation
├── examples/          # Usage examples
├── config/            # Configuration files
└── scripts/           # Utility scripts
```

## Release Process

1. **Version bumping** - Update version in setup.py and __init__.py
2. **Changelog** - Update CHANGELOG.md with new features and fixes
3. **Testing** - Ensure all tests pass
4. **Documentation** - Update docs for new features
5. **Tagging** - Create git tag for the release

## Getting Help

If you need help with development:

- **GitHub Issues** - Ask questions in issues
- **Twitter** - Reach out to [@BrowPixel](https://twitter.com/BrowPixel)
- **Documentation** - Check existing docs and examples

## Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **README.md** acknowledgments section

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Reddit Scraper! Your help makes this project better for everyone.

**Maintainer:** [@pixelbrow720](https://github.com/pixelbrow720)  
**Twitter:** [@BrowPixel](https://twitter.com/BrowPixel)