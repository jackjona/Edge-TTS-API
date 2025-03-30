document.addEventListener('DOMContentLoaded', function() {
    // Get form and relevant elements
    const ttsForm = document.getElementById('ttsForm');
    const convertBtn = document.getElementById('convertBtn');
    const textArea = document.getElementById('text');
    const voiceSelect = document.getElementById('voice');
    const copyApiKeyBtn = document.getElementById('copyApiKeyBtn');
    
    // Character counter for text area
    if (textArea) {
        textArea.addEventListener('input', function() {
            const charCount = this.value.length;
            // Add warning class if text is too long
            if (charCount > 5000) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }
    
    // Handle form submission with loading state
    if (ttsForm) {
        ttsForm.addEventListener('submit', function(e) {
            // Prevent submission if text is too long
            if (textArea.value.length > 5000) {
                e.preventDefault();
                alert('Text is too long. Please limit to 5000 characters.');
                return false;
            }
            
            // Show loading state
            convertBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Converting...';
            convertBtn.disabled = true;
            
            // Form will submit normally
            return true;
        });
    }
    
    // API Key Copy Button Functionality
    if (copyApiKeyBtn) {
        copyApiKeyBtn.addEventListener('click', function() {
            const apiKeyField = document.getElementById('apiKeyField');
            
            // Select the API key field
            apiKeyField.select();
            apiKeyField.setSelectionRange(0, 99999); // For mobile devices
            
            // Copy the text inside the text field
            navigator.clipboard.writeText(apiKeyField.value)
                .then(() => {
                    // Show success message
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy API key: ', err);
                    
                    // Fallback for older browsers
                    document.execCommand('copy');
                    
                    // Show success message
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                });
        });
    }
    
    // Audio player functionality
    const audioPlayer = document.getElementById('audioPlayer');
    if (audioPlayer) {
        // Auto-play when audio is loaded
        audioPlayer.addEventListener('canplay', function() {
            audioPlayer.play().catch(e => {
                console.log('Auto-play prevented by browser policy. User interaction required.');
            });
        });
    }
    
    // API example section - copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const codeBlock = this.closest('.code-block').querySelector('code');
            
            // Create a textarea element to copy from
            const textarea = document.createElement('textarea');
            textarea.value = codeBlock.textContent;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            
            // Show copied message
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 2000);
        });
    });
    
    // Group voices by locale in the select dropdown
    if (voiceSelect && voiceSelect.options.length > 0) {
        organizeVoiceDropdown(voiceSelect);
    }
});

/**
 * Organizes voices dropdown by grouping voices by locale
 * @param {HTMLSelectElement} selectElement - The voice select element
 */
function organizeVoiceDropdown(selectElement) {
    // Get current selected value
    const selectedValue = selectElement.value;
    
    // Create array from options
    const options = Array.from(selectElement.options);
    
    // Group by locale
    const localeGroups = {};
    options.forEach(option => {
        const locale = option.text.split(' - ')[0];
        if (!localeGroups[locale]) {
            localeGroups[locale] = [];
        }
        localeGroups[locale].push(option);
    });
    
    // Clear select
    selectElement.innerHTML = '';
    
    // Add grouped options
    Object.keys(localeGroups).sort().forEach(locale => {
        const group = document.createElement('optgroup');
        group.label = locale;
        
        localeGroups[locale].forEach(option => {
            // Extract the name part from the display name
            const namePart = option.text.split(' - ')[1];
            const newOption = document.createElement('option');
            newOption.value = option.value;
            newOption.text = namePart;
            group.appendChild(newOption);
            
            // Restore selected value
            if (option.value === selectedValue) {
                newOption.selected = true;
            }
        });
        
        selectElement.appendChild(group);
    });
}
