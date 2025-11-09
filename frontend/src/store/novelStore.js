/**
 * Zustand store for global novel generation state.
 *
 * Manages project data, generation state, and UI state.
 */

import { create } from 'zustand';

export const useNovelStore = create((set, get) => ({
  // ============================================================================
  // Project State
  // ============================================================================

  currentProject: null,
  projects: [],
  projectConfig: null,
  projectState: null,

  setCurrentProject: (project) => set({ currentProject: project }),

  setProjects: (projects) => set({ projects }),

  setProjectConfig: (config) => set({ projectConfig: config }),

  setProjectState: (state) => set({ projectState: state }),

  updateProjectState: (updates) =>
    set((state) => ({
      projectState: state.projectState
        ? { ...state.projectState, ...updates }
        : null,
    })),

  // ============================================================================
  // Generation State
  // ============================================================================

  isGenerating: false,
  isPaused: false,
  currentPhase: null,
  progress: 0,

  setGenerating: (isGenerating) => set({ isGenerating }),

  setPaused: (isPaused) => set({ isPaused }),

  setCurrentPhase: (phase) => set({ currentPhase: phase }),

  setProgress: (progress) => set({ progress }),

  // ============================================================================
  // Streaming Content
  // ============================================================================

  streamingContent: '',
  streamingReasoning: '',

  appendStreamingContent: (content) =>
    set((state) => ({
      streamingContent: state.streamingContent + content,
    })),

  appendStreamingReasoning: (reasoning) =>
    set((state) => ({
      streamingReasoning: state.streamingReasoning + reasoning,
    })),

  clearStreaming: () =>
    set({
      streamingContent: '',
      streamingReasoning: '',
    }),

  // ============================================================================
  // Tool Calls
  // ============================================================================

  recentToolCalls: [],

  addToolCall: (toolCall) =>
    set((state) => ({
      recentToolCalls: [...state.recentToolCalls, toolCall],
    })),

  updateToolCall: (toolName, result) =>
    set((state) => ({
      recentToolCalls: state.recentToolCalls.map((call) =>
        call.name === toolName && call.status === 'executing'
          ? { ...call, result, status: 'completed' }
          : call
      ),
    })),

  clearToolCalls: () => set({ recentToolCalls: [] }),

  // ============================================================================
  // Token Usage
  // ============================================================================

  tokenCount: 0,
  tokenLimit: 200000,
  tokenPercentage: 0,

  setTokenUsage: (count, limit) =>
    set({
      tokenCount: count,
      tokenLimit: limit,
      tokenPercentage: limit > 0 ? (count / limit) * 100 : 0,
    }),

  // ============================================================================
  // Approval State
  // ============================================================================

  pendingApproval: null,

  setPendingApproval: (approval) => set({ pendingApproval: approval }),

  clearPendingApproval: () => set({ pendingApproval: null }),

  // ============================================================================
  // Files
  // ============================================================================

  projectFiles: [],
  selectedFile: null,
  fileContent: '',

  setProjectFiles: (files) => set({ projectFiles: files }),

  setSelectedFile: (file) => set({ selectedFile: file }),

  setFileContent: (content) => set({ fileContent: content }),

  // ============================================================================
  // Writing Samples
  // ============================================================================

  writingSamples: [],
  selectedWritingSample: null,

  setWritingSamples: (samples) => set({ writingSamples: samples }),

  setSelectedWritingSample: (sample) => set({ selectedWritingSample: sample }),

  // ============================================================================
  // System Prompts
  // ============================================================================

  systemPrompts: {},
  editingPrompt: null,

  setSystemPrompts: (prompts) => set({ systemPrompts: prompts }),

  setEditingPrompt: (agentType, prompt) =>
    set({ editingPrompt: { agentType, prompt } }),

  clearEditingPrompt: () => set({ editingPrompt: null }),

  // ============================================================================
  // UI State
  // ============================================================================

  sidebarOpen: true,
  activeTab: 'output',
  showSettings: false,
  notifications: [],

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setActiveTab: (tab) => set({ activeTab: tab }),

  toggleSettings: () => set((state) => ({ showSettings: !state.showSettings })),

  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        {
          id: Date.now(),
          timestamp: new Date().toISOString(),
          ...notification,
        },
      ],
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  clearNotifications: () => set({ notifications: [] }),

  // ============================================================================
  // Error Handling
  // ============================================================================

  error: null,

  setError: (error) =>
    set({
      error: typeof error === 'string' ? { message: error } : error,
    }),

  clearError: () => set({ error: null }),

  // ============================================================================
  // Loading States
  // ============================================================================

  loading: {
    projects: false,
    config: false,
    state: false,
    files: false,
    samples: false,
    prompts: false,
  },

  setLoading: (key, value) =>
    set((state) => ({
      loading: { ...state.loading, [key]: value },
    })),

  // ============================================================================
  // Statistics
  // ============================================================================

  generationStats: null,

  setGenerationStats: (stats) => set({ generationStats: stats }),

  // ============================================================================
  // Reset Functions
  // ============================================================================

  resetProject: () =>
    set({
      currentProject: null,
      projectConfig: null,
      projectState: null,
      isGenerating: false,
      isPaused: false,
      currentPhase: null,
      progress: 0,
      streamingContent: '',
      streamingReasoning: '',
      recentToolCalls: [],
      pendingApproval: null,
      projectFiles: [],
      selectedFile: null,
      fileContent: '',
      error: null,
      generationStats: null,
    }),

  resetAll: () =>
    set({
      currentProject: null,
      projects: [],
      projectConfig: null,
      projectState: null,
      isGenerating: false,
      isPaused: false,
      currentPhase: null,
      progress: 0,
      streamingContent: '',
      streamingReasoning: '',
      recentToolCalls: [],
      tokenCount: 0,
      tokenLimit: 200000,
      tokenPercentage: 0,
      pendingApproval: null,
      projectFiles: [],
      selectedFile: null,
      fileContent: '',
      writingSamples: [],
      selectedWritingSample: null,
      systemPrompts: {},
      editingPrompt: null,
      notifications: [],
      error: null,
      generationStats: null,
    }),
}));
