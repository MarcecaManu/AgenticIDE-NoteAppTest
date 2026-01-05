const API_BASE = 'http://localhost:8000/api';
let autoRefreshInterval = null;

// DOM Elements
const submitTaskForm = document.getElementById('submitTaskForm');
const taskTypeSelect = document.getElementById('taskType');
const filterStatus = document.getElementById('filterStatus');
const filterType = document.getElementById('filterType');
const refreshBtn = document.getElementById('refreshBtn');
const autoRefreshCheckbox = document.getElementById('autoRefresh');
const tasksList = document.getElementById('tasksList');
const taskCount = document.getElementById('taskCount');
const taskModal = document.getElementById('taskModal');
const taskDetails = document.getElementById('taskDetails');
const closeModal = document.querySelector('.close');

// Task parameter containers
const csvParams = document.getElementById('csvParams');
const emailParams = document.getElementById('emailParams');
const imageParams = document.getElementById('imageParams');

// Show/hide task parameters based on selected task type
taskTypeSelect.addEventListener('change', () => {
    const taskType = taskTypeSelect.value;
    
    csvParams.style.display = 'none';
    emailParams.style.display = 'none';
    imageParams.style.display = 'none';
    
    if (taskType === 'csv_processing') {
        csvParams.style.display = 'block';
    } else if (taskType === 'email_sending') {
        emailParams.style.display = 'block';
    } else if (taskType === 'image_processing') {
        imageParams.style.display = 'block';
    }
});

