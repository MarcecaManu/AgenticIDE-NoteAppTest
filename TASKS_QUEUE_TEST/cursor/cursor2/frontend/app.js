// API base URL
const API_BASE = '/api';

// State
let tasks = [];
let autoRefreshInterval = null;

// DOM Elements
const taskTypeSelect = document.getElementById('taskType');
const submitBtn = document.getElementById('submitBtn');
const refreshBtn = document.getElementById('refreshBtn');
const filterStatus = document.getElementById('filterStatus');
const filterType = document.getElementById('filterType');
const tasksList = document.getElementById('tasksList');
const taskModal = document.getElementById('taskModal');
const taskDetails = document.getElementById('taskDetails');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Ensure modal is hidden on page load
    if (taskModal) {
        taskModal.classList.add('hidden');
    }
    
    setupEventListeners();
    loadTasks();
    startAutoRefresh();
});

// Event Listeners
function setupEventListeners() {
    taskTypeSelect.addEventListener('change', handleTaskTypeChange);
    submitBtn.addEventListener('click', handleSubmitTask);
    refreshBtn.addEventListener('click', loadTasks);
    filterStatus.addEventListener('change', renderTasks);
    filterType.addEventListener('change', renderTasks);
    
    // Modal close - using event delegation for better reliability
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeModal();
        });
    }
    
    taskModal.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            closeModal();
        }
    });
    
    // Also close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !taskModal.classList.contains('hidden')) {
            closeModal();
        }
    });
}

// Close modal function
function closeModal() {
    taskModal.classList.add('hidden');
}

// Handle task type change - show/hide parameters
function handleTaskTypeChange() {
    const taskType = taskTypeSelect.value;
    
    document.getElementById('dataProcessingParams').classList.add('hidden');
    document.getElementById('emailParams').classList.add('hidden');
    document.getElementById('imageParams').classList.add('hidden');
    
    if (taskType === 'data_processing') {
        document.getElementById('dataProcessingParams').classList.remove('hidden');
    } else if (taskType === 'email_simulation') {
        document.getElementById('emailParams').classList.remove('hidden');
    } else if (taskType === 'image_processing') {
        document.getElementById('imageParams').classList.remove('hidden');
    }
}

// Submit new task
async function handleSubmitTask() {
    const taskType = taskTypeSelect.value;
    let parameters = {};
    
    // Get parameters based on task type
    if (taskType === 'data_processing') {
        parameters = {
            rows: parseInt(document.getElementById('rows').value)
        };
    } else if (taskType === 'email_simulation') {
        parameters = {
            count: parseInt(document.getElementById('emailCount').value)
        };
    } else if (taskType === 'image_processing') {
        parameters = {
            count: parseInt(document.getElementById('imageCount').value),
            operation: document.getElementById('operation').value
        };
    }
    
    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        const response = await fetch(`${API_BASE}/tasks/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_type: taskType,
                parameters: parameters
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit task');
        }
        
        const result = await response.json();
        showNotification('Task submitted successfully!', 'success');
        loadTasks();
    } catch (error) {
        showNotification('Error submitting task: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Task';
    }
}

// Load tasks from API
async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks/`);
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        
        tasks = await response.json();
        renderTasks();
    } catch (error) {
        tasksList.innerHTML = `<p class="error-message">Error loading tasks: ${error.message}</p>`;
    }
}

// Render tasks list
function renderTasks() {
    const statusFilter = filterStatus.value;
    const typeFilter = filterType.value;
    
    let filteredTasks = tasks;
    
    if (statusFilter) {
        filteredTasks = filteredTasks.filter(t => t.status === statusFilter);
    }
    
    if (typeFilter) {
        filteredTasks = filteredTasks.filter(t => t.task_type === typeFilter);
    }
    
    if (filteredTasks.length === 0) {
        tasksList.innerHTML = '<p class="loading">No tasks found</p>';
        return;
    }
    
    tasksList.innerHTML = filteredTasks.map(task => createTaskCard(task)).join('');
    
    // Attach event listeners
    filteredTasks.forEach(task => {
        const card = document.getElementById(`task-${task.id}`);
        card.addEventListener('click', (e) => {
            if (!e.target.classList.contains('btn')) {
                showTaskDetails(task.id);
            }
        });
        
        const cancelBtn = document.getElementById(`cancel-${task.id}`);
        if (cancelBtn) {
            cancelBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                cancelTask(task.id);
            });
        }
        
        const retryBtn = document.getElementById(`retry-${task.id}`);
        if (retryBtn) {
            retryBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                retryTask(task.id);
            });
        }
    });
}

