// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
let autoRefreshInterval = null;
let currentFilters = {
    status: '',
    type: ''
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadTasks();
    setupAutoRefresh();
});

// Event Listeners
function initializeEventListeners() {
    // Task form submission
    document.getElementById('taskForm').addEventListener('submit', handleTaskSubmission);
    
    // Task type selection
    document.getElementById('taskType').addEventListener('change', handleTaskTypeChange);
    
    // Filters
    document.getElementById('statusFilter').addEventListener('change', handleFilterChange);
    document.getElementById('typeFilter').addEventListener('change', handleFilterChange);
    document.getElementById('refreshBtn').addEventListener('click', loadTasks);
    
    // Auto-refresh toggle
    document.getElementById('autoRefresh').addEventListener('change', handleAutoRefreshToggle);
    
    // Modal close
    document.querySelector('.close').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('taskModal');
        if (e.target === modal) {
            closeModal();
        }
    });
}

// Task Type Change Handler
function handleTaskTypeChange(e) {
    const taskType = e.target.value;
    
    // Hide all options
    document.querySelectorAll('.task-options').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show relevant options
    if (taskType === 'data_processing') {
        document.getElementById('dataProcessingOptions').style.display = 'block';
    } else if (taskType === 'email_simulation') {
        document.getElementById('emailOptions').style.display = 'block';
    } else if (taskType === 'image_processing') {
        document.getElementById('imageOptions').style.display = 'block';
    }
}

// Task Submission Handler
async function handleTaskSubmission(e) {
    e.preventDefault();
    
    const taskType = document.getElementById('taskType').value;
    if (!taskType) {
        alert('Please select a task type');
        return;
    }
    
    let inputData = {};
    
    // Gather input data based on task type
    if (taskType === 'data_processing') {
        inputData = {
            rows: parseInt(document.getElementById('rowCount').value)
        };
    } else if (taskType === 'email_simulation') {
        inputData = {
            recipient_count: parseInt(document.getElementById('recipientCount').value),
            delay_per_email: parseFloat(document.getElementById('emailDelay').value)
        };
    } else if (taskType === 'image_processing') {
        inputData = {
            image_count: parseInt(document.getElementById('imageCount').value),
            operation: document.getElementById('operation').value,
            target_size: document.getElementById('targetSize').value
        };
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_type: taskType,
                input_data: inputData,
                parameters: inputData  // Support both field names
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit task');
        }
        
        const task = await response.json();
        showNotification(`Task submitted successfully! ID: ${task.id.substring(0, 8)}...`, 'success');
        
        // Reset form
        document.getElementById('taskForm').reset();
        document.querySelectorAll('.task-options').forEach(el => {
            el.style.display = 'none';
        });
        
        // Reload tasks
        setTimeout(() => loadTasks(), 500);
        
    } catch (error) {
        console.error('Error submitting task:', error);
        showNotification('Failed to submit task. Please try again.', 'error');
    }
}

// Filter Change Handler
function handleFilterChange() {
    currentFilters.status = document.getElementById('statusFilter').value;
    currentFilters.type = document.getElementById('typeFilter').value;
    loadTasks();
}

// Auto-refresh Toggle
function handleAutoRefreshToggle(e) {
    if (e.target.checked) {
        setupAutoRefresh();
    } else {
        clearAutoRefresh();
    }
}

function setupAutoRefresh() {
    clearAutoRefresh();
    autoRefreshInterval = setInterval(() => {
        loadTasks(true); // Silent refresh
    }, 5000);
}

function clearAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Load Tasks
async function loadTasks(silent = false) {
    try {
        const params = new URLSearchParams();
        if (currentFilters.status) params.append('status', currentFilters.status);
        if (currentFilters.type) params.append('task_type', currentFilters.type);
        params.append('limit', '100');
        
        const response = await fetch(`${API_BASE_URL}/api/tasks/?${params.toString()}`);
        
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        
        const data = await response.json();
        displayTasks(data.tasks, data.total);
        
    } catch (error) {
        console.error('Error loading tasks:', error);
        if (!silent) {
            showNotification('Failed to load tasks. Please check if the backend is running.', 'error');
        }
    }
}

// Display Tasks
function displayTasks(tasks, total) {
    const tasksList = document.getElementById('tasksList');
    const taskCount = document.getElementById('taskCount');
    
    taskCount.textContent = total;
    
    if (tasks.length === 0) {
        tasksList.innerHTML = '<p class="no-tasks">No tasks found.</p>';
        return;
    }
    
    tasksList.innerHTML = tasks.map(task => createTaskCard(task)).join('');
    
    // Add event listeners to task action buttons
    tasks.forEach(task => {
        const viewBtn = document.getElementById(`view-${task.id}`);
        if (viewBtn) {
            viewBtn.addEventListener('click', () => viewTaskDetails(task.id));
        }
        
        const cancelBtn = document.getElementById(`cancel-${task.id}`);
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => cancelTask(task.id));
        }
        
        const retryBtn = document.getElementById(`retry-${task.id}`);
        if (retryBtn) {
            retryBtn.addEventListener('click', () => retryTask(task.id));
        }
    });
}

