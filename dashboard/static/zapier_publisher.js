/**
 * Zapier Publisher - Frontend JavaScript
 * Handles UI interactions for publishing posts via Zapier webhooks
 */

// Configuration
const PUBLISH_API_BASE = '/api/publish';
const TOAST_DURATION = 5000; // 5 seconds

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Toast type (success, error, info, warning)
 */
function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${getToastIcon(type)}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;

    // Add to page
    document.body.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add('toast-fade-out');
            setTimeout(() => toast.remove(), 300);
        }
    }, TOAST_DURATION);
}

/**
 * Get icon for toast type
 */
function getToastIcon(type) {
    const icons = {
        success: '✓',
        error: '✗',
        info: 'ℹ',
        warning: '⚠'
    };
    return icons[type] || icons.info;
}

/**
 * Show loading state on button
 * @param {HTMLElement} button - Button element
 * @param {boolean} loading - Whether to show loading state
 */
function setButtonLoading(button, loading) {
    if (loading) {
        button.dataset.originalText = button.textContent;
        button.textContent = '⏳ Publishing...';
        button.disabled = true;
        button.classList.add('btn-loading');
    } else {
        button.textContent = button.dataset.originalText || button.textContent;
        button.disabled = false;
        button.classList.remove('btn-loading');
    }
}

/**
 * Publish post to a specific platform
 * @param {number} postId - Database ID of post
 * @param {string} platform - Platform name (linkedin, instagram, twitter, facebook)
 * @param {HTMLElement} button - Button that triggered the action (optional)
 */
