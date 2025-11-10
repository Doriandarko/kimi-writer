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
    <div className="bg-pearl-100 rounded-lg border border-obsidian-200 hover:border-obsidian-400 transition-all overflow-hidden shadow-pearl hover:shadow-pearl-lg">
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-serif font-semibold text-obsidian-900 line-clamp-1">
            {project.project_name}
          </h3>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setDeleteConfirm(project.project_id);
            }}
            className="p-1.5 hover:bg-pearl-200 rounded transition-colors"
            title="Delete project"
          >
            <Trash2 className="w-4 h-4 text-obsidian-600" />
          </button>
        </div>

        <p className="text-sm font-body text-obsidian-700 mb-4 line-clamp-2">{project.theme}</p>

        <div className="space-y-3 mb-4">
          <div className="flex items-center justify-between text-xs font-body text-obsidian-600">
            <span className="px-2 py-1 bg-pearl-200 rounded font-medium">
              {project.phase}
            </span>
            <span className="uppercase tracking-wider">{project.novel_length}</span>
          </div>
          <div className="w-full bg-pearl-200 rounded-full h-1.5">
            <div
              className="bg-obsidian-900 h-full rounded-full transition-all duration-300"
              style={{ width: `${project.progress_percentage}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-xs font-body text-obsidian-600">
            <span className="uppercase tracking-wider">Progress</span>
            <span className="font-semibold">{project.progress_percentage.toFixed(0)}%</span>
          </div>
        </div>

        <button
          onClick={() => navigate(`/workspace/${project.project_id}`)}
          className="w-full px-4 py-2.5 text-sm font-serif font-medium text-pearl-50 bg-obsidian-900 rounded-md hover:bg-obsidian-800 transition-colors"
        >
          Open Project
        </button>
      </div>

      <div className="px-6 py-3 bg-pearl-200 border-t border-obsidian-200 text-xs font-body text-obsidian-600">
        Last updated: {new Date(project.last_updated).toLocaleDateString()}
      </div>
    </div>
  );

  const ProjectRow = ({ project }) => (
    <div className="bg-pearl-100 rounded-lg border border-obsidian-200 hover:border-obsidian-400 transition-all p-5 flex items-center gap-6 shadow-pearl hover:shadow-pearl-lg">
      <div className="flex-1 min-w-0">
        <h3 className="font-serif font-semibold text-obsidian-900 truncate mb-1">{project.project_name}</h3>
        <p className="text-sm font-body text-obsidian-700 truncate">{project.theme}</p>
      </div>

      <div className="flex items-center gap-6 flex-shrink-0">
        <div className="text-right">
          <div className="text-xs font-body text-obsidian-600 mb-1 uppercase tracking-wider">{project.phase}</div>
          <div className="text-sm font-serif font-semibold text-obsidian-900">
            {project.progress_percentage.toFixed(0)}%
          </div>
        </div>

        <button
          onClick={() => navigate(`/workspace/${project.project_id}`)}
          className="px-5 py-2 text-sm font-serif font-medium text-pearl-50 bg-obsidian-900 rounded-md hover:bg-obsidian-800 transition-colors"
        >
          Open
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            setDeleteConfirm(project.project_id);
          }}
          className="p-2 hover:bg-pearl-200 rounded transition-colors"
        >
          <Trash2 className="w-4 h-4 text-obsidian-600" />
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-pearl-50">
      {/* Header */}
      <header className="bg-pearl-50 border-b border-obsidian-200">
        <div className="max-w-7xl mx-auto px-8 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <button
                onClick={() => navigate('/')}
                className="p-2 hover:bg-pearl-200 rounded-md transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-obsidian-700" />
              </button>
              <div>
                <h1 className="text-4xl font-serif font-bold text-obsidian-900">My Projects</h1>
                <p className="text-sm font-body text-obsidian-600 mt-1">
                  {projects.length} {projects.length === 1 ? 'project' : 'projects'}
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 text-sm font-serif font-medium text-pearl-50 bg-obsidian-900 rounded-md hover:bg-obsidian-800 transition-colors"
            >
              New Project
            </button>
          </div>
        </div>
      </header>

      {/* Filters & Search */}
      <div className="bg-pearl-100 border-b border-obsidian-200">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-obsidian-500" />
              <input
                type="text"
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-pearl-50 border border-obsidian-300 rounded-md font-body text-obsidian-900 placeholder-obsidian-400 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600 transition-all"
              />
            </div>

            <div className="flex items-center gap-3">
              <select
                value={filterPhase}
                onChange={(e) => setFilterPhase(e.target.value)}
                className="px-4 py-3 bg-pearl-50 border border-obsidian-300 rounded-md font-body text-obsidian-900 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600 transition-all"
              >
                {phases.map((phase) => (
                  <option key={phase.value} value={phase.value}>
                    {phase.label}
                  </option>
                ))}
              </select>

              <div className="flex items-center gap-1 border border-obsidian-300 rounded-md p-1 bg-pearl-50">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded transition-colors ${
                    viewMode === 'grid' ? 'bg-obsidian-900 text-pearl-50' : 'text-obsidian-600 hover:bg-pearl-200'
                  }`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded transition-colors ${
                    viewMode === 'list' ? 'bg-obsidian-900 text-pearl-50' : 'text-obsidian-600 hover:bg-pearl-200'
                  }`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Projects */}
      <main className="max-w-7xl mx-auto px-8 py-8">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-obsidian-500 font-body">Loading projects...</div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-obsidian-500">
            <p className="text-xl font-serif font-semibold mb-2">
              {projects.length === 0 ? 'No projects yet' : 'No matching projects'}
            </p>
            <p className="text-sm font-body mb-6">
              {projects.length === 0
                ? 'Create your first novel project to get started'
                : 'Try adjusting your filters'}
            </p>
            {projects.length === 0 && (
              <button
                onClick={() => navigate('/')}
                className="px-6 py-3 text-sm font-serif font-medium text-pearl-50 bg-obsidian-900 rounded-md hover:bg-obsidian-800 transition-colors"
              >
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
            className="absolute inset-0 bg-obsidian-900 bg-opacity-60"
            onClick={() => setDeleteConfirm(null)}
          />
          <div className="relative bg-pearl-50 rounded-lg border-2 border-obsidian-300 shadow-obsidian-lg p-8 max-w-md">
            <h3 className="text-xl font-serif font-bold text-obsidian-900 mb-3">Delete Project?</h3>
            <p className="text-sm font-body text-obsidian-700 mb-8 leading-relaxed">
              This will permanently delete the project and all its files. This action cannot
              be undone.
            </p>
            <div className="flex items-center gap-4 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-5 py-2.5 text-sm font-serif font-medium text-obsidian-700 bg-pearl-100 border border-obsidian-300 rounded-md hover:bg-pearl-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="px-5 py-2.5 text-sm font-serif font-medium text-pearl-50 bg-obsidian-900 rounded-md hover:bg-obsidian-800 transition-colors"
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
