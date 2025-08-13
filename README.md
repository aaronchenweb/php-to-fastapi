# PHP to FastAPI Converter

An intelligent, AI-powered tool that automatically converts PHP web APIs to FastAPI applications using a systematic 4-stage workflow with LLM assistance.

## 🚀 Features

- **Multi-Framework Support**: Works with Laravel, CodeIgniter, Symfony, Slim, and vanilla PHP projects
- **AI-Powered Analysis**: Leverages LLM providers (OpenAI, Anthropic, Gemini) for intelligent code understanding
- **4-Stage Workflow**: Systematic conversion process with user approval at each stage
- **Interactive CLI**: User-friendly command-line interface with progress tracking
- **Comprehensive Detection**: Automatically detects PHP frameworks, versions, and project structures
- **Code Verification**: Built-in verification stage to ensure generated code quality
- **Flexible Configuration**: Support for multiple LLM providers and customizable settings
- **Dry Run Mode**: Preview conversion plan without generating files

## 🏗️ Architecture

The converter follows a modular 4-stage architecture:

```
Stage 1: Analysis & Understanding
├── Local PHP project analysis
├── LLM-enhanced code understanding
└── User approval checkpoint

Stage 2: Conversion Planning
├── Strategic conversion planning
├── LLM-generated conversion strategy
└── User approval checkpoint

Stage 3: FastAPI Generation
├── Automated code generation
├── Project structure creation
└── Configuration file generation

Stage 4: Verification & Validation
├── Code syntax verification
├── Functionality testing
├── Performance comparison
└── Final quality report
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- API key for your chosen LLM provider (OpenAI, Anthropic, or Gemini)

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/php-to-fastapi-converter.git
cd php-to-fastapi-converter

# Install required packages
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Required: LLM API Configuration
LLM_API_KEY=your_api_key_here
LLM_PROVIDER=openai  # or 'anthropic', 'gemini'
LLM_MODEL=gpt-4      # or 'claude-3-sonnet-20240229', 'gemini-1.5-pro'

# Optional: Customization
DEFAULT_OUTPUT_DIR=./fastapi_output
LLM_BASE_URL=https://api.openai.com/v1  # Custom API endpoint if needed
```

## 🎯 Quick Start

### Basic Conversion

```bash
# Convert a PHP project to FastAPI
python main.py convert /path/to/php/project

# Specify custom output directory
python main.py convert /path/to/php/project --output /custom/output/path

# Use different LLM provider
python main.py convert /path/to/php/project --llm-provider anthropic
```

### Advanced Usage

```bash
# Dry run (analysis and planning only)
python main.py convert /path/to/php/project --dry-run

# Skip backup creation
python main.py convert /path/to/php/project --no-backup

# Skip test generation
python main.py convert /path/to/php/project --no-tests

# Verbose output for detailed information
python main.py convert /path/to/php/project --verbose

# Skip verification stage
python main.py convert /path/to/php/project --skip-verification
```

## 📋 Supported PHP Frameworks

| Framework          | Detection | Conversion | Status       |
| ------------------ | --------- | ---------- | ------------ |
| **Laravel**        | ✅        | ✅         | Full Support |
| **CodeIgniter**    | ✅        | ✅         | Full Support |
| **Symfony**        | ✅        | ✅         | Full Support |
| **Slim Framework** | ✅        | ✅         | Full Support |
| **Vanilla PHP**    | ✅        | ✅         | Full Support |

## 🔧 Configuration

### LLM Provider Settings

#### OpenAI

```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4                    # or gpt-3.5-turbo
LLM_API_KEY=sk-your-openai-key
```

#### Anthropic

```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229 # or claude-3-opus-20240229
LLM_API_KEY=your-anthropic-key
```

#### Google Gemini

```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-pro          # or gemini-1.5-flash
LLM_API_KEY=your-gemini-key
```

### Conversion Settings

```python
# config/settings.py customization
class ConversionSettings:
    backup_original: bool = True      # Create backup of PHP project
    generate_tests: bool = True       # Generate FastAPI tests
    include_documentation: bool = True # Generate API documentation
    preserve_comments: bool = True    # Preserve code comments
```

## 📁 Project Structure

