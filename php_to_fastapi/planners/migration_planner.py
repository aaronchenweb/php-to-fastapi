# planners/migration_planner.py
"""Plans database and data migration strategies for PHP to FastAPI conversion."""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re


class MigrationStrategy(Enum):
    """Different migration strategies."""
    DIRECT_CONVERSION = "direct_conversion"
    SCHEMA_RECREATION = "schema_recreation"
    GRADUAL_MIGRATION = "gradual_migration"
    DUAL_WRITE = "dual_write"
    EVENT_SOURCING = "event_sourcing"


class DataMigrationApproach(Enum):
    """Data migration approaches."""
    FULL_EXPORT_IMPORT = "full_export_import"
    INCREMENTAL_SYNC = "incremental_sync"
    LIVE_MIGRATION = "live_migration"
    SNAPSHOT_RESTORE = "snapshot_restore"


@dataclass
class TableMigration:
    """Migration plan for a single table."""
    php_table_name: str
    python_table_name: str
    python_model_name: str
    migration_priority: int = 1  # 1=high, 2=medium, 3=low
    migration_complexity: str = "low"  # low, medium, high
    estimated_rows: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    schema_changes: List[str] = field(default_factory=list)
    data_transformations: List[str] = field(default_factory=list)
    validation_queries: List[str] = field(default_factory=list)
    rollback_strategy: Optional[str] = None


@dataclass
class SchemaMapping:
    """Mapping between PHP and Python schema elements."""
    php_column: str
    python_column: str
    php_type: str
    python_type: str
    nullable: bool = True
    default_value: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    transformation_needed: bool = False
    transformation_logic: Optional[str] = None


@dataclass
class RelationshipMapping:
    """Mapping for table relationships."""
    relationship_type: str  # one_to_one, one_to_many, many_to_many
    source_table: str
    target_table: str
    source_column: str
    target_column: str
    php_implementation: str
    python_implementation: str
    migration_notes: List[str] = field(default_factory=list)


@dataclass
class MigrationPhase:
    """A phase in the migration process."""
    name: str
    description: str
    tables: List[str] = field(default_factory=list)
    estimated_duration: str = ""
    prerequisites: List[str] = field(default_factory=list)
    validation_steps: List[str] = field(default_factory=list)
    rollback_plan: List[str] = field(default_factory=list)


