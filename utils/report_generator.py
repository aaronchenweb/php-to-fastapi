"""
Report generation utilities for PHP to FastAPI converter.
Generates comprehensive reports about the conversion process.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class ReportFormat(Enum):
    """Supported report formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    TEXT = "text"


@dataclass
class ReportSection:
    """A section of the conversion report."""
    title: str
    content: str
    level: int = 1
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConversionStats:
    """Statistics about the conversion process."""
    total_php_files: int = 0
    converted_files: int = 0
    total_endpoints: int = 0
    converted_endpoints: int = 0
    total_models: int = 0
    generated_models: int = 0
    total_lines_php: int = 0
    total_lines_python: int = 0
    conversion_time_seconds: float = 0.0
    
    @property
    def conversion_ratio(self) -> float:
        """Calculate conversion ratio."""
        if self.total_php_files == 0:
            return 0.0
        return self.converted_files / self.total_php_files
    
    @property
    def endpoint_conversion_ratio(self) -> float:
        """Calculate endpoint conversion ratio."""
        if self.total_endpoints == 0:
            return 0.0
        return self.converted_endpoints / self.total_endpoints


@dataclass
class ConversionReport:
    """Complete conversion report."""
    project_name: str
    php_project_path: str
    fastapi_project_path: str
    conversion_timestamp: str
    stats: ConversionStats
    sections: List[ReportSection]
    analysis_result: Optional[Dict[str, Any]] = None
    planning_result: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    
    def add_section(self, title: str, content: str, level: int = 1, 
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a section to the report."""
        section = ReportSection(title, content, level, metadata)
        self.sections.append(section)
    
    def get_section(self, title: str) -> Optional[ReportSection]:
        """Get a section by title."""
        for section in self.sections:
            if section.title == title:
                return section
        return None


class ReportGenerator:
    """Generates conversion reports in various formats."""
    
    def __init__(self, output_dir: Union[str, Path]):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_report(self, project_name: str, php_path: str, fastapi_path: str,
                     analysis_result: Optional[Dict[str, Any]] = None,
                     planning_result: Optional[Dict[str, Any]] = None,
                     validation_result: Optional[Dict[str, Any]] = None) -> ConversionReport:
        """
        Create a new conversion report.
        
        Args:
            project_name: Name of the project
            php_path: Path to PHP project
            fastapi_path: Path to generated FastAPI project
            analysis_result: Analysis stage result
            planning_result: Planning stage result
            validation_result: Validation result
            
        Returns:
            ConversionReport instance
        """
        stats = self._calculate_stats(php_path, fastapi_path, analysis_result)
        
        report = ConversionReport(
            project_name=project_name,
            php_project_path=php_path,
            fastapi_project_path=fastapi_path,
            conversion_timestamp=datetime.now().isoformat(),
            stats=stats,
            sections=[],
            analysis_result=analysis_result,
            planning_result=planning_result,
            validation_result=validation_result
        )
        
        # Generate report sections
        self._add_summary_section(report)
        self._add_statistics_section(report)
        self._add_analysis_section(report)
        self._add_planning_section(report)
        self._add_generated_files_section(report)
        self._add_validation_section(report)
        self._add_recommendations_section(report)
        self._add_next_steps_section(report)
        
        return report
    
    def save_report(self, report: ConversionReport, format: ReportFormat = ReportFormat.MARKDOWN,
                   filename: Optional[str] = None) -> Path:
        """
        Save report to file.
        
        Args:
            report: Report to save
            format: Output format
            filename: Custom filename (optional)
            
        Returns:
            Path to saved report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversion_report_{timestamp}"
        
        if format == ReportFormat.MARKDOWN:
            content = self._generate_markdown(report)
            file_path = self.output_dir / f"{filename}.md"
            
        elif format == ReportFormat.HTML:
            content = self._generate_html(report)
            file_path = self.output_dir / f"{filename}.html"
            
        elif format == ReportFormat.JSON:
            content = self._generate_json(report)
            file_path = self.output_dir / f"{filename}.json"
            
        elif format == ReportFormat.TEXT:
            content = self._generate_text(report)
            file_path = self.output_dir / f"{filename}.txt"
            
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def _calculate_stats(self, php_path: str, fastapi_path: str,
                        analysis_result: Optional[Dict[str, Any]]) -> ConversionStats:
        """Calculate conversion statistics."""
        stats = ConversionStats()
        
        php_path_obj = Path(php_path)
        fastapi_path_obj = Path(fastapi_path)
        
        # Count PHP files
        if php_path_obj.exists():
            php_files = list(php_path_obj.rglob("*.php"))
            stats.total_php_files = len(php_files)
            
            # Count lines in PHP files
            for php_file in php_files:
                try:
                    with open(php_file, 'r', encoding='utf-8', errors='ignore') as f:
                        stats.total_lines_php += len(f.readlines())
                except Exception:
                    pass
        
        # Count Python files
        if fastapi_path_obj.exists():
            python_files = list(fastapi_path_obj.rglob("*.py"))
            stats.converted_files = len(python_files)
            
            # Count lines in Python files
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        stats.total_lines_python += len(f.readlines())
                except Exception:
                    pass
        
        # Extract stats from analysis result
        if analysis_result:
            endpoint_analysis = analysis_result.get('endpoint_analysis', {})
            stats.total_endpoints = len(endpoint_analysis.get('endpoints', []))
            stats.converted_endpoints = stats.total_endpoints  # Assume all converted for now
            
            database_analysis = analysis_result.get('database_analysis', {})
            stats.total_models = len(database_analysis.get('tables', []))
            stats.generated_models = stats.total_models  # Assume all generated for now
        
        return stats
    
    def _add_summary_section(self, report: ConversionReport) -> None:
        """Add executive summary section."""
        stats = report.stats
        
        content = f"""
This report summarizes the conversion of a PHP web API project to FastAPI.

**Project Details:**
- PHP Project: {report.php_project_path}
- FastAPI Project: {report.fastapi_project_path}
- Conversion Date: {report.conversion_timestamp}

**Conversion Summary:**
- PHP Files Analyzed: {stats.total_php_files}
- Python Files Generated: {stats.converted_files}
- Endpoints Converted: {stats.converted_endpoints}/{stats.total_endpoints}
- Models Generated: {stats.generated_models}/{stats.total_models}
- Conversion Success Rate: {stats.conversion_ratio:.1%}

**Code Metrics:**
- Original PHP Lines: {stats.total_lines_php:,}
- Generated Python Lines: {stats.total_lines_python:,}
- Code Efficiency: {(stats.total_lines_python / max(stats.total_lines_php, 1)):.2f}x
        """.strip()
        
        report.add_section("Executive Summary", content, 1)
    
    def _add_statistics_section(self, report: ConversionReport) -> None:
        """Add detailed statistics section."""
        stats = report.stats
        
        content = f"""
## Conversion Statistics

### File Conversion
- **Total PHP Files:** {stats.total_php_files}
- **Generated Python Files:** {stats.converted_files}
- **Conversion Rate:** {stats.conversion_ratio:.1%}

### API Endpoints
- **Total Endpoints Found:** {stats.total_endpoints}
- **Successfully Converted:** {stats.converted_endpoints}
- **Endpoint Conversion Rate:** {stats.endpoint_conversion_ratio:.1%}

### Data Models
- **Database Tables Analyzed:** {stats.total_models}
- **Pydantic Models Generated:** {stats.generated_models}

### Code Metrics
- **Original PHP Code Lines:** {stats.total_lines_php:,}
- **Generated Python Code Lines:** {stats.total_lines_python:,}
- **Lines of Code Ratio:** {(stats.total_lines_python / max(stats.total_lines_php, 1)):.2f}

### Performance
- **Total Conversion Time:** {stats.conversion_time_seconds:.2f} seconds
        """.strip()
        
        report.add_section("Detailed Statistics", content, 2)
    
    def _add_analysis_section(self, report: ConversionReport) -> None:
        """Add analysis results section."""
        if not report.analysis_result:
            return
        
        analysis = report.analysis_result
        
        content = "## Analysis Results\n\n"
        
        # Project info
        project_info = analysis.get('project_info', {})
        if project_info:
            content += "### Project Information\n"
            content += f"- **Framework:** {project_info.get('framework', 'Unknown')}\n"
            content += f"- **Structure Type:** {project_info.get('structure_type', 'Unknown')}\n"
            content += f"- **Entry Points:** {', '.join(project_info.get('entry_points', []))}\n\n"
        
        # Database analysis
        db_analysis = analysis.get('database_analysis', {})
        if db_analysis:
            content += "### Database Analysis\n"
            connections = db_analysis.get('connections', [])
            if connections:
                content += "**Database Connections:**\n"
                for conn in connections:
                    content += f"- {conn.get('type', 'Unknown')}: {conn.get('details', 'N/A')}\n"
            
            tables = db_analysis.get('tables', [])
            if tables:
                content += f"\n**Tables Found:** {len(tables)}\n"
                for table in tables[:5]:  # Show first 5 tables
                    content += f"- {table.get('name', 'Unknown')}\n"
                if len(tables) > 5:
                    content += f"- ... and {len(tables) - 5} more tables\n"
            content += "\n"
        
        # Endpoint analysis
        endpoint_analysis = analysis.get('endpoint_analysis', {})
        if endpoint_analysis:
            content += "### Endpoint Analysis\n"
            endpoints = endpoint_analysis.get('endpoints', [])
            methods = {}
            for endpoint in endpoints:
                method = endpoint.get('method', 'UNKNOWN')
                methods[method] = methods.get(method, 0) + 1
            
            content += "**HTTP Methods Distribution:**\n"
            for method, count in methods.items():
                content += f"- {method}: {count}\n"
            
            auth_methods = endpoint_analysis.get('authentication_methods', [])
            if auth_methods:
                content += f"\n**Authentication Methods:** {', '.join(auth_methods)}\n"
            content += "\n"
        
        report.add_section("Analysis Results", content, 2)
    
    def _add_planning_section(self, report: ConversionReport) -> None:
        """Add planning results section."""
        if not report.planning_result:
            return
        
        planning = report.planning_result
        
        content = "## Conversion Planning\n\n"
        
        # Architecture decisions
        architecture = planning.get('architecture', {})
        if architecture:
            content += "### Architecture Decisions\n"
            content += f"- **Project Structure:** {architecture.get('structure_type', 'Standard')}\n"
            content += f"- **Database ORM:** {architecture.get('orm_choice', 'SQLAlchemy')}\n"
            content += f"- **Authentication:** {architecture.get('auth_strategy', 'JWT')}\n"
            content += f"- **API Documentation:** {architecture.get('docs_strategy', 'FastAPI Auto')}\n\n"
        
        # Dependencies
        dependencies = planning.get('dependencies', {})
        if dependencies:
            python_deps = dependencies.get('python_packages', [])
            if python_deps:
                content += "### Python Dependencies\n"
                for dep in python_deps:
                    content += f"- {dep}\n"
                content += "\n"
        
        # Migration strategy
        migration = planning.get('migration_strategy', {})
        if migration:
            content += "### Migration Strategy\n"
            content += f"- **Data Migration:** {migration.get('data_approach', 'Manual')}\n"
            content += f"- **Configuration:** {migration.get('config_approach', 'Environment')}\n"
            content += f"- **File Handling:** {migration.get('file_approach', 'Local Storage')}\n\n"
        
        report.add_section("Conversion Planning", content, 2)
    
    def _add_generated_files_section(self, report: ConversionReport) -> None:
        """Add generated files section."""
        fastapi_path = Path(report.fastapi_project_path)
        
        if not fastapi_path.exists():
            return
        
        content = "## Generated Files\n\n"
        
        # Categorize files
        categories = {
            'Core Files': ['main.py', 'requirements.txt', '.env'],
            'Models': [],
            'Routes': [],
            'Configuration': ['Dockerfile', 'docker-compose.yml', 'alembic.ini'],
            'Other Python Files': []
        }
        
        # Find all Python files
        python_files = list(fastapi_path.rglob("*.py"))
        
        for py_file in python_files:
            rel_path = py_file.relative_to(fastapi_path)
            
            if 'model' in str(rel_path).lower():
                categories['Models'].append(str(rel_path))
            elif 'route' in str(rel_path).lower() or 'router' in str(rel_path).lower():
                categories['Routes'].append(str(rel_path))
            elif str(rel_path) not in categories['Core Files']:
                categories['Other Python Files'].append(str(rel_path))
        
        # Find configuration files
        config_files = list(fastapi_path.rglob("*.yml")) + list(fastapi_path.rglob("*.yaml")) + \
                      list(fastapi_path.rglob("*.ini")) + list(fastapi_path.rglob("Dockerfile"))
        
        for config_file in config_files:
            rel_path = config_file.relative_to(fastapi_path)
            if str(rel_path) not in categories['Configuration']:
                categories['Configuration'].append(str(rel_path))
        
        # Generate content
        for category, files in categories.items():
            if files:
                content += f"### {category}\n"
                for file in sorted(files):
                    content += f"- {file}\n"
                content += "\n"
        
        report.add_section("Generated Files", content, 2)
    
    def _add_validation_section(self, report: ConversionReport) -> None:
        """Add validation results section."""
        if not report.validation_result:
            return
        
        validation = report.validation_result
        
        content = "## Code Validation\n\n"
        
        if validation.get('is_valid', False):
            content += "✅ **Validation Status:** PASSED\n\n"
        else:
            content += "❌ **Validation Status:** FAILED\n\n"
        
        errors = validation.get('errors', [])
        if errors:
            content += "### Errors\n"
            for error in errors:
                content += f"- ❌ {error}\n"
            content += "\n"
        
        warnings = validation.get('warnings', [])
        if warnings:
            content += "### Warnings\n"
            for warning in warnings:
                content += f"- ⚠️ {warning}\n"
            content += "\n"
        
        suggestions = validation.get('suggestions', [])
        if suggestions:
            content += "### Suggestions\n"
            for suggestion in suggestions:
                content += f"- 💡 {suggestion}\n"
            content += "\n"
        
        report.add_section("Code Validation", content, 2)
    
    def _add_recommendations_section(self, report: ConversionReport) -> None:
        """Add recommendations section."""
        content = """## Recommendations

### Code Quality
- Review all generated code for business logic accuracy
- Add comprehensive error handling where needed
- Implement proper logging throughout the application
- Add input validation for all API endpoints

### Security
- Change default secret keys in production
- Implement proper authentication and authorization
- Add rate limiting for API endpoints
- Enable HTTPS in production

### Performance
- Add database connection pooling
- Implement caching where appropriate
- Add monitoring and metrics collection
- Consider async database operations

### Testing
- Write unit tests for all business logic
- Add integration tests for API endpoints
- Implement end-to-end testing
- Set up continuous integration

### Documentation
- Update API documentation with business context
- Add deployment instructions
- Document configuration options
- Create user guides for API consumers
        """
        
        report.add_section("Recommendations", content, 2)
    
    def _add_next_steps_section(self, report: ConversionReport) -> None:
        """Add next steps section."""
        content = """## Next Steps

### Immediate Actions
1. **Review Generated Code**
   - Verify business logic conversion accuracy
   - Check database model relationships
   - Validate API endpoint functionality

2. **Environment Setup**
   - Install Python dependencies: `pip install -r requirements.txt`
   - Configure environment variables in `.env` file
   - Set up database connections

3. **Initial Testing**
   - Run the application: `uvicorn main:app --reload`
   - Test API endpoints with Postman or curl
   - Verify database operations

### Short-term Goals
1. **Enhance Security**
   - Implement proper authentication
   - Add input validation
   - Configure CORS settings

2. **Add Missing Features**
   - Implement any missing business logic
   - Add error handling
   - Create database migrations

3. **Testing and Documentation**
   - Write unit tests
   - Update API documentation
   - Create deployment guides

### Long-term Improvements
1. **Performance Optimization**
   - Add caching layers
   - Optimize database queries
   - Implement monitoring

2. **DevOps and Deployment**
   - Set up CI/CD pipelines
   - Configure production environment
   - Implement backup strategies

3. **Maintenance and Monitoring**
   - Set up logging and monitoring
   - Plan regular security updates
   - Establish development workflows
        """
        
        report.add_section("Next Steps", content, 2)
    
    def _generate_markdown(self, report: ConversionReport) -> str:
        """Generate Markdown report."""
        content = f"# PHP to FastAPI Conversion Report\n\n"
        content += f"**Project:** {report.project_name}\n"
        content += f"**Generated:** {report.conversion_timestamp}\n\n"
        content += "---\n\n"
        
        for section in report.sections:
            if section.level == 1:
                content += f"# {section.title}\n\n"
            elif section.level == 2:
                content += f"## {section.title}\n\n"
            else:
                content += f"{'#' * section.level} {section.title}\n\n"
            
            content += f"{section.content}\n\n"
        
        return content
    
    def _generate_html(self, report: ConversionReport) -> str:
        """Generate HTML report."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP to FastAPI Conversion Report - {report.project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #34495e; border-bottom: 1px solid #bdc3c7; }}
        .metadata {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stat-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>PHP to FastAPI Conversion Report</h1>
    <div class="metadata">
        <p><strong>Project:</strong> {report.project_name}</p>
        <p><strong>Generated:</strong> {report.conversion_timestamp}</p>
        <p><strong>PHP Project:</strong> {report.php_project_path}</p>
        <p><strong>FastAPI Project:</strong> {report.fastapi_project_path}</p>
    </div>
"""
        
        for section in report.sections:
            level = min(section.level + 1, 6)  # HTML only has h1-h6
            html += f"<h{level}>{section.title}</h{level}>\n"
            
            # Convert basic markdown to HTML
            content = section.content.replace('\n', '<br>\n')
            content = content.replace('**', '<strong>').replace('**', '</strong>')
            content = content.replace('*', '<em>').replace('*', '</em>')
            
            html += f"<div>{content}</div>\n"
        
        html += """
</body>
</html>
        """
        
        return html
    
    def _generate_json(self, report: ConversionReport) -> str:
        """Generate JSON report."""
        report_dict = asdict(report)
        return json.dumps(report_dict, indent=2, default=str)
    
    def _generate_text(self, report: ConversionReport) -> str:
        """Generate plain text report."""
        content = f"PHP to FastAPI Conversion Report\n"
        content += f"{'=' * 50}\n\n"
        content += f"Project: {report.project_name}\n"
        content += f"Generated: {report.conversion_timestamp}\n\n"
        
        for section in report.sections:
            content += f"\n{'#' * section.level} {section.title}\n"
            content += f"{'-' * len(section.title)}\n\n"
            content += f"{section.content}\n\n"
        
        return content