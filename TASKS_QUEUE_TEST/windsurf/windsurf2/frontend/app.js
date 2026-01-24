const API_BASE_URL = 'http://localhost:8000';

let tasks = [];
let autoRefreshInterval = null;

const taskTypeSelect = document.getElementById('taskType');
const submitBtn = document.getElementById('submitBtn');
const statusFilter = document.getElementById('statusFilter');
const typeFilter = document.getElementById('typeFilter');
const refreshBtn = document.getElementById('refreshBtn');
const tasksList = document.getElementById('tasksList');
const taskCount = document.getElementById('taskCount');
const modal = document.getElementById('taskModal');
const closeModal = document.querySelector('.close');
const taskDetails = document.getElementById('taskDetails');
const notification = document.getElementById('notification');

taskTypeSelect.addEventListener('change', updateParametersSection);
submitBtn.addEventListener('click', submitTask);
refreshBtn.addEventListener('click', loadTasks);
statusFilter.addEventListener('change', filterTasks);
typeFilter.addEventListener('change', filterTasks);
closeModal.addEventListener('click', () => modal.style.display = 'none');

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

function updateParametersSection() {
    const taskType = taskTypeSelect.value;
    
    document.getElementById('dataProcessingParams').style.display = 'none';
    document.getElementById('emailSimulationParams').style.display = 'none';
    document.getElementById('imageProcessingParams').style.display = 'none';
    
    if (taskType === 'data_processing') {
        document.getElementById('dataProcessingParams').style.display = 'block';
    } else if (taskType === 'email_simulation') {
        document.getElementById('emailSimulationParams').style.display = 'block';
    } else if (taskType === 'image_processing') {
        document.getElementById('imageProcessingParams').style.display = 'block';
    }
}

function getTaskParameters() {
    const taskType = taskTypeSelect.value;
    
    if (taskType === 'data_processing') {
        return {
            rows: parseInt(document.getElementById('rows').value)
        };
    } else if (taskType === 'email_simulation') {
        return {
            recipient_count: parseInt(document.getElementById('recipientCount').value)
        };
    } else if (taskType === 'image_processing') {
        return {
            image_count: parseInt(document.getElementById('imageCount').value),
            operation: document.getElementById('operation').value
        };
    }
    
    return {};
}

async function submitTask() {
    const taskType = taskTypeSelect.value;
    const parameters = getTaskParameters();
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/submit`, {
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
        await loadTasks();
        
    } catch (error) {
        console.error('Error submitting task:', error);
        showNotification('Failed to submit task', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Task';
    }
}

async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/`);
        
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        
        tasks = await response.json();
        filterTasks();
        
    } catch (error) {
        console.error('Error loading tasks:', error);
        showNotification('Failed to load tasks', 'error');
    }
}

function filterTasks() {
    const statusValue = statusFilter.value;
    const typeValue = typeFilter.value;
    
    let filteredTasks = tasks;
    
    if (statusValue) {
        filteredTasks = filteredTasks.filter(t => t.status === statusValue);
    }
    
    if (typeValue) {
        filteredTasks = filteredTasks.filter(t => t.task_type === typeValue);
    }
    
    renderTasks(filteredTasks);
}

function renderTasks(tasksToRender) {
    taskCount.textContent = tasksToRender.length;
    
    if (tasksToRender.length === 0) {
        tasksList.innerHTML = '<p class="empty-state">No tasks found</p>';
        return;
    }
    
    tasksList.innerHTML = tasksToRender.map(task => createTaskCard(task)).join('');
}

