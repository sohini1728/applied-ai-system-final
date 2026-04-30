/* VibeFinder Pro Frontend JavaScript */

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadGenres();
    loadMoods();
    checkHealth();
    
    // Form submission
    document.getElementById('recommendationForm').addEventListener('submit', (e) => {
        e.preventDefault();
        getRecommendations();
    });
    
    // Energy slider sync
    document.getElementById('energy').addEventListener('input', (e) => {
        document.getElementById('energyValue').textContent = e.target.value;
    });
});

// ===== API Calls =====

async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        const healthCheck = document.getElementById('healthCheck');
        healthCheck.innerHTML = `✅ System Healthy | ${data.songsLoaded} Songs | ${data.genres} Genres`;
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

async function loadGenres() {
    try {
        const response = await fetch('/api/genres');
        const genres = await response.json();
        const select = document.getElementById('genre');
        genres.forEach(genre => {
            const option = document.createElement('option');
            option.value = genre;
            option.textContent = genre.charAt(0).toUpperCase() + genre.slice(1);
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load genres:', error);
    }
}

async function loadMoods() {
    try {
        const response = await fetch('/api/moods');
        const moods = await response.json();
        const select = document.getElementById('mood');
        moods.forEach(mood => {
            const option = document.createElement('option');
            option.value = mood;
            option.textContent = mood.charAt(0).toUpperCase() + mood.slice(1);
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load moods:', error);
    }
}

async function getRecommendations() {
    const formData = new FormData(document.getElementById('recommendationForm'));
    const data = {
        favorite_genre: formData.get('favorite_genre'),
        favorite_mood: formData.get('favorite_mood'),
        target_energy: parseFloat(formData.get('target_energy')),
        likes_acoustic: formData.get('likes_acoustic') === 'true',
    };
    
    showLoading(true);
    hideAllSections();
    
    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        
        if (!response.ok) {
            throw new Error('Failed to get recommendations');
        }
        
        const result = await response.json();
        displayRecommendations(result);
        showLoading(false);
        
    } catch (error) {
        showError(`Error: ${error.message}`);
        showLoading(false);
    }
}

async function runEvaluation() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/evaluate', {
            method: 'POST',
        });
        
        if (!response.ok) {
            throw new Error('Evaluation failed');
        }
        
        const result = await response.json();
        displayEvaluationResults(result);
        showLoading(false);
        
    } catch (error) {
        showError(`Evaluation Error: ${error.message}`);
        showLoading(false);
    }
}

// ===== Display Functions =====

function displayRecommendations(result) {
    // Show confidence and workflow
    document.getElementById('confidenceScore').textContent = (result.confidence * 100).toFixed(0) + '%';
    
    const workflowList = document.getElementById('workflowList');
    workflowList.innerHTML = '';
    result.workflowSteps.forEach((step, index) => {
        const li = document.createElement('li');
        li.textContent = `Step ${index + 1}: ${step}`;
        workflowList.appendChild(li);
    });
    
    // Display recommendations
    const recList = document.getElementById('recommendationsList');
    recList.innerHTML = '';
    result.recommendations.forEach((rec, index) => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        
        let reasonsHtml = '';
        if (rec.reasons && rec.reasons.length > 0) {
            reasonsHtml = `<ul class="reasons-list">
                ${rec.reasons.map(reason => `<li>${reason}</li>`).join('')}
            </ul>`;
        }
        
        card.innerHTML = `
            <h4>${index + 1}. ${rec.title}</h4>
            <div class="recommendation-meta">
                <span class="meta-item">🎤 ${rec.artist}</span>
                <span class="meta-item">🎵 ${rec.genre}</span>
                <span class="meta-item">😊 ${rec.mood}</span>
                <span class="meta-item">⚡ ${(rec.energy * 100).toFixed(0)}%</span>
                <span class="score-badge">Score: ${rec.score}</span>
                <span class="source-badge">${rec.source}</span>
            </div>
            ${reasonsHtml}
        `;
        recList.appendChild(card);
    });
    
    // Display reasoning
    document.getElementById('reasoningText').textContent = result.reasoning;
    
    // Show sections
    document.getElementById('workflowSection').classList.remove('hidden');
    document.getElementById('recommendationsSection').classList.remove('hidden');
    document.getElementById('reasoningSection').classList.remove('hidden');
    document.getElementById('emptyState').classList.add('hidden');
}

function displayEvaluationResults(result) {
    const metricsGrid = document.getElementById('metricsGrid');
    metricsGrid.innerHTML = `
        <div class="metric-card">
            <div class="metric-value">${(result.metricsAveraged.diversity * 100).toFixed(0)}%</div>
            <div class="metric-label">Diversity</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${(result.metricsAveraged.relevance * 100).toFixed(0)}%</div>
            <div class="metric-label">Relevance</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${(result.metricsAveraged.novelty * 100).toFixed(0)}%</div>
            <div class="metric-label">Novelty</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${(result.metricsAveraged.calibration * 100).toFixed(0)}%</div>
            <div class="metric-label">Calibration</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${(result.overallScore * 100).toFixed(0)}%</div>
            <div class="metric-label">Overall Score</div>
        </div>
    `;
    
    document.getElementById('evaluationSummary').textContent = result.summary;
    document.getElementById('evaluationResults').classList.remove('hidden');
}

// ===== UI Helpers =====

function showLoading(show) {
    const loading = document.getElementById('loadingState');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function showError(message) {
    const error = document.getElementById('errorState');
    const msg = document.getElementById('errorMessage');
    msg.textContent = message;
    error.classList.remove('hidden');
    
    setTimeout(() => {
        error.classList.add('hidden');
    }, 5000);
}

function hideAllSections() {
    document.getElementById('workflowSection').classList.add('hidden');
    document.getElementById('recommendationsSection').classList.add('hidden');
    document.getElementById('reasoningSection').classList.add('hidden');
    document.getElementById('errorState').classList.add('hidden');
}

function loadProfile(genre, mood, energy, acoustic) {
    document.getElementById('genre').value = genre;
    document.getElementById('mood').value = mood;
    document.getElementById('energy').value = energy;
    document.getElementById('energyValue').textContent = energy;
    document.getElementById('acoustic').checked = acoustic;
    
    getRecommendations();
}
