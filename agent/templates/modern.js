// Ultra-Performance Optimized JavaScript - Minimal Operations

// Disable all heavy operations
let isAnimating = false;
let scrollTimeout = null;

// Minimal initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('Synapse UI loaded - Performance Mode');
    
    // Only essential setup
    setupFormValidation();
    setupCopyButtons();
    setupLinkedInLinks();
    
    // Disable all animations and effects
    disableAllAnimations();
});

// Disable all animations and effects
function disableAllAnimations() {
    // Remove all CSS transitions and animations
    const style = document.createElement('style');
    style.textContent = `
        * {
            transition: none !important;
            animation: none !important;
            transform: none !important;
            will-change: auto !important;
        }
    `;
    document.head.appendChild(style);
}

// Minimal form validation - no debouncing
function setupFormValidation() {
    const jobDescription = document.getElementById('jobDescription');
    const searchButton = document.getElementById('searchButton');
    
    if (jobDescription && searchButton) {
        jobDescription.addEventListener('input', function() {
            const isValid = jobDescription.value.trim().length >= 10;
            searchButton.disabled = !isValid;
        });
    }
}

// Minimal copy functionality
function setupCopyButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-btn')) {
            const messageElement = e.target.closest('.outreach-message');
            if (messageElement) {
                const messageText = messageElement.querySelector('.message-content').textContent;
                copyToClipboard(messageText);
                showAlert('Message copied to clipboard!', 'success');
            }
        }
    });
}

// Minimal LinkedIn link setup
function setupLinkedInLinks() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('linkedin-link')) {
            e.preventDefault();
            const url = e.target.href;
            openLinkedInProfile(url);
        }
    });
}

// Minimal copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).catch(err => {
            console.error('Failed to copy: ', err);
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

// Fallback copy method
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
    } catch (err) {
        console.error('Fallback copy failed: ', err);
    }
    
    document.body.removeChild(textArea);
}

// Minimal LinkedIn profile opening
function openLinkedInProfile(url) {
    // Try multiple methods to open the link
    const methods = [
        () => window.open(url, '_blank'),
        () => window.location.href = url,
        () => {
            const link = document.createElement('a');
            link.href = url;
            link.target = '_blank';
            link.click();
        }
    ];
    
    for (const method of methods) {
        try {
            method();
            break;
        } catch (error) {
            console.error('Failed to open LinkedIn profile:', error);
        }
    }
    
    showAlert('Opening LinkedIn profile...', 'info');
}

// Minimal alert system
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button type="button" class="btn-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 3000);
}

// Minimal search functionality
function performSearch() {
    const jobDescription = document.getElementById('jobDescription');
    const searchButton = document.getElementById('searchButton');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (!jobDescription || !searchButton || !resultsContainer) return;
    
    const description = jobDescription.value.trim();
    if (description.length < 10) {
        showAlert('Please enter a job description (at least 10 characters)', 'error');
        return;
    }
    
    // Show loading state
    searchButton.disabled = true;
    searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
    resultsContainer.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Finding candidates...</p></div>';
    
    // Make API call
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_description: description })
    })
    .then(response => response.json())
    .then(data => {
        displayResults(data);
    })
    .catch(error => {
        console.error('Search error:', error);
        showAlert('Search failed. Please try again.', 'error');
        resultsContainer.innerHTML = '<div class="alert alert-error">Search failed. Please try again.</div>';
    })
    .finally(() => {
        searchButton.disabled = false;
        searchButton.innerHTML = '<i class="fas fa-search"></i> Find Candidates';
    });
}

// Minimal results display
function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;
    
    if (!data.candidates || data.candidates.length === 0) {
        resultsContainer.innerHTML = '<div class="alert alert-info">No candidates found. Try a different job description.</div>';
        return;
    }
    
    const resultsHTML = data.candidates.map(candidate => `
        <div class="candidate-card">
            <div class="candidate-header">
                <h3>${candidate.name}</h3>
                <div class="candidate-score">
                    <span class="score-number">${candidate.score}%</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${candidate.score}%"></div>
                    </div>
                </div>
                ${candidate.is_demo ? '<span class="demo-badge">Demo</span>' : '<span class="real-badge">Real</span>'}
            </div>
            
            <div class="candidate-details">
                <div class="detail-item">
                    <i class="fas fa-briefcase"></i>
                    <span>${candidate.title}</span>
                </div>
                <div class="detail-item">
                    <i class="fas fa-building"></i>
                    <span>${candidate.company}</span>
                </div>
                <div class="detail-item">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${candidate.location}</span>
                </div>
                <div class="detail-item">
                    <i class="fas fa-link"></i>
                    <a href="${candidate.linkedin_url}" class="linkedin-link" target="_blank">LinkedIn Profile</a>
                </div>
            </div>
            
            <div class="candidate-skills">
                <h4>Key Skills:</h4>
                <div class="skills-container">
                    ${candidate.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                </div>
            </div>
            
            <div class="outreach-message">
                <h4>Personalized Message:</h4>
                <div class="message-content">${candidate.outreach_message}</div>
                <button class="btn btn-primary copy-btn">
                    <i class="fas fa-copy"></i> Copy Message
                </button>
            </div>
        </div>
    `).join('');
    
    resultsContainer.innerHTML = resultsHTML;
}

// Minimal stats update
function updateStats(candidates) {
    const totalCandidates = document.getElementById('totalCandidates');
    const avgScore = document.getElementById('avgScore');
    const topScore = document.getElementById('topScore');
    
    if (totalCandidates) totalCandidates.textContent = candidates.length;
    
    if (candidates.length > 0) {
        const scores = candidates.map(c => c.score);
        const average = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
        const max = Math.max(...scores);
        
        if (avgScore) avgScore.textContent = average + '%';
        if (topScore) topScore.textContent = max + '%';
    }
}

// Minimal scroll handling - disabled
function handleScroll() {
    // Disabled for performance
}

// Minimal window resize handling - disabled
function handleResize() {
    // Disabled for performance
}

// Global functions for HTML onclick handlers
window.performSearch = performSearch;
window.showAlert = showAlert; 