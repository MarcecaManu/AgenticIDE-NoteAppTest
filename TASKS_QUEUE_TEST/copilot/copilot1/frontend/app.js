// API base URL
const API_BASE = 'http://localhost:8000/api';

// State
let tasks = [];
let refreshInterval = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    startAutoRefresh();
    refreshTasks();
});

// Initialize event listeners
function initializeEventListeners() {
    // Task type change handler
    document.getElementById('taskType').addEventListener('change', (e) => {
        showParametersForTaskType(e.target.value);
    });

    // Form submit handler
    document.getElementById('taskForm').addEventListener('submit', handleTaskSubmit);

    // Filter change handlers
    document.getElementById('filterStatus').addEventListener('change', applyFilters);
    document.getElementById('filterType').addEventListener('change', applyFilters);
    document.getElementById('searchId').addEventListener('input', applyFilters);
}

// Show parameters based on task type
function showParametersForTaskType(taskType) {
    const allParams = document.querySelectorAll('.parameters-inputs');
    allParams.forEach(p => p.classList.remove('active'));

    if (taskType === 'DATA_PROCESSING') {
        document.getElementById('dataProcessingParams').classList.add('active');
    } else if (taskType === 'EMAIL_SIMULATION') {
        document.getElementById('emailSimulationParams').classList.add('active');
    } else if (taskType === 'IMAGE_PROCESSING') {
        document.getElementById('imageProcessingParams').classList.add('active');
    }
}

