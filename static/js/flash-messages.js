// Flash Messages Handler
document.addEventListener('DOMContentLoaded', function() {
    // Initialize flash messages
    initFlashMessages();
});

function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(function(message) {
        // Add close button if it doesn't exist
        if (!message.querySelector('.close-btn')) {
            addCloseButton(message);
        }
        
        // Auto-dismiss after 5 seconds (except for errors)
        if (!message.classList.contains('error')) {
            setTimeout(function() {
                dismissMessage(message);
            }, 5000);
        }
    });
}

function addCloseButton(message) {
    // Create message content wrapper if it doesn't exist
    let messageContent = message.querySelector('.message-content');
    if (!messageContent) {
        messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Move existing content to the wrapper
        const existingContent = Array.from(message.childNodes);
        existingContent.forEach(node => {
            if (node.nodeType === Node.ELEMENT_NODE && !node.classList.contains('close-btn')) {
                messageContent.appendChild(node);
            } else if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                messageContent.appendChild(node);
            }
        });
        
        message.insertBefore(messageContent, message.firstChild);
    }
    
    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '×';
    closeBtn.setAttribute('aria-label', 'Close message');
    closeBtn.addEventListener('click', function() {
        dismissMessage(message);
    });
    
    message.appendChild(closeBtn);
}

function dismissMessage(message) {
    message.classList.add('fade-out');
    
    setTimeout(function() {
        if (message.parentNode) {
            message.parentNode.removeChild(message);
        }
    }, 300);
}

// Function to show new flash messages programmatically
function showFlashMessage(message, type = 'info') {
    const flashContainer = document.querySelector('.flash-messages');
    
    if (!flashContainer) {
        // Create flash container if it doesn't exist
        const container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = `flash-message ${type}`;
    messageElement.innerHTML = `
        <div class="message-content">
            <span>${message}</span>
        </div>
        <button class="close-btn" aria-label="Close message">×</button>
    `;
    
    // Add close button functionality
    const closeBtn = messageElement.querySelector('.close-btn');
    closeBtn.addEventListener('click', function() {
        dismissMessage(messageElement);
    });
    
    // Auto-dismiss after 5 seconds (except for errors)
    if (type !== 'error') {
        setTimeout(function() {
            dismissMessage(messageElement);
        }, 5000);
    }
    
    flashContainer.appendChild(messageElement);
} 