document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeUrlBtn = document.getElementById('analyzeUrlBtn');
    const emailText = document.getElementById('emailText');
    const urlText = document.getElementById('urlText');
    const resultSection = document.getElementById('resultSection');
    const loadingSection = document.getElementById('loadingSection');
    const errorSection = document.getElementById('errorSection');
    const tabs = document.querySelectorAll('.tab-link');

    // --- Event Listeners ---
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(tabId).classList.add('active');
            hideAllSections();
        });
    });
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', () => analyze('email'));
    }
    
    if (analyzeUrlBtn) {
        analyzeUrlBtn.addEventListener('click', () => analyze('url'));
    }

    // --- Main Analysis Function ---
    async function analyze(type) {
        let text, endpoint, inputElement;

        if (type === 'email') {
            text = emailText.value.trim();
            endpoint = '/detect';
            inputElement = emailText;
        } else {
            text = urlText.value.trim();
            endpoint = '/detect_url'; // New endpoint for URL analysis
            inputElement = urlText;
        }

        if (!text) {
            showError(`Please enter a ${type} to analyze`);
            inputElement.classList.add('shake');
            setTimeout(() => inputElement.classList.remove('shake'), 500);
            return;
        }
        
        hideAllSections();
        loadingSection.classList.remove('hidden');
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            if (!response.ok) {
                throw new Error('Analysis failed');
            }
            
            const result = await response.json();
            displayResult(result);

        } catch (error) {
            console.error('Error:', error);
            showError('Failed to analyze. Please try again.');
        }
    }

    // --- UI Update Functions ---
    function displayResult(result) {
        hideAllSections();
        
        const resultCard = document.getElementById('resultCard');
        const resultIcon = document.getElementById('resultIcon');
        const resultTitle = document.getElementById('resultTitle');
        const confidence = document.getElementById('confidence');
        const modelStage = document.getElementById('modelStage');
        const resultMessage = document.getElementById('resultMessage');
        
        if (result.prediction === 'Phishing') {
            resultCard.className = 'result-card phishing';
            resultIcon.textContent = '⚠️';
            resultTitle.textContent = '🚨 Phishing Detected!';
            resultMessage.innerHTML = `<strong>Warning!</strong> This content shows signs of a phishing attempt.`;
        } else {
            resultCard.className = 'result-card legitimate';
            resultIcon.textContent = '✅';
            resultTitle.textContent = '✨ Legitimate Content';
            resultMessage.innerHTML = `<strong>Safe!</strong> This content appears to be legitimate.`;
        }
        
        confidence.textContent = (result.confidence * 100).toFixed(1) + '%';
        modelStage.textContent = result.model_stage;
        
        resultSection.classList.remove('hidden');
    }
    
    function showError(message) {
        hideAllSections();
        document.getElementById('errorMessage').textContent = '❌ ' + message;
        errorSection.classList.remove('hidden');
    }
    
    function hideAllSections() {
        resultSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
        errorSection.classList.add('hidden');
    }
});
