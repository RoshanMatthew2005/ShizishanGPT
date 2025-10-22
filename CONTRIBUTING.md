# Contributing to ShizishanGPT

Thank you for your interest in contributing to ShizishanGPT! 🌾

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs
- Provide clear description and reproduction steps
- Include system information and error messages

### Feature Requests
- Open an issue with label "enhancement"
- Describe the feature and its benefits
- Discuss implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow code style guidelines
   - Add tests if applicable
   - Update documentation
4. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request**

## Code Style

### Python
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for functions and classes
- Keep functions focused and small

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Start with a verb (Add, Fix, Update, Remove)
- Keep first line under 50 characters
- Add detailed description if needed

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ShizishanGPT.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8
```

## Testing

```bash
# Run tests
pytest tests/

# Run linter
flake8 src/

# Format code
black src/
```

## Areas for Contribution

### High Priority
- [ ] Model training and optimization
- [ ] Dataset collection and curation
- [ ] Documentation improvements
- [ ] Bug fixes

### Medium Priority
- [ ] New features
- [ ] UI/UX improvements
- [ ] Performance optimization
- [ ] Testing coverage

### Low Priority
- [ ] Code refactoring
- [ ] Additional examples
- [ ] Language translations

## Questions?

Feel free to open an issue or reach out to the maintainers.

---

**Thank you for contributing!** 🙏
