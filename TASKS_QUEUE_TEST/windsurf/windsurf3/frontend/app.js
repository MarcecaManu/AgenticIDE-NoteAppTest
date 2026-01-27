const API_BASE_URL = 'http://localhost:8000';

let refreshInterval = null;

const taskParamsConfig = {
    data_processing: [
        { name: 'rows', label: 'Number of Rows', type: 'number', default: 1000, min: 100, max: 10000 },
        { name: 'processing_time', label: 'Processing Time (seconds)', type: 'number', default: 15, min: 5, max: 30 }
    ],
    email_simulation: [
        { name: 'recipient_count', label: 'Number of Recipients', type: 'number', default: 10, min: 1, max: 50 },
        { name: 'delay_per_email', label: 'Delay per Email (seconds)', type: 'number', default: 1, min: 0.5, max: 5, step: 0.5 },
        { name: 'subject', label: 'Email Subject', type: 'text', default: 'Test Email' }
    ],
    image_processing: [
        { name: 'image_count', label: 'Number of Images', type: 'number', default: 5, min: 1, max: 20 },
        { name: 'operation', label: 'Operation', type: 'select', options: ['resize', 'convert', 'compress'], default: 'resize' },
        { name: 'processing_time', label: 'Processing Time (seconds)', type: 'number', default: 10, min: 5, max: 30 }
    ]
};

function updateTaskParams() {
    const taskType = document.getElementById('taskType').value;
    const paramsContainer = document.getElementById('taskParams');
    const params = taskParamsConfig[taskType];
    
    paramsContainer.innerHTML = '';
    
    params.forEach(param => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        
        const label = document.createElement('label');
        label.textContent = param.label;
        label.htmlFor = param.name;
        formGroup.appendChild(label);
        
        let input;
        if (param.type === 'select') {
            input = document.createElement('select');
            param.options.forEach(option => {
                const opt = document.createElement('option');
                opt.value = option;
                opt.textContent = option.charAt(0).toUpperCase() + option.slice(1);
                if (option === param.default) opt.selected = true;
                input.appendChild(opt);
            });
        } else {
            input = document.createElement('input');
            input.type = param.type;
            input.value = param.default;
            if (param.min !== undefined) input.min = param.min;
            if (param.max !== undefined) input.max = param.max;
            if (param.step !== undefined) input.step = param.step;
        }
        
        input.id = param.name;
        input.name = param.name;
        formGroup.appendChild(input);
        paramsContainer.appendChild(formGroup);
    });
}

function getTaskParameters() {
    const taskType = document.getElementById('taskType').value;
    const params = taskParamsConfig[taskType];
    const parameters = {};
    
    params.forEach(param => {
        const input = document.getElementById(param.name);
        if (param.type === 'number') {
            parameters[param.name] = parseFloat(input.value);
        } else {
            parameters[param.name] = input.value;
        }
    });
    
    return parameters;
}

async function submitTask(event) {
    event.preventDefault();
    
    const taskType = document.getElementById('taskType').value;
    const parameters = getTaskParameters();
    
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
        showNotification('Error submitting task: ' + error.message, 'error');
    }
}

