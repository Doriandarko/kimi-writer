/**
 * Projects Sidebar Component
 *
 * Collapsible sidebar showing list of projects with minimal, elegant design.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import * as api from '../services/api';

export function ProjectsSidebar({ currentProjectId }) {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

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

  const handleProjectClick = (projectId) => {
    if (projectId === 'new') {
      navigate('/');
    } else {
      navigate(`/workspace/${projectId}`);
    }
  };

  if (isCollapsed) {
    return (
      <div className="h-screen w-12 bg-pearl-50 border-r border-obsidian-200 flex flex-col items-center py-6">
        <button
          onClick={() => setIsCollapsed(false)}
          className="p-2 hover:bg-pearl-200 rounded-md transition-colors"
          title="Expand projects"
        >
          <ChevronRight className="w-5 h-5 text-obsidian-700" />
        </button>
      </div>
    );
  }

  return (
    <div className="h-screen w-72 bg-pearl-50 border-r border-obsidian-200 flex flex-col">
      {/* Header */}
      <div className="px-6 py-6 border-b border-obsidian-200 flex items-center justify-between">
        <h2 className="text-lg font-serif font-semibold text-obsidian-900">Projects</h2>
        <button
          onClick={() => setIsCollapsed(true)}
          className="p-1.5 hover:bg-pearl-200 rounded-md transition-colors"
          title="Collapse sidebar"
        >
          <ChevronLeft className="w-4 h-4 text-obsidian-600" />
        </button>
      </div>

      {/* Projects List */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {loading ? (
          <div className="text-center py-8 text-obsidian-500 text-sm font-body">
            Loading...
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-8 text-obsidian-500 text-sm font-body">
            No projects yet
          </div>
        ) : (
          <div className="space-y-2">
            {projects.map((project) => (
              <button
                key={project.project_id}
                onClick={() => handleProjectClick(project.project_id)}
                className={`w-full text-left px-4 py-3 rounded-md transition-all duration-200 ${
                  currentProjectId === project.project_id
                    ? 'bg-obsidian-900 text-pearl-50 shadow-obsidian'
                    : 'hover:bg-pearl-200 text-obsidian-800'
                }`}
              >
                <div className="font-serif font-medium text-sm mb-1 truncate">
                  {project.project_name}
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs opacity-70 truncate flex-1 mr-2">
                    {project.phase}
                  </span>
                  <span className="text-xs opacity-70 font-medium">
                    {project.progress_percentage.toFixed(0)}%
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* New Project Button */}
      <div className="px-4 py-4 border-t border-obsidian-200">
        <button
          onClick={() => handleProjectClick('new')}
          className="w-full px-4 py-3 bg-obsidian-900 text-pearl-50 rounded-md hover:bg-obsidian-800 transition-colors font-serif text-sm font-medium"
        >
          New Project
        </button>
      </div>
    </div>
  );
}
