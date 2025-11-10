/**
 * Style Card Component
 *
 * Expandable card for configuring writing sample style.
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export function StyleCard({ index, value, onChange }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleNameChange = (newName) => {
    onChange({
      ...value,
      name: newName,
    });
  };

  const handleSampleChange = (newSample) => {
    onChange({
      ...value,
      sample: newSample,
    });
  };

  return (
    <div className="border border-obsidian-300 rounded-lg overflow-hidden transition-all duration-300 hover:border-obsidian-500">
      {/* Card Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-5 py-4 bg-pearl-100 hover:bg-pearl-200 transition-colors flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-obsidian-900 text-pearl-50 rounded-md flex items-center justify-center font-serif text-sm font-semibold">
            {index + 1}
          </div>
          <span className="font-serif text-sm font-medium text-obsidian-900">
            {value.name || `Custom Style ${index + 1}`}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-obsidian-600" />
        ) : (
          <ChevronDown className="w-5 h-5 text-obsidian-600" />
        )}
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-5 py-5 bg-pearl-50 border-t border-obsidian-200 space-y-4">
          <div>
            <label className="block text-xs font-body font-semibold text-obsidian-700 mb-2 tracking-wide uppercase">
              Style Name
            </label>
            <input
              type="text"
              value={value.name || ''}
              onChange={(e) => handleNameChange(e.target.value)}
              placeholder={`Custom Style ${index + 1}`}
              className="w-full px-3 py-2 bg-pearl-50 border border-obsidian-300 rounded-md text-sm font-body text-obsidian-900 placeholder-obsidian-400 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600 transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-body font-semibold text-obsidian-700 mb-2 tracking-wide uppercase">
              Writing Sample
            </label>
            <textarea
              value={value.sample || ''}
              onChange={(e) => handleSampleChange(e.target.value)}
              placeholder="Paste a sample of writing style you'd like to emulate..."
              rows={6}
              className="w-full px-3 py-2 bg-pearl-50 border border-obsidian-300 rounded-md text-sm font-body text-obsidian-900 placeholder-obsidian-400 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600 transition-all resize-none"
            />
            <p className="mt-2 text-xs text-obsidian-500 font-body italic">
              {value.sample?.length || 0} characters
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
