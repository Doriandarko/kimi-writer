/**
 * REST API client for the Kimi Novel Writing System backend.
 *
 * Provides functions to interact with all backend endpoints.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Generic fetch wrapper with error handling.
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

// ============================================================================
// Configuration Endpoints
// ============================================================================

/**
 * Create a new novel project with configuration.
 */
export async function createProject(config) {
  return apiFetch('/config', {
    method: 'POST',
    body: JSON.stringify(config),
  });
}

/**
 * Get project configuration by ID.
 */
export async function getProjectConfig(projectId) {
  return apiFetch(`/config/${projectId}`);
}

/**
 * Update project configuration.
 */
export async function updateProjectConfig(projectId, updates) {
  return apiFetch(`/config/${projectId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

// ============================================================================
// Project Management Endpoints
// ============================================================================

/**
 * Get list of all projects.
 */
export async function listProjects() {
  return apiFetch('/projects');
}

/**
 * Get detailed project information.
 */
export async function getProject(projectId) {
  return apiFetch(`/projects/${projectId}`);
}

/**
 * Delete a project.
 */
export async function deleteProject(projectId) {
  return apiFetch(`/projects/${projectId}`, {
    method: 'DELETE',
  });
}

// ============================================================================
// Execution Control Endpoints
// ============================================================================

/**
 * Start novel generation for a project.
 */
export async function startGeneration(projectId) {
  return apiFetch(`/projects/${projectId}/start`, {
    method: 'POST',
  });
}

/**
 * Pause novel generation.
 */
export async function pauseGeneration(projectId) {
  return apiFetch(`/projects/${projectId}/pause`, {
    method: 'POST',
  });
}

/**
 * Resume paused generation.
 */
export async function resumeGeneration(projectId) {
  return apiFetch(`/projects/${projectId}/resume`, {
    method: 'POST',
  });
}

// ============================================================================
// State & Progress Endpoints
// ============================================================================

/**
 * Get current project state.
 */
export async function getProjectState(projectId) {
  return apiFetch(`/projects/${projectId}/state`);
}

/**
 * Get project progress information.
 */
export async function getProjectProgress(projectId) {
  return apiFetch(`/projects/${projectId}/progress`);
}

/**
 * Get generation statistics.
 */
export async function getGenerationStats(projectId) {
  return apiFetch(`/projects/${projectId}/stats`);
}

// ============================================================================
// Approval Endpoints
// ============================================================================

/**
 * Get pending approval information.
 */
export async function getPendingApproval(projectId) {
  return apiFetch(`/projects/${projectId}/pending-approval`);
}

/**
 * Submit approval decision.
 */
export async function submitApproval(projectId, decision) {
  return apiFetch(`/projects/${projectId}/approve`, {
    method: 'POST',
    body: JSON.stringify(decision),
  });
}

// ============================================================================
// File Management Endpoints
// ============================================================================

/**
 * List all files in project output directory.
 */
export async function listProjectFiles(projectId) {
  return apiFetch(`/projects/${projectId}/files`);
}

/**
 * Get content of a specific file.
 */
export async function getFileContent(projectId, filename) {
  return apiFetch(`/projects/${projectId}/files/${filename}`);
}

// ============================================================================
// Writing Samples Endpoints
// ============================================================================

/**
 * Get list of available writing samples.
 */
export async function listWritingSamples() {
  return apiFetch('/writing-samples');
}

/**
 * Get specific writing sample content.
 */
export async function getWritingSample(sampleId) {
  return apiFetch(`/writing-samples/${sampleId}`);
}

/**
 * Save a custom writing sample.
 */
export async function saveCustomWritingSample(sample) {
  return apiFetch('/writing-samples/custom', {
    method: 'POST',
    body: JSON.stringify(sample),
  });
}

// ============================================================================
// System Prompts Endpoints
// ============================================================================

/**
 * Get all system prompts.
 */
export async function getAllSystemPrompts() {
  return apiFetch('/system-prompts');
}

/**
 * Get system prompt for specific agent.
 */
export async function getSystemPrompt(agentType) {
  return apiFetch(`/system-prompts/${agentType}`);
}

/**
 * Update system prompt for specific agent.
 */
export async function updateSystemPrompt(agentType, prompt) {
  return apiFetch(`/system-prompts/${agentType}`, {
    method: 'PUT',
    body: JSON.stringify({ prompt }),
  });
}

/**
 * Reset system prompt to default.
 */
export async function resetSystemPrompt(agentType) {
  return apiFetch(`/system-prompts/${agentType}/reset`, {
    method: 'POST',
  });
}

// ============================================================================
// Health Check
// ============================================================================

/**
 * Check API health status.
 */
export async function healthCheck() {
  const url = API_BASE_URL.replace('/api', '/health');
  const response = await fetch(url);
  return response.json();
}

// Export API base URL for WebSocket connection
export { API_BASE_URL };
