/**
 * File Viewer Component
 *
 * Displays project files and allows viewing their contents.
 */

import { useState, useEffect } from 'react';
import { FileText, Download, RefreshCw, Folder } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export function FileViewer({
  projectId,
  files,
  selectedFile,
  fileContent,
  onFileSelect,
  onRefresh,
  loading,
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFiles = files.filter((file) =>
    file.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDownload = () => {
    if (!fileContent || !selectedFile) return;

    const blob = new Blob([fileContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = selectedFile;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getFileIcon = (filename) => {
    if (filename.includes('chapter')) return '📖';
    if (filename.includes('summary')) return '📋';
    if (filename.includes('outline')) return '📝';
    if (filename.includes('character') || filename.includes('dramatis')) return '👤';
    if (filename.includes('structure')) return '🏗️';
    return '📄';
  };

  return (
    <div className="flex h-full bg-white rounded-lg shadow-md overflow-hidden">
      {/* File List Sidebar */}
      <div className="w-80 border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Folder className="w-5 h-5 text-gray-600" />
              <h3 className="font-semibold text-gray-900">Project Files</h3>
            </div>
            <button
              onClick={onRefresh}
              disabled={loading}
              className="p-1 hover:bg-gray-200 rounded transition-colors disabled:opacity-50"
              title="Refresh files"
            >
              <RefreshCw
                className={`w-4 h-4 text-gray-600 ${loading ? 'animate-spin' : ''}`}
              />
            </button>
          </div>
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* File List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="text-sm text-gray-400">Loading files...</div>
            </div>
          ) : filteredFiles.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-gray-400">
              <FileText className="w-8 h-8 mb-2 opacity-50" />
              <p className="text-sm">
                {files.length === 0 ? 'No files yet' : 'No matching files'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredFiles.map((file) => (
                <button
                  key={file}
                  onClick={() => onFileSelect(file)}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                    selectedFile === file ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getFileIcon(file)}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {file}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* File Count */}
        <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-600">
            {filteredFiles.length} {filteredFiles.length === 1 ? 'file' : 'files'}
            {searchQuery && ` (filtered from ${files.length})`}
          </p>
        </div>
      </div>

      {/* File Content Viewer */}
      <div className="flex-1 flex flex-col">
        {selectedFile ? (
          <>
            {/* Content Header */}
            <div className="flex items-center justify-between px-6 py-3 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getFileIcon(selectedFile)}</span>
                <div>
                  <h3 className="font-semibold text-gray-900">{selectedFile}</h3>
                  {fileContent && (
                    <p className="text-xs text-gray-600 mt-1">
                      {fileContent.split(/\s+/).filter(Boolean).length} words •{' '}
                      {fileContent.length} characters
                    </p>
                  )}
                </div>
              </div>
              <button
                onClick={handleDownload}
                disabled={!fileContent}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
            </div>

            {/* Content Display */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {fileContent ? (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{fileContent}</ReactMarkdown>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-sm text-gray-400">Loading content...</div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-sm">Select a file to view its content</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
