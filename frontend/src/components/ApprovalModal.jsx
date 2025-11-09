/**
 * Approval Modal Component
 *
 * Modal dialog for approving or rejecting checkpoints (plan, chapters).
 */

import { useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, FileText } from 'lucide-react';

export function ApprovalModal({
  isOpen,
  approvalType,
  approvalData,
  onApprove,
  onReject,
  onClose,
  loading,
}) {
  const [notes, setNotes] = useState('');

  if (!isOpen) return null;

  const getApprovalInfo = () => {
    switch (approvalType) {
      case 'plan':
        return {
          title: 'Plan Approval Required',
          icon: FileText,
          description:
            'The planning phase is complete. Please review the plan materials before proceeding to the writing phase.',
          files: [
            'summary.txt - Story summary',
            'dramatis_personae.txt - Character descriptions',
            'story_structure.txt - Three-act structure',
            'plot_outline.txt - Chapter-by-chapter outline',
          ],
        };
      case 'chapter':
        return {
          title: `Chapter ${approvalData?.chapter_number || '?'} Approval`,
          icon: FileText,
          description:
            'This chapter has been written and reviewed. Please approve it to continue to the next chapter.',
          files: [`chapter_${approvalData?.chapter_number || '?'}.txt - Chapter content`],
        };
      default:
        return {
          title: 'Approval Required',
          icon: AlertCircle,
          description: 'Please review and approve to continue.',
          files: [],
        };
    }
  };

  const info = getApprovalInfo();
  const Icon = info.icon;

  const handleApprove = () => {
    onApprove({ approved: true, notes: notes.trim() || undefined });
    setNotes('');
  };

  const handleReject = () => {
    onReject({ approved: false, notes: notes.trim() || undefined });
    setNotes('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Icon className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">{info.title}</h2>
              <p className="text-sm text-gray-600 mt-1">{info.description}</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {/* Files to Review */}
          {info.files.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-2">
                Files to Review:
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <ul className="space-y-2">
                  {info.files.map((file, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span>{file}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Additional Context */}
          {approvalData && (
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-2">
                Additional Information:
              </h3>
              <div className="bg-blue-50 rounded-lg p-4">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(approvalData, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Notes Input */}
          <div>
            <label
              htmlFor="approval-notes"
              className="block text-sm font-semibold text-gray-900 mb-2"
            >
              Notes (Optional):
            </label>
            <textarea
              id="approval-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any notes or feedback..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm resize-none"
            />
          </div>

          {/* Instructions */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <p className="font-medium mb-1">Important:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Review all materials carefully before approving</li>
                  <li>Approving will continue to the next phase</li>
                  <li>Rejecting will pause generation for manual intervention</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-end gap-3">
            <button
              onClick={handleReject}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-md hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <XCircle className="w-4 h-4" />
              Reject
            </button>
            <button
              onClick={handleApprove}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CheckCircle className="w-4 h-4" />
              {loading ? 'Processing...' : 'Approve & Continue'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
