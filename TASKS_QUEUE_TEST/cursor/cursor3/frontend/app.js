// API Base URL
const API_BASE = '/api';

// State
let tasks = [];
let autoRefreshInterval = null;

// DOM Elements
const taskTypeSelect = document.getElementById('taskType');
const submitTaskBtn = document.getElementById('submitTask');
const filterStatusSelect = document.getElementById('filterStatus');
const filterTypeSelect = document.getElementById('filterType');
const refreshTasksBtn = document.getElementById('refreshTasks');
const taskListDiv = document.getElementById('taskList');
const taskModal = document.getElementById('taskModal');
const taskDetailsDiv = document.getElementById('taskDetails');
const closeModal = document.querySelector('.close');

// Task parameter containers
const dataProcessingParams = document.getElementById('dataProcessingParams');
const emailParams = document.getElementById('emailParams');
const imageParams = document.getElementById('imageParams');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadTasks();
    startAutoRefresh();
});

// Setup Event Listeners
function setupEventListeners() {
    taskTypeSelect.addEventListener('change', updateTaskParams);
    submitTaskBtn.addEventListener('click', submitTask);
    filterStatusSelect.addEventListener('change', loadTasks);
    filterTypeSelect.addEventListener('change', loadTasks);
    refreshTasksBtn.addEventListener('click', loadTasks);
    closeModal.addEventListener('click', () => taskModal.style.display = 'none');
    
    window.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            taskModal.style.display = 'none';
        }
    });
}

// Update task parameters based on selected type
function updateTaskParams() {
    const taskType = taskTypeSelect.value;
    
    dataProcessingParams.style.display = 'none';
    emailParams.style.display = 'none';
    imageParams.style.display = 'none';
    
    if (taskType === 'DATA_PROCESSING') {
        dataProcessingParams.style.display = 'block';
    } else if (taskType === 'EMAIL_SIMULATION') {
        emailParams.style.display = 'block';
    } else if (taskType === 'IMAGE_PROCESSING') {
        imageParams.style.display = 'block';
    }
}

// Submit a new task
async function submitTask() {
    const taskType = taskTypeSelect.value;
    const parameters = getTaskParameters(taskType);
    
    submitTaskBtn.disabled = true;
    submitTaskBtn.textContent = 'Submitting...';
    
    try {
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
        
        const task = await response.json();
        showNotification('Task submitted successfully!', 'success');
        loadTasks();
    } catch (error) {
        showNotification('Error submitting task: ' + error.message, 'error');
    } finally {
        submitTaskBtn.disabled = false;
        submitTaskBtn.textContent = 'Submit Task';
    }
}

// Get task parameters based on type
function getTaskParameters(taskType) {
    if (taskType === 'DATA_PROCESSING') {
        return {
            rows: parseInt(document.getElementById('rows').value),
            processing_time: parseInt(document.getElementById('processingTime').value)
        };
    } else if (taskType === 'EMAIL_SIMULATION') {
        return {
            recipient_count: parseInt(document.getElementById('recipientCount').value),
            delay_per_email: parseInt(document.getElementById('delayPerEmail').value)
        };
    } else if (taskType === 'IMAGE_PROCESSING') {
        return {
            image_count: parseInt(document.getElementById('imageCount').value),
            target_size: document.getElementById('targetSize').value,
            operation: document.getElementById('operation').value
        };
    }
    return {};
}

// Load tasks from API
async function loadTasks() {
    const status = filterStatusSelect.value;
    const taskType = filterTypeSelect.value;
    
    let url = `${API_BASE}/tasks/`;
    const params = new URLSearchParams();
    
    if (status) params.append('status', status);
    if (taskType) params.append('task_type', taskType);
    
    if (params.toString()) {
        url += '?' + params.toString();
    }
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        
        tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
        taskListDiv.innerHTML = '<p class="empty-state">Error loading tasks. Please try again.</p>';
    }
}

// Render tasks in the UI
function renderTasks() {
    if (tasks.length === 0) {
        taskListDiv.innerHTML = '<p class="empty-state">No tasks found matching your filters.</p>';
        return;
    }
    
    taskListDiv.innerHTML = tasks.map(task => createTaskCard(task)).join('');
}