function createTaskCard(task) {
    const createdDate = new Date(task.created_at).toLocaleString();
    const taskTypeDisplay = task.task_type.replace('_', ' ').toUpperCase();
    
    let progressBar = '';
    if (task.status === 'RUNNING' || task.status === 'PENDING') {
        progressBar = `
            <div class="task-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${task.progress}%">
                        ${task.progress}%
                    </div>
                </div>
            </div>
        `;
    }
    
    let actions = `<button class="btn-view" onclick="viewTaskDetails('${task.id}')">View Details</button>`;
    
    if (task.status === 'PENDING' || task.status === 'RUNNING') {
        actions += `<button class="btn-cancel" onclick="cancelTask('${task.id}')">Cancel</button>`;
    }
    
    if (task.status === 'FAILED') {
        actions += `<button class="btn-retry" onclick="retryTask('${task.id}')">Retry</button>`;
    }
    
    return `
        <div class="task-card">
            <div class="task-header">
                <div class="task-id">ID: ${task.id.substring(0, 8)}...</div>
                <div class="task-status status-${task.status}">${task.status}</div>
            </div>
            <div class="task-type">${taskTypeDisplay}</div>
            ${progressBar}
            <div class="task-times">
                <div><strong>Created:</strong> ${createdDate}</div>
            </div>
            <div class="task-actions">
                ${actions}
            </div>
        </div>
    `;
}

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
        showNotification('Failed to load task details', 'error');
    }
}

function displayTaskDetails(task) {
    const createdDate = new Date(task.created_at).toLocaleString();
    const startedDate = task.started_at ? new Date(task.started_at).toLocaleString() : 'N/A';
    const completedDate = task.completed_at ? new Date(task.completed_at).toLocaleString() : 'N/A';
    
    let duration = 'N/A';
    if (task.started_at && task.completed_at) {
        const start = new Date(task.started_at);
        const end = new Date(task.completed_at);
        const seconds = Math.round((end - start) / 1000);
        duration = `${seconds} seconds`;
    }
    
    let resultSection = '';
    if (task.result_data) {
        resultSection = `
            <div class="detail-section">
                <h3>Result Data</h3>
                <div class="result-data">${JSON.stringify(task.result_data, null, 2)}</div>
            </div>
        `;
    }
    
    let errorSection = '';
    if (task.error_message) {
        errorSection = `
            <div class="detail-section">
                <h3>Error Message</h3>
                <div class="result-data" style="color: #dc3545;">${task.error_message}</div>
            </div>
        `;
    }
    
    let parametersSection = '';
    if (task.parameters && Object.keys(task.parameters).length > 0) {
        parametersSection = `
            <div class="detail-section">
                <h3>Parameters</h3>
                <div class="result-data">${JSON.stringify(task.parameters, null, 2)}</div>
            </div>
        `;
    }
    
    taskDetails.innerHTML = `
        <div class="detail-section">
            <h3>Basic Information</h3>
            <div class="detail-item">
                <span class="detail-label">Task ID:</span>
                <span class="detail-value">${task.id}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Task Type:</span>
                <span class="detail-value">${task.task_type}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Status:</span>
                <span class="detail-value">
                    <span class="task-status status-${task.status}">${task.status}</span>
                </span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Progress:</span>
                <span class="detail-value">${task.progress}%</span>
            </div>
        </div>
        
        <div class="detail-section">
            <h3>Timeline</h3>
            <div class="detail-item">
                <span class="detail-label">Created:</span>
                <span class="detail-value">${createdDate}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Started:</span>
                <span class="detail-value">${startedDate}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Completed:</span>
                <span class="detail-value">${completedDate}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Duration:</span>
                <span class="detail-value">${duration}</span>
            </div>
        </div>
        
        ${parametersSection}
        ${resultSection}
        ${errorSection}
    `;
    
    modal.style.display = 'block';
}

async function cancelTask(taskId) {
    if (!confirm('Are you sure you want to cancel this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to cancel task');
        }
        
        showNotification('Task cancelled successfully', 'success');
        await loadTasks();
        
    } catch (error) {
        console.error('Error cancelling task:', error);
        showNotification(error.message, 'error');
    }
}

async function retryTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/retry`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to retry task');
        }
        
        showNotification('Task retry initiated', 'success');
        await loadTasks();
        
    } catch (error) {
        console.error('Error retrying task:', error);
        showNotification(error.message, 'error');
    }
}

function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(async () => {
        const hasRunningTasks = tasks.some(t => t.status === 'RUNNING' || t.status === 'PENDING');
        if (hasRunningTasks) {
            await loadTasks();
        }
    }, 2000);
}

updateParametersSection();
loadTasks();
startAutoRefresh();
