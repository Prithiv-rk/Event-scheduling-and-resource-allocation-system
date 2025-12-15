function switchTab(tab, e) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    e.target.classList.add('active');
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(tab + '-tab').classList.add('active');
    if (tab === 'events') loadEvents();
    else if (tab === 'resources') loadResources();
    else if (tab === 'allocations') {
        loadAllocations();
        populateAllocationSelects();
    }
}
function showMessage(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    const content = document.querySelector('.content');
    content.insertBefore(alertDiv, content.firstChild);
    setTimeout(() => alertDiv.remove(), 3000);
}
async function createEvent(e) {
    e.preventDefault();
    const data = {
        name: document.getElementById('event-name').value,
        description: document.getElementById('event-description').value,
        date: document.getElementById('event-date').value,
        start_time: document.getElementById('event-start-time').value,
        end_time: document.getElementById('event-end-time').value
    };
    const response = await fetch('/api/events', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const result = await response.json();
    if (response.ok) {
        showMessage('Event created successfully!', 'success');
        e.target.reset();
        loadEvents();
    } else {
        showMessage(result.error || 'Failed to create event', 'error');
    }
    return false;
}
async function createResource(e) {
    e.preventDefault();
    const data = {
        name: document.getElementById('resource-name').value,
        type: document.getElementById('resource-type').value,
        capacity: parseInt(document.getElementById('resource-capacity').value)
    };
    const response = await fetch('/api/resources', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const result = await response.json();
    if (response.ok) {
        showMessage('Resource added successfully!', 'success');
        e.target.reset();
        loadResources();
    } else {
        showMessage(result.error || 'Failed to add resource', 'error');
    }
    return false;
}
async function allocateResource(e) {
    e.preventDefault();
    const data = {
        event_id: parseInt(document.getElementById('alloc-event').value),
        resource_id: parseInt(document.getElementById('alloc-resource').value),
        quantity: parseInt(document.getElementById('alloc-quantity').value)
    };
    const response = await fetch('/api/allocations', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const result = await response.json();
    if (response.ok) {
        showMessage('Resource allocated successfully!', 'success');
        e.target.reset();
        loadAllocations();
    } else {
        showMessage(result.error || 'Failed to allocate resource', 'error');
    }
    return false;
}
async function loadEvents() {
    const response = await fetch('/api/events');
    const events = await response.json();
    const list = document.getElementById('events-list');
    if (events.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <svg fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2H6zm1 2h6v2H7V4zm0 4h6v2H7V8zm0 4h6v2H7v-2z"/>
                </svg>
                <p>No events yet. Create your first event!</p>
            </div>
        `;
    } else {
        list.innerHTML = events.map(event => `
            <div class="card">
                <div class="card-header">
                    <div class="card-title">${event.name}</div>
                    <button class="btn btn-danger" onclick="deleteEvent(${event.id})">Delete</button>
                </div>
                <div class="card-body">
                    <p><strong>Description:</strong> ${event.description || 'N/A'}</p>
                    <p><strong>Date:</strong> ${event.date}</p>
                    <p><strong>Time:</strong> ${event.start_time} - ${event.end_time}</p>
                    <span class="badge badge-info">Event ID: ${event.id}</span>
                </div>
            </div>
        `).join('');
    }
}
async function loadResources() {
    const response = await fetch('/api/resources');
    const resources = await response.json();
    const list = document.getElementById('resources-list');
    if (resources.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <svg fill="currentColor" viewBox="0 0 20 20">
                    <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                </svg>
                <p>No resources yet. Add your first resource!</p>
            </div>
        `;
    } else {
        list.innerHTML = resources.map(resource => `
            <div class="card">
                <div class="card-header">
                    <div class="card-title">${resource.name}</div>
                    <button class="btn btn-danger" onclick="deleteResource(${resource.id})">Delete</button>
                </div>
                <div class="card-body">
                    <p><strong>Type:</strong> ${resource.type}</p>
                    <p><strong>Capacity:</strong> ${resource.capacity}</p>
                    <p><strong>Available:</strong> ${resource.available}</p>
                    <span class="badge badge-${resource.available > 0 ? 'success' : 'warning'}">
                        ${resource.available > 0 ? 'Available' : 'Fully Allocated'}
                    </span>
                </div>
            </div>
        `).join('');
    }
}
async function loadAllocations() {
    const response = await fetch('/api/allocations');
    const allocations = await response.json();
    const list = document.getElementById('allocations-list');
    if (allocations.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <svg fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <p>No allocations yet. Allocate resources to events!</p>
            </div>
        `;
    } else {
        list.innerHTML = allocations.map(alloc => `
            <div class="card">
                <div class="card-header">
                    <div class="card-title">${alloc.event_name} → ${alloc.resource_name}</div>
                    <button class="btn btn-danger" onclick="deleteAllocation(${alloc.event_id}, ${alloc.resource_id})">Remove</button>
                </div>
                <div class="card-body">
                    <p><strong>Event:</strong> ${alloc.event_name} (${alloc.event_date})</p>
                    <p><strong>Resource:</strong> ${alloc.resource_name}</p>
                    <p><strong>Quantity Allocated:</strong> ${alloc.quantity}</p>
                </div>
            </div>
        `).join('');
    }
}

async function populateAllocationSelects() {
    const eventsResponse = await fetch('/api/events');
    const events = await eventsResponse.json();
    const resourcesResponse = await fetch('/api/resources');
    const resources = await resourcesResponse.json();
    const eventSelect = document.getElementById('alloc-event');
    eventSelect.innerHTML = '<option value="">Select an event</option>' + 
        events.map(e => `<option value="${e.id}">${e.name} - ${e.date}</option>`).join('');
    
    const resourceSelect = document.getElementById('alloc-resource');
    resourceSelect.innerHTML = '<option value="">Select a resource</option>' + 
        resources.map(r => `<option value="${r.id}">${r.name} (Available: ${r.available})</option>`).join('');
}

async function deleteEvent(id) {
    if (!confirm('Are you sure you want to delete this event?')) return;
    
    const response = await fetch(`/api/events/${id}`, {method: 'DELETE'});
    if (response.ok) {
        showMessage('Event deleted successfully!', 'success');
        loadEvents();
    } else {
        showMessage('Failed to delete event', 'error');
    }
}

async function deleteResource(id) {
    if (!confirm('Are you sure you want to delete this resource?')) return;
    
    const response = await fetch(`/api/resources/${id}`, {method: 'DELETE'});
    if (response.ok) {
        showMessage('Resource deleted successfully!', 'success');
        loadResources();
    } else {
        showMessage('Failed to delete resource', 'error');
    }
}

async function deleteAllocation(eventId, resourceId) {
    if (!confirm('Are you sure you want to remove this allocation?')) return;
    
    const response = await fetch(`/api/allocations/${eventId}/${resourceId}`, {method: 'DELETE'});
    if (response.ok) {
        showMessage('Allocation removed successfully!', 'success');
        loadAllocations();
        loadResources(); // Refresh resources to show updated availability
    } else {
        showMessage('Failed to remove allocation', 'error');
    }
}

// Load initial data
loadEvents();

// Add event listeners to forms
document.getElementById('event-form').addEventListener('submit', createEvent);
document.getElementById('resource-form').addEventListener('submit', createResource);
document.getElementById('allocation-form').addEventListener('submit', allocateResource);
