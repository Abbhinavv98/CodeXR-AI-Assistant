const submitBtn = document.getElementById('submit-btn');
const voiceBtn = document.getElementById('voice-input-btn');
const queryTextArea = document.getElementById('query');
const resultsDiv = document.getElementById('results');

submitBtn.addEventListener('click', () => {
    const query = queryTextArea.value.trim();
    if (!query) {
        alert('Please enter a query.');
        return;
    }
    
    // Placeholder: API call to backend with query...
    displayResults(`Results for: ${query} (API integration needed)`);
});

voiceBtn.addEventListener('click', () => {
    if (!('webkitSpeechRecognition' in window)) {
        alert('Voice recognition not supported in this browser.');
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    recognition.start();
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        queryTextArea.value = transcript;
        displayResults(`Voice recognized: ${transcript}`);
    };
    
    recognition.onerror = (event) => {
        alert('Error occurred in voice recognition: ' + event.error);
    }
});

function displayResults(content) {
    resultsDiv.innerHTML = `<pre class="code-block">${content}</pre>`;
    Prism.highlightAll();
}
