from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict

app = FastAPI(title="CodeXR - AI Coding Assistant for AR/VR Developers")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data models
class QueryRequest(BaseModel):
    query: str
    category: Optional[str] = None

class SubTask(BaseModel):
    description: str
    code_snippet: Optional[str] = None
    explanation: Optional[str] = None

class CodeXRResponse(BaseModel):
    query: str
    category: str
    subtasks: List[SubTask]
    code_snippet: str
    best_practices: List[str]
    gotchas: List[str]
    difficulty_rating: int
    documentation_links: List[str]
    estimated_time: str

# Mock knowledge bases (Unity, Unreal, Shader)
UNITY_KNOWLEDGE = {
    "teleport": {
        "subtasks": [
            {"description": "Set up XR Interaction Toolkit", "code_snippet": "// Install XR Interaction Toolkit package via Package Manager"},
            {"description": "Create XR Origin (Camera Rig)", "code_snippet": "GameObject.Find(\"XR Origin\")"},
            {"description": "Add Teleportation Provider", "code_snippet": "GetComponent<TeleportationProvider>()"},
            {"description": "Configure Teleport Areas", "code_snippet": "// Add TeleportationArea components to valid surfaces"}
        ],
        "main_code": """using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

public class TeleportSetup : MonoBehaviour
{
    public TeleportationProvider teleportProvider;
    public XRRayInteractor rayInteractor;
    
    void Start()
    {
        if (teleportProvider == null)
            teleportProvider = FindObjectOfType<TeleportationProvider>();
            
        if (rayInteractor != null)
        {
            rayInteractor.enableUIInteraction = false;
            rayInteractor.lineType = XRRayInteractor.LineType.ProjectileCurve;
        }
    }
}""",
        "best_practices": [
            "Use NavMesh for teleportation boundaries",
            "Provide visual feedback for valid teleport areas",
            "Consider comfort settings to reduce motion sickness",
            "Test on different VR headsets for compatibility"
        ],
        "gotchas": [
            "Ensure TeleportationProvider is assigned in the scene",
            "NavMesh must be baked for teleportation to work",
            "Ray interactor may conflict with UI interactions",
            "Performance impact on mobile VR platforms"
        ],
        "docs": [
            "https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.5/manual/teleportation.html",
            "https://docs.unity3d.com/Manual/nav-BuildingNavMesh.html"
        ]
    }
}

UNREAL_KNOWLEDGE = {
    "multiplayer": {
        "subtasks": [
            {"description": "Enable VR Template", "code_snippet": "// Create new VR project in Unreal Engine"},
            {"description": "Configure Network Settings", "code_snippet": "// Enable multiplayer in Project Settings"},
            {"description": "Setup Game Mode", "code_snippet": "// Create custom VRGameMode class"},
            {"description": "Implement Player Replication", "code_snippet": "// Configure pawn replication"}
        ],
        "main_code": """// VRGameMode.h
UCLASS()
class VRGAME_API AVRGameMode : public AGameModeBase
{
    GENERATED_BODY()
    
public:
    AVRGameMode();
    
protected:
    virtual void PostLogin(APlayerController* NewPlayer) override;
    virtual void Logout(AController* Exiting) override;
    
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    int32 MaxPlayers = 4;
};

// VRGameMode.cpp
AVRGameMode::AVRGameMode()
{
    DefaultPawnClass = AVRPawn::StaticClass();
    PlayerControllerClass = AVRPlayerController::StaticClass();
}

void AVRGameMode::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);
    UE_LOG(LogTemp, Log, TEXT("Player joined VR session"));
}""",
        "best_practices": [
            "Use dedicated servers for stable multiplayer",
            "Implement proper VR controller replication",
            "Optimize network traffic for VR-specific data",
            "Handle VR-specific player disconnections gracefully"
        ],
        "gotchas": [
            "VR pawns require special network setup",
            "Hand tracking data needs careful replication",
            "Locomotion can cause network prediction issues",
            "Performance drops significantly with multiple VR players"
        ],
        "docs": [
            "https://docs.unrealengine.com/5.0/en-us/multiplayer-programming-quick-start-for-unreal-engine/",
            "https://docs.unrealengine.com/5.0/en-us/vr-development-in-unreal-engine/"
        ]
    }
}

SHADER_KNOWLEDGE = {
    "occlusion": {
        "subtasks": [
            {"description": "Create Occlusion Shader", "code_snippet": "// Create new Unlit shader in Unity"},
            {"description": "Configure Depth Testing", "code_snippet": "// Setup depth buffer comparison"},
            {"description": "Implement Alpha Blending", "code_snippet": "// Configure transparency for occlusion"},
            {"description": "Optimize for Mobile AR", "code_snippet": "// Reduce shader complexity for mobile"}
        ],
        "main_code": """Shader "AR/OcclusionShader"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Alpha ("Alpha", Range(0,1)) = 0.5
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Geometry-1" }
        LOD 100
        
        Pass
        {
            ZWrite On
            ZTest LEqual
            ColorMask 0
            
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            
            #include "UnityCG.cginc"
            
            struct appdata
            {
                float4 vertex : POSITION;
            };
            
            struct v2f
            {
                float4 vertex : SV_POSITION;
            };
            
            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                return o;
            }
            
            fixed4 frag (v2f i) : SV_Target
            {
                return fixed4(0,0,0,0);
            }
            ENDCG
        }
    }
}""",
        "best_practices": [
            "Use depth-only rendering for performance",
            "Implement proper depth buffer management",
            "Consider mobile GPU limitations",
            "Test with different AR tracking systems"
        ],
        "gotchas": [
            "Render queue order is critical for occlusion",
            "Mobile GPUs may have depth precision issues",
            "Alpha blending can cause sorting problems",
            "Performance impact on older devices"
        ],
        "docs": [
            "https://docs.unity3d.com/Manual/SL-ShaderReplacement.html",
            "https://developers.google.com/ar/develop/unity/occlusion"
        ]
    }
}

