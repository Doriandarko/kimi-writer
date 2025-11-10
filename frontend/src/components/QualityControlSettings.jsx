/**
 * Quality Control Settings Component
 *
 * Dropdown menu for advanced quality control settings.
 */

import { useState, useRef, useEffect } from 'react';
import { Settings, X } from 'lucide-react';

export function QualityControlSettings({ config, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleChange = (field, value) => {
    onChange({
      ...config,
      [field]: value,
    });
  };

  return (
    <div className="relative" ref={menuRef}>
      {/* Settings Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 hover:bg-pearl-200 rounded-md transition-colors"
        title="Quality Control Settings"
      >
        <Settings className="w-5 h-5 text-obsidian-600" />
      </button>

      {/* Settings Dropdown */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-96 bg-pearl-50 border border-obsidian-300 rounded-lg shadow-obsidian-lg z-50">
          {/* Header */}
          <div className="px-5 py-4 border-b border-obsidian-200 flex items-center justify-between">
            <h3 className="font-serif font-semibold text-obsidian-900">
              Quality Control
            </h3>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-pearl-200 rounded-md transition-colors"
            >
              <X className="w-4 h-4 text-obsidian-600" />
            </button>
          </div>

          {/* Content */}
          <div className="px-5 py-4 space-y-5">
            <div>
              <label className="block text-xs font-body font-semibold text-obsidian-700 mb-2 tracking-wide uppercase">
                Plan Critique Iterations
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={config.max_plan_critique_iterations}
                onChange={(e) =>
                  handleChange('max_plan_critique_iterations', parseInt(e.target.value))
                }
                className="w-full px-3 py-2 bg-pearl-50 border border-obsidian-300 rounded-md text-sm font-body text-obsidian-900 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600"
              />
              <p className="mt-2 text-xs text-obsidian-500 font-body italic">
                How many times the plan will be critiqued and revised
              </p>
            </div>

            <div>
              <label className="block text-xs font-body font-semibold text-obsidian-700 mb-2 tracking-wide uppercase">
                Chapter Critique Iterations
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={config.max_write_critique_iterations}
                onChange={(e) =>
                  handleChange('max_write_critique_iterations', parseInt(e.target.value))
                }
                className="w-full px-3 py-2 bg-pearl-50 border border-obsidian-300 rounded-md text-sm font-body text-obsidian-900 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600"
              />
              <p className="mt-2 text-xs text-obsidian-500 font-body italic">
                How many times each chapter will be critiqued and revised
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
