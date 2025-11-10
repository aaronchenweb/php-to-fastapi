graph TB
    subgraph "Stage 2: Conversion Planning"
        direction TB
        
        subgraph "1: Overall Conversion Planning ConversionPlanner"
            C1["Analyze Project Size<br/>• Total PHP files<br/>• Total endpoints<br/>• Total classes<br/>• Framework type"] --> C2["Determine Approach<br/>• FULL_REWRITE: Small projects<br/>• INCREMENTAL: Medium projects<br/>• HYBRID: Complex projects<br/>• GRADUAL_MIGRATION: Large projects"]
            C2 --> C3["Assess Complexity<br/>• Code volume factors<br/>• Framework complexity<br/>• Database complexity<br/>• API complexity<br/>• Dependency complexity"]
            C3 --> C4["Calculate Risk Score<br/>• Technical risks<br/>• Business risks<br/>• Timeline risks<br/>• Overall risk 0-10 scale"]
            C4 --> C5["Estimate Duration<br/>• Base duration by approach<br/>• Adjust for endpoints<br/>• Adjust for DB complexity<br/>• Format: weeks/months"]
            C5 --> C6["Define Conversion Phases<br/>• Foundation Setup<br/>• Database Migration<br/>• Core API Development<br/>• Feature Implementation<br/>• Testing & Validation"]
            C6 --> C7["Create Rollback Strategy<br/>• Trigger conditions<br/>• Recovery procedures<br/>• RTO/RPO objectives"]
        end
        
        subgraph "2: Project Structure Planning StructurePlanner"
            SP1["Select Template<br/>• MINIMAL: <5 files, <5 endpoints<br/>• STANDARD: Medium projects<br/>• ENTERPRISE: >50 files or >30 classes<br/>• MICROSERVICE: Domain-driven"] --> SP2["Plan Directory Structure<br/>• app/ main package<br/>• app/api/v1/endpoints/<br/>• app/core/ configuration<br/>• app/models/ database<br/>• app/schemas/ validation<br/>• app/services/ business logic"]
            SP2 --> SP3["Map PHP Sources<br/>• Controllers → endpoints<br/>• Models → models<br/>• Config → core<br/>• Tests → tests<br/>• Custom → appropriate dirs"]
            SP3 --> SP4["Plan Dynamic Files<br/>• Endpoint files by API categories<br/>• Model files by domain groups<br/>• Schema files by endpoints<br/>• Service files by business logic"]
            SP4 --> SP5["Create Migration Mapping<br/>• PHP directories → FastAPI dirs<br/>• File organization patterns<br/>• Structure recommendations"]
            SP5 --> SP6["Generate File Plans<br/>• File names and paths<br/>• Content types<br/>• Template assignments<br/>• PHP source mappings"]
        end
        
        subgraph "3: Dependency Planning DependencyPlanner"
            DP1["Analyze Requirements<br/>• Web framework: FastAPI<br/>• Database: from analysis<br/>• Authentication: from endpoints<br/>• File uploads: from routes<br/>• Background tasks: from deps<br/>• Caching: from Redis usage"] --> DP2["Plan Core Dependencies<br/>• fastapi>=0.104.0<br/>• uvicorn[standard]>=0.24.0<br/>• pydantic>=2.5.0<br/>• python-multipart>=0.0.6"]
            DP2 --> DP3["Plan Database Dependencies<br/>• MySQL: mysql-connector-python<br/>• PostgreSQL: psycopg2-binary<br/>• MongoDB: motor<br/>• SQLAlchemy + Alembic<br/>• Redis: redis"]
            DP3 --> DP4["Plan Auth Dependencies<br/>• JWT: python-jose[cryptography]<br/>• Passwords: passlib[bcrypt]<br/>• OAuth: authlib<br/>• Encryption: cryptography"]
            DP4 --> DP5["Plan Utility Dependencies<br/>• HTTP: httpx<br/>• Images: pillow<br/>• Excel: openpyxl + pandas<br/>• PDF: reportlab<br/>• Email: fastapi-mail<br/>• Tasks: celery"]
            DP5 --> DP6["Plan Dev Dependencies<br/>• Testing: pytest + pytest-asyncio<br/>• Formatting: black + isort<br/>• Linting: flake8<br/>• Type checking: mypy<br/>• Git hooks: pre-commit"]
            DP6 --> DP7["Create Dependency Groups<br/>• Core Web Framework<br/>• Database<br/>• Authentication & Security<br/>• Utilities<br/>• Development Tools<br/>• Optional Enhancements"]
            DP7 --> DP8["Detect Conflicts<br/>• Mutually exclusive packages<br/>• Version compatibility<br/>• Pydantic v2 compatibility<br/>• Generate requirements files"]
        end
        
        subgraph "4: Database Migration Planning MigrationPlanner"
            MP1["Determine Strategy<br/>• DIRECT_CONVERSION: Low complexity<br/>• SCHEMA_RECREATION: Medium complexity<br/>• GRADUAL_MIGRATION: Many tables<br/>• DUAL_WRITE: High complexity"] --> MP2["Plan Table Migrations<br/>• Priority: High/Medium/Low<br/>• Complexity assessment<br/>• Schema changes needed<br/>• Data transformations<br/>• Validation queries"]
            MP2 --> MP3["Create Schema Mappings<br/>• PHP types → SQLAlchemy types<br/>• int → Integer<br/>• varchar → String<br/>• datetime → DateTime<br/>• json → JSON<br/>• Column transformations"]
            MP3 --> MP4["Plan Relationships<br/>• hasOne → one_to_one<br/>• hasMany → one_to_many<br/>• belongsTo → many_to_one<br/>• belongsToMany → many_to_many<br/>• Generate relationship code"]
            MP4 --> MP5["Define Migration Phases<br/>• Preparation: Backup & environment<br/>• Schema Migration: Structure creation<br/>• Data Migration: Data transfer<br/>• Validation: Integrity checks<br/>• Or gradual/dual-write phases"]
            MP5 --> MP6["Plan Validation Strategy<br/>• Pre-migration checks<br/>• During-migration monitoring<br/>• Post-migration validation<br/>• Automated test scripts<br/>• Manual validation steps"]
            MP6 --> MP7["Create Rollback Plan<br/>• Trigger conditions<br/>• Rollback procedures<br/>• Recovery time objectives<br/>• Data recovery methods<br/>• Testing requirements"]
        end
        
        subgraph "5: Configuration & Testing Planning"
            CT1["Plan Configuration<br/>• Environment variables<br/>• DATABASE_URL<br/>• SECRET_KEY<br/>• DEBUG mode<br/>• CORS_ORIGINS"] --> CT2["Plan Config Files<br/>• .env for variables<br/>• app/core/config.py<br/>• Pydantic Settings<br/>• Configuration strategy"]
            CT2 --> CT3["Plan Testing Strategy<br/>• Framework: pytest<br/>• Types: unit/integration/api<br/>• Coverage target: 80-90%<br/>• Testing tools<br/>• Test structure"]
        end
    end
    
    subgraph "Data Integration & Compilation"
        INT1["Compile Planning Data<br/>• Conversion strategy dict<br/>• Project structure dict<br/>• Dependency conversion dict<br/>• Database migration plan dict<br/>• Configuration strategy dict<br/>• Testing strategy dict"] --> INT2["Generate Overall Recommendations<br/>• Top recommendations from each planner<br/>• Remove duplicates<br/>• Prioritize by importance<br/>• Limit to top 10"]
        INT2 --> INT3["Display Local Planning Results<br/>• Conversion strategy summary<br/>• Project structure overview<br/>• Dependency planning stats<br/>• Database migration plan<br/>• Key recommendations"]
        INT3 --> INT4["User Confirmation<br/>Send to LLM for enhancement?"]
    end
    
    subgraph "LLM Enhancement Process"
        LLM1["Prepare LLM Prompts<br/>• System prompt<br/>• Planning prompt with<br/>  analysis_result + local_planning"] --> LLM2["Send to LLM<br/>• Generate response<br/>• Parse JSON response<br/>• Handle errors with fallback"]
        LLM2 --> LLM3["Display LLM Results<br/>• Enhanced conversion strategy<br/>• API conversion plan details<br/>• Database migration plan<br/>• LLM improvements"]
        LLM3 --> LLM4["Display Comparison<br/>• Approach differences<br/>• Duration estimate differences<br/>• Risk assessment comparison<br/>• LLM enhancements highlight<br/>• Critical points identification"]
        LLM4 --> LLM5["Return Final Planning<br/>• LLM-enhanced planning OR<br/>• Converted local planning<br/>• Ready for Generation Stage"]
    end
    
    subgraph "Fallback & Error Handling"
        FB1["LLM Enhancement Skipped"] --> FB2["Convert Local to LLM Format<br/>• Map conversion_strategy<br/>• Map project_structure<br/>• Add default api_conversion_plan<br/>• Add default deployment_considerations<br/>• Add default implementation_notes"]
        FB2 --> FB3["Return Converted Planning<br/>• Compatible with Generation Stage<br/>• All required fields present<br/>• Default values for missing data"]
    end
    
    %% Connect the main flows
    C7 --> INT1
    SP6 --> INT1
    DP8 --> INT1
    MP7 --> INT1
    CT3 --> INT1
    
    INT4 -->|Yes| LLM1
    INT4 -->|No| FB1
    
    LLM2 -->|Success| LLM3
    LLM2 -->|Failure| FB1
    
    LLM5 --> RESULT["Planning Complete<br/>Ready for Generation Stage"]
    FB3 --> RESULT
    
    %% Styling
    classDef conversion fill:#e3f2fd,color:#000
    classDef structure fill:#f3e5f5,color:#000
    classDef dependency fill:#e8f5e8,color:#000
    classDef migration fill:#fff3e0,color:#000
    classDef config fill:#fce4ec,color:#000
    classDef integration fill:#f1f8e9,color:#000
    classDef llm fill:#e1f5fe,color:#000
    classDef fallback fill:#ffebee,color:#000
    
    class C1,C2,C3,C4,C5,C6,C7 conversion
    class SP1,SP2,SP3,SP4,SP5,SP6 structure
    class DP1,DP2,DP3,DP4,DP5,DP6,DP7,DP8 dependency
    class MP1,MP2,MP3,MP4,MP5,MP6,MP7 migration
    class CT1,CT2,CT3 config
    class INT1,INT2,INT3,INT4 integration
    class LLM1,LLM2,LLM3,LLM4,LLM5 llm
    class FB1,FB2,FB3 fallback