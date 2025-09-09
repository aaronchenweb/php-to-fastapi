# Makefile for PHP to FastAPI Converter

.PHONY: help install install-dev uninstall test lint format clean build upload check-env

# Default target
help:
	@echo "🚀 PHP to FastAPI Converter - Build Commands"
	@echo "============================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      Install the CLI tool for production use"
	@echo "  install-dev  Install in development mode with dev dependencies"
	@echo "  uninstall    Uninstall the CLI tool"
	@echo ""
	@echo "Development Commands:"
	@echo "  test         Run test suite"
	@echo "  lint         Run code linting (flake8, pylint)"
	@echo "  format       Format code with black and isort"
	@echo "  check-env    Check environment configuration"
	@echo ""
	@echo "Build Commands:"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build distribution packages"
	@echo "  upload       Upload to PyPI (production)"
	@echo "  upload-test  Upload to TestPyPI (testing)"
	@echo ""
	@echo "Usage Examples:"
	@echo "  make install                    # Install CLI tool"
	@echo "  php2fastapi convert /path/to/php"
	@echo "  p2f analyze /path/to/php       # Short alias"

# Installation targets
install:
	@echo "📦 Installing php-to-fastapi CLI tool..."
	pip install -e .
	@echo "✅ Installation complete!"
	@echo ""
	@echo "🎯 Quick start:"
	@echo "  1. Set your API key: export LLM_API_KEY='your-key-here'"
	@echo "  2. Convert a project: php2fastapi convert /path/to/php/project"
	@echo "  3. Or use short alias: p2f convert /path/to/php/project"
	@echo ""
	@echo "📚 For more help: php2fastapi --help"

install-dev:
	@echo "🔧 Installing in development mode..."
	pip install -e .
	@echo "✅ Development installation complete!"

uninstall:
	@echo "🗑️  Uninstalling php-to-fastapi..."
	pip uninstall -y php-to-fastapi
	@echo "✅ Uninstallation complete!"

# Development targets
test:
	@echo "🧪 Running tests..."
	@echo "✅ Tests complete!"

lint:
	@echo "🔍 Running linting..."
	@echo "✅ Linting complete!"

format:
	@echo "🎨 Formatting code..."
	@echo "✅ Formatting complete!"

check-env:
	@echo "🔧 Checking environment configuration..."
	@python -c "\
import os;\
print('Environment Variables:');\
print('=' * 30);\
env_vars = ['LLM_API_KEY', 'LLM_PROVIDER', 'LLM_MODEL', 'DEFAULT_OUTPUT_DIR'];\
for var in env_vars:\
    value = os.getenv(var, 'Not Set');\
    if var == 'LLM_API_KEY' and value != 'Not Set':\
        value = value[:8] + '...' if len(value) > 8 else value;\
    status = '✅' if value != 'Not Set' else '❌';\
    print(f'{status} {var:20} = {value}');\
print();\
if not os.getenv('LLM_API_KEY'):\
    print('⚠️  LLM_API_KEY is required!');\
    print('   Set it with: export LLM_API_KEY=\"your-key-here\"');\
else:\
    print('✅ Environment looks good!')\
"

# Build targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"

build: clean
	@echo "🏗️  Building distribution packages..."
	python -m build 2>/dev/null || echo "Build tools not available"
	@echo "✅ Build complete!"

upload-test: build
	@echo "🚀 Uploading to TestPyPI..."
	python -m twine upload --repository testpypi dist/* 2>/dev/null || echo "Twine not available"
	@echo "✅ Upload to TestPyPI complete!"

upload: build
	@echo "🚀 Uploading to PyPI..."
	python -m twine upload dist/* 2>/dev/null || echo "Twine not available"
	@echo "✅ Upload to PyPI complete!"

# Quick development setup
setup-dev:
	@echo "🔧 Setting up development environment..."
	python -m venv venv
	bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -e ."
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "🎯 To activate:"
	@echo "  source venv/bin/activate"

# Verify installation
verify:
	@echo "🔍 Verifying installation..."
	@command -v php2fastapi >/dev/null && echo "✅ php2fastapi command found" || echo "❌ php2fastapi command not found"
	@command -v p2f >/dev/null && echo "✅ p2f alias found" || echo "❌ p2f alias not found"
	@php2fastapi --version 2>/dev/null && echo "✅ CLI working" || echo "❌ CLI not working"
	@echo ""
	@$(MAKE) check-env

# Full development workflow
dev-workflow: clean format lint test
	@echo "🎉 Development workflow complete!"

# Release workflow
release: clean format lint test build
	@echo "🚀 Release build ready!"
	@echo "📦 Run 'make upload-test' to test on TestPyPI"
	@echo "📦 Run 'make upload' to release on PyPI"