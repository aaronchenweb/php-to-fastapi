# stages/analysis_stage.py
"""Stage 1: Analysis and Understanding of PHP project using modular analyzers."""

import os
import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from core.detector import PHPProjectDetector, PHPProjectInfo
from core.llm_client import LLMClient
from core.user_interface import UserInterface
from config.prompts import Prompts

# Import modular analyzers
from analyzers.php_parser import PHPParser
from analyzers.api_extractor import APIExtractor
from analyzers.dependency_mapper import DependencyMapper
from analyzers.structure_analyzer import StructureAnalyzer
from analyzers.database_analyzer import DatabaseAnalyzer


class AnalysisStage:
    """Handles the analysis stage of PHP to FastAPI conversion using modular analyzers."""
    
    def __init__(self, 
                 detector: PHPProjectDetector, 
                 llm_client: LLMClient, 
                 prompts: Prompts, 
                 ui: UserInterface):
        self.detector = detector
        self.llm_client = llm_client
        self.prompts = prompts
        self.ui = ui
        
        # Initialize modular analyzers
        self.php_parser = PHPParser()
        self.api_extractor = APIExtractor()
        self.dependency_mapper = DependencyMapper()
        self.structure_analyzer = StructureAnalyzer()
        self.database_analyzer = DatabaseAnalyzer()

    def perform_local_analysis(self, php_project_path: str) -> Optional[Dict[str, Any]]:
        """
        Perform local analysis of the PHP project using modular analyzers.
        
        Args:
            php_project_path: Path to the PHP project
            
        Returns:
            Dictionary containing analysis data, or None if analysis failed
        """
        try:
            self.ui.debug("Starting modular analysis...")
            
            # Get basic project information from detector
            project_info = self.detector.analyze_project(php_project_path)
            
            # 1. PHP Code Analysis
            self.ui.debug("Analyzing PHP code structure...")
            php_analysis = self._analyze_php_code(project_info.php_files)
            
            # 2. API Endpoint Analysis
            self.ui.debug("Extracting API endpoints...")
            api_analysis = self._analyze_api_endpoints(php_project_path)
            
            # 3. Database Analysis
            self.ui.debug("Analyzing database usage...")
            database_analysis = self._analyze_database_usage(php_project_path)
            
            # 4. Dependency Analysis
            self.ui.debug("Analyzing dependencies...")
            dependency_analysis = self._analyze_dependencies(php_project_path)
            
            # 5. Structure Analysis
            self.ui.debug("Analyzing project structure...")
            structure_analysis = self._analyze_project_structure(php_project_path)
            
            # Compile complete analysis in format expected by LLM
            analysis_data = {
                'project_info': {
                    'root_path': project_info.root_path,
                    'framework': project_info.framework,
                    'php_version': project_info.php_version,
                    'total_php_files': len(project_info.php_files),
                    'total_api_files': len(project_info.api_files),
                    'entry_points': project_info.entry_points,
                    'config_files': project_info.config_files,
                    'database_configs': project_info.database_configs
                },
                'php_code_analysis': php_analysis,
                'api_analysis': api_analysis,
                'database_analysis': database_analysis,
                'dependency_analysis': dependency_analysis,
                'structure_analysis': structure_analysis,
                'summary_metrics': self._generate_summary_metrics(
                    php_analysis, api_analysis, database_analysis, 
                    dependency_analysis, structure_analysis
                )
            }
            
            self.ui.debug(f"Local analysis completed successfully")
            return analysis_data
            
        except Exception as e:
            self.ui.error(f"Local analysis failed: {str(e)}")
            import traceback
            self.ui.debug(f"Traceback: {traceback.format_exc()}")
            return None
    
    def display_local_analysis_results(self, local_analysis: Dict[str, Any]) -> None:
        """Display local analysis results to the user before sending to LLM."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("📊 LOCAL ANALYSIS RESULTS (Before LLM Enhancement)")
        self.ui.info("=" * 80)
        
        # Display project info
        project_info = local_analysis.get('project_info', {})
        self.ui.info(f"🏗️  Project Framework: {project_info.get('framework', 'Unknown')}")
        self.ui.info(f"🐘 PHP Version: {project_info.get('php_version', 'Unknown')}")
        self.ui.info(f"📁 Total PHP Files: {project_info.get('total_php_files', 0)}")
        self.ui.info(f"🔗 API Files: {project_info.get('total_api_files', 0)}")
        
        # Display PHP code analysis
        php_analysis = local_analysis.get('php_code_analysis', {})
        self.ui.info(f"\n📝 CODE ANALYSIS:")
        self.ui.info(f"   • Classes: {php_analysis.get('code_metrics', {}).get('total_classes', 0)}")
        self.ui.info(f"   • Functions: {php_analysis.get('code_metrics', {}).get('total_functions', 0)}")
        self.ui.info(f"   • Methods: {php_analysis.get('code_metrics', {}).get('total_methods', 0)}")
        self.ui.info(f"   • Complexity: {php_analysis.get('complexity_level', 'Unknown')}")
        
        # Display language features
        lang_features = php_analysis.get('language_features', {})
        features_found = [k for k, v in lang_features.items() if v]
        if features_found:
            self.ui.info(f"   • PHP Features: {', '.join(features_found)}")
        
        # Display API analysis
        api_analysis = local_analysis.get('api_analysis', {})
        self.ui.info(f"\n🌐 API ANALYSIS:")
        self.ui.info(f"   • Total Endpoints: {api_analysis.get('total_endpoints', 0)}")
        self.ui.info(f"   • HTTP Methods: {', '.join(api_analysis.get('http_methods_used', []))}")
        self.ui.info(f"   • Auth Methods: {', '.join(api_analysis.get('authentication_methods', []))}")
        self.ui.info(f"   • Complexity: {api_analysis.get('complexity_level', 'Unknown')}")
        
        # Display endpoint categories
        categories = api_analysis.get('endpoint_categories', [])
        if categories:
            self.ui.info(f"   • Categories:")
            for cat in categories[:5]:  # Show first 5 categories
                self.ui.info(f"     - {cat.get('category', 'Unknown')}: {len(cat.get('endpoints', []))} endpoints")
        
        # Display database analysis
        db_analysis = local_analysis.get('database_analysis', {})
        self.ui.info(f"\n🗄️  DATABASE ANALYSIS:")
        self.ui.info(f"   • Database Type: {db_analysis.get('database_type', 'Unknown')}")
        self.ui.info(f"   • ORM Framework: {db_analysis.get('orm_framework', 'None')}")
        self.ui.info(f"   • Tables Found: {db_analysis.get('tables_estimated', 0)}")
        self.ui.info(f"   • Complexity: {db_analysis.get('relationships_complexity', 'Unknown')}")
        
        # Display query patterns
        query_patterns = db_analysis.get('query_patterns', {})
        if any(query_patterns.values()):
            self.ui.info(f"   • Query Types:")
            for query_type, count in query_patterns.items():
                if count > 0:
                    self.ui.info(f"     - {query_type}: {count}")
        
        # Display dependency analysis
        dep_analysis = local_analysis.get('dependency_analysis', {})
        self.ui.info(f"\n📦 DEPENDENCY ANALYSIS:")
        self.ui.info(f"   • Total Dependencies: {dep_analysis.get('total_dependencies', 0)}")
        self.ui.info(f"   • Migration Complexity: {dep_analysis.get('migration_complexity', 'Unknown')}")
        self.ui.info(f"   • Unmapped Dependencies: {len(dep_analysis.get('unmapped_dependencies', []))}")
        
        # Show some Python equivalents
        python_equiv = dep_analysis.get('python_equivalents', {})
        if python_equiv:
            self.ui.info(f"   • Key Mappings (first 3):")
            for i, (php_pkg, py_pkg) in enumerate(list(python_equiv.items())[:3]):
                self.ui.info(f"     - {php_pkg} → {py_pkg}")
        
        # Display structure analysis
        struct_analysis = local_analysis.get('structure_analysis', {})
        self.ui.info(f"\n🏗️  STRUCTURE ANALYSIS:")
        self.ui.info(f"   • Organization: {struct_analysis.get('organization_pattern', 'Unknown')}")
        self.ui.info(f"   • Architecture Score: {struct_analysis.get('architecture_score', 0):.1f}/10")
        self.ui.info(f"   • Separation Quality: {struct_analysis.get('separation_of_concerns', 'Unknown')}")
        self.ui.info(f"   • Entry Points: {len(struct_analysis.get('entry_points', []))}")
        
        # Display summary metrics
        summary = local_analysis.get('summary_metrics', {})
        self.ui.info(f"\n📈 SUMMARY METRICS:")
        self.ui.info(f"   • Overall Complexity: {summary.get('overall_complexity', 'Unknown')}")
        self.ui.info(f"   • Migration Readiness: {summary.get('migration_readiness', 'Unknown')}")
        self.ui.info(f"   • Estimated Effort: {summary.get('estimated_effort', 'Unknown')}")
        
        # Display risk factors
        risks = summary.get('risk_factors', [])
        if risks:
            self.ui.info(f"   • Risk Factors:")
            for risk in risks[:3]:  # Show first 3 risks
                self.ui.info(f"     - {risk}")
        
        self.ui.info("=" * 80)

    
    def get_llm_analysis(self, local_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send local analysis to LLM for deeper understanding and insights.
        
        Args:
            local_analysis: Results from local analysis
            
        Returns:
            LLM analysis results, or None if failed
        """
        try:
            # Display local results first
            self.display_local_analysis_results(local_analysis)
            
            # Ask user if they want to proceed to LLM analysis
            if not self.ui.confirm("📤 Send local analysis to LLM for enhancement?", default=True):
                self.ui.warning("LLM analysis skipped by user.")
                return self._convert_local_to_llm_format(local_analysis)
            
            # Get system prompt
            system_prompt = self.prompts.get_system_prompt()
            
            # Get analysis prompt with local data
            user_prompt = self.prompts.get_analysis_prompt(local_analysis)
            
            # Send to LLM
            self.ui.debug("Sending analysis request to LLM...")
            response = self.llm_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            if not response.success:
                self.ui.show_llm_error(response.error_message, "analysis")
                self.ui.warning("Using local analysis results only.")
                return self._convert_local_to_llm_format(local_analysis)
            
            # Parse JSON response
            llm_analysis = self.llm_client.parse_json_response(response)
            
            # Display LLM results and comparison
            self.display_llm_analysis_results(llm_analysis)
            self.display_analysis_comparison(local_analysis, llm_analysis)
            
            self.ui.debug("LLM analysis completed successfully")
            return llm_analysis
            
        except Exception as e:
            self.ui.error(f"LLM analysis failed: {str(e)}")
            self.ui.warning("Using local analysis results only.")
            return self._convert_local_to_llm_format(local_analysis)
    
    def display_llm_analysis_results(self, llm_analysis: Dict[str, Any]) -> None:
        """Display LLM analysis results."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("🤖 LLM ENHANCED ANALYSIS RESULTS")
        self.ui.info("=" * 80)
        
        # Display project summary
        project_summary = llm_analysis.get('project_summary', {})
        self.ui.info(f"🏗️  PROJECT SUMMARY:")
        self.ui.info(f"   • Framework: {project_summary.get('framework_detected', 'Unknown')}")
        self.ui.info(f"   • PHP Version: {project_summary.get('php_version_estimated', 'Unknown')}")
        self.ui.info(f"   • Architecture: {project_summary.get('architecture_pattern', 'Unknown')}")
        self.ui.info(f"   • Complexity: {project_summary.get('complexity_level', 'Unknown')}")
        self.ui.info(f"   • API Type: {project_summary.get('api_type', 'Unknown')}")
        
        # Display endpoints analysis
        endpoints = llm_analysis.get('endpoints_analysis', {})
        self.ui.info(f"\n🌐 ENDPOINTS ANALYSIS:")
        self.ui.info(f"   • Total Endpoints: {endpoints.get('total_endpoints', 0)}")
        self.ui.info(f"   • HTTP Methods: {', '.join(endpoints.get('http_methods_used', []))}")
        self.ui.info(f"   • Auth Methods: {', '.join(endpoints.get('authentication_methods', []))}")
        
        # Display database analysis
        database = llm_analysis.get('database_analysis', {})
        self.ui.info(f"\n🗄️  DATABASE ANALYSIS:")
        self.ui.info(f"   • Database Type: {database.get('database_type', 'Unknown')}")
        self.ui.info(f"   • ORM Framework: {database.get('orm_framework', 'Unknown')}")
        self.ui.info(f"   • Tables Estimated: {database.get('tables_estimated', 0)}")
        self.ui.info(f"   • Complexity: {database.get('relationships_complexity', 'Unknown')}")
        
        # Display architecture insights
        insights = llm_analysis.get('architecture_insights', {})
        if insights:
            self.ui.info(f"\n🔍 ARCHITECTURE INSIGHTS:")
            patterns = insights.get('design_patterns_used', [])
            if patterns:
                self.ui.info(f"   • Patterns: {', '.join(patterns)}")
            
            issues = insights.get('potential_issues', [])
            if issues:
                self.ui.info(f"   • Potential Issues:")
                for issue in issues[:3]:
                    self.ui.info(f"     - {issue}")
        
        # Display recommendations
        recommendations = llm_analysis.get('recommendations', {})
        if recommendations:
            self.ui.info(f"\n💡 RECOMMENDATIONS:")
            structure = recommendations.get('suggested_fastapi_structure', 'Standard')
            self.ui.info(f"   • FastAPI Structure: {structure}")
            
            priorities = recommendations.get('key_conversion_priorities', [])
            if priorities:
                self.ui.info(f"   • Conversion Priorities:")
                for priority in priorities[:3]:
                    self.ui.info(f"     - {priority}")
        
        self.ui.info("=" * 80)
    
    def display_analysis_comparison(self, local_analysis: Dict[str, Any], llm_analysis: Dict[str, Any]) -> None:
        """Display comparison between local and LLM analysis."""
        self.ui.info("\n" + "=" * 80)
        self.ui.info("🔍 LOCAL vs LLM ANALYSIS COMPARISON")
        self.ui.info("=" * 80)
        
        # Compare complexity assessments
        local_complexity = local_analysis.get('summary_metrics', {}).get('overall_complexity', 'Unknown')
        llm_complexity = llm_analysis.get('project_summary', {}).get('complexity_level', 'Unknown')
        
        self.ui.info(f"📊 COMPLEXITY ASSESSMENT:")
        self.ui.info(f"   • Local Analysis:  {local_complexity}")
        self.ui.info(f"   • LLM Analysis:    {llm_complexity}")
        if local_complexity != llm_complexity:
            self.ui.warning(f"   ⚠️  Complexity assessment differs!")
        
        # Compare endpoint counts
        local_endpoints = local_analysis.get('api_analysis', {}).get('total_endpoints', 0)
        llm_endpoints = llm_analysis.get('endpoints_analysis', {}).get('total_endpoints', 0)
        
        self.ui.info(f"\n🌐 ENDPOINT DETECTION:")
        self.ui.info(f"   • Local Found:     {local_endpoints}")
        self.ui.info(f"   • LLM Confirmed:   {llm_endpoints}")
        if abs(local_endpoints - llm_endpoints) > 0:
            diff = llm_endpoints - local_endpoints
            self.ui.warning(f"   ⚠️  Difference: {diff:+d} endpoints")
        
        # Compare database detection
        local_db = local_analysis.get('database_analysis', {}).get('database_type', 'Unknown')
        llm_db = llm_analysis.get('database_analysis', {}).get('database_type', 'Unknown')
        
        self.ui.info(f"\n🗄️  DATABASE DETECTION:")
        self.ui.info(f"   • Local Detected:  {local_db}")
        self.ui.info(f"   • LLM Confirmed:   {llm_db}")
        if local_db != llm_db:
            self.ui.warning(f"   ⚠️  Database type differs!")
        
        # Show what LLM added
        self.ui.info(f"\n💡 LLM ENHANCEMENTS:")
        
        # Architecture insights (LLM only)
        insights = llm_analysis.get('architecture_insights', {})
        if insights:
            patterns = insights.get('design_patterns_used', [])
            if patterns:
                self.ui.info(f"   • Design Patterns Identified: {', '.join(patterns)}")
            
            issues = insights.get('potential_issues', [])
            if issues:
                self.ui.info(f"   • Issues Identified: {len(issues)} potential concerns")
        
        # Recommendations (LLM only)
        recommendations = llm_analysis.get('recommendations', {})
        if recommendations:
            priorities = recommendations.get('key_conversion_priorities', [])
            self.ui.info(f"   • Conversion Priorities: {len(priorities)} recommendations")
        
        self.ui.info("=" * 80)
        
        # Ask user if they want to see detailed differences
        if self.ui.verbose and self.ui.confirm("🔍 Show detailed JSON comparison?", default=False):
            self._show_detailed_json_comparison(local_analysis, llm_analysis)
    
    def _show_detailed_json_comparison(self, local_analysis: Dict[str, Any], llm_analysis: Dict[str, Any]) -> None:
        """Show detailed JSON comparison for debugging."""
        self.ui.info("\n" + "-" * 80)
        self.ui.info("📋 DETAILED JSON COMPARISON (for debugging)")
        self.ui.info("-" * 80)
        
        self.ui.info("\n🔧 LOCAL ANALYSIS JSON:")
        self.ui.info(json.dumps(local_analysis, indent=2, default=str)[:1000] + "...")
        
        self.ui.info("\n🤖 LLM ANALYSIS JSON:")
        self.ui.info(json.dumps(llm_analysis, indent=2, default=str)[:1000] + "...")
        
        self.ui.info("-" * 80)

    def _convert_local_to_llm_format(self, local_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Convert local analysis to LLM-expected format when LLM is skipped."""
        return {
            'project_summary': {
                'framework_detected': local_analysis.get('project_info', {}).get('framework', 'unknown'),
                'php_version_estimated': local_analysis.get('project_info', {}).get('php_version', 'unknown'),
                'architecture_pattern': local_analysis.get('structure_analysis', {}).get('organization_pattern', 'unknown'),
                'complexity_level': local_analysis.get('summary_metrics', {}).get('overall_complexity', 'unknown'),
                'api_type': 'rest'  # Default assumption
            },
            'endpoints_analysis': {
                'total_endpoints': local_analysis.get('api_analysis', {}).get('total_endpoints', 0),
                'http_methods_used': local_analysis.get('api_analysis', {}).get('http_methods_used', []),
                'authentication_methods': local_analysis.get('api_analysis', {}).get('authentication_methods', []),
                'endpoint_categories': local_analysis.get('api_analysis', {}).get('endpoint_categories', [])
            },
            'database_analysis': {
                'database_type': local_analysis.get('database_analysis', {}).get('database_type', 'unknown'),
                'orm_framework': local_analysis.get('database_analysis', {}).get('orm_framework', 'none'),
                'tables_estimated': local_analysis.get('database_analysis', {}).get('tables_estimated', 0),
                'relationships_complexity': local_analysis.get('database_analysis', {}).get('relationships_complexity', 'low')
            },
            'dependencies_analysis': {
                'critical_dependencies': local_analysis.get('dependency_analysis', {}).get('critical_dependencies', []),
                'python_equivalents': local_analysis.get('dependency_analysis', {}).get('python_equivalents', {}),
                'migration_complexity': local_analysis.get('dependency_analysis', {}).get('migration_complexity', 'low')
            },
            'architecture_insights': {
                'design_patterns_used': ['mvc'],  # Default assumption
                'code_organization': local_analysis.get('structure_analysis', {}).get('separation_of_concerns', 'fair'),
                'separation_of_concerns': local_analysis.get('structure_analysis', {}).get('separation_of_concerns', 'fair'),
                'potential_issues': local_analysis.get('summary_metrics', {}).get('risk_factors', []),
                'conversion_challenges': []
            },
            'recommendations': {
                'suggested_fastapi_structure': 'standard',
                'key_conversion_priorities': ['Setup project structure', 'Convert API endpoints', 'Migrate database'],
                'estimated_conversion_effort': local_analysis.get('summary_metrics', {}).get('estimated_effort', 'medium'),
                'recommended_python_packages': ['fastapi', 'uvicorn', 'pydantic', 'sqlalchemy']
            }
        }

    def _analyze_php_code(self, php_files: List[str]) -> Dict[str, Any]:
        """Analyze PHP code using PHPParser."""
        try:
            # Parse PHP files
            parsed_files = []
            for file_path in php_files[:100]:  # Limit for performance
                parsed_file = self.php_parser.parse_file(file_path)
                if parsed_file:
                    parsed_files.append(parsed_file)
            
            # Get analysis summary
            parser_summary = self.php_parser.get_analysis_summary(parsed_files)
            
            # Transform to expected format
            analysis = {
                'total_files': len(parsed_files),
                'parsed_files': len(parsed_files),
                'code_metrics': {
                    'total_lines': 0,  # PHPParser doesn't track this directly
                    'total_functions': parser_summary['total_functions'],
                    'total_classes': parser_summary['total_classes'],
                    'total_methods': parser_summary['total_methods'],
                    'average_methods_per_class': parser_summary['complexity_metrics']['avg_methods_per_class'],
                    'max_class_methods': parser_summary['complexity_metrics']['max_class_methods']
                },
                'language_features': {
                    'namespaces_used': 'namespaces' in parser_summary['php_features'],
                    'traits_used': 'traits' in parser_summary['php_features'],
                    'interfaces_used': any('interface' in str(cls.implements) for file in parsed_files for cls in file.classes),
                    'abstract_classes_used': any(cls.is_abstract for file in parsed_files for cls in file.classes),
                    'static_methods_used': any(method.is_static for file in parsed_files for cls in file.classes for method in cls.methods)
                },
                'php_version_features': list(parser_summary['php_features']),
                'namespaces': parser_summary['namespaces'],
                'file_types': parser_summary['file_types'],
                'complexity_level': self._calculate_code_complexity(parser_summary)
            }
            
            return analysis
            
        except Exception as e:
            self.ui.error(f"PHP code analysis failed: {str(e)}")
            return {'error': str(e), 'total_files': 0}
    
    
    def _analyze_api_endpoints(self, project_path: str) -> Dict[str, Any]:
        """Analyze API endpoints using APIExtractor with enhanced detection."""
        try:
            # Extract endpoints from directory
            endpoints = self.api_extractor.extract_from_directory(project_path)
            self.ui.debug(f"Found {len(endpoints)} raw endpoints")
            
            # ADDITIONAL: Check specific router setup files
            router_files = []
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['vendor', 'node_modules', '.git']]
                for file in files:
                    if file.endswith('.php'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # Look for router setup patterns
                            if any(pattern in content.lower() for pattern in [
                                '$this->router->', 'setuproutes', 'addroute', 'router->get', 'router->post'
                            ]):
                                router_files.append(file_path)
                                self.ui.debug(f"Found router setup in: {file_path}")
                                
                                # Extract additional endpoints from this file
                                additional_endpoints = self.api_extractor.extract_from_file(file_path)
                                endpoints.extend(additional_endpoints)
                                
                        except Exception as e:
                            continue
            
            self.ui.debug(f"Total endpoints after enhanced detection: {len(endpoints)}")
            
            # Analyze endpoints (MUST USE THIS RESULT)
            endpoint_analysis = self.api_extractor.analyze_endpoints(endpoints)
            self.ui.debug(f"Endpoint analysis: {endpoint_analysis.get('total_endpoints', 0)} endpoints")
            
            # Group endpoints (MUST USE THIS RESULT)
            endpoint_groups = self.api_extractor.group_endpoints(endpoints)
            self.ui.debug(f"Created {len(endpoint_groups)} endpoint groups")
            
            # Enhanced HTTP methods detection
            http_methods_used = list(endpoint_analysis.get('http_methods', {}).keys())
            if not http_methods_used and endpoints:
                # Fallback: extract directly from endpoints
                http_methods_used = list(set(ep.method.upper() for ep in endpoints if ep.method))
            
            # Build comprehensive categories
            endpoint_categories = []
            
            # Add categories from groups
            for group in endpoint_groups:
                if group.endpoints:
                    endpoint_categories.append({
                        'category': group.name,
                        'endpoints': [f"{ep.method} {ep.route}" for ep in group.endpoints],
                        'complexity': self._assess_endpoint_group_complexity(group)
                    })
            
            # Add method-based categories
            for method, count in endpoint_analysis.get('http_methods', {}).items():
                if count > 0:
                    method_endpoints = [ep for ep in endpoints if ep.method.upper() == method.upper()]
                    endpoint_categories.append({
                        'category': f'{method.lower()}_endpoints',
                        'endpoints': [f"{ep.method} {ep.route}" for ep in method_endpoints],
                        'complexity': self._assess_endpoint_group_complexity_by_count(count)
                    })
            
            # Enhanced authentication detection
            auth_methods = []
            auth_count = endpoint_analysis.get('authentication_required', 0)
            if auth_count > 0:
                auth_methods.append('required')
            
            # Check for authentication patterns in the codebase
            auth_patterns_found = []
            for file_path in router_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if any(pattern in content.lower() for pattern in ['auth', 'jwt', 'token', 'middleware']):
                        auth_patterns_found.append('middleware_based')
                except:
                    continue
            
            if auth_patterns_found:
                auth_methods.extend(auth_patterns_found)
            if not auth_methods:
                auth_methods = ['none']
            
            # Return comprehensive analysis
            analysis = {
                'total_endpoints': len(endpoints),  # Use actual count
                'http_methods_used': http_methods_used,
                'authentication_methods': list(set(auth_methods)),
                'endpoint_categories': endpoint_categories,
                'endpoints_detail': [
                    {
                        'method': ep.method,
                        'route': ep.route,
                        'handler': ep.handler,
                        'file_path': ep.file_path,
                        'parameters': ep.parameters,
                        'middleware': ep.middleware,
                        'authentication': ep.authentication,
                        'response_format': ep.response_format
                    }
                    for ep in endpoints
                ],
                'complexity_score': endpoint_analysis.get('complexity_score', len(endpoints) * 0.5),
                'complexity_level': 'low' if len(endpoints) <= 5 else 'medium' if len(endpoints) <= 15 else 'high',
                'response_formats': endpoint_analysis.get('response_formats', {}),
                'parameter_statistics': endpoint_analysis.get('parameters', {}),
                'middleware_usage': endpoint_analysis.get('middleware_usage', {}),
                'file_distribution': endpoint_analysis.get('file_distribution', {}),
                'router_files_found': len(router_files)
            }
            
            self.ui.debug(f"Final API analysis: {analysis['total_endpoints']} endpoints, methods: {http_methods_used}")
            return analysis
            
        except Exception as e:
            self.ui.error(f"API endpoint analysis failed: {str(e)}")
            import traceback
            self.ui.debug(f"Traceback: {traceback.format_exc()}")
            return {'error': str(e), 'total_endpoints': 0, 'http_methods_used': []}

    def _assess_endpoint_group_complexity_by_count(self, count: int) -> str:
        """Assess complexity based on endpoint count."""
        if count <= 2:
            return 'low'
        elif count <= 5:
            return 'medium'
        else:
            return 'high'

    
    def _analyze_database_usage(self, project_path: str) -> Dict[str, Any]:
        """Analyze database usage using DatabaseAnalyzer with improved detection."""
        try:
            # FORCE database detection by checking all PHP files directly
            php_files = []
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['vendor', 'node_modules', '.git']]
                for file in files:
                    if file.endswith(('.php', '.phtml', '.inc')):
                        php_files.append(os.path.join(root, file))
            
            # Check each PHP file for database patterns
            detected_db_type = "unknown"
            connection_info = {}
            
            for php_file in php_files:
                try:
                    with open(php_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Direct pattern matching for your code structure
                    if 'mysql:' in content.lower():
                        detected_db_type = "mysql"
                        self.ui.debug(f"Found MySQL reference in {php_file}")
                        
                        # Extract connection details
                        db_name_match = re.search(r'\$dbname\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                        if db_name_match:
                            connection_info['database'] = db_name_match.group(1)
                        
                        host_match = re.search(r'\$host\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                        if host_match:
                            connection_info['host'] = host_match.group(1)
                        
                        user_match = re.search(r'\$username\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                        if user_match:
                            connection_info['username'] = user_match.group(1)
                        
                        break
                    elif 'pgsql:' in content.lower():
                        detected_db_type = "postgresql"
                        break
                    elif 'sqlite:' in content.lower():
                        detected_db_type = "sqlite"
                        break
                        
                except Exception as e:
                    self.ui.debug(f"Error reading {php_file}: {e}")
                    continue
            
            # Perform database analysis using DatabaseAnalyzer
            db_analysis = self.database_analyzer.analyze_database_usage(project_path)
            
            # Override the database type if we detected it manually
            if detected_db_type != "unknown":
                # Update the connection type in the analysis
                for conn in db_analysis.connections:
                    conn.type = detected_db_type
                    conn.host = connection_info.get('host', conn.host)
                    conn.database = connection_info.get('database', conn.database)
                    conn.username = connection_info.get('username', conn.username)
            
            # If no connections found, create one from our detection
            if not db_analysis.connections and detected_db_type != "unknown":
                from analyzers.database_analyzer import DatabaseConnection
                connection = DatabaseConnection(
                    name=f"{detected_db_type}_detected",
                    type=detected_db_type,
                    host=connection_info.get('host', 'localhost'),
                    database=connection_info.get('database', 'unknown'),
                    username=connection_info.get('username', 'root'),
                    file_path=php_files[0] if php_files else ""
                )
                db_analysis.connections.append(connection)
            
            # Transform to expected format
            analysis = {
                'database_type': detected_db_type,  # Use our detected type
                'orm_framework': db_analysis.orm_framework or 'none',
                'connection_patterns': [
                    f"{conn.type}://{conn.host or 'localhost'}:{conn.port or 3306}/{conn.database or 'unknown'}" 
                    for conn in db_analysis.connections
                ],
                'table_references': [table.name for table in db_analysis.tables],
                'tables_estimated': len(db_analysis.tables),
                'migration_files': db_analysis.migration_files,
                'query_patterns': {
                    'raw_sql': len([q for q in db_analysis.queries if q.query_type == 'raw_sql']),
                    'prepared_statements': len([q for q in db_analysis.queries if q.query_type == 'pdo']),
                    'orm_queries': len([q for q in db_analysis.queries if q.query_type == 'eloquent'])
                },
                'relationships_complexity': db_analysis.complexity_metrics.get('complexity_level', 'low'),
                'migration_challenges': db_analysis.recommendations[:3],
                'models_detected': [
                    {'table': table.name, 'model_class': table.model_class}
                    for table in db_analysis.tables if table.model_class
                ]
            }
            
            self.ui.debug(f"Database analysis completed: type={detected_db_type}")
            return analysis
            
        except Exception as e:
            self.ui.error(f"Database analysis failed: {str(e)}")
            return {'error': str(e), 'database_type': 'unknown'}
    
    def _analyze_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Analyze dependencies using DependencyMapper."""
        try:
            # Check for composer.json
            composer_path = os.path.join(project_path, 'composer.json')
            
            if os.path.exists(composer_path):
                dep_analysis = self.dependency_mapper.analyze_composer_json(composer_path)
            else:
                # Create empty analysis if no composer.json
                from analyzers.dependency_mapper import DependencyAnalysis
                dep_analysis = DependencyAnalysis(
                    total_dependencies=0,
                    mapped_dependencies=[],
                    unmapped_dependencies=[],
                    framework_dependencies=[],
                    development_dependencies=[],
                    complexity_score=0.0,
                    migration_recommendations=[]
                )
            
            # Analyze code dependencies
            php_files = []
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['vendor', 'node_modules', '.git']]
                for file in files:
                    if file.endswith(('.php', '.phtml')):
                        php_files.append(os.path.join(root, file))
            
            implicit_deps = self.dependency_mapper.analyze_code_dependencies(php_files[:50])
            
            # Transform to expected format
            analysis = {
                'total_dependencies': dep_analysis.total_dependencies,
                'critical_dependencies': [dep.php_package for dep in dep_analysis.mapped_dependencies if dep.migration_complexity == 'high'],
                'python_equivalents': {
                    dep.php_package: dep.python_package 
                    for dep in dep_analysis.mapped_dependencies
                },
                'migration_complexity': self.dependency_mapper._get_complexity_level(dep_analysis.complexity_score),
                'framework_dependencies': dep_analysis.framework_dependencies,
                'unmapped_dependencies': dep_analysis.unmapped_dependencies,
                'implicit_dependencies': implicit_deps,
                'migration_effort': self.dependency_mapper._estimate_migration_effort(dep_analysis),
                'recommendations': dep_analysis.migration_recommendations
            }
            
            return analysis
            
        except Exception as e:
            self.ui.error(f"Dependency analysis failed: {str(e)}")
            return {'error': str(e), 'total_dependencies': 0}
    
    def _analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project structure using StructureAnalyzer."""
        try:
            # Perform structure analysis
            struct_analysis = self.structure_analyzer.analyze_structure(project_path)
            
            # Transform to expected format
            analysis = {
                'directory_structure': [d.path for d in struct_analysis.directories if d.path],
                'organization_pattern': struct_analysis.organization_pattern,
                'separation_of_concerns': struct_analysis.separation_quality,
                'configuration_approach': self._determine_config_approach(struct_analysis.config_files),
                'framework_type': struct_analysis.framework_type,
                'entry_points': struct_analysis.entry_points,
                'architecture_score': struct_analysis.architecture_score,
                'complexity_indicators': struct_analysis.complexity_indicators,
                'fastapi_mapping': self.structure_analyzer.get_fastapi_structure_mapping(struct_analysis),
                'recommendations': struct_analysis.recommendations
            }
            
            return analysis
            
        except Exception as e:
            self.ui.error(f"Structure analysis failed: {str(e)}")
            return {'error': str(e), 'organization_pattern': 'unknown'}
    
    def _generate_summary_metrics(self, 
                                 php_analysis: Dict[str, Any], 
                                 api_analysis: Dict[str, Any], 
                                 database_analysis: Dict[str, Any], 
                                 dependency_analysis: Dict[str, Any], 
                                 structure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall summary metrics."""
        return {
            'overall_complexity': self._calculate_overall_complexity(
                php_analysis, api_analysis, database_analysis, dependency_analysis, structure_analysis
            ),
            'migration_readiness': self._assess_migration_readiness(
                php_analysis, api_analysis, database_analysis, dependency_analysis, structure_analysis
            ),
            'estimated_effort': self._estimate_conversion_effort(
                php_analysis, api_analysis, database_analysis, dependency_analysis, structure_analysis
            ),
            'risk_factors': self._identify_risk_factors(
                php_analysis, api_analysis, database_analysis, dependency_analysis, structure_analysis
            )
        }
    
    # Helper methods
    def _calculate_code_complexity(self, parser_summary: Dict[str, Any]) -> str:
        """Calculate code complexity level."""
        factors = [
            parser_summary['total_classes'] > 20,
            parser_summary['total_functions'] > 50,
            parser_summary['complexity_metrics']['avg_methods_per_class'] > 10,
            len(parser_summary['php_features']) > 5
        ]
        
        complexity_score = sum(factors)
        if complexity_score <= 1:
            return 'low'
        elif complexity_score <= 2:
            return 'medium'
        else:
            return 'high'
    
    def _extract_auth_methods(self, endpoints) -> List[str]:
        """Extract authentication methods from endpoints."""
        auth_methods = set()
        
        for endpoint in endpoints:
            if endpoint.authentication:
                if endpoint.authentication == "required":
                    auth_methods.add("required")
                else:
                    auth_methods.add(endpoint.authentication)
            
            # Check middleware for auth indicators
            for middleware in endpoint.middleware:
                if any(auth_term in middleware.lower() for auth_term in ['auth', 'jwt', 'token']):
                    auth_methods.add('middleware_auth')
            
            # Check handler context for auth calls
            if 'authenticate' in endpoint.handler.lower():
                auth_methods.add('required')
        
        # If no specific auth found but we detect Auth::authenticate pattern, mark as required
        if not auth_methods:
            # Check if any endpoint handlers suggest authentication
            has_auth_pattern = any('auth' in ep.handler.lower() or ep.authentication for ep in endpoints)
            if has_auth_pattern:
                auth_methods.add('required')
        
        return list(auth_methods) if auth_methods else ['none']
    
    def _assess_endpoint_group_complexity(self, group) -> str:
        """Assess complexity of an endpoint group."""
        endpoint_count = len(group.endpoints)
        if endpoint_count <= 3:
            return 'low'
        elif endpoint_count <= 8:
            return 'medium'
        else:
            return 'high'
    
    def _determine_primary_db_type(self, connections) -> str:
        """Determine primary database type."""
        if not connections:
            return 'unknown'
        
        # Count connection types
        type_counts = {}
        for conn in connections:
            type_counts[conn.type] = type_counts.get(conn.type, 0) + 1
        
        # Return most common type
        return max(type_counts, key=type_counts.get) if type_counts else 'unknown'
    
    def _determine_config_approach(self, config_files: List[str]) -> str:
        """Determine configuration approach."""
        if not config_files:
            return 'none'
        
        has_env = any('.env' in f for f in config_files)
        config_count = len(config_files)
        
        if has_env:
            return 'environment_based'
        elif config_count > 5:
            return 'multiple_files'
        else:
            return 'single_file'
    
    def _calculate_overall_complexity(self, *analyses) -> str:
        """Calculate overall project complexity."""
        complexity_scores = []
        
        for analysis in analyses:
            if 'complexity_level' in analysis:
                level = analysis['complexity_level']
                if level == 'high':
                    complexity_scores.append(3)
                elif level == 'medium':
                    complexity_scores.append(2)
                else:
                    complexity_scores.append(1)
        
        if not complexity_scores:
            return 'unknown'
        
        avg_score = sum(complexity_scores) / len(complexity_scores)
        if avg_score >= 2.5:
            return 'high'
        elif avg_score >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _assess_migration_readiness(self, *analyses) -> str:
        """Assess how ready the project is for migration."""
        readiness_factors = []
        
        # Check structure quality
        structure_analysis = analyses[4] if len(analyses) > 4 else {}
        if structure_analysis.get('architecture_score', 0) >= 7:
            readiness_factors.append(True)
        else:
            readiness_factors.append(False)
        
        # Check dependency mappability
        dependency_analysis = analyses[3] if len(analyses) > 3 else {}
        mapped_ratio = 1.0  # Default if no deps
        if dependency_analysis.get('total_dependencies', 0) > 0:
            mapped_count = len(dependency_analysis.get('python_equivalents', {}))
            mapped_ratio = mapped_count / dependency_analysis['total_dependencies']
        
        readiness_factors.append(mapped_ratio >= 0.7)
        
        # Check API complexity
        api_analysis = analyses[1] if len(analyses) > 1 else {}
        readiness_factors.append(api_analysis.get('complexity_level', 'low') != 'high')
        
        ready_count = sum(readiness_factors)
        if ready_count >= 3:
            return 'high'
        elif ready_count >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_conversion_effort(self, *analyses) -> str:
        """Estimate conversion effort."""
        effort_factors = []
        
        # Factor in code size
        php_analysis = analyses[0] if analyses else {}
        file_count = php_analysis.get('total_files', 0)
        if file_count > 100:
            effort_factors.append(3)
        elif file_count > 30:
            effort_factors.append(2)
        else:
            effort_factors.append(1)
        
        # Factor in API complexity
        api_analysis = analyses[1] if len(analyses) > 1 else {}
        endpoint_count = api_analysis.get('total_endpoints', 0)
        if endpoint_count > 50:
            effort_factors.append(3)
        elif endpoint_count > 15:
            effort_factors.append(2)
        else:
            effort_factors.append(1)
        
        # Factor in dependency complexity
        dependency_analysis = analyses[3] if len(analyses) > 3 else {}
        dep_complexity = dependency_analysis.get('migration_complexity', 'low')
        if dep_complexity == 'high':
            effort_factors.append(3)
        elif dep_complexity == 'medium':
            effort_factors.append(2)
        else:
            effort_factors.append(1)
        
        avg_effort = sum(effort_factors) / len(effort_factors) if effort_factors else 1
        
        if avg_effort >= 2.5:
            return 'high'
        elif avg_effort >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _identify_risk_factors(self, *analyses) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        # Check each analysis for risk indicators
        php_analysis = analyses[0] if analyses else {}
        if php_analysis.get('complexity_level') == 'high':
            risks.append('High code complexity detected')
        
        api_analysis = analyses[1] if len(analyses) > 1 else {}
        if api_analysis.get('total_endpoints', 0) > 30:
            risks.append('Large number of API endpoints')
        
        database_analysis = analyses[2] if len(analyses) > 2 else {}
        if database_analysis.get('relationships_complexity') == 'high':
            risks.append('Complex database relationships')
        
        dependency_analysis = analyses[3] if len(analyses) > 3 else {}
        if dependency_analysis.get('unmapped_dependencies'):
            risks.append('Unmapped dependencies requiring research')
        
        structure_analysis = analyses[4] if len(analyses) > 4 else {}
        if structure_analysis.get('architecture_score', 10) < 5:
            risks.append('Poor project organization')
        
        return risks