// Create Task Card HTML
function createTaskCard(task) {
    const createdAt = new Date(task.created_at).toLocaleString();
    const startedAt = task.started_at ? new Date(task.started_at).toLocaleString() : 'Not started';
    const completedAt = task.completed_at ? new Date(task.completed_at).toLocaleString() : 'Not completed';
    
    const showCancel = task.status === 'PENDING' || task.status === 'RUNNING';
    const showRetry = task.status === 'FAILED';
    const showProgress = task.status === 'RUNNING' || task.status === 'PENDING';
    
    return `
        <div class="task-card">
            <div class="task-header">
                <div class="task-info">
                    <div class="task-id">ID: ${task.id}</div>
                    <div class="task-type">${formatTaskType(task.task_type)}</div>
                </div>
                <span class="task-status status-${task.status}">${task.status}</span>
            </div>
            
            ${showProgress ? `
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${task.progress}%">
                        ${task.progress}%
                    </div>
                </div>
            ` : ''}
            
            <div class="task-timestamps">
                <div><strong>Created:</strong> ${createdAt}</div>
                <div><strong>Started:</strong> ${startedAt}</div>
                <div><strong>Completed:</strong> ${completedAt}</div>
            </div>
            
            ${task.error_message ? `
                <div class="detail-row">
                    <div class="detail-label">Error:</div>
                    <div class="detail-value" style="color: #dc3545;">${task.error_message}</div>
                </div>
            ` : ''}
            
            <div class="task-actions">
                <button id="view-${task.id}" class="btn btn-info btn-small">View Details</button>
                ${showCancel ? `<button id="cancel-${task.id}" class="btn btn-danger btn-small">Cancel</button>` : ''}
                ${showRetry ? `<button id="retry-${task.id}" class="btn btn-success btn-small">Retry</button>` : ''}
            </div>
        </div>
    `;
}

// Format Task Type
function formatTaskType(taskType) {
    const typeMap = {
        'data_processing': 'Data Processing',
        'email_simulation': 'Email Simulation',
        'image_processing': 'Image Processing'
    };
    return typeMap[taskType] || taskType;
}

// View Task Details
async function viewTaskDetails(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load task details');
        }
        
        const task = await response.json();
        displayTaskDetails(task);
        
    } catch (error) {
        console.error('Error loading task details:', error);
        showNotification('Failed to load task details.', 'error');
    }
}

// Display Task Details in Modal
function displayTaskDetails(task) {
    const taskDetails = document.getElementById('taskDetails');
    
    let resultHtml = '';
    if (task.result_data) {
        try {
            const result = JSON.parse(task.result_data);
            resultHtml = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        } catch {
            resultHtml = task.result_data;
        }
    }
    
    taskDetails.innerHTML = `
        <div class="detail-row">
            <div class="detail-label">Task ID:</div>
            <div class="detail-value">${task.id}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Task Type:</div>
            <div class="detail-value">${formatTaskType(task.task_type)}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Status:</div>
            <div class="detail-value"><span class="task-status status-${task.status}">${task.status}</span></div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Progress:</div>
            <div class="detail-value">
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${task.progress}%">${task.progress}%</div>
                </div>
            </div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Created At:</div>
            <div class="detail-value">${new Date(task.created_at).toLocaleString()}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Started At:</div>
            <div class="detail-value">${task.started_at ? new Date(task.started_at).toLocaleString() : 'Not started'}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Completed At:</div>
            <div class="detail-value">${task.completed_at ? new Date(task.completed_at).toLocaleString() : 'Not completed'}</div>
        </div>
        ${task.error_message ? `
            <div class="detail-row">
                <div class="detail-label">Error Message:</div>
                <div class="detail-value" style="color: #dc3545;">${task.error_message}</div>
            </div>
        ` : ''}
        ${resultHtml ? `
            <div class="detail-row">
                <div class="detail-label">Result:</div>
                <div class="detail-value">${resultHtml}</div>
            </div>
        ` : ''}
    `;
    
    document.getElementById('taskModal').style.display = 'block';
}

// Close Modal
function closeModal() {
    document.getElementById('taskModal').style.display = 'none';
}

// Cancel Task
async function cancelTask(taskId) {
    if (!confirm('Are you sure you want to cancel this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to cancel task');
        }
        
        showNotification('Task cancelled successfully!', 'success');
        setTimeout(() => loadTasks(), 500);
        
    } catch (error) {
        console.error('Error cancelling task:', error);
        showNotification('Failed to cancel task.', 'error');
    }
}

// Retry Task
async function retryTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/retry`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to retry task');
        }
        
        const data = await response.json();
        showNotification(`Task retry submitted! New task ID: ${data.new_task_id.substring(0, 8)}...`, 'success');
        setTimeout(() => loadTasks(), 500);
        
    } catch (error) {
        console.error('Error retrying task:', error);
        showNotification('Failed to retry task.', 'error');
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        border-radius: 6px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: fadeIn 0.3s;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
