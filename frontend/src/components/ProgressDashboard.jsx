/**
 * Progress Dashboard Component
 *
 * Displays current generation progress, phase, chapter info, and statistics.
 */

import { CheckCircle, Circle, Clock, FileText, Zap } from 'lucide-react';

export function ProgressDashboard({
  phase,
  progress,
  currentChapter,
  totalChapters,
  chaptersCompleted,
  isGenerating,
  isPaused,
  tokenCount,
  tokenLimit,
  tokenPercentage,
  stats,
}) {
  const phases = [
    { name: 'PLANNING', label: 'Planning', icon: FileText },
    { name: 'PLAN_CRITIQUE', label: 'Plan Review', icon: CheckCircle },
    { name: 'WRITING', label: 'Writing', icon: Zap },
    { name: 'WRITE_CRITIQUE', label: 'Chapter Review', icon: CheckCircle },
  ];

  const getCurrentPhaseIndex = () => {
    return phases.findIndex((p) => p.name === phase);
  };

  const currentPhaseIndex = getCurrentPhaseIndex();

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      {/* Status Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Generation Progress</h2>
        <div className="flex items-center gap-2">
          {isGenerating && !isPaused && (
            <div className="flex items-center gap-2 text-green-600">
              <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
              <span className="text-sm font-medium">Active</span>
            </div>
          )}
          {isPaused && (
            <div className="flex items-center gap-2 text-yellow-600">
              <Clock className="w-4 h-4" />
              <span className="text-sm font-medium">Paused</span>
            </div>
          )}
          {!isGenerating && !isPaused && (
            <div className="flex items-center gap-2 text-gray-400">
              <Circle className="w-4 h-4" />
              <span className="text-sm font-medium">Idle</span>
            </div>
          )}
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-medium text-gray-900">{progress.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-blue-600 h-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Phase Progress */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Current Phase</h3>
        <div className="flex items-center justify-between">
          {phases.map((phaseInfo, index) => {
            const Icon = phaseInfo.icon;
            const isActive = index === currentPhaseIndex;
            const isCompleted = index < currentPhaseIndex;

            return (
              <div key={phaseInfo.name} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : isCompleted
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-200 text-gray-400'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <span
                    className={`mt-2 text-xs font-medium ${
                      isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-400'
                    }`}
                  >
                    {phaseInfo.label}
                  </span>
                </div>
                {index < phases.length - 1 && (
                  <div
                    className={`h-1 flex-1 ${
                      isCompleted ? 'bg-green-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Chapter Progress (if in writing phase) */}
      {phase === 'WRITING' && totalChapters > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Chapter Progress</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">
                Chapter {currentChapter} of {totalChapters}
              </span>
              <span className="text-sm font-medium text-gray-900">
                {chaptersCompleted.length} completed
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-full rounded-full transition-all duration-300"
                style={{
                  width: `${(chaptersCompleted.length / totalChapters) * 100}%`,
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Token Usage */}
      {tokenLimit > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Context Usage</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">
                {tokenCount.toLocaleString()} / {tokenLimit.toLocaleString()} tokens
              </span>
              <span className="text-sm font-medium text-gray-900">
                {tokenPercentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  tokenPercentage > 90
                    ? 'bg-red-600'
                    : tokenPercentage > 75
                    ? 'bg-yellow-600'
                    : 'bg-blue-600'
                }`}
                style={{ width: `${Math.min(tokenPercentage, 100)}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      {stats && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Statistics</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-gray-900">
                {stats.total_iterations || 0}
              </div>
              <div className="text-xs text-gray-600">Total Iterations</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-gray-900">
                {stats.plan_critique_iterations || 0}
              </div>
              <div className="text-xs text-gray-600">Plan Critiques</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-gray-900">
                {stats.total_words_written?.toLocaleString() || 0}
              </div>
              <div className="text-xs text-gray-600">Words Written</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-gray-900">
                {stats.time_elapsed
                  ? `${Math.floor(stats.time_elapsed / 60)}m`
                  : '0m'}
              </div>
              <div className="text-xs text-gray-600">Time Elapsed</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
