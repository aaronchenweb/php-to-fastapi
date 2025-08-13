# config/prompts.py
"""LLM prompt templates for PHP to FastAPI conversion."""

from typing import Dict, Any


class Prompts:
    """Container for all LLM prompt templates."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Base system prompt for all LLM interactions."""
        return """You are an expert software architect specializing in converting PHP web APIs to Python FastAPI applications. 

You have deep knowledge of:
- PHP frameworks (Laravel, CodeIgniter, Symfony, Slim, vanilla PHP)
- Python FastAPI framework and ecosystem
- RESTful API design patterns
- Database migration strategies
- Modern web development best practices

Your responses should be:
- Technically accurate and detailed
- Focused on practical implementation
- Considerate of performance and security implications
- Structured in JSON format when requested

Always provide clear reasoning for your architectural decisions."""

    @staticmethod
    def get_analysis_prompt(analysis_data: Dict[str, Any]) -> str:
        """Prompt for Stage 1: Analysis and Understanding."""
        return f"""
# PHP to FastAPI Analysis Task

I need you to analyze a PHP web API project and provide a comprehensive understanding of its architecture.

## Project Analysis Data:
```json
{analysis_data}
```

## Required Analysis:

Please analyze this PHP project and provide a detailed JSON response with the following structure:

```json
{{
    "project_summary": {{
        "framework_detected": "string",
        "php_version_estimated": "string", 
        "architecture_pattern": "string",
        "complexity_level": "low|medium|high",
        "api_type": "rest|soap|graphql|mixed"
    }},
    "endpoints_analysis": {{
        "total_endpoints": number,
        "http_methods_used": ["GET", "POST", "PUT", "DELETE"],
        "authentication_methods": ["session", "jwt", "api_key", "oauth"],
        "endpoint_categories": [
            {{
                "category": "string",
                "endpoints": ["endpoint1", "endpoint2"],
                "complexity": "low|medium|high"
            }}
        ]
    }},
    "database_analysis": {{
        "database_type": "mysql|postgresql|sqlite|mongodb|none",
        "orm_framework": "string|none",
        "tables_estimated": number,
        "relationships_complexity": "low|medium|high",
        "migration_challenges": ["challenge1", "challenge2"]
    }},
    "dependencies_analysis": {{
        "critical_dependencies": ["dep1", "dep2"],
        "python_equivalents": {{
            "php_dependency": "python_equivalent"
        }},
        "migration_complexity": "low|medium|high"
    }},
    "architecture_insights": {{
        "design_patterns_used": ["pattern1", "pattern2"],
        "code_organization": "good|fair|poor",
        "separation_of_concerns": "good|fair|poor",
        "potential_issues": ["issue1", "issue2"],
        "conversion_challenges": ["challenge1", "challenge2"]
    }},
    "recommendations": {{
        "suggested_fastapi_structure": "string",
        "key_conversion_priorities": ["priority1", "priority2"],
        "estimated_conversion_effort": "low|medium|high",
        "recommended_python_packages": ["package1", "package2"]
    }}
}}
```

Focus on providing actionable insights that will guide the conversion planning stage.
"""

    @staticmethod
    def get_planning_prompt(analysis_result: Dict[str, Any], planning_data: Dict[str, Any]) -> str:
        """Prompt for Stage 2: Conversion Planning."""
        return f"""
# PHP to FastAPI Conversion Planning Task

Based on the approved analysis, create a detailed conversion plan for transforming this PHP API to FastAPI.

## Approved Analysis:
```json
{analysis_result}
```

## Planning Data:
```json
{planning_data}
```

## Required Conversion Plan:

Please create a comprehensive conversion plan in the following JSON structure:

```json
{{
    "conversion_strategy": {{
        "approach": "incremental|full_rewrite|hybrid",
        "conversion_order": ["phase1", "phase2", "phase3"],
        "estimated_timeline": "string",
        "risk_level": "low|medium|high"
    }},
    "project_structure": {{
        "root_directory": "string",
        "main_directories": [
            {{
                "name": "string",
                "purpose": "string",
                "php_equivalent": "string"
            }}
        ],
        "key_files": [
            {{
                "filename": "string",
                "purpose": "string",
                "dependencies": ["dep1", "dep2"]
            }}
        ]
    }},
    "api_conversion_plan": {{
        "routing_strategy": "string",
        "endpoint_mappings": [
            {{
                "php_endpoint": "string",
                "fastapi_endpoint": "string",
                "http_method": "string",
                "conversion_notes": "string",
                "dependencies": ["dep1", "dep2"]
            }}
        ],
        "middleware_plan": [
            {{
                "middleware_type": "authentication|cors|logging|custom",
                "implementation": "string",
                "php_equivalent": "string"
            }}
        ]
    }},
    "database_migration_plan": {{
        "database_setup": "string",
        "orm_choice": "sqlalchemy|tortoise|none",
        "migration_strategy": "string",
        "model_mappings": [
            {{
                "php_model": "string",
                "python_model": "string",
                "fields_mapping": {{}},
                "relationships": ["rel1", "rel2"]
            }}
        ]
    }},
    "dependency_conversion": {{
        "requirements_txt": [
            {{
                "package": "string",
                "version": "string",
                "purpose": "string",
                "php_equivalent": "string"
            }}
        ],
        "dev_dependencies": ["package1", "package2"],
        "optional_dependencies": ["package1", "package2"]
    }},
    "configuration_plan": {{
        "environment_variables": [
            {{
                "name": "string",
                "purpose": "string",
                "default_value": "string",
                "php_equivalent": "string"
            }}
        ],
        "config_files": [
            {{
                "filename": "string",
                "format": "json|yaml|env",
                "purpose": "string"
            }}
        ]
    }},
    "testing_strategy": {{
        "testing_framework": "pytest|unittest",
        "test_types": ["unit", "integration", "api"],
        "coverage_target": "percentage",
        "test_file_structure": "string"
    }},
    "deployment_considerations": {{
        "deployment_options": ["docker", "gunicorn", "uvicorn"],
        "performance_optimizations": ["opt1", "opt2"],
        "security_implementations": ["sec1", "sec2"],
        "monitoring_setup": ["tool1", "tool2"]
    }},
    "implementation_notes": {{
        "critical_conversion_points": ["point1", "point2"],
        "potential_breaking_changes": ["change1", "change2"],
        "fallback_strategies": ["strategy1", "strategy2"],
        "validation_checkpoints": ["checkpoint1", "checkpoint2"]
    }}
}}
```

Ensure the plan is:
1. Technically feasible and follows FastAPI best practices
2. Maintains API compatibility where possible
3. Addresses all identified challenges from the analysis
4. Provides clear implementation guidance
5. Considers performance, security, and maintainability
"""

    @staticmethod
    def get_validation_prompt(generated_code: str, original_analysis: Dict[str, Any]) -> str:
        """Prompt for validating generated FastAPI code."""
        return f"""
# FastAPI Code Validation Task

Please validate the generated FastAPI code against the original PHP API requirements.

## Original Analysis:
```json
{original_analysis}
```

## Generated FastAPI Code:
```python
{generated_code}
```

## Validation Requirements:

Check for:
1. **API Compatibility**: Do the endpoints match the original PHP API?
2. **Best Practices**: Does the code follow FastAPI and Python best practices?
3. **Security**: Are security measures properly implemented?
4. **Performance**: Are there any obvious performance issues?
5. **Completeness**: Are all required features implemented?

Provide a validation report in JSON format:

```json
{{
    "validation_status": "passed|failed|warnings",
    "api_compatibility": {{
        "endpoints_match": true/false,
        "missing_endpoints": ["endpoint1"],
        "extra_endpoints": ["endpoint1"],
        "method_mismatches": ["endpoint: expected vs actual"]
    }},
    "code_quality": {{
        "follows_fastapi_patterns": true/false,
        "proper_error_handling": true/false,
        "appropriate_response_models": true/false,
        "documentation_quality": "good|fair|poor"
    }},
    "security_assessment": {{
        "authentication_implemented": true/false,
        "input_validation": true/false,
        "sql_injection_protection": true/false,
        "cors_configured": true/false
    }},
    "issues_found": [
        {{
            "severity": "error|warning|info",
            "category": "string",
            "description": "string",
            "suggested_fix": "string",
            "line_number": number
        }}
    ],
    "recommendations": [
        "recommendation1",
        "recommendation2"
    ]
}}
```
"""

    @staticmethod
    def get_error_analysis_prompt(error_message: str, context: str) -> str:
        """Prompt for analyzing conversion errors."""
        return f"""
# Conversion Error Analysis

An error occurred during the PHP to FastAPI conversion process.

## Error Details:
```
{error_message}
```

## Context:
```
{context}
```

Please analyze this error and provide:

1. **Root Cause**: What caused this error?
2. **Impact**: How does this affect the conversion?
3. **Solutions**: What are the possible fixes?
4. **Prevention**: How can similar errors be avoided?

Respond in JSON format:

```json
{{
    "error_analysis": {{
        "root_cause": "string",
        "error_category": "syntax|dependency|logic|configuration|other",
        "impact_level": "low|medium|high|critical"
    }},
    "solutions": [
        {{
            "approach": "string",
            "complexity": "low|medium|high",
            "steps": ["step1", "step2"],
            "risks": ["risk1", "risk2"]
        }}
    ],
    "prevention_strategies": [
        "strategy1",
        "strategy2"
    ],
    "recommended_action": "retry|skip|manual_intervention|abort"
}}
```
"""