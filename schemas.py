"""
CodeXR Pydantic Models for JSON Schema Validation
As specified in the document: "JSON Validation: Schema enforcement via structured prompting or Pydantic"
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class CategoryEnum(str, Enum):
    """Valid categories for AR/VR development queries"""
    UNITY = "Unity"
    UNREAL = "Unreal"
    SHADER = "Shader"
    GENERAL = "General"

class DifficultyLevel(int, Enum):
    """Difficulty ratings from 1-5 as specified in document"""
    BEGINNER = 1
    EASY = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5

class SubTask(BaseModel):
    """Individual subtask in step-by-step breakdown"""
    description: str = Field(
        ..., 
        min_length=10,
        max_length=200,
        description="Clear, actionable description of the subtask"
    )
    code_snippet: Optional[str] = Field(
        None,
        description="Ready-to-paste code snippet for this subtask"
    )
    explanation: Optional[str] = Field(
        None,
        description="Detailed explanation of why this subtask is necessary"
    )
    
    @validator('description')
    def description_must_be_actionable(cls, v):
        if not any(word in v.lower() for word in ['create', 'add', 'configure', 'setup', 'implement', 'install']):
            raise ValueError('Description must contain actionable verbs')
        return v

class CodeXRResponse(BaseModel):
    """Main response schema enforcing document specifications"""
    query: str = Field(
        ...,
        description="Original developer query"
    )
    category: CategoryEnum = Field(
        ...,
        description="Detected category (Unity/Unreal/Shader/General)"
    )
    subtasks: List[SubTask] = Field(
        ...,
        min_items=3,
        max_items=8,
        description="Step-by-step breakdown into manageable subtasks"
    )
    code_snippet: str = Field(
        ...,
        min_length=50,
        description="Main production-ready code implementation"
    )
    best_practices: List[str] = Field(
        ...,
        min_items=3,
        max_items=10,
        description="Industry best practices and expert recommendations"
    )
    gotchas: List[str] = Field(
        ...,
        min_items=2,
        max_items=8,
        description="Common pitfalls and things to watch out for"
    )
    difficulty_rating: DifficultyLevel = Field(
        ...,
        description="Complexity rating from 1 (Beginner) to 5 (Expert)"
    )
    documentation_links: List[str] = Field(
        ...,
        min_items=2,
        max_items=6,
        description="Links to official documentation and resources"
    )
    estimated_time: str = Field(
        ...,
        description="Time estimate for implementation (e.g., '2-4 hours', '1-2 days')"
    )
    
    @validator('best_practices', each_item=True)
    def validate_best_practices(cls, v):
        if len(v) < 10:
            raise ValueError('Best practices must be at least 10 characters long')
        return v
    
    @validator('gotchas', each_item=True)
    def validate_gotchas(cls, v):
        if len(v) < 15:
            raise ValueError('Gotchas must be descriptive (at least 15 characters)')
        return v
    
    @validator('documentation_links', each_item=True)
    def validate_documentation_links(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Documentation links must be valid URLs')
        return v
    
    @validator('estimated_time')
    def validate_estimated_time(cls, v):
        time_patterns = ['hour', 'day', 'week', 'minute']
        if not any(pattern in v.lower() for pattern in time_patterns):
            raise ValueError('Estimated time must include time units')
        return v

class QueryRequest(BaseModel):
    """Input request model for API endpoints"""
    query: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Developer query about AR/VR development"
    )
    category: Optional[CategoryEnum] = Field(
        None,
        description="Optional category hint (auto-detected if not provided)"
    )
    llm_backend: Optional[str] = Field(
        "Demo Mode",
        description="Preferred LLM backend (Gemini 2.5, GPT-4o-mini, StarCoder2, Demo Mode)"
    )

class SearchResult(BaseModel):
    """Web search result structure"""
    title: str = Field(..., description="Search result title")
    url: str = Field(..., description="Source URL")
    snippet: str = Field(..., description="Content snippet")
    relevance_score: Optional[float] = Field(None, ge=0, le=1, description="Relevance score 0-1")

class WebSearchResponse(BaseModel):
    """Response from web search grounding"""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    search_engine: str = Field(..., description="Search engine used (SERP/Bing)")
    timestamp: str = Field(..., description="Search timestamp")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    suggestions: List[str] = Field(default=[], description="Suggestions to fix the error")

# Phase 2 Models (RAG-Lite & Debugging Mode)
class DocumentChunk(BaseModel):
    """Document chunk for RAG-Lite implementation"""
    content: str = Field(..., description="Document content chunk")
    source: str = Field(..., description="Source document (Unity docs, Unreal docs, etc.)")
    section: str = Field(..., description="Document section")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")

class ErrorDebugRequest(BaseModel):
    """Error debugging request for Phase 2"""
    error_log: str = Field(..., min_length=10, description="Full error log to analyze")
    context: Optional[str] = Field(None, description="Additional context about when error occurred")
    platform: Optional[CategoryEnum] = Field(None, description="Platform where error occurred")

class ErrorDebugResponse(BaseModel):
    """Error debugging response for Phase 2"""
    error_analysis: str = Field(..., description="Analysis of what caused the error")
    likely_fix: str = Field(..., description="Most likely fix for the error")
    code_fix: Optional[str] = Field(None, description="Code snippet to fix the error")
    prevention_tips: List[str] = Field(..., description="Tips to prevent this error in future")

# Phase 3 Models (VS Code Extension)
class VSCodeCommand(BaseModel):
    """VS Code extension command structure"""
    command: str = Field(..., description="Command name")
    title: str = Field(..., description="Display title")
    category: str = Field(default="CodeXR", description="Command category")

class SnippetInsertRequest(BaseModel):
    """Request to insert code snippet in VS Code"""
    code: str = Field(..., description="Code to insert")
    language: str = Field(..., description="Programming language")
    position: Optional[Dict[str, int]] = Field(None, description="Cursor position")

# Validation Functions
def validate_demo_scenario(query: str) -> bool:
    """Validate if query matches required demo scenarios"""
    demo_queries = [
        "How do I add teleport locomotion in Unity VR?",
        "How do I set up multiplayer in Unreal VR?", 
        "Which shader works best for AR occlusion?"
    ]
    return query in demo_queries

def validate_success_criteria(response: CodeXRResponse) -> Dict[str, bool]:
    """Validate response against Phase 1 success criteria"""
    criteria = {
        "structured_subtasks_and_code": len(response.subtasks) >= 3 and len(response.code_snippet) >= 50,
        "grounded_in_real_docs": len(response.documentation_links) >= 2,
        "best_practices_and_difficulty": len(response.best_practices) >= 3 and response.difficulty_rating is not None,
        "ready_for_demo": response.category in [cat.value for cat in CategoryEnum]
    }
    return criteria

# Export all models
__all__ = [
    'CategoryEnum', 'DifficultyLevel', 'SubTask', 'CodeXRResponse', 
    'QueryRequest', 'SearchResult', 'WebSearchResponse', 'ErrorResponse',
    'DocumentChunk', 'ErrorDebugRequest', 'ErrorDebugResponse',
    'VSCodeCommand', 'SnippetInsertRequest',
    'validate_demo_scenario', 'validate_success_criteria'
]