// Create task card HTML
function createTaskCard(task) {
    const taskTypeName = formatTaskType(task.task_type);
    const createdAt = new Date(task.created_at).toLocaleString();
    const duration = calculateDuration(task);
    
    let actionsHtml = '';
    if (task.status === 'PENDING' || task.status === 'RUNNING') {
        actionsHtml = `<button id="cancel-${task.id}" class="btn btn-danger">Cancel</button>`;
    } else if (task.status === 'FAILED') {
        actionsHtml = `<button id="retry-${task.id}" class="btn btn-success">Retry</button>`;
    }
    
    return `
        <div id="task-${task.id}" class="task-item">
            <div class="task-header">
                <div>
                    <div class="task-type">${taskTypeName}</div>
                    <div class="task-id">ID: ${task.id}</div>
                </div>
                <span class="status-badge status-${task.status}">${task.status}</span>
            </div>
            
            ${task.status === 'RUNNING' || (task.status === 'PENDING' && task.progress > 0) ? `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${task.progress}%"></div>
                </div>
                <div style="text-align: right; font-size: 0.85rem; color: #666; margin-top: 5px;">
                    ${Math.round(task.progress)}%
                </div>
            ` : ''}
            
            <div class="task-meta">
                <div class="meta-item">
                    <strong>Created:</strong> ${createdAt}
                </div>
                ${duration ? `
                    <div class="meta-item">
                        <strong>Duration:</strong> ${duration}
                    </div>
                ` : ''}
            </div>
            
            ${task.error_message ? `
                <div class="error-message">
                    <strong>Error:</strong> ${task.error_message}
                </div>
            ` : ''}
            
            ${actionsHtml ? `
                <div class="task-actions">
                    ${actionsHtml}
                </div>
            ` : ''}
        </div>
    `;
}

// Show task details modal
async function showTaskDetails(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`);
        if (!response.ok) {
            throw new Error('Failed to load task details');
        }
        
        const task = await response.json();
        
        let detailsHtml = `
            <div class="detail-section">
                <h3>Task Information</h3>
                <p><strong>ID:</strong> ${task.id}</p>
                <p><strong>Type:</strong> ${formatTaskType(task.task_type)}</p>
                <p><strong>Status:</strong> <span class="status-badge status-${task.status}">${task.status}</span></p>
                <p><strong>Progress:</strong> ${Math.round(task.progress)}%</p>
                <p><strong>Created:</strong> ${new Date(task.created_at).toLocaleString()}</p>
                ${task.started_at ? `<p><strong>Started:</strong> ${new Date(task.started_at).toLocaleString()}</p>` : ''}
                ${task.completed_at ? `<p><strong>Completed:</strong> ${new Date(task.completed_at).toLocaleString()}</p>` : ''}
            </div>
        `;
        
        if (task.parameters) {
            detailsHtml += `
                <div class="detail-section">
                    <h3>Parameters</h3>
                    <pre>${JSON.stringify(JSON.parse(task.parameters), null, 2)}</pre>
                </div>
            `;
        }
        
        if (task.result_data) {
            detailsHtml += `
                <div class="detail-section">
                    <h3>Results</h3>
                    <pre>${JSON.stringify(JSON.parse(task.result_data), null, 2)}</pre>
                </div>
            `;
        }
        
        if (task.error_message) {
            detailsHtml += `
                <div class="detail-section">
                    <h3>Error</h3>
                    <div class="error-message">${task.error_message}</div>
                </div>
            `;
        }
        
        taskDetails.innerHTML = detailsHtml;
        taskModal.classList.remove('hidden');
    } catch (error) {
        showNotification('Error loading task details: ' + error.message, 'error');
    }
}

// Cancel task
async function cancelTask(taskId) {
    if (!confirm('Are you sure you want to cancel this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to cancel task');
        }
        
        showNotification('Task cancelled successfully', 'success');
        loadTasks();
    } catch (error) {
        showNotification('Error cancelling task: ' + error.message, 'error');
    }
}

// Retry task
async function retryTask(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}/retry`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to retry task');
        }
        
        const result = await response.json();
        showNotification('Task retry submitted successfully', 'success');
        loadTasks();
    } catch (error) {
        showNotification('Error retrying task: ' + error.message, 'error');
    }
}

// Helper functions
function formatTaskType(taskType) {
    const types = {
        'data_processing': 'Data Processing',
        'email_simulation': 'Email Simulation',
        'image_processing': 'Image Processing'
    };
    return types[taskType] || taskType;
}

function calculateDuration(task) {
    if (!task.started_at) return null;
    
    const start = new Date(task.started_at);
    const end = task.completed_at ? new Date(task.completed_at) : new Date();
    const duration = (end - start) / 1000; // seconds
    
    if (duration < 60) {
        return `${Math.round(duration)}s`;
    } else if (duration < 3600) {
        return `${Math.round(duration / 60)}m`;
    } else {
        return `${Math.round(duration / 3600)}h`;
    }
}

function showNotification(message, type) {
    // Simple notification - could be enhanced with a toast library
    alert(message);
}

// Auto-refresh tasks every 2 seconds
function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        loadTasks();
    }, 2000);
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