def categorize_query(query: str) -> str:
    query_lower = query.lower()
    unity_keywords = ["unity", "c#", "xr toolkit", "teleport", "vr", "ar", "interaction"]
    unreal_keywords = ["unreal", "c++", "ue4", "ue5", "blueprint", "multiplayer"]
    shader_keywords = ["shader", "hlsl", "glsl", "material", "rendering", "occlusion"]
    scores = {
        "Unity": sum(kw in query_lower for kw in unity_keywords),
        "Unreal": sum(kw in query_lower for kw in unreal_keywords),
        "Shader": sum(kw in query_lower for kw in shader_keywords)
    }
    max_cat = max(scores, key=scores.get)
    return max_cat if scores[max_cat] > 0 else "General"

def generate_response(query: str, category: str) -> CodeXRResponse:
    knowledge_base = None
    key = None
    if category == "Unity":
        knowledge_base = UNITY_KNOWLEDGE
        for k in knowledge_base:
            if k in query.lower():
                key = k
                break
        key = key or "teleport"
    elif category == "Unreal":
        knowledge_base = UNREAL_KNOWLEDGE
        key = "multiplayer"
    elif category == "Shader":
        knowledge_base = SHADER_KNOWLEDGE
        key = "occlusion"
    else:
        return CodeXRResponse(
            query=query,
            category="General",
            subtasks=[
                SubTask(description="Choose your development platform (Unity/Unreal)",
                        explanation="Select based on your team's expertise and project requirements"),
                SubTask(description="Set up VR/AR SDK",
                        explanation="Install platform-specific SDKs and tools"),
                SubTask(description="Configure development environment",
                        explanation="Set up IDE, version control, and testing devices"),
            ],
            code_snippet="// Choose your platform and follow platform-specific setup guides",
            best_practices=[
                "Start with simple interactions before complex features",
                "Test regularly on target devices",
                "Follow platform-specific design guidelines",
                "Optimize for performance from the beginning"
            ],
            gotchas=[
                "Each platform has different performance characteristics",
                "SDK updates can break existing functionality",
                "Device compatibility varies significantly"
            ],
            difficulty_rating=3,
            documentation_links=[
                "https://docs.unity3d.com/Manual/XR.html",
                "https://docs.unrealengine.com/5.0/en-us/vr-development-in-unreal-engine/"
            ],
            estimated_time="2-4 hours for basic setup"
        )
    if knowledge_base and key in knowledge_base:
        kb_entry = knowledge_base[key]
        subtasks = [SubTask(
            description=task["description"],
            code_snippet=task.get("code_snippet"),
            explanation=f"This step is essential for {task['description'].lower()}"
        ) for task in kb_entry["subtasks"]]
        return CodeXRResponse(
            query=query,
            category=category,
            subtasks=subtasks,
            code_snippet=kb_entry["main_code"],
            best_practices=kb_entry["best_practices"],
            gotchas=kb_entry["gotchas"],
            difficulty_rating=4 if category == "Shader" else 3,
            documentation_links=kb_entry["docs"],
            estimated_time="3-6 hours" if category == "Unreal" else "1-3 hours"
        )
    return CodeXRResponse(
        query=query,
        category=category,
        subtasks=[SubTask(description="Research specific implementation", explanation="Look up official documentation")],
        code_snippet="// Implementation depends on specific requirements",
        best_practices=["Follow official guidelines", "Test thoroughly"],
        gotchas=["Implementation may vary by platform version"],
        difficulty_rating=3,
        documentation_links=["https://docs.example.com"],
        estimated_time="2-4 hours"
    )

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/api/query", response_model=CodeXRResponse)
async def process_query(request: QueryRequest):
    try:
        category = request.category or categorize_query(request.query)
        response = generate_response(request.query, category)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    return {
        "categories": ["Unity", "Unreal", "Shader", "General"],
        "examples": {
            "Unity": ["How do I add teleport locomotion in Unity VR?", "Setting up XR Interaction Toolkit"],
            "Unreal": ["How do I set up multiplayer in Unreal VR?", "VR pawn setup in UE5"],
            "Shader": ["Which shader works best for AR occlusion?", "Optimizing shaders for mobile VR"],
            "General": ["Getting started with VR development", "Choosing between Unity and Unreal"]
        }
    }
