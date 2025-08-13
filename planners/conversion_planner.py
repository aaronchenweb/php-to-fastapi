# planners/conversion_planner.py
"""Main conversion planner that coordinates all aspects of PHP to FastAPI conversion."""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .structure_planner import StructurePlanner
from .dependency_planner import DependencyPlanner
from .migration_planner import MigrationPlanner


class ConversionApproach(Enum):
    """Different approaches for conversion."""
    FULL_REWRITE = "full_rewrite"
    INCREMENTAL = "incremental"
    HYBRID = "hybrid"
    GRADUAL_MIGRATION = "gradual_migration"


class ConversionPhase(Enum):
    """Different phases of conversion."""
    ANALYSIS = "analysis"
    PLANNING = "planning"
    FOUNDATION = "foundation"
    CORE_MIGRATION = "core_migration"
    FEATURE_MIGRATION = "feature_migration"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    CLEANUP = "cleanup"


@dataclass
class ConversionPlan:
    """Complete conversion plan."""
    approach: ConversionApproach
    estimated_duration: str
    complexity_level: str
    risk_level: str
    phases: List[Dict[str, Any]] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    rollback_strategy: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """Risk assessment for the conversion."""
    technical_risks: List[Dict[str, Any]] = field(default_factory=list)
    business_risks: List[Dict[str, Any]] = field(default_factory=list)
    timeline_risks: List[Dict[str, Any]] = field(default_factory=list)
    overall_risk_score: float = 0.0
    mitigation_strategies: List[str] = field(default_factory=list)


