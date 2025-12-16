async function loadExample() {
    try {
        // Show loading state
        exampleBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        exampleBtn.disabled = true;
        
        // Call the API
        const response = await fetch('/api/load_example');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Update UI with example data
            contextTextarea.value = data.context;
            questionInput.value = data.question;
            
            // Update character counts
            updateCounts();
            
            // Clear any previous answer
            answerPlaceholder.style.display = 'block';
            answerContent.style.display = 'none';
            confidenceFill.style.width = '0%';
            confidenceValue.textContent = '--%';
            answerLength.textContent = '0 chars';
            
            // Focus on the question input for user convenience
            questionInput.focus();
            
            showNotification('✅ Example loaded successfully! You can now click "Get Answer"', 'success');
            
        } else {
            throw new Error('Invalid response from server');
        }
        
    } catch (error) {
        console.error('Error loading example:', error);
        showNotification(`❌ Failed to load example: ${error.message}`, 'error');
        
        // Fallback: Set default example if API fails
        contextTextarea.value = "The Mars 2020 mission is part of NASA's Mars Exploration Program. The Perseverance rover landed on Mars on February 18, 2021, in Jezero Crater.";
        questionInput.value = "When did Perseverance land on Mars?";
        updateCounts();
        
    } finally {
        // Reset button state
        exampleBtn.innerHTML = '<i class="fas fa-lightbulb"></i> Load Example';
        exampleBtn.disabled = false;
    }
}