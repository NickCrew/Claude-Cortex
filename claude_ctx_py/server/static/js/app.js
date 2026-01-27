let allAgents = [];
let agentModal = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchAgents();
    fetchModes();
    fetchWorkflows();
    
    // Initialize modal
    const modalEl = document.getElementById('agentModal');
    if (modalEl) {
        agentModal = new bootstrap.Modal(modalEl);
    }
});

async function fetchAgents() {
    try {
        const response = await fetch('/api/agents');
        allAgents = await response.json();
        
        document.getElementById('agent-count').textContent = `${allAgents.length} Agents`;
        renderAgents();
    } catch (error) {
        console.error('Error fetching agents:', error);
    }
}

function renderAgents() {
    const list = document.getElementById('agents-list');
    list.innerHTML = '';
    
    // Group by category
    const grouped = {};
    allAgents.forEach(agent => {
        const cat = agent.category || 'General';
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(agent);
    });

    // Sort categories
    const categories = Object.keys(grouped).sort();

    categories.forEach(category => {
        // Render Category Header
        const headerCol = document.createElement('div');
        headerCol.className = 'col-12 mt-4 mb-2 border-bottom border-secondary pb-2';
        headerCol.innerHTML = `<h5 class="text-info-emphasis"><i class="bi bi-folder2-open me-2"></i>${category}</h5>`;
        list.appendChild(headerCol);

        // Render Agents in this category
        grouped[category].forEach(agent => {
            const col = document.createElement('div');
            col.className = 'col-md-4 mb-3';
            
            const isActive = agent.state === 'active';
            const badgeClass = isActive ? 'bg-success' : 'bg-secondary';
            const switchId = `switch-${agent.name}`;
            
            col.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title text-info mb-0">${agent.name}</h5>
                            <span class="badge ${badgeClass}">${agent.state}</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" role="switch" id="${switchId}" ${isActive ? 'checked' : ''} onchange="toggleAgent('${agent.name}', this.checked)">
                                <label class="form-check-label text-muted small" for="${switchId}">${isActive ? 'Enabled' : 'Disabled'}</label>
                            </div>
                            <button class="btn btn-sm btn-outline-light" onclick="showAgentDetails('${agent.name}')">Details</button>
                        </div>
                    </div>
                </div>
            `;
            list.appendChild(col);
        });
    });
}

async function toggleAgent(name, isChecked) {
    const action = isChecked ? 'activate' : 'deactivate';
    try {
        const response = await fetch(`/api/agents/${name}/${action}`, { method: 'POST' });
        const result = await response.json();
        if (result.success) {
            // Refresh list to update state/badge
            fetchAgents();
        } else {
            alert(`Failed to ${action} ${name}: ${result.message}`);
            // Revert switch state if failed
            document.getElementById(`switch-${name}`).checked = !isChecked;
        }
    } catch (error) {
        console.error(`Error toggling agent ${name}:`, error);
        alert(`Error: ${error.message}`);
    }
}

function showAgentDetails(name) {
    const agent = allAgents.find(a => a.name === name);
    if (agent && agentModal) {
        document.getElementById('agentModalLabel').textContent = agent.name;
        document.getElementById('agentModalContent').textContent = agent.content || "No details available. (Try restarting 'cortex dashboard')";
        agentModal.show();
    }
}

async function fetchModes() {
    try {
        const response = await fetch('/api/modes');
        const modes = await response.json();
        
        document.getElementById('mode-count').textContent = `${modes.length} Modes`;
        
        const list = document.getElementById('modes-list');
        list.innerHTML = '';
        
        modes.forEach(mode => {
            const item = document.createElement('a');
            item.className = 'list-group-item list-group-item-action';
            item.href = '#';
            item.innerHTML = `<span class="fw-bold text-warning">${mode.name}</span>`;
            list.appendChild(item);
        });
    } catch (error) {
        console.error('Error fetching modes:', error);
    }
}

async function fetchWorkflows() {
    try {
        const response = await fetch('/api/workflows');
        const workflows = await response.json();
        
        const list = document.getElementById('workflows-list');
        list.innerHTML = '';
        
        workflows.forEach(wf => {
            const item = document.createElement('a');
            item.className = 'list-group-item list-group-item-action';
            item.href = '#';
            item.innerHTML = `<span class="fw-bold text-primary">${wf.name}</span>`;
            list.appendChild(item);
        });
    } catch (error) {
        console.error('Error fetching workflows:', error);
    }
}
