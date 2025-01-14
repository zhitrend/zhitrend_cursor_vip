// Debug logging function
function log(message) {
    console.log(`[reCAPTCHA Bypass] ${new Date().toISOString()}: ${message}`);
}

// Function to get element by selector
function qSelector(selector) {
    return document.querySelector(selector);
}

// Constants
const MAX_ATTEMPTS = 1;
const SELECTORS = {
    CHECK_BOX: ".recaptcha-checkbox-border",
    AUDIO_BUTTON: "#recaptcha-audio-button",
    PLAY_BUTTON: ".rc-audiochallenge-play-button .rc-button-default",
    AUDIO_SOURCE: "#audio-source",
    IMAGE_SELECT: "#rc-imageselect",
    RESPONSE_FIELD: ".rc-audiochallenge-response-field",
    AUDIO_ERROR_MESSAGE: ".rc-audiochallenge-error-message",
    AUDIO_RESPONSE: "#audio-response",
    RELOAD_BUTTON: "#recaptcha-reload-button",
    RECAPTCHA_STATUS: "#recaptcha-accessible-status",
    DOSCAPTCHA: ".rc-doscaptcha-body",
    VERIFY_BUTTON: "#recaptcha-verify-button"
};

// Function to check if element is hidden
function isHidden(el) {
    return (el.offsetParent === null);
}

// Function to handle the bypass process
async function bypassRecaptcha() {
    try {
        log('Starting bypass process...');
        log('Waiting 3 seconds before starting...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        let solved = false;
        let checkBoxClicked = false;
        let requestCount = 0;
        
        const recaptchaInitialStatus = qSelector(SELECTORS.RECAPTCHA_STATUS) ? 
            qSelector(SELECTORS.RECAPTCHA_STATUS).innerText : "";
        
        log('Initial reCAPTCHA status: ' + recaptchaInitialStatus);

        // Main bypass logic
        try {
            if (!checkBoxClicked && qSelector(SELECTORS.CHECK_BOX) && 
                !isHidden(qSelector(SELECTORS.CHECK_BOX))) {
                log('Clicking checkbox...');
                qSelector(SELECTORS.CHECK_BOX).click();
                checkBoxClicked = true;
            }

            // Check if the captcha is solved
            if (qSelector(SELECTORS.RECAPTCHA_STATUS) && 
                (qSelector(SELECTORS.RECAPTCHA_STATUS).innerText != recaptchaInitialStatus)) {
                solved = true;
                log('SOLVED!');
            }

            if (requestCount > MAX_ATTEMPTS) {
                log('Attempted Max Retries. Stopping the solver');
                solved = true;
            }

            // Stop solving when Automated queries message is shown
            if (qSelector(SELECTORS.DOSCAPTCHA) && 
                qSelector(SELECTORS.DOSCAPTCHA).innerText.length > 0) {
                log('Automated Queries Detected');
            }

        } catch (err) {
            log(`Error in main bypass logic: ${err.message}`);
        }

        log('Bypass process completed');
        
        // If not solved, retry after delay
        if (!solved && requestCount < MAX_ATTEMPTS) {
            requestCount++;
            log(`Retrying... Attempt ${requestCount} of ${MAX_ATTEMPTS}`);
            setTimeout(bypassRecaptcha, 2000);
        }

    } catch (e) {
        log(`Bypass failed: ${e.message}`);
    }
}

// Create a MutationObserver to watch for reCAPTCHA elements
log('Setting up MutationObserver...');
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1 && // Element node
                ((node.tagName === 'SCRIPT' && node.src && node.src.includes('recaptcha')) ||
                 (node.tagName === 'IFRAME' && node.src && node.src.includes('recaptcha')))) {
                log(`Detected new reCAPTCHA element: ${node.tagName} - ${node.src}`);
                bypassRecaptcha();
            }
        });
    });
});

// Start observing
observer.observe(document, {
    childList: true,
    subtree: true
});
log('MutationObserver started');

// Run on page load
if (document.readyState === 'loading') {
    log('Document still loading, waiting for DOMContentLoaded');
    document.addEventListener('DOMContentLoaded', bypassRecaptcha);
} else {
    log('Document already loaded, starting bypass process');
    bypassRecaptcha();
}