// Handle task submission
async function handleTaskSubmit(e) {
    e.preventDefault();
    
    const taskType = document.getElementById('taskType').value;
    if (!taskType) {
        alert('Please select a task type');
        return;
    }

    const parameters = getParametersForTaskType(taskType);
    
    try {
        const response = await fetch(`${API_BASE}/tasks/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_type: taskType,
                parameters: parameters
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const task = await response.json();
        console.log('Task submitted:', task);
        
        // Reset form
        document.getElementById('taskForm').reset();
        showParametersForTaskType('');
        
        // Refresh tasks
        await refreshTasks();
        
        alert(`Task submitted successfully! ID: ${task.id}`);
    } catch (error) {
        console.error('Error submitting task:', error);
        alert(`Error submitting task: ${error.message}`);
    }
}

// Get parameters for task type
function getParametersForTaskType(taskType) {
    const parameters = {};

    if (taskType === 'DATA_PROCESSING') {
        parameters.num_rows = parseInt(document.getElementById('numRows').value);
        parameters.processing_time = parseInt(document.getElementById('processingTime').value);
    } else if (taskType === 'EMAIL_SIMULATION') {
        parameters.num_emails = parseInt(document.getElementById('numEmails').value);
        parameters.delay_per_email = parseFloat(document.getElementById('emailDelay').value);
        parameters.subject = document.getElementById('emailSubject').value;
    } else if (taskType === 'IMAGE_PROCESSING') {
        parameters.num_images = parseInt(document.getElementById('numImages').value);
        parameters.target_size = document.getElementById('targetSize').value;
        parameters.output_format = document.getElementById('outputFormat').value;
    }

    return parameters;
}

// Refresh tasks from API
async function refreshTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        tasks = await response.json();
        updateStatistics(tasks);
        applyFilters();
    } catch (error) {
        console.error('Error fetching tasks:', error);
        document.getElementById('tasksGrid').innerHTML = `
            <div class="error-message">
                Error loading tasks: ${error.message}
            </div>
        `;
    }
}

// Update statistics
function updateStatistics(tasks) {
    const stats = {
        total: tasks.length,
        PENDING: tasks.filter(t => t.status === 'PENDING').length,
        RUNNING: tasks.filter(t => t.status === 'RUNNING').length,
        SUCCESS: tasks.filter(t => t.status === 'SUCCESS').length,
        FAILED: tasks.filter(t => t.status === 'FAILED').length,
    };

    document.getElementById('statTotal').textContent = stats.total;
    document.getElementById('statPending').textContent = stats.PENDING;
    document.getElementById('statRunning').textContent = stats.RUNNING;
    document.getElementById('statSuccess').textContent = stats.SUCCESS;
    document.getElementById('statFailed').textContent = stats.FAILED;
}

// Apply filters
function applyFilters() {
    const statusFilter = document.getElementById('filterStatus').value;
    const typeFilter = document.getElementById('filterType').value;
    const searchId = document.getElementById('searchId').value.toLowerCase();

    let filteredTasks = tasks.filter(task => {
        if (statusFilter && task.status !== statusFilter) return false;
        if (typeFilter && task.task_type !== typeFilter) return false;
        if (searchId && !task.id.toLowerCase().includes(searchId)) return false;
        return true;
    });

    renderTasks(filteredTasks);
}

// Render tasks
function renderTasks(tasksToRender) {
    const grid = document.getElementById('tasksGrid');

    if (tasksToRender.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                </svg>
                <h3>No tasks found</h3>
                <p>Submit a new task to get started</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = tasksToRender.map(task => createTaskCard(task)).join('');
}

// Create task card HTML
function createTaskCard(task) {
    const progress = task.progress || 0;
    const showProgress = task.status === 'RUNNING' || (task.status === 'SUCCESS' && task.progress === 100);
    
    return `
        <div class="task-card">
            <div class="task-header">
                <div class="task-id">${task.id}</div>
                <div class="task-status status-${task.status}">${task.status}</div>
            </div>

            <div class="task-info">
                <div class="task-info-item">
                    <span class="label">Type:</span>
                    <span class="value">${formatTaskType(task.task_type)}</span>
                </div>
                <div class="task-info-item">
                    <span class="label">Created:</span>
                    <span class="value">${formatDateTime(task.created_at)}</span>
                </div>
                ${task.started_at ? `
                <div class="task-info-item">
                    <span class="label">Started:</span>
                    <span class="value">${formatDateTime(task.started_at)}</span>
                </div>
                ` : ''}
                ${task.completed_at ? `
                <div class="task-info-item">
                    <span class="label">Completed:</span>
                    <span class="value">${formatDateTime(task.completed_at)}</span>
                </div>
                ` : ''}
            </div>

            ${showProgress ? `
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress}%">
                    ${progress.toFixed(1)}%
                </div>
            </div>
            ` : ''}

            <div class="task-actions">
                ${task.status === 'PENDING' || task.status === 'RUNNING' ? `
                    <button class="btn btn-danger btn-sm" onclick="cancelTask('${task.id}')">
                        ❌ Cancel
                    </button>
                ` : ''}
                ${task.status === 'FAILED' ? `
                    <button class="btn btn-success btn-sm" onclick="retryTask('${task.id}')">
                        🔄 Retry
                    </button>
                ` : ''}
                <button class="btn btn-secondary btn-sm" onclick="viewTaskDetails('${task.id}')">
                    👁️ View Details
                </button>
            </div>

            ${task.result_data ? `
            <div class="task-result">
                <strong>Results:</strong>
                <pre>${JSON.stringify(task.result_data, null, 2)}</pre>
            </div>
            ` : ''}

            ${task.error_message ? `
            <div class="error-message">
                <strong>Error:</strong> ${task.error_message}
            </div>
            ` : ''}
        </div>
    `;
}

// Format task type
function formatTaskType(taskType) {
    const types = {
        'DATA_PROCESSING': '📊 Data Processing',
        'EMAIL_SIMULATION': '📧 Email Simulation',
        'IMAGE_PROCESSING': '🖼️ Image Processing'
    };
    return types[taskType] || taskType;
}

// Format date time
function formatDateTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
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
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        await refreshTasks();
        alert('Task cancelled successfully');
    } catch (error) {
        console.error('Error cancelling task:', error);
        alert(`Error cancelling task: ${error.message}`);
    }
}

// Retry task
async function retryTask(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}/retry`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const newTask = await response.json();
        await refreshTasks();
        alert(`Task retried successfully! New task ID: ${newTask.id}`);
    } catch (error) {
        console.error('Error retrying task:', error);
        alert(`Error retrying task: ${error.message}`);
    }
}

// View task details
async function viewTaskDetails(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const task = await response.json();
        alert(JSON.stringify(task, null, 2));
    } catch (error) {
        console.error('Error viewing task details:', error);
        alert(`Error viewing task details: ${error.message}`);
    }
}

// Auto-refresh tasks
function startAutoRefresh() {
    // Refresh every 2 seconds
    refreshInterval = setInterval(refreshTasks, 2000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Stop auto-refresh when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        refreshTasks();
    }
});