// Create a task card HTML
function createTaskCard(task) {
    const progress = task.progress || '0';
    const showProgress = task.status === 'RUNNING';
    
    return `
        <div class="task-item">
            <div class="task-header">
                <span class="task-id">ID: ${task.id}</span>
                <span class="task-status status-${task.status}">${task.status}</span>
            </div>
            
            <div class="task-info">
                <div class="task-info-item">
                    <span class="task-info-label">Type:</span>
                    <span class="task-info-value">${formatTaskType(task.task_type)}</span>
                </div>
                <div class="task-info-item">
                    <span class="task-info-label">Created:</span>
                    <span class="task-info-value">${formatDateTime(task.created_at)}</span>
                </div>
                ${task.started_at ? `
                <div class="task-info-item">
                    <span class="task-info-label">Started:</span>
                    <span class="task-info-value">${formatDateTime(task.started_at)}</span>
                </div>
                ` : ''}
                ${task.completed_at ? `
                <div class="task-info-item">
                    <span class="task-info-label">Completed:</span>
                    <span class="task-info-value">${formatDateTime(task.completed_at)}</span>
                </div>
                ` : ''}
            </div>
            
            ${showProgress ? `
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${progress}%">${progress}%</div>
            </div>
            ` : ''}
            
            ${task.error_message ? `
            <div style="color: #dc3545; margin-top: 10px; font-size: 0.9rem;">
                <strong>Error:</strong> ${task.error_message}
            </div>
            ` : ''}
            
            <div class="task-actions">
                <button class="btn btn-info" onclick="viewTaskDetails('${task.id}')">View Details</button>
                ${task.status === 'PENDING' || task.status === 'RUNNING' ? `
                <button class="btn btn-danger" onclick="cancelTask('${task.id}')">Cancel</button>
                ` : ''}
                ${task.status === 'FAILED' ? `
                <button class="btn btn-success" onclick="retryTask('${task.id}')">Retry</button>
                ` : ''}
            </div>
        </div>
    `;
}

// View task details in modal
async function viewTaskDetails(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`);
        if (!response.ok) {
            throw new Error('Failed to load task details');
        }
        
        const task = await response.json();
        
        taskDetailsDiv.innerHTML = `
            <div class="detail-section">
                <h3>Task Information</h3>
                <p><strong>ID:</strong> ${task.id}</p>
                <p><strong>Type:</strong> ${formatTaskType(task.task_type)}</p>
                <p><strong>Status:</strong> <span class="task-status status-${task.status}">${task.status}</span></p>
                <p><strong>Progress:</strong> ${task.progress || '0'}%</p>
            </div>
            
            <div class="detail-section">
                <h3>Timestamps</h3>
                <p><strong>Created:</strong> ${formatDateTime(task.created_at)}</p>
                ${task.started_at ? `<p><strong>Started:</strong> ${formatDateTime(task.started_at)}</p>` : ''}
                ${task.completed_at ? `<p><strong>Completed:</strong> ${formatDateTime(task.completed_at)}</p>` : ''}
            </div>
            
            ${task.parameters ? `
            <div class="detail-section">
                <h3>Parameters</h3>
                <pre>${JSON.stringify(task.parameters, null, 2)}</pre>
            </div>
            ` : ''}
            
            ${task.result_data ? `
            <div class="detail-section">
                <h3>Results</h3>
                <pre>${JSON.stringify(task.result_data, null, 2)}</pre>
            </div>
            ` : ''}
            
            ${task.error_message ? `
            <div class="detail-section">
                <h3>Error Message</h3>
                <pre style="color: #dc3545;">${task.error_message}</pre>
            </div>
            ` : ''}
        `;
        
        taskModal.style.display = 'block';
    } catch (error) {
        showNotification('Error loading task details: ' + error.message, 'error');
    }
}

// Cancel a task
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
        
        showNotification('Task cancelled successfully!', 'success');
        loadTasks();
    } catch (error) {
        showNotification('Error cancelling task: ' + error.message, 'error');
    }
}

// Retry a failed task
async function retryTask(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}/retry`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to retry task');
        }
        
        const newTask = await response.json();
        showNotification('Task retry submitted successfully!', 'success');
        loadTasks();
    } catch (error) {
        showNotification('Error retrying task: ' + error.message, 'error');
    }
}

// Start auto-refresh
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(() => {
        loadTasks();
    }, 3000); // Refresh every 3 seconds
}

// Utility functions
function formatTaskType(taskType) {
    return taskType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatDateTime(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleString();
}

function showNotification(message, type) {
    // Simple notification - could be enhanced with a toast library
    const color = type === 'success' ? '#28a745' : '#dc3545';
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${color};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Make functions available globally
window.viewTaskDetails = viewTaskDetails;
window.cancelTask = cancelTask;
window.retryTask = retryTask;


