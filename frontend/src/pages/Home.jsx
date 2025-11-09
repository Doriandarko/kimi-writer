/**
 * Home Page
 *
 * Landing page with project creation and quick access to recent projects.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Plus, Clock, ArrowRight } from 'lucide-react';
import { ConfigPanel } from '../components/ConfigPanel';
import { useNovelStore } from '../store/novelStore';
import * as api from '../services/api';

export function Home() {
  const navigate = useNavigate();
  const [showConfig, setShowConfig] = useState(false);
  const [writingSamples, setWritingSamples] = useState([]);
  const [recentProjects, setRecentProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const { setError } = useNovelStore();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load writing samples
      const samplesData = await api.listWritingSamples();
      setWritingSamples(samplesData.samples || []);

      // Load recent projects
      const projectsData = await api.listProjects();
      setRecentProjects((projectsData.projects || []).slice(0, 5));
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleCreateProject = async (config) => {
    setLoading(true);

    try {
      const result = await api.createProject(config);
      navigate(`/workspace/${result.project_id}`);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Kimi Writer</h1>
                <p className="text-sm text-gray-600">Multi-Agent Novel Writing System</p>
              </div>
            </div>
            <button
              onClick={() => navigate('/projects')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            >
              <Clock className="w-4 h-4" />
              Browse Projects
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {!showConfig ? (
          <div className="space-y-12">
            {/* Hero Section */}
            <div className="text-center max-w-3xl mx-auto">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Write Your Novel with AI
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Harness the power of multi-agent AI collaboration to create compelling
                stories. From planning to final draft, our autonomous agents work together
                to bring your ideas to life.
              </p>
              <button
                onClick={() => setShowConfig(true)}
                className="inline-flex items-center gap-2 px-6 py-3 text-lg font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
              >
                <Plus className="w-5 h-5" />
                Start New Project
              </button>
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              <div className="bg-white rounded-lg p-6 shadow-md">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-2xl">📝</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Intelligent Planning
                </h3>
                <p className="text-gray-600 text-sm">
                  AI agents create detailed outlines, character profiles, and story
                  structures tailored to your theme.
                </p>
              </div>

              <div className="bg-white rounded-lg p-6 shadow-md">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-2xl">✍️</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Iterative Writing
                </h3>
                <p className="text-gray-600 text-sm">
                  Each chapter is written, critiqued, and refined by specialized agents
                  to ensure quality and consistency.
                </p>
              </div>

              <div className="bg-white rounded-lg p-6 shadow-md">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-2xl">🎯</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Full Control
                </h3>
                <p className="text-gray-600 text-sm">
                  Review and approve plans and chapters, or let the system work
                  autonomously. You decide.
                </p>
              </div>
            </div>

            {/* Recent Projects */}
            {recentProjects.length > 0 && (
              <div className="max-w-5xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-gray-900">Recent Projects</h3>
                  <button
                    onClick={() => navigate('/projects')}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View All
                  </button>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recentProjects.map((project) => (
                    <button
                      key={project.project_id}
                      onClick={() => navigate(`/workspace/${project.project_id}`)}
                      className="bg-white rounded-lg p-4 shadow-md hover:shadow-lg transition-shadow text-left group"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                          {project.project_name}
                        </h4>
                        <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600 transition-colors" />
                      </div>
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                        {project.theme}
                      </p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span className="px-2 py-1 bg-gray-100 rounded">
                          {project.phase}
                        </span>
                        <span>{project.progress_percentage.toFixed(0)}%</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            <ConfigPanel
              writingSamples={writingSamples}
              onSave={handleCreateProject}
              onCancel={() => setShowConfig(false)}
              loading={loading}
              mode="create"
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-20 py-8 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-600">
          <p>Powered by Moonshot AI • Built with React & FastAPI</p>
        </div>
      </footer>
    </div>
  );
}