class ConversionPlanner:
    """Main planner for PHP to FastAPI conversion."""
    
    def __init__(self):
        self.structure_planner = StructurePlanner()
        self.dependency_planner = DependencyPlanner()
        self.migration_planner = MigrationPlanner()
    
    def create_conversion_plan(self, analysis_result: Dict[str, Any]) -> ConversionPlan:
        """Create a comprehensive conversion plan based on analysis results."""
        
        # Determine conversion approach
        approach = self._determine_conversion_approach(analysis_result)
        
        # Assess complexity and risks
        complexity_level = self._assess_complexity(analysis_result)
        risk_assessment = self._assess_risks(analysis_result)
        
        # Create conversion plan
        plan = ConversionPlan(
            approach=approach,
            complexity_level=complexity_level,
            risk_level=self._calculate_risk_level(risk_assessment),
            estimated_duration=self._estimate_duration(analysis_result, approach, complexity_level)
        )
        
        # Define phases
        plan.phases = self._define_conversion_phases(approach, analysis_result)
        
        # Set prerequisites
        plan.prerequisites = self._define_prerequisites(analysis_result)
        
        # Define milestones
        plan.milestones = self._define_milestones(approach, analysis_result)
        
        # Calculate resource requirements
        plan.resource_requirements = self._calculate_resource_requirements(analysis_result, approach)
        
        # Define success criteria
        plan.success_criteria = self._define_success_criteria(analysis_result)
        
        # Create rollback strategy
        plan.rollback_strategy = self._create_rollback_strategy(approach, analysis_result)
        
        return plan
    
    def _determine_conversion_approach(self, analysis_result: Dict[str, Any]) -> ConversionApproach:
        """Determine the best conversion approach based on analysis."""
        project_info = analysis_result.get('project_info', {})
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        database_analysis = analysis_result.get('database_analysis', {})
        file_analysis = analysis_result.get('file_analysis', {})
        
        # Scoring factors
        score_factors = {
            'size': 0,
            'complexity': 0,
            'framework_maturity': 0,
            'dependencies': 0,
            'database_complexity': 0,
            'business_criticality': 0
        }
        
        # Size factor
        total_files = project_info.get('total_php_files', 0)
        total_endpoints = endpoint_analysis.get('total_endpoints', 0)
        
        if total_files < 10 and total_endpoints < 5:
            score_factors['size'] = 1  # Small - full rewrite
        elif total_files < 50 and total_endpoints < 20:
            score_factors['size'] = 2  # Medium - incremental
        else:
            score_factors['size'] = 3  # Large - hybrid/gradual
        
        # Complexity factor
        file_complexity = file_analysis.get('complexity_metrics', {})
        avg_methods = file_complexity.get('avg_methods_per_class', 0)
        
        if avg_methods < 5:
            score_factors['complexity'] = 1  # Low complexity
        elif avg_methods < 15:
            score_factors['complexity'] = 2  # Medium complexity
        else:
            score_factors['complexity'] = 3  # High complexity
        
        # Framework maturity
        framework = project_info.get('framework', 'vanilla')
        if framework in ['laravel', 'symfony']:
            score_factors['framework_maturity'] = 3  # Well-structured
        elif framework in ['codeigniter', 'slim']:
            score_factors['framework_maturity'] = 2  # Moderately structured
        else:
            score_factors['framework_maturity'] = 1  # Unstructured
        
        # Database complexity
        db_complexity = database_analysis.get('complexity_level', 'low')
        if db_complexity == 'low':
            score_factors['database_complexity'] = 1
        elif db_complexity == 'medium':
            score_factors['database_complexity'] = 2
        else:
            score_factors['database_complexity'] = 3
        
        # Calculate weighted score
        total_score = (
            score_factors['size'] * 0.3 +
            score_factors['complexity'] * 0.25 +
            score_factors['framework_maturity'] * 0.2 +
            score_factors['database_complexity'] * 0.15 +
            score_factors['business_criticality'] * 0.1
        )
        
        # Determine approach based on score
        if total_score <= 1.5:
            return ConversionApproach.FULL_REWRITE
        elif total_score <= 2.5:
            return ConversionApproach.INCREMENTAL
        elif total_score <= 3.5:
            return ConversionApproach.HYBRID
        else:
            return ConversionApproach.GRADUAL_MIGRATION
    
    def _assess_complexity(self, analysis_result: Dict[str, Any]) -> str:
        """Assess overall complexity of the conversion."""
        complexity_factors = []
        
        # Code complexity
        file_analysis = analysis_result.get('file_analysis', {})
        total_files = file_analysis.get('total_files', 0)
        total_classes = file_analysis.get('total_classes', 0)
        total_functions = file_analysis.get('total_functions', 0)
        
        if total_files > 100 or total_classes > 50 or total_functions > 200:
            complexity_factors.append('high_code_volume')
        
        # Framework complexity
        project_info = analysis_result.get('project_info', {})
        framework = project_info.get('framework', 'vanilla')
        if framework in ['symfony', 'laravel']:
            complexity_factors.append('complex_framework')
        
        # Database complexity
        database_analysis = analysis_result.get('database_analysis', {})
        if database_analysis.get('complexity_level') == 'high':
            complexity_factors.append('complex_database')
        
        # API complexity
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        endpoints = endpoint_analysis.get('total_endpoints', 0)
        if endpoints > 50:
            complexity_factors.append('many_endpoints')
        
        # Dependency complexity
        dependency_analysis = analysis_result.get('dependency_analysis', {})
        unmapped_deps = len(dependency_analysis.get('python_mappings', {}))
        if unmapped_deps > 10:
            complexity_factors.append('many_dependencies')
        
        # Determine complexity level
        if len(complexity_factors) <= 1:
            return 'low'
        elif len(complexity_factors) <= 3:
            return 'medium'
        else:
            return 'high'
    
    def _assess_risks(self, analysis_result: Dict[str, Any]) -> RiskAssessment:
        """Assess risks associated with the conversion."""
        assessment = RiskAssessment()
        
        # Technical risks
        self._assess_technical_risks(analysis_result, assessment)
        
        # Business risks
        self._assess_business_risks(analysis_result, assessment)
        
        # Timeline risks
        self._assess_timeline_risks(analysis_result, assessment)
        
        # Calculate overall risk score
        assessment.overall_risk_score = self._calculate_overall_risk_score(assessment)
        
        # Generate mitigation strategies
        assessment.mitigation_strategies = self._generate_mitigation_strategies(assessment)
        
        return assessment
    
    def _assess_technical_risks(self, analysis_result: Dict[str, Any], assessment: RiskAssessment) -> None:
        """Assess technical risks."""
        
        # Database migration risk
        database_analysis = analysis_result.get('database_analysis', {})
        if database_analysis.get('complexity_level') == 'high':
            assessment.technical_risks.append({
                'category': 'database',
                'risk': 'Complex database schema migration',
                'impact': 'high',
                'probability': 'medium',
                'description': 'Complex relationships and queries may be difficult to migrate'
            })
        
        # Framework dependency risk
        project_info = analysis_result.get('project_info', {})
        framework = project_info.get('framework', 'vanilla')
        if framework in ['laravel', 'symfony']:
            assessment.technical_risks.append({
                'category': 'framework',
                'risk': 'Framework-specific feature migration',
                'impact': 'high',
                'probability': 'high',
                'description': 'Framework-specific features may not have direct Python equivalents'
            })
        
        # Legacy code risk
        file_analysis = analysis_result.get('file_analysis', {})
        php_features = file_analysis.get('php_features', [])
        if 'legacy_features' in php_features:
            assessment.technical_risks.append({
                'category': 'legacy',
                'risk': 'Legacy PHP features',
                'impact': 'medium',
                'probability': 'high',
                'description': 'Legacy PHP features may require significant refactoring'
            })
        
        # API compatibility risk
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        auth_methods = endpoint_analysis.get('authentication_methods', [])
        if len(auth_methods) > 1:
            assessment.technical_risks.append({
                'category': 'api',
                'risk': 'Multiple authentication methods',
                'impact': 'medium',
                'probability': 'medium',
                'description': 'Multiple auth methods may complicate migration'
            })
    
    def _assess_business_risks(self, analysis_result: Dict[str, Any], assessment: RiskAssessment) -> None:
        """Assess business risks."""
        
        # Downtime risk
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        critical_endpoints = len([ep for ep in endpoint_analysis.get('endpoints', []) 
                                if 'auth' in ep.get('route', '').lower()])
        
        if critical_endpoints > 5:
            assessment.business_risks.append({
                'category': 'availability',
                'risk': 'Service disruption during migration',
                'impact': 'high',
                'probability': 'medium',
                'description': 'Critical authentication endpoints may cause service disruption'
            })
        
        # Performance risk
        assessment.business_risks.append({
            'category': 'performance',
            'risk': 'Performance degradation',
            'impact': 'medium',
            'probability': 'low',
            'description': 'New FastAPI implementation may have different performance characteristics'
        })
        
        # User experience risk
        assessment.business_risks.append({
            'category': 'user_experience',
            'risk': 'API behavior changes',
            'impact': 'medium',
            'probability': 'medium',
            'description': 'Subtle differences in API behavior may affect client applications'
        })
    
    def _assess_timeline_risks(self, analysis_result: Dict[str, Any], assessment: RiskAssessment) -> None:
        """Assess timeline risks."""
        
        # Complexity-based delay risk
        complexity = self._assess_complexity(analysis_result)
        if complexity == 'high':
            assessment.timeline_risks.append({
                'category': 'complexity',
                'risk': 'Development delays due to complexity',
                'impact': 'high',
                'probability': 'high',
                'description': 'High complexity may lead to unexpected delays'
            })
        
        # Resource availability risk
        assessment.timeline_risks.append({
            'category': 'resources',
            'risk': 'Developer availability',
            'impact': 'medium',
            'probability': 'medium',
            'description': 'Limited availability of developers familiar with both PHP and Python'
        })
        
        # Testing time risk
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        total_endpoints = endpoint_analysis.get('total_endpoints', 0)
        if total_endpoints > 20:
            assessment.timeline_risks.append({
                'category': 'testing',
                'risk': 'Extended testing period',
                'impact': 'medium',
                'probability': 'high',
                'description': 'Large number of endpoints requires extensive testing'
            })
    
    def _calculate_overall_risk_score(self, assessment: RiskAssessment) -> float:
        """Calculate overall risk score (0-10)."""
        total_score = 0.0
        total_risks = 0
        
        impact_weights = {'low': 1, 'medium': 2, 'high': 3}
        probability_weights = {'low': 1, 'medium': 2, 'high': 3}
        
        all_risks = (assessment.technical_risks + 
                    assessment.business_risks + 
                    assessment.timeline_risks)
        
        for risk in all_risks:
            impact = impact_weights.get(risk.get('impact', 'medium'), 2)
            probability = probability_weights.get(risk.get('probability', 'medium'), 2)
            risk_score = impact * probability
            total_score += risk_score
            total_risks += 1
        
        if total_risks == 0:
            return 0.0
        
        # Normalize to 0-10 scale
        avg_score = total_score / total_risks
        return min(avg_score * 1.1, 10.0)  # Scale up slightly and cap at 10
    
    def _calculate_risk_level(self, assessment: RiskAssessment) -> str:
        """Calculate risk level from assessment."""
        score = assessment.overall_risk_score
        
        if score <= 3:
            return 'low'
        elif score <= 6:
            return 'medium'
        else:
            return 'high'
    
    def _estimate_duration(self, analysis_result: Dict[str, Any], 
                          approach: ConversionApproach, 
                          complexity_level: str) -> str:
        """Estimate conversion duration."""
        
        # Base duration by approach
        base_durations = {
            ConversionApproach.FULL_REWRITE: {'low': 2, 'medium': 4, 'high': 8},
            ConversionApproach.INCREMENTAL: {'low': 3, 'medium': 6, 'high': 12},
            ConversionApproach.HYBRID: {'low': 4, 'medium': 8, 'high': 16},
            ConversionApproach.GRADUAL_MIGRATION: {'low': 6, 'medium': 12, 'high': 24}
        }
        
        base_weeks = base_durations[approach][complexity_level]
        
        # Adjust based on specific factors
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        total_endpoints = endpoint_analysis.get('total_endpoints', 0)
        
        if total_endpoints > 50:
            base_weeks *= 1.5
        elif total_endpoints > 20:
            base_weeks *= 1.2
        
        # Database complexity adjustment
        database_analysis = analysis_result.get('database_analysis', {})
        if database_analysis.get('complexity_level') == 'high':
            base_weeks *= 1.3
        
        # Convert to readable format
        if base_weeks <= 2:
            return f"{int(base_weeks)} weeks"
        elif base_weeks <= 8:
            return f"{int(base_weeks)} weeks"
        elif base_weeks <= 16:
            return f"{int(base_weeks/4)} months"
        else:
            return f"{base_weeks/4:.1f} months"
    
    def _define_conversion_phases(self, approach: ConversionApproach, 
                                 analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define conversion phases based on approach."""
        
        if approach == ConversionApproach.FULL_REWRITE:
            return self._define_full_rewrite_phases(analysis_result)
        elif approach == ConversionApproach.INCREMENTAL:
            return self._define_incremental_phases(analysis_result)
        elif approach == ConversionApproach.HYBRID:
            return self._define_hybrid_phases(analysis_result)
        else:  # GRADUAL_MIGRATION
            return self._define_gradual_migration_phases(analysis_result)
    
    def _define_full_rewrite_phases(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define phases for full rewrite approach."""
        return [
            {
                'name': 'Foundation Setup',
                'duration': '1 week',
                'description': 'Set up FastAPI project structure and basic configuration',
                'deliverables': ['Project structure', 'Basic configuration', 'Development environment'],
                'prerequisites': ['Development environment setup'],
                'risks': ['Configuration complexity']
            },
            {
                'name': 'Database Migration',
                'duration': '1-2 weeks',
                'description': 'Migrate database schema and create SQLAlchemy models',
                'deliverables': ['Database models', 'Migration scripts', 'Data validation'],
                'prerequisites': ['Database analysis complete'],
                'risks': ['Data integrity', 'Schema complexity']
            },
            {
                'name': 'Core API Development',
                'duration': '2-3 weeks',
                'description': 'Implement core API endpoints and business logic',
                'deliverables': ['API endpoints', 'Authentication', 'Core business logic'],
                'prerequisites': ['Database models ready'],
                'risks': ['Logic complexity', 'Authentication issues']
            },
            {
                'name': 'Feature Implementation',
                'duration': '1-2 weeks',
                'description': 'Implement remaining features and integrations',
                'deliverables': ['All features', 'External integrations', 'Error handling'],
                'prerequisites': ['Core API complete'],
                'risks': ['Integration complexity']
            },
            {
                'name': 'Testing & Validation',
                'duration': '1 week',
                'description': 'Comprehensive testing and validation',
                'deliverables': ['Test suite', 'Performance tests', 'API documentation'],
                'prerequisites': ['All features implemented'],
                'risks': ['Test coverage', 'Performance issues']
            }
        ]
    
    def _define_incremental_phases(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define phases for incremental approach."""
        return [
            {
                'name': 'Parallel Setup',
                'duration': '1 week',
                'description': 'Set up FastAPI alongside existing PHP application',
                'deliverables': ['FastAPI project', 'Routing strategy', 'Deployment pipeline'],
                'prerequisites': ['Infrastructure planning'],
                'risks': ['Environment conflicts']
            },
            {
                'name': 'Authentication Migration',
                'duration': '1-2 weeks',
                'description': 'Migrate authentication system first',
                'deliverables': ['Auth endpoints', 'Token validation', 'User management'],
                'prerequisites': ['User data analysis'],
                'risks': ['Session compatibility', 'Security gaps']
            },
            {
                'name': 'Core Endpoints Migration',
                'duration': '2-4 weeks',
                'description': 'Migrate most critical API endpoints',
                'deliverables': ['Priority endpoints', 'Database integration', 'Error handling'],
                'prerequisites': ['Authentication ready'],
                'risks': ['Data consistency', 'API compatibility']
            },
            {
                'name': 'Remaining Features',
                'duration': '2-3 weeks',
                'description': 'Migrate remaining endpoints and features',
                'deliverables': ['All endpoints', 'Feature parity', 'Documentation'],
                'prerequisites': ['Core endpoints stable'],
                'risks': ['Edge cases', 'Performance differences']
            },
            {
                'name': 'Traffic Migration',
                'duration': '1-2 weeks',
                'description': 'Gradually redirect traffic to FastAPI',
                'deliverables': ['Load balancer config', 'Monitoring', 'Rollback procedures'],
                'prerequisites': ['Full functionality verified'],
                'risks': ['Traffic routing', 'Performance under load']
            },
            {
                'name': 'PHP Retirement',
                'duration': '1 week',
                'description': 'Decommission PHP application',
                'deliverables': ['Cleanup completed', 'Documentation updated'],
                'prerequisites': ['FastAPI fully operational'],
                'risks': ['Missed dependencies']
            }
        ]
    
    def _define_hybrid_phases(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define phases for hybrid approach."""
        return [
            {
                'name': 'Architecture Planning',
                'duration': '1 week',
                'description': 'Plan hybrid architecture and component boundaries',
                'deliverables': ['Architecture diagram', 'Integration strategy', 'Component mapping'],
                'prerequisites': ['Component analysis'],
                'risks': ['Architecture complexity']
            },
            {
                'name': 'API Gateway Setup',
                'duration': '1 week',
                'description': 'Set up API gateway for routing between PHP and FastAPI',
                'deliverables': ['API gateway', 'Routing rules', 'Monitoring'],
                'prerequisites': ['Architecture approved'],
                'risks': ['Gateway complexity', 'Single point of failure']
            },
            {
                'name': 'New Features in FastAPI',
                'duration': '2-3 weeks',
                'description': 'Implement new features directly in FastAPI',
                'deliverables': ['New features', 'Integration layer', 'Testing'],
                'prerequisites': ['Gateway operational'],
                'risks': ['Integration issues']
            },
            {
                'name': 'Core Migration',
                'duration': '3-4 weeks',
                'description': 'Migrate core functionality to FastAPI',
                'deliverables': ['Migrated core features', 'Updated routing', 'Data consistency'],
                'prerequisites': ['New features stable'],
                'risks': ['Migration complexity', 'Data synchronization']
            },
            {
                'name': 'Legacy Migration',
                'duration': '2-3 weeks',
                'description': 'Migrate remaining legacy components',
                'deliverables': ['All components migrated', 'Full FastAPI deployment'],
                'prerequisites': ['Core migration complete'],
                'risks': ['Legacy complexity']
            },
            {
                'name': 'Consolidation',
                'duration': '1 week',
                'description': 'Remove API gateway and consolidate to pure FastAPI',
                'deliverables': ['Unified FastAPI application', 'Simplified architecture'],
                'prerequisites': ['All migration complete'],
                'risks': ['Consolidation issues']
            }
        ]
    
    def _define_gradual_migration_phases(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define phases for gradual migration approach."""
        return [
            {
                'name': 'Component Analysis',
                'duration': '2 weeks',
                'description': 'Detailed analysis and prioritization of components',
                'deliverables': ['Component inventory', 'Migration priorities', 'Dependency map'],
                'prerequisites': ['Full system analysis'],
                'risks': ['Analysis completeness']
            },
            {
                'name': 'Infrastructure Setup',
                'duration': '1 week',
                'description': 'Set up infrastructure for gradual migration',
                'deliverables': ['Deployment pipeline', 'Monitoring', 'Rollback procedures'],
                'prerequisites': ['Infrastructure planning'],
                'risks': ['Infrastructure complexity']
            },
            {
                'name': 'Pilot Migration',
                'duration': '2-3 weeks',
                'description': 'Migrate a small, isolated component as pilot',
                'deliverables': ['Pilot component', 'Migration process', 'Lessons learned'],
                'prerequisites': ['Component selected'],
                'risks': ['Pilot complexity']
            },
            {
                'name': 'Iterative Migration',
                'duration': '8-12 weeks',
                'description': 'Gradually migrate components in iterations',
                'deliverables': ['Migrated components', 'Updated documentation', 'Performance metrics'],
                'prerequisites': ['Pilot successful'],
                'risks': ['Integration complexity', 'Performance degradation']
            },
            {
                'name': 'Final Integration',
                'duration': '2 weeks',
                'description': 'Complete migration and final integration',
                'deliverables': ['Complete FastAPI system', 'Full documentation'],
                'prerequisites': ['All components migrated'],
                'risks': ['Final integration issues']
            },
            {
                'name': 'Optimization',
                'duration': '1-2 weeks',
                'description': 'Optimize performance and cleanup',
                'deliverables': ['Optimized system', 'Performance baseline'],
                'prerequisites': ['Migration complete'],
                'risks': ['Performance issues']
            }
        ]
    
    def _define_prerequisites(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Define prerequisites for the conversion."""
        prerequisites = [
            'Development team trained in Python and FastAPI',
            'Development environment set up with Python 3.8+',
            'Database backup and recovery procedures in place',
            'Version control system configured',
            'Testing environment available'
        ]
        
        # Add database-specific prerequisites
        database_analysis = analysis_result.get('database_analysis', {})
        if database_analysis.get('total_connections', 0) > 0:
            prerequisites.append('Database connection credentials and access verified')
            
        # Add framework-specific prerequisites
        project_info = analysis_result.get('project_info', {})
        framework = project_info.get('framework', 'vanilla')
        if framework in ['laravel', 'symfony']:
            prerequisites.append(f'{framework.title()} framework expertise available for consultation')
        
        return prerequisites
    
    def _define_milestones(self, approach: ConversionApproach, 
                          analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define project milestones."""
        milestones = []
        
        # Common milestones
        milestones.extend([
            {
                'name': 'Project Kickoff',
                'description': 'Project officially started with team and resources allocated',
                'criteria': ['Team assembled', 'Environment ready', 'Plan approved'],
                'timeline': 'Week 1'
            },
            {
                'name': 'Foundation Complete',
                'description': 'Basic FastAPI structure and configuration ready',
                'criteria': ['Project structure created', 'Configuration working', 'Basic endpoints responding'],
                'timeline': 'Week 2-3'
            }
        ])
        
        # Approach-specific milestones
        if approach == ConversionApproach.FULL_REWRITE:
            milestones.extend([
                {
                    'name': 'Database Migration Complete',
                    'description': 'All database models and migrations ready',
                    'criteria': ['Models created', 'Data migrated', 'Tests passing'],
                    'timeline': 'Week 4-5'
                },
                {
                    'name': 'API Parity Achieved',
                    'description': 'All original API endpoints implemented',
                    'criteria': ['All endpoints working', 'Authentication functional', 'Core features complete'],
                    'timeline': 'Week 6-8'
                }
            ])
        elif approach == ConversionApproach.INCREMENTAL:
            milestones.extend([
                {
                    'name': 'First Component Migrated',
                    'description': 'Authentication system successfully migrated',
                    'criteria': ['Auth working', 'Users can login', 'No regressions'],
                    'timeline': 'Week 3-4'
                },
                {
                    'name': 'Core APIs Migrated',
                    'description': 'Most critical API endpoints migrated',
                    'criteria': ['Core functionality working', 'Performance acceptable', 'Data consistent'],
                    'timeline': 'Week 6-8'
                }
            ])
        
        # Final milestone
        milestones.append({
            'name': 'Go-Live',
            'description': 'FastAPI application live in production',
            'criteria': ['All tests passing', 'Performance acceptable', 'Monitoring active', 'Team trained'],
            'timeline': 'Final week'
        })
        
        return milestones
    
    def _calculate_resource_requirements(self, analysis_result: Dict[str, Any], 
                                       approach: ConversionApproach) -> Dict[str, Any]:
        """Calculate resource requirements."""
        
        complexity = self._assess_complexity(analysis_result)
        
        # Base team requirements
        team_size = {
            'low': {'developers': 1, 'senior_developers': 1, 'devops': 0.5, 'qa': 0.5},
            'medium': {'developers': 2, 'senior_developers': 1, 'devops': 1, 'qa': 1},
            'high': {'developers': 3, 'senior_developers': 2, 'devops': 1, 'qa': 1}
        }
        
        base_team = team_size[complexity]
        
        # Adjust for approach
        if approach == ConversionApproach.GRADUAL_MIGRATION:
            base_team['developers'] += 1
            base_team['devops'] += 0.5
        elif approach == ConversionApproach.HYBRID:
            base_team['senior_developers'] += 1
        
        # Infrastructure requirements
        infrastructure = {
            'development_servers': 2,
            'testing_servers': 1,
            'staging_servers': 1,
            'monitoring_tools': ['Application monitoring', 'Database monitoring', 'Log aggregation'],
            'ci_cd_pipeline': True
        }
        
        # Tool requirements
        tools = [
            'Python IDE (PyCharm/VSCode)',
            'Database management tools',
            'API testing tools (Postman/Insomnia)',
            'Version control (Git)',
            'Project management tools'
        ]
        
        return {
            'team': base_team,
            'infrastructure': infrastructure,
            'tools': tools,
            'budget_considerations': [
                'Development team costs',
                'Infrastructure costs',
                'Tool licensing',
                'Training costs',
                'Potential downtime costs'
            ]
        }
    
    def _define_success_criteria(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Define success criteria for the conversion."""
        criteria = [
            'All API endpoints functional and tested',
            'Authentication and authorization working correctly',
            'Database migration completed without data loss',
            'Performance meets or exceeds original system',
            'All automated tests passing',
            'Documentation complete and up-to-date',
            'Team trained on new system',
            'Monitoring and alerting configured',
            'Rollback procedures tested and ready'
        ]
        
        # Add specific criteria based on analysis
        endpoint_analysis = analysis_result.get('endpoint_analysis', {})
        total_endpoints = endpoint_analysis.get('total_endpoints', 0)
        
        if total_endpoints > 0:
            criteria.append(f'All {total_endpoints} API endpoints migrated and functional')
        
        database_analysis = analysis_result.get('database_analysis', {})
        total_tables = len(database_analysis.get('tables', []))
        
        if total_tables > 0:
            criteria.append(f'All {total_tables} database tables migrated with data integrity verified')
        
        return criteria
    
    def _create_rollback_strategy(self, approach: ConversionApproach, 
                                 analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create rollback strategy."""
        
        base_strategy = {
            'triggers': [
                'Critical bugs discovered in production',
                'Performance degradation beyond acceptable limits',
                'Data integrity issues',
                'Security vulnerabilities',
                'Business continuity at risk'
            ],
            'preparation': [
                'Complete backup of original PHP application',
                'Database backup and recovery procedures',
                'DNS and load balancer rollback procedures',
                'Communication plan for stakeholders',
                'Rollback testing in staging environment'
            ],
            'execution_steps': [
                '1. Stop traffic to FastAPI application',
                '2. Restore PHP application to production',
                '3. Restore database if necessary',
                '4. Update DNS/load balancer configuration',
                '5. Verify original functionality',
                '6. Communicate status to stakeholders',
                '7. Document issues for future resolution'
            ],
            'recovery_time_objective': '2 hours',
            'recovery_point_objective': '1 hour'
        }
        
        # Adjust based on approach
        if approach == ConversionApproach.INCREMENTAL:
            base_strategy['execution_steps'].insert(1, '1.5. Redirect traffic back to PHP components')
            base_strategy['recovery_time_objective'] = '30 minutes'
        elif approach == ConversionApproach.GRADUAL_MIGRATION:
            base_strategy['execution_steps'].insert(1, '1.5. Rollback individual components as needed')
            base_strategy['recovery_time_objective'] = '1 hour'
        
        return base_strategy
    
    def _generate_mitigation_strategies(self, assessment: RiskAssessment) -> List[str]:
        """Generate risk mitigation strategies."""
        strategies = []
        
        # Technical risk mitigations
        for risk in assessment.technical_risks:
            if risk['category'] == 'database':
                strategies.append('Implement comprehensive database testing and validation procedures')
                strategies.append('Create detailed data migration scripts with rollback capabilities')
            elif risk['category'] == 'framework':
                strategies.append('Research and document framework-specific migration patterns')
                strategies.append('Consider gradual migration approach for complex framework features')
            elif risk['category'] == 'legacy':
                strategies.append('Prioritize refactoring of legacy code before migration')
                strategies.append('Create comprehensive test coverage for legacy functionality')
        
        # Business risk mitigations
        for risk in assessment.business_risks:
            if risk['category'] == 'availability':
                strategies.append('Implement blue-green deployment strategy')
                strategies.append('Set up comprehensive monitoring and alerting')
            elif risk['category'] == 'performance':
                strategies.append('Conduct thorough performance testing before go-live')
                strategies.append('Implement performance monitoring and optimization')
        
        # Timeline risk mitigations
        for risk in assessment.timeline_risks:
            if risk['category'] == 'complexity':
                strategies.append('Break down complex tasks into smaller, manageable pieces')
                strategies.append('Build in buffer time for unexpected complications')
            elif risk['category'] == 'testing':
                strategies.append('Start testing early and continuously throughout development')
                strategies.append('Implement automated testing to reduce manual testing time')
        
        # General strategies
        strategies.extend([
            'Maintain regular communication with stakeholders',
            'Document all decisions and changes thoroughly',
            'Conduct regular code reviews and quality checks',
            'Plan for team training and knowledge transfer',
            'Establish clear escalation procedures'
        ])
        
        return list(set(strategies))  # Remove duplicates