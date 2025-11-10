/**
 * Novel Workspace Page
 *
 * Main workspace for monitoring and interacting with novel generation.
 * Integrates all components and WebSocket updates.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Play,
  Pause,
  FileText,
  Activity,
  Settings as SettingsIcon,
} from 'lucide-react';

import { useNovelStore } from '../store/novelStore';
import { useWebSocket, useStreamingContent, useToolCalls } from '../hooks/useWebSocket';
import { ProgressDashboard } from '../components/ProgressDashboard';
import { StreamingOutput } from '../components/StreamingOutput';
import { FileViewer } from '../components/FileViewer';
import { ApprovalModal } from '../components/ApprovalModal';
import * as api from '../services/api';

export function NovelWorkspace() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('live'); // 'live' or 'files'
  const [approvalLoading, setApprovalLoading] = useState(false);

  const {
    currentProject,
    setCurrentProject,
    projectConfig,
    setProjectConfig,
    projectState,
    setProjectState,
    updateProjectState,
    isGenerating,
    setGenerating,
    isPaused,
    setPaused,
    currentPhase,
    setCurrentPhase,
    progress,
    setProgress,
    tokenCount,
    tokenLimit,
    tokenPercentage,
    setTokenUsage,
    pendingApproval,
    setPendingApproval,
    clearPendingApproval,
    projectFiles,
    setProjectFiles,
    selectedFile,
    setSelectedFile,
    fileContent,
    setFileContent,
    generationStats,
    setGenerationStats,
    error,
    setError,
  } = useNovelStore();

  // WebSocket connection
  const wsHandlers = {
    phase_change: (data) => {
      setCurrentPhase(data.to_phase);
      updateProjectState({ phase: data.to_phase });
    },
    token_update: (data) => {
      setTokenUsage(data.token_count, data.token_limit);
    },
    approval_required: (data) => {
      setPendingApproval({
        type: data.approval_type,
        data: data.data,
      });
    },
    error: (data) => {
      setError(data.message);
    },
    complete: (data) => {
      setGenerating(false);
      setGenerationStats(data.stats);
    },
    progress: (data) => {
      setProgress(data.percentage);
    },
  };

  const { isConnected, wsClient } = useWebSocket(projectId, wsHandlers, true);

  // Streaming content
  const { content, reasoning, isStreaming, clearContent } = useStreamingContent(wsClient);

  // Tool calls
  const { toolCalls } = useToolCalls(wsClient);

  // Load initial data
  useEffect(() => {
    if (projectId) {
      loadProjectData();
    }
  }, [projectId]);

  const loadProjectData = async () => {
    try {
      // Load project info
      const project = await api.getProject(projectId);
      setCurrentProject(project);

      // Load config
      const config = await api.getProjectConfig(projectId);
      setProjectConfig(config);

      // Load state
      const state = await api.getProjectState(projectId);
      setProjectState(state);
      setCurrentPhase(state.phase);
      setProgress(state.progress_percentage);
      setGenerating(!state.paused && state.phase !== 'COMPLETE');
      setPaused(state.paused);

      // Load files
      await loadFiles();
    } catch (error) {
      setError(error.message);
      console.error('Failed to load project:', error);
    }
  };

  const loadFiles = async () => {
    try {
      const data = await api.listProjectFiles(projectId);
      setProjectFiles(data.files || []);
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const handleFileSelect = async (filename) => {
    setSelectedFile(filename);
    try {
      const data = await api.getFileContent(projectId, filename);
      setFileContent(data.content);
    } catch (error) {
      console.error('Failed to load file content:', error);
    }
  };

  const handleStart = async () => {
    try {
      await api.startGeneration(projectId);
      setGenerating(true);
      setPaused(false);
    } catch (error) {
      setError(error.message);
    }
  };

  const handlePause = async () => {
    try {
      await api.pauseGeneration(projectId);
      setPaused(true);
    } catch (error) {
      setError(error.message);
    }
  };

  const handleResume = async () => {
    try {
      await api.resumeGeneration(projectId);
      setPaused(false);
    } catch (error) {
      setError(error.message);
    }
  };

  const handleApprove = async (decision) => {
    setApprovalLoading(true);
    try {
      await api.submitApproval(projectId, decision);
      clearPendingApproval();
      await loadProjectData();
    } catch (error) {
      setError(error.message);
    } finally {
      setApprovalLoading(false);
    }
  };

  const handleReject = async (decision) => {
    setApprovalLoading(true);
    try {
      await api.submitApproval(projectId, decision);
      clearPendingApproval();
      await loadProjectData();
    } catch (error) {
      setError(error.message);
    } finally {
      setApprovalLoading(false);
    }
  };

  if (!projectConfig || !projectState) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-pearl-50">
        <div className="text-obsidian-500 font-body">Loading project...</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-pearl-50">
      {/* Header */}
      <header className="bg-pearl-50 border-b border-obsidian-200 flex-shrink-0">
        <div className="px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/projects')}
                className="p-2 hover:bg-pearl-200 rounded-md transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-obsidian-700" />
              </button>
              <div>
                <h1 className="text-2xl font-serif font-bold text-obsidian-900">
                  {projectConfig.project_name}
                </h1>
                <p className="text-sm font-body text-obsidian-600 line-clamp-1 mt-0.5">
                  {projectConfig.theme}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Connection Status */}
              <div className="flex items-center gap-2 text-sm font-body">
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? 'bg-obsidian-900' : 'bg-obsidian-400'
                  }`}
                />
                <span className="text-obsidian-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {/* Control Buttons */}
              {!isGenerating && !isPaused && (
                <button
                  onClick={handleStart}
                  className="flex items-center gap-2 px-5 py-2.5 text-sm font-serif font-medium text-pearl-50 bg-obsidian-900 rounded-md hover:bg-obsidian-800 transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Start Generation
                </button>
              )}

              {isGenerating && !isPaused && (
                <button
                  onClick={handlePause}
                  className="flex items-center gap-2 px-5 py-2.5 text-sm font-serif font-medium text-obsidian-900 bg-pearl-200 border border-obsidian-300 rounded-md hover:bg-pearl-300 transition-colors"
                >
                  <Pause className="w-4 h-4" />
                  Pause
                </button>
              )}

              {isPaused && (
                <button
                  onClick={handleResume}
                  className="flex items-center gap-2 px-5 py-2.5 text-sm font-serif font-medium text-pearl-50 bg-obsidian-900 rounded-md hover:bg-obsidian-800 transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Resume
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex">
        {/* Left Sidebar - Progress */}
        <aside className="w-96 border-r border-obsidian-200 bg-pearl-100 overflow-y-auto p-5">
          <ProgressDashboard
            phase={currentPhase}
            progress={progress}
            currentChapter={projectState.current_chapter}
            totalChapters={projectState.total_chapters}
            chaptersCompleted={projectState.chapters_completed || []}
            isGenerating={isGenerating}
            isPaused={isPaused}
            tokenCount={tokenCount}
            tokenLimit={tokenLimit}
            tokenPercentage={tokenPercentage}
            stats={generationStats}
          />
        </aside>

        {/* Main Area */}
        <main className="flex-1 overflow-hidden flex flex-col">
          {/* Tabs */}
          <div className="border-b border-obsidian-200 bg-pearl-100">
            <div className="flex gap-1 px-5">
              <button
                onClick={() => setActiveTab('live')}
                className={`flex items-center gap-2 px-5 py-3 border-b-2 transition-all font-serif ${
                  activeTab === 'live'
                    ? 'border-obsidian-900 text-obsidian-900 font-semibold'
                    : 'border-transparent text-obsidian-600 hover:text-obsidian-900'
                }`}
              >
                <Activity className="w-4 h-4" />
                Live Output
              </button>
              <button
                onClick={() => setActiveTab('files')}
                className={`flex items-center gap-2 px-5 py-3 border-b-2 transition-all font-serif ${
                  activeTab === 'files'
                    ? 'border-obsidian-900 text-obsidian-900 font-semibold'
                    : 'border-transparent text-obsidian-600 hover:text-obsidian-900'
                }`}
              >
                <FileText className="w-4 h-4" />
                Files ({projectFiles.length})
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden p-5 bg-pearl-50">
            {activeTab === 'live' ? (
              <StreamingOutput
                content={content}
                reasoning={reasoning}
                isStreaming={isStreaming}
              />
            ) : (
              <FileViewer
                projectId={projectId}
                files={projectFiles}
                selectedFile={selectedFile}
                fileContent={fileContent}
                onFileSelect={handleFileSelect}
                onRefresh={loadFiles}
                loading={false}
              />
            )}
          </div>
        </main>
      </div>

      {/* Approval Modal */}
      {pendingApproval && (
        <ApprovalModal
          isOpen={true}
          approvalType={pendingApproval.type}
          approvalData={pendingApproval.data}
          onApprove={handleApprove}
          onReject={handleReject}
          onClose={() => {}}
          loading={approvalLoading}
        />
      )}

      {/* Error Toast */}
      {error && (
        <div className="fixed bottom-6 right-6 bg-obsidian-900 text-pearl-50 px-6 py-4 rounded-lg border border-obsidian-700 shadow-obsidian-lg max-w-md">
          <p className="text-sm font-body">{error.message || error}</p>
          <button
            onClick={() => setError(null)}
            className="mt-2 text-xs font-body underline hover:no-underline opacity-80 hover:opacity-100 transition-opacity"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
}
