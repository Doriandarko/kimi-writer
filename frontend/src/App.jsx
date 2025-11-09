/**
 * Main App Component
 *
 * Sets up routing and global application structure.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { ProjectBrowser } from './pages/ProjectBrowser';
import { NovelWorkspace } from './pages/NovelWorkspace';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/projects" element={<ProjectBrowser />} />
        <Route path="/workspace/:projectId" element={<NovelWorkspace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
