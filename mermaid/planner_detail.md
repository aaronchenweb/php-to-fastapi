flowchart TD
    Start[PlanningStage Entry Point] --> Init[PlanningStage init method]
    
    Init --> InitPlanners[Initialize Modular Planners]
    InitPlanners --> CP[Create ConversionPlanner]
    InitPlanners --> SP[Create StructurePlanner]
    InitPlanners --> DP[Create DependencyPlanner]
    InitPlanners --> MP[Create MigrationPlanner]
    
    CP --> Ready[Planners Ready]
    SP --> Ready
    DP --> Ready
    MP --> Ready
    
    Ready --> LocalPlanning[prepare_local_planning<br/>with analysis_result]
    
    LocalPlanning --> Debug1[DEBUG: Starting modular planning preparation]
    Debug1 --> ConvPlan[conversion_planner.create_conversion_plan<br/>with analysis_result]
    
    ConvPlan --> ConvPlanDetails[ConversionPlanner determines:<br/>• Conversion approach enum<br/>• Complexity level assessment<br/>• Risk assessment with scores<br/>• Duration estimation<br/>• Conversion phases with deliverables<br/>• Prerequisites and success criteria<br/>• Rollback strategy]
    
    ConvPlanDetails --> Debug2[DEBUG: Planning project structure]
    Debug2 --> StructPlan[structure_planner.plan_structure<br/>with analysis_result]
    
    StructPlan --> StructPlanDetails[StructurePlanner determines:<br/>• Template selection minimal/standard/enterprise<br/>• Directory structure with purposes<br/>• File plans with PHP mappings<br/>• Migration mapping PHP to FastAPI<br/>• Structure recommendations]
    
    StructPlanDetails --> Debug3[DEBUG: Planning dependencies]
    Debug3 --> DepPlan[dependency_planner.plan_dependencies<br/>with analysis_result]
    
    DepPlan --> DepPlanDetails[DependencyPlanner determines:<br/>• Requirement analysis from PHP<br/>• Core/Database/Auth/Utility deps<br/>• Dependency groups with priorities<br/>• Conflict detection<br/>• Requirements.txt generation<br/>• Migration notes]
    
    DepPlanDetails --> Debug4[DEBUG: Planning database migration]
    Debug4 --> MigPlan[migration_planner.plan_migration<br/>with analysis_result]
    
    MigPlan --> MigPlanDetails[MigrationPlanner determines:<br/>• Migration strategy enum<br/>• Data migration approach<br/>• Table-by-table migration plans<br/>• Schema mappings PHP to Python<br/>• Migration phases with validation<br/>• Risk assessment and rollback]
    
    MigPlanDetails --> Debug5[DEBUG: Planning configuration and testing]
    Debug5 --> ConfigTest[plan_configuration_approach<br/>plan_testing_approach]
    
    ConfigTest --> ConfigDetails[Configuration Planning:<br/>• Environment variables list<br/>• Config file structures<br/>• Pydantic settings strategy]
    
    ConfigTest --> TestDetails[Testing Planning:<br/>• Framework selection pytest<br/>• Test types unit/integration/api<br/>• Coverage targets<br/>• Testing tools recommendations]
    
    ConfigDetails --> CompileData[Compile Comprehensive Planning Data]
    TestDetails --> CompileData
    
    CompileData --> PlanningData[planning_data contains:<br/>conversion_strategy dict<br/>project_structure dict<br/>dependency_conversion dict<br/>database_migration_plan dict<br/>configuration_strategy dict<br/>testing_strategy dict<br/>overall_recommendations list]
    
    PlanningData --> LocalSuccess[DEBUG: Modular planning preparation completed]
    LocalSuccess --> ReturnLocal[return planning_data]
    
    ReturnLocal --> LLMPlanning[get_llm_planning method<br/>with analysis_result and local_planning]
    
    LLMPlanning --> DisplayLocal[display_local_planning_results<br/>with local_planning]
    
    DisplayLocal --> DisplayDetails[Display Local Planning:<br/>• Conversion strategy summary<br/>• Project structure overview<br/>• Dependency planning stats<br/>• Database migration plan<br/>• Key recommendations top 5]
    
    DisplayDetails --> UserConfirm{ui.confirm<br/>Send to LLM for enhancement?}
    
    UserConfirm -->|No| SkipLLM[WARNING: LLM planning skipped]
    UserConfirm -->|Yes| SendLLM[Send to LLM]
    
    SkipLLM --> ConvertLocal[convert_local_to_llm_format<br/>with local_planning]
    ConvertLocal --> ConvertDetails[Convert to LLM Format:<br/>• Map local planning to expected JSON<br/>• Add default values for missing fields<br/>• Structure for compatibility]
    ConvertDetails --> ReturnConverted[return converted_planning]
    
    SendLLM --> GetPrompts[Get system and planning prompts<br/>with analysis_result and local_planning]
    GetPrompts --> LLMRequest[llm_client.generate_response<br/>with system_prompt and user_prompt]
    
    LLMRequest --> LLMSuccess{response.success check}
    LLMSuccess -->|No| LLMError[show_llm_error<br/>with error_message and stage planning]
    LLMError --> UseLocal[WARNING: Using local planning results only]
    UseLocal --> ConvertLocal
    
    LLMSuccess -->|Yes| ParseJSON[llm_client.parse_json_response<br/>with response]
    ParseJSON --> DisplayLLM[display_llm_planning_results<br/>with llm_planning]
    
    DisplayLLM --> LLMDisplayDetails[Display LLM Results:<br/>• Enhanced conversion strategy<br/>• API conversion plan details<br/>• Database migration plan<br/>• LLM improvements]
    
    LLMDisplayDetails --> DisplayComparison[display_planning_comparison<br/>with local_planning and llm_planning]
    
    DisplayComparison --> ComparisonDetails[Display Comparison:<br/>• Conversion approach differences<br/>• Duration estimate differences<br/>• Risk assessment comparison<br/>• LLM enhancements highlight<br/>• Critical points and breaking changes]
    
    ComparisonDetails --> LLMDebug[DEBUG: LLM planning completed]
    LLMDebug --> ReturnLLM[return llm_planning]
    
    ReturnConverted --> End[Planning Stage Complete]
    ReturnLLM --> End
    
    style Start fill:#e1f5fe,color:#000
    style End fill:#c8e6c9,color:#000
    style LocalPlanning fill:#fff3e0,color:#000
    style LLMPlanning fill:#f3e5f5,color:#000
    style ConvPlan fill:#ffebee,color:#000
    style StructPlan fill:#e8f5e8,color:#000
    style DepPlan fill:#e3f2fd,color:#000
    style MigPlan fill:#fce4ec,color:#000
    style DisplayLocal fill:#fff8e1,color:#000
    style DisplayLLM fill:#f1f8e9,color:#000
    style DisplayComparison fill:#e0f2f1,color:#000