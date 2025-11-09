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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-400">Loading project...</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/projects')}
                className="p-2 hover:bg-gray-100 rounded-md transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  {projectConfig.project_name}
                </h1>
                <p className="text-sm text-gray-600 line-clamp-1">
                  {projectConfig.theme}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Connection Status */}
              <div className="flex items-center gap-2 text-sm">
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? 'bg-green-600' : 'bg-red-600'
                  }`}
                />
                <span className="text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {/* Control Buttons */}
              {!isGenerating && !isPaused && (
                <button
                  onClick={handleStart}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Start Generation
                </button>
              )}

              {isGenerating && !isPaused && (
                <button
                  onClick={handlePause}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-yellow-600 rounded-md hover:bg-yellow-700 transition-colors"
                >
                  <Pause className="w-4 h-4" />
                  Pause
                </button>
              )}

              {isPaused && (
                <button
                  onClick={handleResume}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
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
        <aside className="w-96 border-r border-gray-200 bg-white overflow-y-auto p-4">
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
          <div className="border-b border-gray-200 bg-white">
            <div className="flex gap-4 px-4">
              <button
                onClick={() => setActiveTab('live')}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  activeTab === 'live'
                    ? 'border-blue-600 text-blue-600 font-medium'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Activity className="w-4 h-4" />
                Live Output
              </button>
              <button
                onClick={() => setActiveTab('files')}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  activeTab === 'files'
                    ? 'border-blue-600 text-blue-600 font-medium'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <FileText className="w-4 h-4" />
                Files ({projectFiles.length})
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden p-4">
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
        <div className="fixed bottom-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg max-w-md">
          <p className="text-sm font-medium">{error.message || error}</p>
          <button
            onClick={() => setError(null)}
            className="mt-2 text-xs underline hover:no-underline"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
}
