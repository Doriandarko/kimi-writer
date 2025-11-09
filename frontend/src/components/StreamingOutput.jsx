/**
 * Streaming Output Component
 *
 * Displays real-time streaming content and reasoning from the agent.
 */

import { useState, useEffect, useRef } from 'react';
import { Eye, EyeOff, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export function StreamingOutput({ content, reasoning, isStreaming }) {
  const [showReasoning, setShowReasoning] = useState(true);
  const [copied, setCopied] = useState(false);
  const contentRef = useRef(null);
  const reasoningRef = useRef(null);

  // Auto-scroll to bottom when new content arrives
  useEffect(() => {
    if (isStreaming) {
      if (contentRef.current) {
        contentRef.current.scrollTop = contentRef.current.scrollHeight;
      }
      if (reasoningRef.current && showReasoning) {
        reasoningRef.current.scrollTop = reasoningRef.current.scrollHeight;
      }
    }
  }, [content, reasoning, isStreaming, showReasoning]);

  const handleCopy = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold text-gray-900">Live Output</h3>
          {isStreaming && (
            <div className="flex items-center gap-2 text-green-600">
              <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
              <span className="text-sm">Streaming...</span>
            </div>
          )}
        </div>
        <button
          onClick={() => setShowReasoning(!showReasoning)}
          className="flex items-center gap-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-200 rounded-md transition-colors"
        >
          {showReasoning ? (
            <>
              <EyeOff className="w-4 h-4" />
              Hide Reasoning
            </>
          ) : (
            <>
              <Eye className="w-4 h-4" />
              Show Reasoning
            </>
          )}
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {/* Reasoning Section */}
        {showReasoning && reasoning && (
          <div className="border-b border-gray-200">
            <div className="flex items-center justify-between px-4 py-2 bg-blue-50 border-b border-blue-100">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full" />
                <span className="text-sm font-medium text-blue-900">Agent Reasoning</span>
              </div>
              <button
                onClick={() => handleCopy(reasoning, 'reasoning')}
                className="p-1 hover:bg-blue-100 rounded transition-colors"
                title="Copy reasoning"
              >
                {copied === 'reasoning' ? (
                  <Check className="w-4 h-4 text-green-600" />
                ) : (
                  <Copy className="w-4 h-4 text-blue-600" />
                )}
              </button>
            </div>
            <div
              ref={reasoningRef}
              className="max-h-48 overflow-y-auto px-4 py-3 bg-blue-50"
            >
              <pre className="text-sm text-blue-900 whitespace-pre-wrap font-mono">
                {reasoning}
              </pre>
            </div>
          </div>
        )}

        {/* Main Content Section */}
        <div className="flex-1 flex flex-col">
          <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-gray-900 rounded-full" />
              <span className="text-sm font-medium text-gray-900">Content</span>
            </div>
            <button
              onClick={() => handleCopy(content, 'content')}
              className="p-1 hover:bg-gray-200 rounded transition-colors"
              title="Copy content"
            >
              {copied === 'content' ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4 text-gray-600" />
              )}
            </button>
          </div>
          <div
            ref={contentRef}
            className="flex-1 overflow-y-auto px-4 py-3"
          >
            {content ? (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                <p className="text-sm">Waiting for content...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer with word count */}
      {content && (
        <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <span>{content.split(/\s+/).filter(Boolean).length} words</span>
            <span>{content.length} characters</span>
          </div>
        </div>
      )}
    </div>
  );
}
