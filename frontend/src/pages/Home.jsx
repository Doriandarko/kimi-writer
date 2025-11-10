/**
 * Home Page
 *
 * Redesigned landing page with integrated project creation.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { ProjectsSidebar } from '../components/ProjectsSidebar';
import { StyleCard } from '../components/StyleCard';
import { QualityControlSettings } from '../components/QualityControlSettings';
import { useNovelStore } from '../store/novelStore';
import * as api from '../services/api';

const NOVEL_LENGTHS = [
  { value: 'short_story', label: 'Short Story', chapters: 3 },
  { value: 'novella', label: 'Novella', chapters: 8 },
  { value: 'novel', label: 'Novel', chapters: 15 },
  { value: 'long_novel', label: 'Long Novel', chapters: 30 },
  { value: 'ai_decide', label: "Kimi's Choice", chapters: '?' },
];

export function Home() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const { setError } = useNovelStore();

  // Form state
  const [premise, setPremise] = useState('');
  const [showTitle, setShowTitle] = useState(false);
  const [title, setTitle] = useState('');
  const [showGenre, setShowGenre] = useState(false);
  const [genre, setGenre] = useState('');
  const [showLength, setShowLength] = useState(false);
  const [length, setLength] = useState('ai_decide');
  const [styleCards, setStyleCards] = useState([
    { name: '', sample: '' },
    { name: '', sample: '' },
    { name: '', sample: '' },
  ]);
  const [requirePlanApproval, setRequirePlanApproval] = useState(true);
  const [requireChapterApproval, setRequireChapterApproval] = useState(false);
  const [qualityConfig, setQualityConfig] = useState({
    max_plan_critique_iterations: 2,
    max_write_critique_iterations: 2,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Any initial data loading can go here
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleCreateProject = async () => {
    if (!premise.trim()) {
      setError('Please enter a premise for your novel');
      return;
    }

    setLoading(true);

    try {
      // Find the first non-empty style card
      const selectedStyle = styleCards.find(card => card.sample?.trim());

      const config = {
        project_name: title.trim() || undefined,
        theme: premise.trim(),
        novel_length: length === 'ai_decide' ? undefined : length,
        genre: genre.trim() || undefined,
        custom_writing_sample: selectedStyle?.sample || undefined,
        require_plan_approval: requirePlanApproval,
        require_chapter_approval: requireChapterApproval,
        ...qualityConfig,
      };

      const result = await api.createProject(config);
      navigate(`/workspace/${result.project_id}`);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStyleCardChange = (index, value) => {
    const newStyleCards = [...styleCards];
    newStyleCards[index] = value;
    setStyleCards(newStyleCards);
  };

  return (
    <div className="flex h-screen bg-pearl-50 overflow-hidden">
      {/* Projects Sidebar */}
      <ProjectsSidebar currentProjectId={null} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-pearl-50 border-b border-obsidian-200 px-12 py-8">
          <h1 className="text-5xl font-serif font-bold text-obsidian-900 tracking-tight">
            Kimi Writer Tau
          </h1>
          <p className="text-sm font-body text-obsidian-600 mt-2 tracking-wide">
            Multi-Agent Novel Writing System
          </p>
        </header>

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto px-12 py-8">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Premise Section */}
            <div className="relative">
              <div className="flex items-start justify-between mb-3">
                <label className="block text-sm font-body font-semibold text-obsidian-700 tracking-wide uppercase">
                  Premise
                </label>
                <QualityControlSettings
                  config={qualityConfig}
                  onChange={setQualityConfig}
                />
              </div>
              <textarea
                value={premise}
                onChange={(e) => setPremise(e.target.value)}
                placeholder="Describe your story idea... What is your novel about?"
                rows={8}
                className="w-full px-5 py-4 bg-pearl-50 border-2 border-obsidian-300 rounded-lg text-base font-body text-obsidian-900 placeholder-obsidian-400 focus:outline-none focus:ring-2 focus:ring-obsidian-600 focus:border-obsidian-600 transition-all resize-none shadow-pearl"
              />
            </div>

            {/* Toggleable Options */}
            <div className="flex gap-4">
              {/* Title Toggle */}
              <button
                onClick={() => setShowTitle(!showTitle)}
                className={`flex-1 px-5 py-3 rounded-lg border-2 transition-all font-serif font-medium ${
                  showTitle
                    ? 'bg-obsidian-900 text-pearl-50 border-obsidian-900'
                    : 'bg-pearl-100 text-obsidian-700 border-obsidian-300 hover:border-obsidian-500'
                }`}
              >
                Add Title
              </button>

              {/* Genre Toggle */}
              <button
                onClick={() => setShowGenre(!showGenre)}
                className={`flex-1 px-5 py-3 rounded-lg border-2 transition-all font-serif font-medium ${
                  showGenre
                    ? 'bg-obsidian-900 text-pearl-50 border-obsidian-900'
                    : 'bg-pearl-100 text-obsidian-700 border-obsidian-300 hover:border-obsidian-500'
                }`}
              >
                Add Genre
              </button>

              {/* Length Toggle */}
              <button
                onClick={() => setShowLength(!showLength)}
                className={`flex-1 px-5 py-3 rounded-lg border-2 transition-all font-serif font-medium ${
                  showLength
                    ? 'bg-obsidian-900 text-pearl-50 border-obsidian-900'
                    : 'bg-pearl-100 text-obsidian-700 border-obsidian-300 hover:border-obsidian-500'
                }`}
              >
                Customize Length
              </button>
            </div>

            {/* Collapsible Fields */}
            {showTitle && (
              <div className="animate-in slide-in-from-top">
                <label className="block text-sm font-body font-semibold text-obsidian-700 mb-2 tracking-wide uppercase">
                  Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Leave empty for Kimi's Choice"
                  className="w-full px-4 py-3 bg-pearl-50 border border-obsidian-300 rounded-lg text-base font-body text-obsidian-900 placeholder-obsidian-400 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600 transition-all"
                />
                {!title && (
                  <p className="mt-2 text-xs text-obsidian-500 font-body italic">
                    Kimi's Choice
                  </p>
                )}
              </div>
            )}

            {showGenre && (
              <div className="animate-in slide-in-from-top">
                <label className="block text-sm font-body font-semibold text-obsidian-700 mb-2 tracking-wide uppercase">
                  Genre
                </label>
                <input
                  type="text"
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  placeholder="Leave empty for Kimi's Choice"
                  className="w-full px-4 py-3 bg-pearl-50 border border-obsidian-300 rounded-lg text-base font-body text-obsidian-900 placeholder-obsidian-400 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600 transition-all"
                />
                {!genre && (
                  <p className="mt-2 text-xs text-obsidian-500 font-body italic">
                    Kimi's Choice
                  </p>
                )}
              </div>
            )}

            {showLength && (
              <div className="animate-in slide-in-from-top">
                <label className="block text-sm font-body font-semibold text-obsidian-700 mb-2 tracking-wide uppercase">
                  Novel Length
                </label>
                <select
                  value={length}
                  onChange={(e) => setLength(e.target.value)}
                  className="w-full px-4 py-3 bg-pearl-50 border border-obsidian-300 rounded-lg text-base font-body text-obsidian-900 focus:outline-none focus:ring-1 focus:ring-obsidian-600 focus:border-obsidian-600 transition-all"
                >
                  {NOVEL_LENGTHS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label} ({option.chapters} chapters)
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Writing Style Cards */}
            <div>
              <label className="block text-sm font-body font-semibold text-obsidian-700 mb-4 tracking-wide uppercase">
                Writing Style
              </label>
              <div className="grid grid-cols-3 gap-4">
                {styleCards.map((card, index) => (
                  <StyleCard
                    key={index}
                    index={index}
                    value={card}
                    onChange={(value) => handleStyleCardChange(index, value)}
                  />
                ))}
              </div>
            </div>

            {/* Approval Checkpoints */}
            <div>
              <label className="block text-sm font-body font-semibold text-obsidian-700 mb-4 tracking-wide uppercase">
                Approval Checkpoints
              </label>
              <div className="space-y-3">
                <label className="flex items-center gap-4 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={requirePlanApproval}
                      onChange={(e) => setRequirePlanApproval(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-6 h-6 border-2 border-obsidian-400 rounded-md peer-checked:bg-obsidian-900 peer-checked:border-obsidian-900 transition-all flex items-center justify-center">
                      {requirePlanApproval && (
                        <svg className="w-4 h-4 text-pearl-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-body font-medium text-obsidian-900">
                      Require Plan Approval
                    </div>
                    <p className="text-xs text-obsidian-600 font-body">
                      Pause after planning phase for manual review
                    </p>
                  </div>
                </label>

                <label className="flex items-center gap-4 cursor-pointer group">
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={requireChapterApproval}
                      onChange={(e) => setRequireChapterApproval(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-6 h-6 border-2 border-obsidian-400 rounded-md peer-checked:bg-obsidian-900 peer-checked:border-obsidian-900 transition-all flex items-center justify-center">
                      {requireChapterApproval && (
                        <svg className="w-4 h-4 text-pearl-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-body font-medium text-obsidian-900">
                      Require Chapter Approval
                    </div>
                    <p className="text-xs text-obsidian-600 font-body">
                      Pause after each chapter for manual review
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Begin Writing Button */}
            <div className="pt-4 pb-8">
              <button
                onClick={handleCreateProject}
                disabled={loading || !premise.trim()}
                className="group relative w-full px-8 py-6 bg-pearlescent hover:bg-pearlescent-hover bg-[length:200%_200%] rounded-lg border-2 border-obsidian-300 hover:border-obsidian-400 transition-all duration-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-pearl-lg hover:shadow-obsidian overflow-hidden"
                style={{
                  animation: 'shimmer-slow 5s ease-in-out infinite paused',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.animation = 'shimmer-slow 5s ease-in-out infinite running';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.animation = 'shimmer-slow 5s ease-in-out infinite paused';
                }}
              >
                <span className="relative z-10 block text-center">
                  <span className="block text-2xl font-serif font-bold text-obsidian-900 mb-1">
                    {loading ? 'Creating...' : 'Begin Writing'}
                  </span>
                  <span className="block text-xs font-body text-obsidian-600 tracking-widest uppercase">
                    Start your novel journey
                  </span>
                </span>
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
