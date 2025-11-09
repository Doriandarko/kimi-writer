/**
 * Project Browser Page
 *
 * Browse, search, and manage all novel projects.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Search,
  Plus,
  Trash2,
  ArrowLeft,
  Filter,
  Grid,
  List,
} from 'lucide-react';
import * as api from '../services/api';

export function ProjectBrowser() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [filteredProjects, setFilteredProjects] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPhase, setFilterPhase] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [loading, setLoading] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    filterProjects();
  }, [searchQuery, filterPhase, projects]);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await api.listProjects();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterProjects = () => {
    let filtered = projects;

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(
        (p) =>
          p.project_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.theme.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by phase
    if (filterPhase !== 'all') {
      filtered = filtered.filter((p) => p.phase === filterPhase);
    }

    setFilteredProjects(filtered);
  };

  const handleDelete = async (projectId) => {
    try {
      await api.deleteProject(projectId);
      setProjects(projects.filter((p) => p.project_id !== projectId));
      setDeleteConfirm(null);
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  const phases = [
    { value: 'all', label: 'All Phases' },
    { value: 'PLANNING', label: 'Planning' },
    { value: 'PLAN_CRITIQUE', label: 'Plan Review' },
    { value: 'WRITING', label: 'Writing' },
    { value: 'WRITE_CRITIQUE', label: 'Chapter Review' },
    { value: 'COMPLETE', label: 'Complete' },
  ];

  const ProjectCard = ({ project }) => (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
            {project.project_name}
          </h3>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setDeleteConfirm(project.project_id);
            }}
            className="p-1 hover:bg-red-50 rounded transition-colors"
            title="Delete project"
          >
            <Trash2 className="w-4 h-4 text-red-600" />
          </button>
        </div>

        <p className="text-sm text-gray-600 mb-4 line-clamp-2">{project.theme}</p>

        <div className="space-y-2 mb-4">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span className="px-2 py-1 bg-gray-100 rounded font-medium">
              {project.phase}
            </span>
            <span>{project.novel_length}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-full rounded-full transition-all duration-300"
              style={{ width: `${project.progress_percentage}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Progress</span>
            <span className="font-medium">{project.progress_percentage.toFixed(0)}%</span>
          </div>
        </div>

        <button
          onClick={() => navigate(`/workspace/${project.project_id}`)}
          className="w-full px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
        >
          Open Project
        </button>
      </div>

      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
        Last updated: {new Date(project.last_updated).toLocaleDateString()}
      </div>
    </div>
  );

  const ProjectRow = ({ project }) => (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-4 flex items-center gap-4">
      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
        <BookOpen className="w-6 h-6 text-blue-600" />
      </div>

      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-900 truncate">{project.project_name}</h3>
        <p className="text-sm text-gray-600 truncate">{project.theme}</p>
      </div>

      <div className="flex items-center gap-4 flex-shrink-0">
        <div className="text-right">
          <div className="text-xs text-gray-500 mb-1">{project.phase}</div>
          <div className="text-sm font-medium text-gray-900">
            {project.progress_percentage.toFixed(0)}%
          </div>
        </div>

        <button
          onClick={() => navigate(`/workspace/${project.project_id}`)}
          className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
        >
          Open
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            setDeleteConfirm(project.project_id);
          }}
          className="p-2 hover:bg-red-50 rounded transition-colors"
        >
          <Trash2 className="w-4 h-4 text-red-600" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="p-2 hover:bg-gray-100 rounded-md transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">My Projects</h1>
                <p className="text-sm text-gray-600">
                  {projects.length} {projects.length === 1 ? 'project' : 'projects'}
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Project
            </button>
          </div>
        </div>
      </header>

      {/* Filters & Search */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={filterPhase}
                onChange={(e) => setFilterPhase(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {phases.map((phase) => (
                  <option key={phase.value} value={phase.value}>
                    {phase.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-1 border border-gray-300 rounded-md p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded ${
                  viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'
                }`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded ${
                  viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Projects */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-400">Loading projects...</div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-400">
            <BookOpen className="w-16 h-16 mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">
              {projects.length === 0 ? 'No projects yet' : 'No matching projects'}
            </p>
            <p className="text-sm mb-4">
              {projects.length === 0
                ? 'Create your first novel project to get started'
                : 'Try adjusting your filters'}
            </p>
            {projects.length === 0 && (
              <button
                onClick={() => navigate('/')}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Create Project
              </button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <ProjectCard key={project.project_id} project={project} />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredProjects.map((project) => (
              <ProjectRow key={project.project_id} project={project} />
            ))}
          </div>
        )}
      </main>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={() => setDeleteConfirm(null)}
          />
          <div className="relative bg-white rounded-lg shadow-xl p-6 max-w-md">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Delete Project?</h3>
            <p className="text-sm text-gray-600 mb-6">
              This will permanently delete the project and all its files. This action cannot
              be undone.
            </p>
            <div className="flex items-center gap-3 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
