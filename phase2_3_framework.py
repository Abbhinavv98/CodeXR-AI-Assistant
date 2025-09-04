"""
CodeXR Phase 2 & 3 Framework Implementation
Phase 2: RAG-Lite & Debugging Mode
Phase 3: VS Code Extension
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional

class RAGLiteRetriever:
    """
    RAG-Lite Documentation Retriever for offline documentation access
    Indexes Unity XR Toolkit, Unreal Engine docs, and shader references
    """
    
    def __init__(self, db_path: str = "codexr_rag.db"):
        self.db_path = db_path
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize SQLite database for document storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retrieval_cache (
                query_hash TEXT PRIMARY KEY,
                results BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def index_documentation(self, documents: List[Dict[str, Any]]):
        """Index documentation for offline retrieval"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for doc in documents:
            cursor.execute("""
                INSERT INTO documents (title, content, source, category, url)
                VALUES (?, ?, ?, ?, ?)
            """, (
                doc['title'],
                doc['content'],
                doc['source'],
                doc['category'],
                doc.get('url', '')
            ))
        
        conn.commit()
        conn.close()
        print(f"Indexed {len(documents)} documents")
    
    def retrieve_relevant_docs(self, query: str, category: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documentation paragraphs offline"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query with simple text matching
        if category:
            cursor.execute("""
                SELECT * FROM documents 
                WHERE category = ? AND (content LIKE ? OR title LIKE ?)
                ORDER BY id DESC LIMIT ?
            """, (category, f"%{query}%", f"%{query}%", top_k))
        else:
            cursor.execute("""
                SELECT * FROM documents 
                WHERE content LIKE ? OR title LIKE ?
                ORDER BY id DESC LIMIT ?
            """, (f"%{query}%", f"%{query}%", top_k))
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'source': row[3],
                'category': row[4],
                'url': row[5] or '',
                'similarity': 0.8  # Mock similarity score
            })
        
        conn.close()
        return results

class ErrorDebugger:
    """
    Error Debugging Mode - interprets error logs and provides fixes
    Example: NullReferenceException: TeleportationProvider not set -> "Assign TeleportationProvider in Inspector"
    """
    
    def __init__(self):
        self.error_patterns = {
            "NullReferenceException": {
                "teleportationprovider": {
                    "analysis": "TeleportationProvider component is not assigned",
                    "fix": "Assign TeleportationProvider in the Inspector or via script",
                    "code_fix": "teleportProvider = FindObjectOfType<TeleportationProvider>();",
                    "prevention": ["Always check for null references", "Use [RequireComponent] attribute"]
                }
            },
            "MissingComponentException": {
                "general": {
                    "analysis": "Required component is missing from GameObject",
                    "fix": "Add the missing component via Inspector or AddComponent<T>()",
                    "code_fix": "gameObject.AddComponent<RequiredComponent>();",
                    "prevention": ["Use [RequireComponent] attribute", "Validate components in OnValidate()"]
                }
            }
        }
    
    def debug_error(self, error_log: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Debug an error log and provide fix recommendations"""
        
        error_log_lower = error_log.lower()
        
        # Simple pattern matching
        if "nullreferenceexception" in error_log_lower:
            if "teleportationprovider" in error_log_lower:
                pattern = self.error_patterns["NullReferenceException"]["teleportationprovider"]
                return {
                    "error_type": "NullReferenceException",
                    "error_analysis": pattern["analysis"],
                    "likely_fix": pattern["fix"],
                    "code_fix": pattern["code_fix"],
                    "prevention_tips": pattern["prevention"]
                }
        
        # Generic response
        return {
            "error_type": "Unknown",
            "error_analysis": "Check Unity Console for detailed error information",
            "likely_fix": "Review stack trace and add proper null checks",
            "code_fix": "// Add appropriate error handling here",
            "prevention_tips": ["Enable detailed logging", "Use try-catch blocks"]
        }

class VSCodeExtensionFramework:
    """
    VS Code Extension Framework for native IDE integration
    Provides structure for "Ask CodeXR" command, side panel, and snippet insertion
    """
    
    def __init__(self):
        self.extension_manifest = {
            "name": "codexr",
            "displayName": "CodeXR - AI Coding Assistant for AR/VR",
            "description": "AI-powered coding assistant for Unity, Unreal, and shader development",
            "version": "1.0.0",
            "engines": {"vscode": "^1.60.0"},
            "categories": ["Other"],
            "activationEvents": ["onCommand:codexr.askQuestion"],
            "main": "./out/extension.js",
            "contributes": {
                "commands": [{
                    "command": "codexr.askQuestion",
                    "title": "Ask CodeXR",
                    "category": "CodeXR"
                }]
            }
        }
    
    def generate_extension_files(self, output_dir: str = "vscode-extension"):
        """Generate VS Code extension files"""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            os.makedirs(f"{output_dir}/src")
        
        # Package.json
        with open(f"{output_dir}/package.json", "w") as f:
            json.dump(self.extension_manifest, f, indent=2)
        
        # Main extension file
        extension_ts = '''import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('CodeXR extension is now active!');
    
    const askCommand = vscode.commands.registerCommand('codexr.askQuestion', () => {
        vscode.window.showInputBox({
            prompt: 'Ask CodeXR about AR/VR development'
        }).then(query => {
            if (query) {
                vscode.window.showInformationMessage(`CodeXR: Processing "${query}"`);
            }
        });
    });
    
    context.subscriptions.push(askCommand);
}

export function deactivate() {}'''
        
        with open(f"{output_dir}/src/extension.ts", "w") as f:
            f.write(extension_ts)
        
        print(f"VS Code extension files generated in {output_dir}")

def setup_phase2_rag() -> RAGLiteRetriever:
    """Setup Phase 2 RAG-Lite system with sample docs"""
    retriever = RAGLiteRetriever()
    
    # Sample documentation
    sample_docs = [
        {
            "title": "Unity VR Teleportation Setup", 
            "content": "To set up teleportation in Unity VR, install XR Interaction Toolkit, create XR Origin, add TeleportationProvider component, and configure teleport areas with NavMesh.",
            "source": "Unity Documentation",
            "category": "Unity",
            "url": "https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.5/manual/teleportation.html"
        },
        {
            "title": "Unreal VR Multiplayer Setup",
            "content": "Setting up VR multiplayer in Unreal Engine requires enabling VR template, configuring network settings, creating custom game mode, and implementing proper pawn replication.",
            "source": "Unreal Documentation", 
            "category": "Unreal",
            "url": "https://docs.unrealengine.com/5.0/en-us/multiplayer-programming-quick-start-for-unreal-engine/"
        },
        {
            "title": "AR Occlusion Shaders",
            "content": "AR occlusion shaders write to depth buffer without visible output. Use ZWrite On, ZTest LEqual, ColorMask 0, and Queue Geometry-1 for proper rendering order.",
            "source": "Shader Documentation",
            "category": "Shader", 
            "url": "https://docs.unity3d.com/Manual/SL-ShaderReplacement.html"
        }
    ]
    
    retriever.index_documentation(sample_docs)
    return retriever

def setup_phase3_vscode() -> VSCodeExtensionFramework:
    """Setup Phase 3 VS Code extension framework"""
    framework = VSCodeExtensionFramework()
    framework.generate_extension_files()
    return framework

# Export classes
__all__ = ['RAGLiteRetriever', 'ErrorDebugger', 'VSCodeExtensionFramework', 'setup_phase2_rag', 'setup_phase3_vscode']