```
php-to-fastapi/
├── main.py                    # CLI entry point
├── config/
│   ├── settings.py           # Configuration management
│   └── prompts.py            # LLM prompt templates
├── core/
│   ├── detector.py           # PHP project detection
│   ├── orchestrator.py       # Workflow orchestration
│   ├── llm_client.py         # LLM provider integration
│   └── user_interface.py     # User interaction
├── stages/
│   ├── analysis_stage.py     # Stage 1: Analysis
│   ├── planning_stage.py     # Stage 2: Planning
│   ├── generation_stage.py   # Stage 3: Generation
│   └── verification_stage.py # Stage 4: Verification
├── analyzers/                # PHP code analysis components
├── planners/                 # Conversion planning components
├── generators/               # FastAPI code generation
├── verifiers/                # Code verification components
└── utils/                    # Utility functions
```

## 🔍 How It Works

### Stage 1: Analysis & Understanding

1. **Local Analysis**: Scans PHP project structure, detects framework, identifies API endpoints
2. **LLM Enhancement**: Sends analysis to LLM for deeper code understanding
3. **User Review**: Presents comprehensive analysis for user approval

### Stage 2: Conversion Planning

1. **Strategy Development**: Creates conversion strategy based on analysis
2. **LLM Planning**: Generates detailed conversion plan using LLM
3. **User Approval**: Reviews conversion strategy before proceeding

### Stage 3: FastAPI Generation

1. **Code Generation**: Automatically generates FastAPI application
2. **Structure Creation**: Creates proper FastAPI project structure
3. **Configuration**: Generates requirements.txt, environment files, etc.

### Stage 4: Verification & Validation

1. **Syntax Verification**: Validates generated Python/FastAPI code
2. **Functionality Testing**: Tests API endpoints and functionality
3. **Quality Report**: Generates comprehensive verification report

## 📊 Example Output

After successful conversion, you'll get a complete FastAPI project:

```
fastapi_output/
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration template
├── app/
│   ├── __init__.py
│   ├── models/              # Pydantic models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   ├── database/            # Database configuration
│   └── config.py            # Application configuration
├── tests/                   # Generated test files
├── docs/                    # API documentation
└── docker/                  # Docker configuration (optional)
```

## 🎛️ CLI Reference

```bash
python main.py convert <php-project-path> [OPTIONS]

Arguments:
  php-project-path          Path to PHP project directory

Options:
  -o, --output PATH         Output directory for FastAPI project
  --llm-provider PROVIDER   LLM provider (openai|anthropic|gemini)
  --llm-model MODEL         Specific model to use
  --no-backup              Skip creating backup of PHP project
  --no-tests               Skip generating test files
  --dry-run                Analysis and planning only
  --skip-verification      Skip verification stage
  -v, --verbose            Enable detailed output
  --version                Show version information
  --help                   Show help message
```

## 🧪 Testing

The converter includes comprehensive testing capabilities:

```bash
# Run with verbose output to see detailed analysis
python main.py convert /path/to/php/project --verbose

# Perform dry run to validate before generation
python main.py convert /path/to/php/project --dry-run

# Test generated FastAPI application
cd fastapi_output
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🐛 Troubleshooting

### Common Issues

**1. LLM API Connection Failed**

```bash
# Verify API key and provider settings
export LLM_API_KEY=your-actual-api-key
export LLM_PROVIDER=openai
```

**2. PHP Project Not Detected**

```bash
# Ensure project contains PHP files and API patterns
# Check that you're pointing to the project root directory
```

**3. Generation Errors**

```bash
# Use verbose mode for detailed error information
python main.py convert /path/to/php/project --verbose
```

**4. Permission Errors**

```bash
# Ensure write permissions to output directory
chmod 755 /path/to/output/directory
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Set debug environment variable
export DEBUG=1
python main.py convert /path/to/php/project --verbose
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/yourusername/php-to-fastapi-converter.git
cd php-to-fastapi-converter

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 .
black .
```

### Architecture Guidelines

- Follow the existing 4-stage architecture
- Add new analyzers for PHP frameworks in `analyzers/`
- Add new generators for FastAPI components in `generators/`
- Maintain separation of concerns between stages
- Include comprehensive error handling and user feedback

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI framework for excellent Python API development
- LLM providers (OpenAI, Anthropic, Google) for AI capabilities
- PHP community for the legacy codebases this tool helps modernize

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/php-to-fastapi-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/php-to-fastapi-converter/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/php-to-fastapi-converter/wiki)

## 🗺️ Roadmap

- [ ] **GUI Interface**: Web-based interface for non-technical users
- [ ] **Additional Frameworks**: Support for CakePHP, Zend Framework
- [ ] **Advanced Migration**: Database schema migration tools
- [ ] **Performance Optimization**: Parallel processing for large projects
- [ ] **CI/CD Integration**: GitHub Actions workflows for automated conversion
- [ ] **Plugin System**: Extensible architecture for custom conversions

---

**Made with ❤️ for the PHP and Python communities**