async function loadTasks() {
    const filterStatus = document.getElementById('filterStatus').value;
    const filterType = document.getElementById('filterType').value;
    
    try {
        let url = `${API_BASE_URL}/api/tasks/`;
        const params = new URLSearchParams();
        if (filterStatus) params.append('status', filterStatus);
        if (filterType) params.append('task_type', filterType);
        if (params.toString()) url += '?' + params.toString();
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        
        const tasks = await response.json();
        displayTasks(tasks);
        updateStats(tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function displayTasks(tasks) {
    const taskList = document.getElementById('taskList');
    
    if (tasks.length === 0) {
        taskList.innerHTML = `
            <div class="empty-state">
                <div>No tasks found. Try adjusting your filters or submit a new task!</div>
            </div>
        `;
        return;
    }
    
    taskList.innerHTML = tasks.map(task => createTaskElement(task)).join('');
}

function createTaskElement(task) {
    const createdDate = new Date(task.created_at).toLocaleString();
    const startedDate = task.started_at ? new Date(task.started_at).toLocaleString() : 'Not started';
    const completedDate = task.completed_at ? new Date(task.completed_at).toLocaleString() : 'Not completed';
    
    let resultHtml = '';
    if (task.result_data && task.status === 'SUCCESS') {
        resultHtml = `
            <div class="task-result">
                <strong>Result:</strong>
                <pre>${JSON.stringify(task.result_data, null, 2)}</pre>
            </div>
        `;
    }
    
    let errorHtml = '';
    if (task.error_message) {
        errorHtml = `
            <div class="task-error">
                <strong>Error:</strong> ${task.error_message}
            </div>
        `;
    }
    
    let progressHtml = '';
    if (task.status === 'RUNNING' || task.status === 'PENDING') {
        progressHtml = `
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${task.progress}%"></div>
            </div>
            <div style="text-align: center; font-size: 12px; color: #666; margin-top: 5px;">
                ${task.progress}% Complete
            </div>
        `;
    }
    
    let actionsHtml = '';
    if (task.status === 'PENDING' || task.status === 'RUNNING') {
        actionsHtml = `
            <div class="task-actions">
                <button class="btn-cancel" onclick="cancelTask('${task.id}')">Cancel</button>
            </div>
        `;
    } else if (task.status === 'FAILED') {
        actionsHtml = `
            <div class="task-actions">
                <button class="btn-retry" onclick="retryTask('${task.id}')">Retry</button>
            </div>
        `;
    }
    
    return `
        <div class="task-item">
            <div class="task-header">
                <div class="task-id">ID: ${task.id}</div>
                <div class="task-status status-${task.status}">${task.status}</div>
            </div>
            <div class="task-type">📋 ${formatTaskType(task.task_type)}</div>
            <div class="task-times">
                <div>Created: ${createdDate}</div>
                <div>Started: ${startedDate}</div>
                <div>Completed: ${completedDate}</div>
            </div>
            ${progressHtml}
            ${resultHtml}
            ${errorHtml}
            ${actionsHtml}
        </div>
    `;
}

function formatTaskType(taskType) {
    return taskType.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
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
            throw new Error('Failed to cancel task');
        }
        
        showNotification('Task cancelled successfully!', 'success');
        await loadTasks();
    } catch (error) {
        showNotification('Error cancelling task: ' + error.message, 'error');
    }
}

async function retryTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/retry`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to retry task');
        }
        
        showNotification('Task retried successfully!', 'success');
        await loadTasks();
    } catch (error) {
        showNotification('Error retrying task: ' + error.message, 'error');
    }
}

function updateStats(tasks) {
    const stats = {
        total: tasks.length,
        pending: tasks.filter(t => t.status === 'PENDING').length,
        running: tasks.filter(t => t.status === 'RUNNING').length,
        success: tasks.filter(t => t.status === 'SUCCESS').length,
        failed: tasks.filter(t => t.status === 'FAILED').length
    };
    
    document.getElementById('stat-total').textContent = stats.total;
    document.getElementById('stat-pending').textContent = stats.pending;
    document.getElementById('stat-running').textContent = stats.running;
    document.getElementById('stat-success').textContent = stats.success;
    document.getElementById('stat-failed').textContent = stats.failed;
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.style.background = type === 'success' ? '#4CAF50' : '#f44336';
    notification.style.color = 'white';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

document.getElementById('taskType').addEventListener('change', updateTaskParams);
document.getElementById('taskForm').addEventListener('submit', submitTask);
document.getElementById('filterStatus').addEventListener('change', loadTasks);
document.getElementById('filterType').addEventListener('change', loadTasks);

updateTaskParams();
loadTasks();

refreshInterval = setInterval(loadTasks, 2000);
