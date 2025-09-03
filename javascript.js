class CodeXRApp {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeSpeechRecognition();
        this.loadExamples();
    }
    initializeElements() {
        this.queryInput = document.getElementById('queryInput');
        this.categorySelect = document.getElementById('categorySelect');
        this.submitBtn = document.getElementById('submitBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.exampleBtns = document.querySelectorAll('.example-btn');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultQuery = document.getElementById('resultQuery');
        this.resultCategory = document.getElementById('resultCategory');
        this.resultDifficulty = document.getElementById('resultDifficulty');
        this.resultTime = document.getElementById('resultTime');
        this.subtasksList = document.getElementById('subtasksList');
        this.codeSnippet = document.getElementById('codeSnippet');
        this.bestPracticesList = document.getElementById('bestPracticesList');
        this.gotchasList = document.getElementById('gotchasList');
        this.docLinks = document.getElementById('docLinks');
        this.jsonOutput = document.getElementById('jsonOutput');
        this.copyCodeBtn = document.getElementById('copyCodeBtn');
        this.copyJsonBtn = document.getElementById('copyJsonBtn');
        this.collapsibleElements = document.querySelectorAll('.collapsible');
    }
    initializeEventListeners() {
        this.submitBtn.addEventListener('click', () => this.handleSubmit());
        this.queryInput.addEventListener('keydown', e => {
            if(e.key === 'Enter' && e.ctrlKey) this.handleSubmit();
        });
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
        this.exampleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.queryInput.value = btn.dataset.query;
                this.categorySelect.value = btn.dataset.category;
                this.handleSubmit();
            });
        });
        this.copyCodeBtn.addEventListener('click', () => this.copyToClipboard(this.codeSnippet.textContent, this.copyCodeBtn));
        this.copyJsonBtn.addEventListener('click', () => this.copyToClipboard(this.jsonOutput.textContent, this.copyJsonBtn));
        this.collapsibleElements.forEach(element => {
            element.querySelector('.collapsible-header').addEventListener('click', () => element.classList.toggle('expanded'));
        });
    }
    initializeSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            this.voiceBtn.style.display = 'none';
            return;
        }
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';
        this.recognition.onstart = () => {
            this.isListening = true;
            this.voiceBtn.classList.add('active');
            this.voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        };
        this.recognition.onend = () => {
            this.isListening = false;
            this.voiceBtn.classList.remove('active');
            this.voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        };
        this.recognition.onresult = event => {
            this.queryInput.value = event.results[0][0].transcript;
        };
        this.recognition.onerror = e => {
            console.error('Speech recognition error:', e.error);
            this.showNotification('Speech recognition failed. Please try again.', 'error');
        };
    }
    async handleSubmit() {
        const query = this.queryInput.value.trim();
        if (!query) {
            this.showNotification('Please enter a query', 'warning');
            return;
        }
        const category = this.categorySelect.value || null;
        this.showLoading();
        this.hideResults();
        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({query, category})
            });
            if (!res.ok) throw new Error(res.statusText);
            const data = await res.json();
            this.displayResults(data);
        } catch(e) {
            this.showNotification('Failed to process query. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }
    displayResults(data) {
        this.resultQuery.textContent = data.query;
        this.resultCategory.textContent = data.category;
        this.resultDifficulty.textContent = `Difficulty: ${this.getDifficultyText(data.difficulty_rating)}`;
        this.resultTime.textContent = data.estimated_time;
        this.displaySubtasks(data.subtasks);
        this.displayCodeSnippet(data.code_snippet, data.category);
        this.displayList(this.bestPracticesList, data.best_practices);
        this.displayList(this.gotchasList, data.gotchas);
        this.displayDocLinks(data.documentation_links);
        this.displayJsonOutput(data);
        this.showResults();
        this.resultsSection.scrollIntoView({behavior: 'smooth', block: 'start'});
    }
    displaySubtasks(subtasks) {
        this.subtasksList.innerHTML = '';
        subtasks.forEach((task, i) => {
            const el = document.createElement('div');
            el.className = 'subtask-item';
            el.innerHTML = `<div class="subtask-header"><div class="subtask-number">${i+1}</div><div class="subtask-title">${task.description}</div></div>
                            ${task.explanation ? `<div class="subtask-explanation">${task.explanation}</div>` : ''}
                            ${task.code_snippet ? `<pre class="subtask-code"><code>${task.code_snippet}</code></pre>` : ''}`;
            this.subtasksList.appendChild(el);
        });
    }
    displayCodeSnippet(code, category) {
        const lang = category === 'Unreal' ? 'cpp' : category === 'Shader' ? 'glsl' : 'csharp';
        this.codeSnippet.className = `language-${lang}`;
        this.codeSnippet.textContent = code;
        Prism.highlightElement(this.codeSnippet);
    }
    displayList(elem, items) {
        elem.innerHTML = '';
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            elem.appendChild(li);
        });
    }
    displayDocLinks(links) {
        this.docLinks.innerHTML = '';
        links.forEach(link => {
            const a = document.createElement('a');
            a.href = link;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.className = 'doc-link';
            a.innerHTML = `<i class="fas fa-external-link-alt"></i> ${link}`;
            this.docLinks.appendChild(a);
        });
    }
    displayJsonOutput(data) {
        this.jsonOutput.textContent = JSON.stringify(data, null, 2);
        Prism.highlightElement(this.jsonOutput);
    }
    getDifficultyText(rating) {
        const map = {1: '⭐ Beginner', 2:'⭐⭐ Easy', 3:'⭐⭐⭐ Intermediate', 4:'⭐⭐⭐⭐ Advanced', 5:'⭐⭐⭐⭐⭐ Expert'};
        return map[rating] || '⭐⭐⭐ Intermediate';
    }
    showLoading() {
        document.getElementById('loadingIndicator').classList.remove('hidden');
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    }
    hideLoading() {
        document.getElementById('loadingIndicator').classList.add('hidden');
        this.submitBtn.disabled = false;
        this.submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Ask CodeXR';
    }
    showResults() {
        this.resultsSection.classList.remove('hidden');
    }
    hideResults() {
        this.resultsSection.classList.add('hidden');
    }
    toggleVoiceInput() {
        if (this.recognition) {
            if (this.isListening) this.recognition.stop();
            else this.recognition.start();
        }
    }
    copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            button.classList.add('copied');
            setTimeout(() => button.classList.remove('copied'), 2000);
        });
    }
    showNotification(message, type) {
        alert(message); // simplified for brevity
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.codeXRApp = new CodeXRApp();
});