// Submit task form
submitTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const taskType = taskTypeSelect.value;
    let inputParams = {};
    
    // Get parameters based on task type
    if (taskType === 'csv_processing') {
        inputParams = {
            num_rows: parseInt(document.getElementById('numRows').value),
            processing_time: parseInt(document.getElementById('processingTime').value)
        };
    } else if (taskType === 'email_sending') {
        inputParams = {
            num_emails: parseInt(document.getElementById('numEmails').value),
            subject: document.getElementById('emailSubject').value,
            delay_per_email: parseFloat(document.getElementById('delayPerEmail').value)
        };
    } else if (taskType === 'image_processing') {
        inputParams = {
            num_images: parseInt(document.getElementById('numImages').value),
            target_width: parseInt(document.getElementById('targetWidth').value),
            target_height: parseInt(document.getElementById('targetHeight').value)
        };
    }
    
    try {
        const response = await fetch(`${API_BASE}/tasks/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_type: taskType,
                input_params: inputParams
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit task');
        }
        
        const task = await response.json();
        showNotification('Task submitted successfully!', 'success');
        submitTaskForm.reset();
        taskTypeSelect.value = '';
        csvParams.style.display = 'none';
        emailParams.style.display = 'none';
        imageParams.style.display = 'none';
        
        // Refresh task list
        loadTasks();
    } catch (error) {
        console.error('Error submitting task:', error);
        showNotification('Failed to submit task', 'error');
    }
});

// Load tasks
async function loadTasks() {
    const status = filterStatus.value;
    const taskType = filterType.value;
    
    let url = `${API_BASE}/tasks/?limit=100`;
    if (status) url += `&status=${status}`;
    if (taskType) url += `&task_type=${taskType}`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        
        const data = await response.json();
        taskCount.textContent = data.total;
        renderTasks(data.tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
        tasksList.innerHTML = '<p class="empty-state">Failed to load tasks. Make sure the backend is running.</p>';
    }
}

// Render tasks
function renderTasks(tasks) {
    if (tasks.length === 0) {
        tasksList.innerHTML = `
            <div class="empty-state">
                <p>No tasks found. Submit a task to get started!</p>
            </div>
        `;
        return;
    }
    
    tasksList.innerHTML = tasks.map(task => `
        <div class="task-item" onclick="showTaskDetails('${task.id}')">
            <div class="task-header">
                <div>
                    <div class="task-type">${formatTaskType(task.task_type)}</div>
                    <div class="task-id">ID: ${task.id.substring(0, 8)}...</div>
                </div>
                <span class="task-status status-${task.status}">${task.status}</span>
            </div>
            
            ${task.status === 'RUNNING' || task.progress > 0 ? `
                <div class="task-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${task.progress}%"></div>
                    </div>
                    <div class="progress-text">${task.progress.toFixed(1)}% complete</div>
                </div>
            ` : ''}
            
            <div class="task-times">
                <div><strong>Created:</strong> ${formatDate(task.created_at)}</div>
                ${task.started_at ? `<div><strong>Started:</strong> ${formatDate(task.started_at)}</div>` : ''}
                ${task.completed_at ? `<div><strong>Completed:</strong> ${formatDate(task.completed_at)}</div>` : ''}
            </div>
            
            ${task.error_message ? `
                <div style="color: #842029; margin-top: 10px;">
                    <strong>Error:</strong> ${task.error_message}
                </div>
            ` : ''}
            
            <div class="task-actions" onclick="event.stopPropagation()">
                ${task.status === 'PENDING' || task.status === 'RUNNING' ? `
                    <button class="btn btn-small btn-secondary" onclick="cancelTask('${task.id}')">
                        ❌ Cancel
                    </button>
                ` : ''}
                ${task.status === 'FAILED' || task.status === 'CANCELLED' ? `
                    <button class="btn btn-small btn-primary" onclick="retryTask('${task.id}')">
                        🔄 Retry
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Show task details in modal
async function showTaskDetails(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`);
        if (!response.ok) {
            throw new Error('Failed to load task details');
        }
        
        const task = await response.json();
        
        let resultsHTML = '';
        if (task.result_data) {
            try {
                const results = JSON.parse(task.result_data);
                resultsHTML = `<pre>${JSON.stringify(results, null, 2)}</pre>`;
            } catch {
                resultsHTML = `<pre>${task.result_data}</pre>`;
            }
        }
        
        let inputParamsHTML = '';
        if (task.input_params) {
            try {
                const params = JSON.parse(task.input_params);
                inputParamsHTML = `<pre>${JSON.stringify(params, null, 2)}</pre>`;
            } catch {
                inputParamsHTML = `<pre>${task.input_params}</pre>`;
            }
        }
        
        taskDetails.innerHTML = `
            <div class="detail-section">
                <h3>Task Information</h3>
                <div class="detail-grid">
                    <div class="detail-label">Task ID:</div>
                    <div class="detail-value">${task.id}</div>
                    
                    <div class="detail-label">Type:</div>
                    <div class="detail-value">${formatTaskType(task.task_type)}</div>
                    
                    <div class="detail-label">Status:</div>
                    <div class="detail-value">
                        <span class="task-status status-${task.status}">${task.status}</span>
                    </div>
                    
                    <div class="detail-label">Progress:</div>
                    <div class="detail-value">${task.progress.toFixed(1)}%</div>
                    
                    <div class="detail-label">Created:</div>
                    <div class="detail-value">${formatDate(task.created_at)}</div>
                    
                    ${task.started_at ? `
                        <div class="detail-label">Started:</div>
                        <div class="detail-value">${formatDate(task.started_at)}</div>
                    ` : ''}
                    
                    ${task.completed_at ? `
                        <div class="detail-label">Completed:</div>
                        <div class="detail-value">${formatDate(task.completed_at)}</div>
                    ` : ''}
                </div>
            </div>
            
            ${inputParamsHTML ? `
                <div class="detail-section">
                    <h3>Input Parameters</h3>
                    ${inputParamsHTML}
                </div>
            ` : ''}
            
            ${task.error_message ? `
                <div class="detail-section">
                    <h3>Error Message</h3>
                    <pre style="color: #842029;">${task.error_message}</pre>
                </div>
            ` : ''}
            
            ${resultsHTML ? `
                <div class="detail-section">
                    <h3>Results</h3>
                    ${resultsHTML}
                </div>
            ` : ''}
        `;
        
        taskModal.style.display = 'block';
    } catch (error) {
        console.error('Error loading task details:', error);
        showNotification('Failed to load task details', 'error');
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
            const error = await response.json();
            throw new Error(error.detail || 'Failed to cancel task');
        }
        
        showNotification('Task cancelled successfully', 'success');
        loadTasks();
    } catch (error) {
        console.error('Error cancelling task:', error);
        showNotification(error.message, 'error');
    }
}

// Retry task
async function retryTask(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}/retry`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to retry task');
        }
        
        showNotification('Task resubmitted successfully', 'success');
        loadTasks();
    } catch (error) {
        console.error('Error retrying task:', error);
        showNotification(error.message, 'error');
    }
}

// Helper functions
function formatTaskType(taskType) {
    const types = {
        'csv_processing': 'CSV Data Processing',
        'email_sending': 'Email Sending',
        'image_processing': 'Image Processing'
    };
    return types[taskType] || taskType;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function showNotification(message, type) {
    // Simple notification - could be enhanced with a toast library
    alert(message);
}

// Event listeners
refreshBtn.addEventListener('click', loadTasks);
filterStatus.addEventListener('change', loadTasks);
filterType.addEventListener('change', loadTasks);

closeModal.addEventListener('click', () => {
    taskModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === taskModal) {
        taskModal.style.display = 'none';
    }
});

autoRefreshCheckbox.addEventListener('change', () => {
    if (autoRefreshCheckbox.checked) {
        autoRefreshInterval = setInterval(loadTasks, 3000);
    } else {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
    }
});

// Initialize
loadTasks();
autoRefreshInterval = setInterval(loadTasks, 3000);