async function publishToPlatform(postId, platform, button = null) {
    try {
        // Show loading state
        if (button) {
            setButtonLoading(button, true);
        }

        showToast(`Publishing to ${platform.charAt(0).toUpperCase() + platform.slice(1)}...`, 'info');

        // Call publish API
        const response = await fetch(`${PUBLISH_API_BASE}/posts/${postId}/${platform}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        // Handle response
        if (result.success) {
            showToast(
                `Successfully published to ${platform.charAt(0).toUpperCase() + platform.slice(1)}!`,
                'success'
            );

            // Update UI to show published status
            updatePublishButtonStatus(postId, platform, true);

            // Trigger refresh of publishing history if visible
            if (typeof refreshPublishingHistory === 'function') {
                refreshPublishingHistory();
            }
        } else {
            // Handle specific error cases
            if (result.action === 'configure_webhook') {
                showToast(
                    `${platform.charAt(0).toUpperCase() + platform.slice(1)} webhook not configured. Please add it to your .env file.`,
                    'warning'
                );
            } else {
                showToast(
                    `Failed to publish: ${result.error || 'Unknown error'}`,
                    'error'
                );
            }
        }

        return result;

    } catch (error) {
        console.error('Publishing error:', error);
        showToast(`Error publishing to ${platform}: ${error.message}`, 'error');
        return { success: false, error: error.message };

    } finally {
        // Remove loading state
        if (button) {
            setButtonLoading(button, false);
        }
    }
}

/**
 * Publish post to multiple platforms
 * @param {number} postId - Database ID of post
 * @param {string[]} platforms - Array of platform names
 */
async function publishToMultiplePlatforms(postId, platforms) {
    try {
        showToast(`Publishing to ${platforms.length} platforms...`, 'info');

        const response = await fetch(`${PUBLISH_API_BASE}/posts/${postId}/multi`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ platforms })
        });

        const result = await response.json();

        // Show results
        if (result.success_count > 0) {
            showToast(
                `Successfully published to ${result.success_count} platform(s)!`,
                'success'
            );
        }

        if (result.failure_count > 0) {
            showToast(
                `Failed to publish to ${result.failure_count} platform(s)`,
                'warning'
            );
        }

        // Update UI for each platform
        for (const [platform, platformResult] of Object.entries(result.results)) {
            updatePublishButtonStatus(postId, platform, platformResult.success);
        }

        return result;

    } catch (error) {
        console.error('Multi-platform publishing error:', error);
        showToast(`Error publishing: ${error.message}`, 'error');
        return { success: false, error: error.message };
    }
}

/**
 * Update publish button status after publishing
 * @param {number} postId - Post ID
 * @param {string} platform - Platform name
 * @param {boolean} success - Whether publish was successful
 */
function updatePublishButtonStatus(postId, platform, success) {
    const button = document.querySelector(`[data-post-id="${postId}"][data-platform="${platform}"]`);

    if (button) {
        if (success) {
            button.classList.add('btn-published');
            button.classList.remove('btn-primary');
            button.innerHTML = '✓ Published';
            button.disabled = true;
        } else {
            button.classList.add('btn-error');
            setTimeout(() => button.classList.remove('btn-error'), 3000);
        }
    }
}

/**
 * Show platform configuration dialog
 * @param {string} platform - Platform to configure
 */
async function showPlatformSetup(platform) {
    try {
        const response = await fetch(`${PUBLISH_API_BASE}/platforms/${platform}/setup`);
        const setup = await response.json();

        // Create modal with setup instructions
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Configure ${platform.charAt(0).toUpperCase() + platform.slice(1)} Webhook</h2>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Follow these steps to connect ${platform} via Zapier:</p>
                    <ol class="setup-steps">
                        ${setup.steps.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                    <div class="setup-info">
                        <p><strong>Environment Variable:</strong> <code>${setup.env_var}</code></p>
                        <p><strong>Example Webhook URL:</strong> <code>${setup.example_webhook}</code></p>
                    </div>
                    <div class="setup-actions">
                        <a href="${setup.zapier_url}" target="_blank" class="btn btn-primary">
                            Open Zapier Editor
                        </a>
                        <button onclick="this.closest('.modal').remove()" class="btn btn-secondary">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

    } catch (error) {
        console.error('Error loading setup instructions:', error);
        showToast('Error loading setup instructions', 'error');
    }
}

/**
 * Check which platforms are configured
 * @returns {Promise<Object>} Platform configuration status
 */
async function checkPlatformStatus() {
    try {
        const response = await fetch(`${PUBLISH_API_BASE}/platforms`);
        const data = await response.json();
        return data.platforms;
    } catch (error) {
        console.error('Error checking platform status:', error);
        return {};
    }
}

/**
 * Show publishing options modal for a post
 * @param {number} postId - Post ID
 * @param {Object} post - Post data (optional)
 */
async function showPublishModal(postId, post = null) {
    // Get platform status
    const platforms = await checkPlatformStatus();

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Publish Post #${postId}</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                ${post ? `
                    <div class="post-preview">
                        <p>${post.content ? post.content.substring(0, 200) + (post.content.length > 200 ? '...' : '') : ''}</p>
                    </div>
                ` : ''}

                <h3>Select Platform(s):</h3>
                <div class="platform-selector">
                    ${Object.entries(platforms).map(([platform, configured]) => `
                        <label class="platform-option ${configured ? '' : 'platform-disabled'}">
                            <input
                                type="checkbox"
                                name="platform"
                                value="${platform}"
                                ${configured ? '' : 'disabled'}
                            >
                            <span class="platform-name">
                                ${platform.charAt(0).toUpperCase() + platform.slice(1)}
                            </span>
                            ${configured
                                ? '<span class="platform-status platform-ready">✓ Ready</span>'
                                : '<span class="platform-status platform-not-configured">Not Configured</span>'
                            }
                            ${!configured
                                ? `<button class="btn-setup-link" onclick="showPlatformSetup('${platform}')">Setup</button>`
                                : ''
                            }
                        </label>
                    `).join('')}
                </div>

                <div class="publish-actions">
                    <button onclick="publishSelectedPlatforms(${postId})" class="btn btn-primary">
                        Publish to Selected Platforms
                    </button>
                    <button onclick="this.closest('.modal').remove()" class="btn btn-secondary">
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

/**
 * Publish to selected platforms from modal
 * @param {number} postId - Post ID
 */
async function publishSelectedPlatforms(postId) {
    const checkboxes = document.querySelectorAll('input[name="platform"]:checked');
    const platforms = Array.from(checkboxes).map(cb => cb.value);

    if (platforms.length === 0) {
        showToast('Please select at least one platform', 'warning');
        return;
    }

    // Close modal
    const modal = document.querySelector('.modal');
    if (modal) modal.remove();

    // Publish to selected platforms
    await publishToMultiplePlatforms(postId, platforms);
}

/**
 * Load and display publishing history
 * @param {Object} options - Filter options (platform, limit, success_only)
 */
async function loadPublishingHistory(options = {}) {
    try {
        const params = new URLSearchParams(options);
        const response = await fetch(`${PUBLISH_API_BASE}/history?${params}`);
        const data = await response.json();

        displayPublishingHistory(data.history);

    } catch (error) {
        console.error('Error loading publishing history:', error);
        showToast('Error loading publishing history', 'error');
    }
}

/**
 * Display publishing history in the UI
 * @param {Array} history - Array of publishing records
 */
function displayPublishingHistory(history) {
    const container = document.getElementById('publishing-history');
    if (!container) return;

    if (history.length === 0) {
        container.innerHTML = '<p class="no-data">No publishing history yet.</p>';
        return;
    }

    container.innerHTML = `
        <table class="history-table">
            <thead>
                <tr>
                    <th>Date/Time</th>
                    <th>Post ID</th>
                    <th>Platform</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${history.map(record => `
                    <tr class="${record.success ? 'success-row' : 'error-row'}">
                        <td>${new Date(record.published_at).toLocaleString()}</td>
                        <td>#${record.post_id}</td>
                        <td>${record.platform}</td>
                        <td>
                            ${record.success
                                ? '<span class="status-badge status-success">✓ Success</span>'
                                : '<span class="status-badge status-error">✗ Failed</span>'
                            }
                        </td>
                        <td>
                            ${record.post_url
                                ? `<a href="${record.post_url}" target="_blank" class="btn-link">View Post</a>`
                                : ''
                            }
                            ${!record.success
                                ? `<button onclick="publishToPlatform(${record.post_id}, '${record.platform}')" class="btn-retry">Retry</button>`
                                : ''
                            }
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

/**
 * Test platform webhook configuration
 * @param {string} platform - Platform to test
 */
async function testPlatformWebhook(platform) {
    try {
        showToast(`Testing ${platform} webhook...`, 'info');

        const response = await fetch(`${PUBLISH_API_BASE}/test/${platform}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.test_result && result.test_result.success) {
            showToast(
                `${platform} webhook test successful! Check your Zap history in Zapier.`,
                'success'
            );
        } else {
            showToast(
                `${platform} webhook test failed: ${result.test_result?.error || 'Unknown error'}`,
                'error'
            );
        }

    } catch (error) {
        console.error('Webhook test error:', error);
        showToast(`Error testing ${platform} webhook: ${error.message}`, 'error');
    }
}

// Export functions for use in HTML
window.publishToPlatform = publishToPlatform;
window.publishToMultiplePlatforms = publishToMultiplePlatforms;
window.showPublishModal = showPublishModal;
window.showPlatformSetup = showPlatformSetup;
window.checkPlatformStatus = checkPlatformStatus;
window.loadPublishingHistory = loadPublishingHistory;
window.testPlatformWebhook = testPlatformWebhook;
window.publishSelectedPlatforms = publishSelectedPlatforms;