@dataclass
class MigrationPlan:
    """Complete migration plan."""
    strategy: MigrationStrategy
    data_approach: DataMigrationApproach
    estimated_total_duration: str
    downtime_required: str
    table_migrations: List[TableMigration] = field(default_factory=list)
    schema_mappings: List[SchemaMapping] = field(default_factory=list)
    relationship_mappings: List[RelationshipMapping] = field(default_factory=list)
    migration_phases: List[MigrationPhase] = field(default_factory=list)
    validation_strategy: Dict[str, Any] = field(default_factory=dict)
    rollback_strategy: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class MigrationPlanner:
    """Plans database and data migration for PHP to FastAPI conversion."""
    
    def __init__(self):
        # PHP to Python type mappings
        self.type_mappings = {
            'int': 'Integer',
            'integer': 'Integer',
            'bigint': 'BigInteger',
            'smallint': 'SmallInteger',
            'tinyint': 'SmallInteger',
            'varchar': 'String',
            'char': 'String',
            'text': 'Text',
            'longtext': 'Text',
            'mediumtext': 'Text',
            'datetime': 'DateTime',
            'timestamp': 'DateTime',
            'date': 'Date',
            'time': 'Time',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'decimal': 'Numeric',
            'float': 'Float',
            'double': 'Float',
            'json': 'JSON',
            'blob': 'LargeBinary',
            'enum': 'Enum'
        }
        
        # Common PHP framework relationship patterns
        self.relationship_patterns = {
            'eloquent': {
                'hasOne': 'one_to_one',
                'hasMany': 'one_to_many',
                'belongsTo': 'many_to_one',
                'belongsToMany': 'many_to_many'
            },
            'doctrine': {
                'OneToOne': 'one_to_one',
                'OneToMany': 'one_to_many',
                'ManyToOne': 'many_to_one',
                'ManyToMany': 'many_to_many'
            }
        }
    
    def plan_migration(self, analysis_result: Dict[str, Any]) -> MigrationPlan:
        """Plan the complete database migration."""
        
        database_analysis = analysis_result.get('database_analysis', {})
        
        # Determine migration strategy
        strategy = self._determine_migration_strategy(database_analysis, analysis_result)
        
        # Determine data migration approach
        data_approach = self._determine_data_approach(database_analysis, strategy)
        
        # Create migration plan
        plan = MigrationPlan(
            strategy=strategy,
            data_approach=data_approach,
            estimated_total_duration="",
            downtime_required=""
        )
        
        # Plan table migrations
        plan.table_migrations = self._plan_table_migrations(database_analysis)
        
        # Plan schema mappings
        plan.schema_mappings = self._plan_schema_mappings(database_analysis)
        
        # Plan relationship mappings
        plan.relationship_mappings = self._plan_relationship_mappings(database_analysis)
        
        # Plan migration phases
        plan.migration_phases = self._plan_migration_phases(plan.table_migrations, strategy)
        
        # Plan validation strategy
        plan.validation_strategy = self._plan_validation_strategy(plan)
        
        # Plan rollback strategy
        plan.rollback_strategy = self._plan_rollback_strategy(plan)
        
        # Assess risks
        plan.risk_assessment = self._assess_migration_risks(plan, database_analysis)
        
        # Calculate estimates
        plan.estimated_total_duration = self._estimate_total_duration(plan)
        plan.downtime_required = self._estimate_downtime(plan, strategy)
        
        # Generate recommendations
        plan.recommendations = self._generate_migration_recommendations(plan, database_analysis)
        
        return plan
    
    def _determine_migration_strategy(self, database_analysis: Dict[str, Any], 
                                    analysis_result: Dict[str, Any]) -> MigrationStrategy:
        """Determine the best migration strategy."""
        
        complexity_level = database_analysis.get('complexity_level', 'low')
        total_tables = len(database_analysis.get('tables', []))
        total_connections = database_analysis.get('total_connections', 0)
        
        # Consider project size and complexity
        project_info = analysis_result.get('project_info', {})
        total_files = project_info.get('total_php_files', 0)
        
        # Decision logic
        if complexity_level == 'low' and total_tables <= 10:
            return MigrationStrategy.DIRECT_CONVERSION
        elif total_connections > 1 or total_tables > 50:
            return MigrationStrategy.GRADUAL_MIGRATION
        elif complexity_level == 'high' or total_files > 100:
            return MigrationStrategy.DUAL_WRITE
        else:
            return MigrationStrategy.SCHEMA_RECREATION
    
    def _determine_data_approach(self, database_analysis: Dict[str, Any], 
                               strategy: MigrationStrategy) -> DataMigrationApproach:
        """Determine data migration approach."""
        
        estimated_data_size = self._estimate_data_size(database_analysis)
        
        if strategy == MigrationStrategy.DIRECT_CONVERSION:
            return DataMigrationApproach.FULL_EXPORT_IMPORT
        elif strategy == MigrationStrategy.GRADUAL_MIGRATION:
            return DataMigrationApproach.INCREMENTAL_SYNC
        elif strategy == MigrationStrategy.DUAL_WRITE:
            return DataMigrationApproach.LIVE_MIGRATION
        elif estimated_data_size == 'large':
            return DataMigrationApproach.SNAPSHOT_RESTORE
        else:
            return DataMigrationApproach.FULL_EXPORT_IMPORT
    
    def _estimate_data_size(self, database_analysis: Dict[str, Any]) -> str:
        """Estimate data size category."""
        tables = database_analysis.get('tables', [])
        total_tables = len(tables)
        
        # Simple heuristic based on table count
        if total_tables <= 5:
            return 'small'
        elif total_tables <= 20:
            return 'medium'
        else:
            return 'large'
    
    def _plan_table_migrations(self, database_analysis: Dict[str, Any]) -> List[TableMigration]:
        """Plan migrations for individual tables."""
        migrations = []
        
        tables = database_analysis.get('tables', [])
        
        for table in tables:
            table_name = table.get('name', '')
            
            migration = TableMigration(
                php_table_name=table_name,
                python_table_name=table_name,  # Keep same name by default
                python_model_name=self._table_to_model_name(table_name),
                migration_priority=self._determine_table_priority(table),
                migration_complexity=self._assess_table_complexity(table)
            )
            
            # Determine schema changes needed
            migration.schema_changes = self._identify_schema_changes(table)
            
            # Determine data transformations needed
            migration.data_transformations = self._identify_data_transformations(table)
            
            # Plan validation queries
            migration.validation_queries = self._plan_validation_queries(table)
            
            # Plan rollback strategy
            migration.rollback_strategy = self._plan_table_rollback(table)
            
            migrations.append(migration)
        
        # Sort by priority (high priority first)
        migrations.sort(key=lambda x: x.migration_priority)
        
        return migrations
    
    def _table_to_model_name(self, table_name: str) -> str:
        """Convert table name to Python model name."""
        # Remove plural suffix and convert to PascalCase
        name = table_name
        if name.endswith('ies'):
            name = name[:-3] + 'y'
        elif name.endswith('es'):
            name = name[:-2]
        elif name.endswith('s'):
            name = name[:-1]
        
        # Convert snake_case to PascalCase
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _determine_table_priority(self, table: Dict[str, Any]) -> int:
        """Determine migration priority for a table."""
        table_name = table.get('name', '').lower()
        
        # High priority tables (foundational)
        if any(keyword in table_name for keyword in ['user', 'account', 'auth', 'session']):
            return 1
        
        # Medium priority tables (core business logic)
        elif any(keyword in table_name for keyword in ['order', 'product', 'customer', 'payment']):
            return 2
        
        # Low priority tables (supporting data)
        else:
            return 3
    
    def _assess_table_complexity(self, table: Dict[str, Any]) -> str:
        """Assess complexity of migrating a table."""
        relationships = table.get('relationships', [])
        estimated_columns = table.get('estimated_columns', [])
        
        complexity_score = 0
        
        # More relationships = higher complexity
        complexity_score += len(relationships) * 2
        
        # More columns = higher complexity
        complexity_score += len(estimated_columns)
        
        # Check for complex column types
        for column in estimated_columns:
            if any(keyword in column.lower() for keyword in ['json', 'blob', 'text']):
                complexity_score += 3
        
        if complexity_score <= 5:
            return 'low'
        elif complexity_score <= 15:
            return 'medium'
        else:
            return 'high'
    
    def _identify_schema_changes(self, table: Dict[str, Any]) -> List[str]:
        """Identify necessary schema changes for a table."""
        changes = []
        
        # Check if table name needs changing
        table_name = table.get('name', '')
        if not self._is_python_friendly_name(table_name):
            new_name = self._make_python_friendly(table_name)
            changes.append(f"Rename table from '{table_name}' to '{new_name}'")
        
        # Add standard columns if missing
        estimated_columns = [col.lower() for col in table.get('estimated_columns', [])]
        
        if not any('id' in col for col in estimated_columns):
            changes.append("Add auto-incrementing primary key 'id'")
        
        if not any('created_at' in col for col in estimated_columns):
            changes.append("Add 'created_at' timestamp column")
        
        if not any('updated_at' in col for col in estimated_columns):
            changes.append("Add 'updated_at' timestamp column")
        
        return changes
    
    def _identify_data_transformations(self, table: Dict[str, Any]) -> List[str]:
        """Identify data transformations needed for a table."""
        transformations = []
        
        estimated_columns = table.get('estimated_columns', [])
        
        for column in estimated_columns:
            # Check for date format transformations
            if 'date' in column.lower():
                transformations.append(f"Convert date format for {column}")
            
            # Check for JSON transformations
            if 'json' in column.lower():
                transformations.append(f"Validate and transform JSON data in {column}")
            
            # Check for enum transformations
            if 'enum' in column.lower():
                transformations.append(f"Convert enum values to proper format for {column}")
        
        return transformations
    
    def _plan_validation_queries(self, table: Dict[str, Any]) -> List[str]:
        """Plan validation queries for a table migration."""
        table_name = table.get('name', '')
        queries = []
        
        # Row count validation
        queries.append(f"SELECT COUNT(*) FROM {table_name}")
        
        # Check for null values in required fields
        queries.append(f"SELECT COUNT(*) FROM {table_name} WHERE id IS NULL")
        
        # Check for data integrity
        relationships = table.get('relationships', [])
        for relationship in relationships:
            if 'foreign' in relationship.lower():
                queries.append(f"Validate foreign key relationships for {table_name}")
        
        return queries
    
    def _plan_table_rollback(self, table: Dict[str, Any]) -> str:
        """Plan rollback strategy for a table."""
        table_name = table.get('name', '')
        return f"Restore {table_name} from backup and verify data integrity"
    
    def _plan_schema_mappings(self, database_analysis: Dict[str, Any]) -> List[SchemaMapping]:
        """Plan schema mappings between PHP and Python."""
        mappings = []
        
        tables = database_analysis.get('tables', [])
        
        for table in tables:
            estimated_columns = table.get('estimated_columns', [])
            
            for column_def in estimated_columns:
                # Parse column definition
                if '(' in column_def:
                    column_name = column_def.split('(')[0].strip()
                    column_type = column_def.split('(')[1].split(')')[0].strip()
                else:
                    parts = column_def.split()
                    column_name = parts[0] if parts else column_def
                    column_type = parts[1] if len(parts) > 1 else 'string'
                
                # Map to Python type
                python_type = self._map_column_type(column_type)
                
                mapping = SchemaMapping(
                    php_column=column_name,
                    python_column=self._make_python_friendly(column_name),
                    php_type=column_type,
                    python_type=python_type,
                    transformation_needed=column_name != self._make_python_friendly(column_name)
                )
                
                if mapping.transformation_needed:
                    mapping.transformation_logic = f"Rename {column_name} to {mapping.python_column}"
                
                mappings.append(mapping)
        
        return mappings
    
    def _map_column_type(self, php_type: str) -> str:
        """Map PHP/MySQL column type to SQLAlchemy type."""
        php_type_lower = php_type.lower()
        
        # Extract base type (remove size specifications)
        base_type = re.sub(r'\(\d+\)', '', php_type_lower)
        
        return self.type_mappings.get(base_type, 'String(255)')
    
    def _plan_relationship_mappings(self, database_analysis: Dict[str, Any]) -> List[RelationshipMapping]:
        """Plan relationship mappings between tables."""
        mappings = []
        
        tables = database_analysis.get('tables', [])
        
        for table in tables:
            relationships = table.get('relationships', [])
            
            for relationship in relationships:
                # Parse relationship string (simplified)
                if '->' in relationship:
                    parts = relationship.split('->')
                    source_info = parts[0].strip()
                    target_info = parts[1].strip() if len(parts) > 1 else ''
                    
                    # Determine relationship type
                    rel_type = self._determine_relationship_type(source_info)
                    
                    mapping = RelationshipMapping(
                        relationship_type=rel_type,
                        source_table=table.get('name', ''),
                        target_table=target_info,
                        source_column='',  # Would need more analysis
                        target_column='',  # Would need more analysis
                        php_implementation=relationship,
                        python_implementation=self._generate_sqlalchemy_relationship(rel_type)
                    )
                    
                    mappings.append(mapping)
        
        return mappings
    
    def _determine_relationship_type(self, relationship_info: str) -> str:
        """Determine SQLAlchemy relationship type from PHP relationship."""
        rel_lower = relationship_info.lower()
        
        if 'hasone' in rel_lower or 'belongsto' in rel_lower:
            return 'one_to_one'
        elif 'hasmany' in rel_lower:
            return 'one_to_many'
        elif 'belongstomany' in rel_lower:
            return 'many_to_many'
        else:
            return 'many_to_one'  # Default
    
    def _generate_sqlalchemy_relationship(self, rel_type: str) -> str:
        """Generate SQLAlchemy relationship code."""
        if rel_type == 'one_to_one':
            return "relationship('TargetModel', uselist=False, back_populates='source')"
        elif rel_type == 'one_to_many':
            return "relationship('TargetModel', back_populates='source')"
        elif rel_type == 'many_to_many':
            return "relationship('TargetModel', secondary=association_table, back_populates='sources')"
        else:
            return "relationship('TargetModel', back_populates='targets')"
    
    def _plan_migration_phases(self, table_migrations: List[TableMigration], 
                              strategy: MigrationStrategy) -> List[MigrationPhase]:
        """Plan migration phases based on strategy and table dependencies."""
        phases = []
        
        if strategy == MigrationStrategy.DIRECT_CONVERSION:
            phases = self._plan_direct_conversion_phases(table_migrations)
        elif strategy == MigrationStrategy.GRADUAL_MIGRATION:
            phases = self._plan_gradual_migration_phases(table_migrations)
        elif strategy == MigrationStrategy.DUAL_WRITE:
            phases = self._plan_dual_write_phases(table_migrations)
        else:
            phases = self._plan_schema_recreation_phases(table_migrations)
        
        return phases
    
    def _plan_direct_conversion_phases(self, table_migrations: List[TableMigration]) -> List[MigrationPhase]:
        """Plan phases for direct conversion strategy."""
        return [
            MigrationPhase(
                name="Preparation",
                description="Backup data and prepare migration environment",
                estimated_duration="1 hour",
                prerequisites=["Database backup completed", "Migration environment ready"],
                validation_steps=["Verify backup integrity", "Test migration scripts"],
                rollback_plan=["Restore from backup", "Verify data integrity"]
            ),
            MigrationPhase(
                name="Schema Migration",
                description="Create new schema and migrate table structures",
                tables=[tm.php_table_name for tm in table_migrations],
                estimated_duration="2-4 hours",
                prerequisites=["Preparation phase complete"],
                validation_steps=["Verify schema structure", "Check constraints"],
                rollback_plan=["Drop new schema", "Restore original"]
            ),
            MigrationPhase(
                name="Data Migration",
                description="Migrate all data from old to new schema",
                estimated_duration="4-8 hours",
                prerequisites=["Schema migration complete"],
                validation_steps=["Row count validation", "Data integrity checks"],
                rollback_plan=["Clear new data", "Restore from backup"]
            ),
            MigrationPhase(
                name="Validation",
                description="Comprehensive validation of migrated data",
                estimated_duration="1-2 hours",
                prerequisites=["Data migration complete"],
                validation_steps=["Full data validation", "Performance testing"],
                rollback_plan=["Document issues", "Prepare re-migration"]
            )
        ]
    
    def _plan_gradual_migration_phases(self, table_migrations: List[TableMigration]) -> List[MigrationPhase]:
        """Plan phases for gradual migration strategy."""
        # Group tables by priority
        high_priority = [tm for tm in table_migrations if tm.migration_priority == 1]
        medium_priority = [tm for tm in table_migrations if tm.migration_priority == 2]
        low_priority = [tm for tm in table_migrations if tm.migration_priority == 3]
        
        phases = [
            MigrationPhase(
                name="Phase 1 - Foundation Tables",
                description="Migrate core foundational tables",
                tables=[tm.php_table_name for tm in high_priority],
                estimated_duration="2-3 days",
                prerequisites=["Dual-write system setup"],
                validation_steps=["Core functionality validation"],
                rollback_plan=["Switch back to original tables"]
            )
        ]
        
        if medium_priority:
            phases.append(MigrationPhase(
                name="Phase 2 - Business Logic Tables",
                description="Migrate core business logic tables",
                tables=[tm.php_table_name for tm in medium_priority],
                estimated_duration="3-5 days",
                prerequisites=["Phase 1 complete and validated"],
                validation_steps=["Business logic validation"],
                rollback_plan=["Rollback to Phase 1 state"]
            ))
        
        if low_priority:
            phases.append(MigrationPhase(
                name="Phase 3 - Supporting Tables",
                description="Migrate remaining supporting tables",
                tables=[tm.php_table_name for tm in low_priority],
                estimated_duration="2-3 days",
                prerequisites=["Phase 2 complete and validated"],
                validation_steps=["Complete system validation"],
                rollback_plan=["Rollback to Phase 2 state"]
            ))
        
        return phases
    
    def _plan_dual_write_phases(self, table_migrations: List[TableMigration]) -> List[MigrationPhase]:
        """Plan phases for dual-write strategy."""
        return [
            MigrationPhase(
                name="Dual-Write Setup",
                description="Set up dual-write system for new and old schemas",
                estimated_duration="1-2 days",
                prerequisites=["New schema created", "Dual-write logic implemented"],
                validation_steps=["Dual-write functionality test"],
                rollback_plan=["Disable dual-write", "Use original system only"]
            ),
            MigrationPhase(
                name="Historical Data Migration",
                description="Migrate historical data to new schema",
                tables=[tm.php_table_name for tm in table_migrations],
                estimated_duration="1-3 days",
                prerequisites=["Dual-write system operational"],
                validation_steps=["Historical data validation"],
                rollback_plan=["Clear new historical data"]
            ),
            MigrationPhase(
                name="Read Traffic Migration",
                description="Gradually migrate read traffic to new schema",
                estimated_duration="1-2 weeks",
                prerequisites=["Historical data migrated"],
                validation_steps=["Performance monitoring", "Data consistency checks"],
                rollback_plan=["Route reads back to original schema"]
            ),
            MigrationPhase(
                name="Write Traffic Migration",
                description="Migrate write traffic to new schema only",
                estimated_duration="1 week",
                prerequisites=["Read migration successful"],
                validation_steps=["Write performance validation"],
                rollback_plan=["Re-enable dual-write system"]
            )
        ]
    
    def _plan_schema_recreation_phases(self, table_migrations: List[TableMigration]) -> List[MigrationPhase]:
        """Plan phases for schema recreation strategy."""
        return [
            MigrationPhase(
                name="Schema Analysis",
                description="Analyze and redesign schema for optimal structure",
                estimated_duration="1-2 days",
                prerequisites=["Requirements analysis complete"],
                validation_steps=["Schema design review"],
                rollback_plan=["Use original schema design"]
            ),
            MigrationPhase(
                name="New Schema Creation",
                description="Create optimized schema structure",
                estimated_duration="1 day",
                prerequisites=["Schema design approved"],
                validation_steps=["Schema structure validation"],
                rollback_plan=["Drop new schema"]
            ),
            MigrationPhase(
                name="Data Transformation",
                description="Transform and migrate data to new schema",
                tables=[tm.php_table_name for tm in table_migrations],
                estimated_duration="2-5 days",
                prerequisites=["New schema ready"],
                validation_steps=["Data transformation validation"],
                rollback_plan=["Clear transformed data"]
            ),
            MigrationPhase(
                name="System Cutover",
                description="Switch system to use new schema",
                estimated_duration="4-8 hours",
                prerequisites=["Data transformation complete"],
                validation_steps=["System functionality test"],
                rollback_plan=["Switch back to original schema"]
            )
        ]
    
    def _plan_validation_strategy(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Plan comprehensive validation strategy."""
        return {
            'pre_migration_validation': [
                'Verify data backup integrity',
                'Test migration scripts on sample data',
                'Validate schema mapping accuracy',
                'Check constraint definitions'
            ],
            'during_migration_validation': [
                'Monitor row count consistency',
                'Validate data type conversions',
                'Check referential integrity',
                'Monitor migration performance'
            ],
            'post_migration_validation': [
                'Complete row count validation',
                'Data integrity verification',
                'Performance baseline comparison',
                'Functional testing of all features',
                'Security validation'
            ],
            'automated_tests': [
                'Data comparison scripts',
                'Schema validation tests',
                'Performance benchmark tests',
                'API functionality tests'
            ],
            'manual_validation': [
                'Spot-check critical data',
                'Verify complex relationships',
                'Test edge cases',
                'User acceptance testing'
            ]
        }
    
    def _plan_rollback_strategy(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Plan comprehensive rollback strategy."""
        return {
            'trigger_conditions': [
                'Data integrity issues discovered',
                'Performance degradation beyond acceptable limits',
                'Critical functionality broken',
                'Migration timeline exceeded significantly'
            ],
            'rollback_procedures': [
                'Stop all migration processes',
                'Restore from backup if necessary',
                'Switch application back to original database',
                'Verify original functionality',
                'Document issues for future analysis'
            ],
            'recovery_time_objective': '2 hours',
            'recovery_point_objective': '0 data loss',
            'testing_requirements': [
                'Test rollback procedures in staging',
                'Verify backup restoration process',
                'Document rollback decision tree'
            ]
        }
    
    def _assess_migration_risks(self, plan: MigrationPlan, 
                               database_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with the migration."""
        risks = {
            'high_risks': [],
            'medium_risks': [],
            'low_risks': [],
            'mitigation_strategies': []
        }
        
        # Assess based on data size
        total_tables = len(plan.table_migrations)
        if total_tables > 50:
            risks['high_risks'].append('Large number of tables may cause extended downtime')
        
        # Assess based on complexity
        complex_tables = [tm for tm in plan.table_migrations if tm.migration_complexity == 'high']
        if len(complex_tables) > 5:
            risks['high_risks'].append('Multiple complex tables increase migration risk')
        
        # Assess based on relationships
        total_relationships = len(plan.relationship_mappings)
        if total_relationships > 20:
            risks['medium_risks'].append('Complex relationship structure may cause data integrity issues')
        
        # General risks
        risks['medium_risks'].extend([
            'Schema changes may break existing queries',
            'Data type conversions may cause data loss',
            'Performance characteristics may change'
        ])
        
        risks['low_risks'].extend([
            'Temporary performance impact during migration',
            'Need for additional testing time',
            'Potential for minor data formatting issues'
        ])
        
        # Mitigation strategies
        risks['mitigation_strategies'].extend([
            'Comprehensive backup strategy',
            'Thorough testing in staging environment',
            'Gradual migration approach for large datasets',
            'Real-time monitoring during migration',
            'Quick rollback procedures'
        ])
        
        return risks
    
    def _estimate_total_duration(self, plan: MigrationPlan) -> str:
        """Estimate total migration duration."""
        if plan.strategy == MigrationStrategy.DIRECT_CONVERSION:
            return "1-2 days"
        elif plan.strategy == MigrationStrategy.GRADUAL_MIGRATION:
            return "2-4 weeks"
        elif plan.strategy == MigrationStrategy.DUAL_WRITE:
            return "3-6 weeks"
        else:  # SCHEMA_RECREATION
            return "1-2 weeks"
    
    def _estimate_downtime(self, plan: MigrationPlan, strategy: MigrationStrategy) -> str:
        """Estimate required downtime."""
        if strategy == MigrationStrategy.DUAL_WRITE:
            return "Minimal (15-30 minutes for cutover)"
        elif strategy == MigrationStrategy.GRADUAL_MIGRATION:
            return "Low (2-4 hours total across phases)"
        elif strategy == MigrationStrategy.DIRECT_CONVERSION:
            return "High (8-12 hours)"
        else:  # SCHEMA_RECREATION
            return "Medium (4-8 hours)"
    
    def _generate_migration_recommendations(self, plan: MigrationPlan, 
                                          database_analysis: Dict[str, Any]) -> List[str]:
        """Generate migration recommendations."""
        recommendations = []
        
        # Strategy-specific recommendations
        if plan.strategy == MigrationStrategy.DIRECT_CONVERSION:
            recommendations.append("Test migration process multiple times in staging environment")
            recommendations.append("Plan for extended downtime window")
        elif plan.strategy == MigrationStrategy.GRADUAL_MIGRATION:
            recommendations.append("Implement comprehensive monitoring for each phase")
            recommendations.append("Plan for data synchronization between old and new systems")
        
        # General recommendations
        recommendations.extend([
            "Create comprehensive data backups before starting migration",
            "Implement automated validation scripts for data integrity",
            "Plan for rollback scenarios at each phase",
            "Monitor performance closely during and after migration",
            "Document all schema changes and transformations",
            "Train team on new database structure and models",
            "Plan for user communication about potential downtime"
        ])
        
        # Complexity-based recommendations
        complexity_level = database_analysis.get('complexity_level', 'low')
        if complexity_level == 'high':
            recommendations.extend([
                "Consider hiring database migration specialists",
                "Plan for extended testing and validation period",
                "Implement additional monitoring and alerting"
            ])
        
        return recommendations
    
    def _is_python_friendly_name(self, name: str) -> bool:
        """Check if name follows Python naming conventions."""
        return name.islower() and '_' in name and not name.startswith('_')
    
    def _make_python_friendly(self, name: str) -> str:
        """Convert name to Python-friendly format."""
        # Convert camelCase to snake_case
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Remove special characters
        name = re.sub(r'[^a-z0-9_]', '_', name)
        
        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)
        
        # Remove leading/trailing underscores
        name = name.strip('_')
        
        return name
    
    def generate_alembic_migration_script(self, plan: MigrationPlan) -> str:
        """Generate Alembic migration script template."""
        script_lines = [
            '"""Migration from PHP to FastAPI"""',
            '',
            'from alembic import op',
            'import sqlalchemy as sa',
            '',
            '',
            '# revision identifiers',
            "revision = 'php_to_fastapi_001'",
            "down_revision = None",
            "branch_labels = None",
            "depends_on = None",
            '',
            '',
            'def upgrade():',
            '    """Upgrade database schema."""'
        ]
        
        # Add table creation statements
        for table_migration in plan.table_migrations:
            script_lines.extend([
                f'    # Create {table_migration.python_model_name} table',
                f"    op.create_table('{table_migration.python_table_name}',",
                "        sa.Column('id', sa.Integer(), primary_key=True),",
                "        sa.Column('created_at', sa.DateTime(), nullable=False),",
                "        sa.Column('updated_at', sa.DateTime(), nullable=True),",
                "        # Add other columns here",
                "    )",
                ""
            ])
        
        script_lines.extend([
            '',
            'def downgrade():',
            '    """Downgrade database schema."""'
        ])
        
        # Add table drop statements
        for table_migration in reversed(plan.table_migrations):
            script_lines.append(f"    op.drop_table('{table_migration.python_table_name}')")
        
        return '\n'.join(script_lines)