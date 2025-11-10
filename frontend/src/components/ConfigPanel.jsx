/**
 * Configuration Panel Component
 *
 * Form for creating and editing novel project configuration.
 */

import { useState, useEffect } from 'react';
import { Settings, Save, X, AlertCircle } from 'lucide-react';

const NOVEL_LENGTHS = [
  { value: 'short_story', label: 'Short Story', chapters: 3, words: '3k-10k' },
  { value: 'novella', label: 'Novella', chapters: 8, words: '20k-50k' },
  { value: 'novel', label: 'Novel', chapters: 15, words: '50k-110k' },
  { value: 'long_novel', label: 'Long Novel', chapters: 30, words: '110k-200k' },
  { value: 'ai_decide', label: 'Let AI Decide', chapters: '?', words: 'Variable' },
];

export function ConfigPanel({
  initialConfig,
  writingSamples,
  onSave,
  onCancel,
  loading,
  mode = 'create', // 'create' or 'edit'
}) {
  const [config, setConfig] = useState({
    project_name: '',
    theme: '',
    novel_length: 'novel',
    genre: '',
    writing_sample_id: null,
    custom_writing_sample: '',
    max_plan_critique_iterations: 2,
    max_write_critique_iterations: 2,
    require_plan_approval: true,
    require_chapter_approval: false,
    ...initialConfig,
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (initialConfig) {
      setConfig({ ...config, ...initialConfig });
    }
  }, [initialConfig]);

  const validate = () => {
    const newErrors = {};

    if (!config.project_name?.trim()) {
      newErrors.project_name = 'Project name is required';
    }

    if (!config.theme?.trim()) {
      newErrors.theme = 'Theme is required';
    }

    if (config.custom_writing_sample && config.custom_writing_sample.length < 100) {
      newErrors.custom_writing_sample = 'Writing sample must be at least 100 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    onSave(config);
  };

  const handleChange = (field, value) => {
    setConfig({ ...config, [field]: value });
    // Clear error for this field
    if (errors[field]) {
      setErrors({ ...errors, [field]: undefined });
    }
  };

  const selectedLength = NOVEL_LENGTHS.find((l) => l.value === config.novel_length);

  return (
    <div className="bg-white rounded-lg shadow-md">
      <form onSubmit={handleSubmit}>
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Settings className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {mode === 'create' ? 'Create New Project' : 'Edit Project Configuration'}
              </h2>
              <p className="text-sm text-gray-600">
                Configure your novel generation settings
              </p>
            </div>
          </div>
        </div>

        {/* Form Content */}
        <div className="px-6 py-4 space-y-6 max-h-[70vh] overflow-y-auto">
          {/* Basic Information */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Basic Information</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={config.project_name}
                  onChange={(e) => handleChange('project_name', e.target.value)}
                  placeholder="My Awesome Novel"
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.project_name ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.project_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.project_name}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Theme / Premise *
                </label>
                <textarea
                  value={config.theme}
                  onChange={(e) => handleChange('theme', e.target.value)}
                  placeholder="A detective investigating a mysterious disappearance in a small town..."
                  rows={3}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
                    errors.theme ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.theme && (
                  <p className="mt-1 text-sm text-red-600">{errors.theme}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Genre (Optional)
                </label>
                <input
                  type="text"
                  value={config.genre}
                  onChange={(e) => handleChange('genre', e.target.value)}
                  placeholder="e.g., Mystery, Science Fiction, Romance"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Novel Length
                </label>
                <select
                  value={config.novel_length}
                  onChange={(e) => handleChange('novel_length', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {NOVEL_LENGTHS.map((length) => (
                    <option key={length.value} value={length.value}>
                      {length.label} ({length.chapters} chapters)
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-sm text-gray-600">
                  This project will generate approximately {selectedLength?.chapters} chapters
                </p>
              </div>
            </div>
          </div>

          {/* Writing Style */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Writing Style</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Writing Sample (Optional)
                </label>
                <select
                  value={config.writing_sample_id || ''}
                  onChange={(e) =>
                    handleChange('writing_sample_id', e.target.value || null)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">No writing sample (default style)</option>
                  {writingSamples.map((sample) => (
                    <option key={sample.id} value={sample.id}>
                      {sample.name}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-sm text-gray-600">
                  Select a writing sample to guide the AI's style
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Or Provide Custom Sample
                </label>
                <textarea
                  value={config.custom_writing_sample}
                  onChange={(e) => handleChange('custom_writing_sample', e.target.value)}
                  placeholder="Paste a sample of writing style you'd like to emulate (at least 100 characters)..."
                  rows={4}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
                    errors.custom_writing_sample ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.custom_writing_sample && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.custom_writing_sample}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Quality Control */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Quality Control</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Plan Critique Iterations
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={config.max_plan_critique_iterations}
                  onChange={(e) =>
                    handleChange('max_plan_critique_iterations', parseInt(e.target.value))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="mt-1 text-sm text-gray-600">
                  Number of times the plan will be critiqued and revised
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Write Critique Iterations
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={config.max_write_critique_iterations}
                  onChange={(e) =>
                    handleChange('max_write_critique_iterations', parseInt(e.target.value))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="mt-1 text-sm text-gray-600">
                  Number of times each chapter will be critiqued and revised
                </p>
              </div>
            </div>
          </div>

          {/* Approval Checkpoints */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              Approval Checkpoints
            </h3>
            <div className="space-y-3">
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.require_plan_approval}
                  onChange={(e) => handleChange('require_plan_approval', e.target.checked)}
                  className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">
                    Require Plan Approval
                  </div>
                  <p className="text-sm text-gray-600">
                    Pause after planning phase for manual review
                  </p>
                </div>
              </label>

              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.require_chapter_approval}
                  onChange={(e) =>
                    handleChange('require_chapter_approval', e.target.checked)
                  }
                  className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">
                    Require Chapter Approval
                  </div>
                  <p className="text-sm text-gray-600">
                    Pause after each chapter for manual review
                  </p>
                </div>
              </label>
            </div>
          </div>

          {/* Warning for no approvals */}
          {!config.require_plan_approval && !config.require_chapter_approval && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0" />
                <div className="text-sm text-yellow-800">
                  <p className="font-medium">Autonomous Mode</p>
                  <p className="mt-1">
                    With no approval checkpoints, the system will generate the entire novel
                    autonomously. You won't be able to review or modify the plan or individual
                    chapters during generation.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-end gap-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              {loading
                ? 'Saving...'
                : mode === 'create'
                ? 'Create Project'
                : 'Save Changes'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
