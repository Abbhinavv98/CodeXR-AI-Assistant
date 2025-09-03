# 🚀 CodeXR: AI Assistant for AR/VR Developers

**CodeXR** is an AI-powered coding assistant tailored for **AR/VR developers** working in **Unity, Unreal Engine, and Shaders**.  
It reduces time spent on documentation hunting, debugging, and repetitive coding tasks by providing:

- ✅ Step-by-step subtasks  
- ✅ Ready-to-paste code snippets (Unity C#, Unreal C++, Shaders)  
- ✅ Best practices & common pitfalls  
- ✅ Grounded documentation/tutorial links  
- ✅ Developer-friendly **Streamlit UI**  

---

## 📸 Preview (Demo UI)
*(Add screenshots or demo GIFs here once available)*  

---

## 🔧 Tech Stack
- **Frontend/UI:** Streamlit  
- **LLM Backend:** Gemini 2.5 / GPT-4o-mini / StarCoder2 (open-source alternative)  
- **Speech-to-Text (Optional):** Whisper  
- **Web Search Agent:** Bing/Serper API via LangChain  
- **JSON Validation:** Pydantic / Structured Prompting  

---

## ⚡ Features
- Text-first (voice optional) query system for Unity/Unreal/Shader help  
- Structured JSON outputs with subtasks, snippets, docs, difficulty rating  
- Context-aware responses with grounded external references  
- Demo-ready Streamlit UI for AR/VR coding workflows  

---

## 🎯 Roadmap
### Phase 1 (MVP) – ✅
- Streamlit-based demo UI  
- Unity, Unreal, Shader coding scenarios  
- Subtasks + snippets + best practices  

### Phase 2 – 🔄 In Progress
- **RAG-lite doc retriever** (Unity XR Toolkit, Unreal Engine docs, shader refs)  
- **Debugging Mode** (paste error logs → get fix suggestions)  

### Phase 3 – 📌 Planned
- **VS Code Extension** with “Ask CodeXR” command  
- Inline snippet insertion  
- Error explanation & debugging support  

---

## 📌 Example Queries
- **Unity:** *“How do I add teleport locomotion in Unity VR?”*  
- **Unreal:** *“How do I set up multiplayer in Unreal VR?”*  
- **Shader:** *“Which shader works best for AR occlusion?”*  

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Abbhinavv98/CodeXR-AI-Assistant.git
cd CodeXR-AI-Assistant

