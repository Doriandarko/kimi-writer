# Kimi Multi-Agent Novel Writing System

An intelligent multi-agent system powered by **Moonshot AI's kimi-k2-thinking model** for autonomous novel generation with a modern web interface.

## Features

### Multi-Agent Architecture
- 🎯 **Four-Phase Workflow**: Planning → Plan Critique → Writing → Write Critique
- 🧠 **Specialized Agents**: Each phase has a dedicated agent with specific expertise
- ✅ **Quality Control**: Built-in critique and revision loops for plan and chapters
- 👤 **Human-in-the-Loop**: Optional approval checkpoints at configurable points

### Modern Web Interface
- 🖥️ **Real-Time Dashboard**: Monitor progress, phase transitions, and token usage
- 📡 **WebSocket Streaming**: See agent reasoning and content as it's generated
- 📁 **File Browser**: View and download all generated materials
- ⚙️ **Flexible Configuration**: Customize everything from the web UI
- 📊 **Live Statistics**: Track iterations, word count, and generation time

### Smart Features
- 💾 **Context Compression**: Automatically manages token limits
- 🎨 **Writing Samples**: Optionally guide the AI's writing style
- 📝 **Custom Prompts**: Fully editable system prompts for each agent
- 🔄 **Pause/Resume**: Control generation with real-time controls
- 💾 **State Persistence**: Never lose progress, resume anytime

## Installation

### Prerequisites

We recommend using [uv](https://github.com/astral-sh/uv) for fast Python package management:

```bash
# Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

1. Install dependencies:

**Using uv (recommended):**
```bash
uv pip install -r requirements.txt
```

**Or using pip:**
```bash
pip install -r requirements.txt
```

2. Configure your API key:

Create a `.env` file with your API key:
```bash
# Copy the example file
cp env.example .env

# Edit .env and add your API key
# The file should contain:
MOONSHOT_API_KEY=your-api-key-here
```

**Optional:** Set custom base URL (defaults to https://api.moonshot.ai/v1):
```bash
# Add to your .env file:
MOONSHOT_BASE_URL=https://api.moonshot.ai/v1
```

## Quick Start

### Option 1: Web Interface (Recommended)

1. **Start the backend server:**
```bash
cd backend
python main.py
```
The backend will start on `http://localhost:8000`

2. **Start the frontend (in a new terminal):**
```bash
cd frontend
npm install  # First time only
npm run dev
```
The frontend will start on `http://localhost:5173`

3. **Open your browser to `http://localhost:5173`**

4. **Create a new project:**
   - Click "Start New Project"
   - Fill in your novel details (theme, length, genre)
   - Optionally add a writing sample or custom style
   - Configure approval checkpoints
   - Click "Create Project"

5. **Monitor generation:**
   - Watch real-time progress in the dashboard
   - See live streaming output as the agent writes
   - Review and download generated files
   - Approve plans and chapters as needed

### Option 2: Command-Line Interface

For those who prefer the terminal:

```bash
python -m backend.cli --theme "Your novel theme" --length novel
```

See all CLI options:
```bash
python -m backend.cli --help
```

## How It Works

### Multi-Agent Architecture

The system uses four specialized agents working in sequence:

1. **Planning Agent (Story Architect)**
   - Creates comprehensive story summary
   - Develops detailed character profiles (dramatis personae)
   - Designs three-act story structure
   - Creates chapter-by-chapter plot outline

2. **Plan Critic Agent (Story Editor)**
   - Reviews all planning materials
   - Provides structured feedback
   - Requests revisions to improve quality
   - Approves plan when ready (or auto-approves after max iterations)

3. **Writing Agent (Creative Writer)**
   - Writes chapters based on approved plan
   - Optionally follows provided writing style
   - Maintains consistency with characters and plot
   - Reviews previous chapters for continuity

4. **Write Critic Agent (Chapter Editor)**
   - Reviews each completed chapter
   - Checks for quality, consistency, pacing
   - Requests revisions if needed
   - Approves chapter or auto-approves after max iterations

### The Workflow

```
1. PLANNING Phase
   └─> Story Architect creates plan materials

2. PLAN_CRITIQUE Phase
   └─> Story Editor reviews and refines plan
   └─> [Optional approval checkpoint]

3. WRITING Phase
   └─> Creative Writer writes each chapter
   └─> [Optional approval checkpoint per chapter]

4. WRITE_CRITIQUE Phase
   └─> Chapter Editor reviews and refines chapter
   └─> Loop back to WRITING for next chapter

5. COMPLETE
   └─> All chapters written and approved
```

### Smart Features

- **Token Management**: Automatic compression at 90% of 200K token limit
- **State Persistence**: Never lose progress, resume anytime
- **Real-time Updates**: WebSocket streaming of all agent activity
- **Quality Control**: Built-in critique and revision loops
- **Flexible Checkpoints**: Approve plans/chapters or run fully autonomous

## Project Structure

```
kimi-writer-tau/
├── start.py              # Main launcher (starts both servers)
├── start.bat             # Windows launcher
├── backend/              # Backend server
│   ├── main.py          # FastAPI application
│   ├── cli.py           # Command-line interface
│   ├── agent_loop.py    # Multi-agent orchestration
│   ├── config.py        # Configuration management
│   ├── state_manager.py # State persistence
│   ├── system_prompts.py# Agent prompts
│   ├── agents/          # Four specialized agents
│   │   ├── base_agent.py
│   │   ├── planning_agent.py
│   │   ├── plan_critic_agent.py
│   │   ├── writing_agent.py
│   │   └── write_critic_agent.py
│   ├── tools/           # 22 phase-specific tools
│   │   ├── planning_tools.py
│   │   ├── plan_critique_tools.py
│   │   ├── writing_tools.py
│   │   └── write_critique_tools.py
│   ├── api/             # REST API
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── websocket.py
│   └── utils/
│       ├── token_counter.py
│       └── file_helpers.py
├── frontend/            # React web interface
│   ├── src/
│   │   ├── pages/      # Home, ProjectBrowser, NovelWorkspace
│   │   ├── components/ # ProgressDashboard, StreamingOutput, etc.
│   │   ├── services/   # API & WebSocket clients
│   │   ├── hooks/      # React hooks
│   │   └── store/      # Zustand state management
│   └── package.json
├── output/             # Generated novels
│   └── [project_id]/
│       ├── summary.txt
│       ├── dramatis_personae.txt
│       ├── story_structure.txt
│       ├── plot_outline.txt
│       └── chapter_*.txt
├── requirements.txt    # Python dependencies
└── .env               # API keys (create from env.example)
```

## Tips for Best Results

### Project Configuration
1. **Be Specific**: Clear themes get better results
   - Good: "A detective investigating a murder in Victorian London"
   - Less good: "Write something interesting"

2. **Choose Length Wisely**:
   - Flash Fiction (1 chapter) - Quick tests
   - Short Story (3 chapters) - Complete narratives
   - Novel (12 chapters) - Full-length novels

3. **Use Writing Samples**: Provide a sample to guide the AI's style
   - Can use built-in samples or paste your own
   - At least 100 characters for meaningful effect

4. **Set Approval Checkpoints**:
   - Enable plan approval to review before writing starts
   - Enable chapter approval for granular control
   - Disable both for fully autonomous operation

### Monitoring Generation
- Watch the **Progress Dashboard** for phase and chapter tracking
- Check **Live Output** to see content as it's written
- View **Files** to read completed materials
- Monitor **Token Usage** to see context consumption

## Troubleshooting

### "MOONSHOT_API_KEY environment variable not set"
1. Copy `env.example` to `.env`
2. Add your API key: `MOONSHOT_API_KEY=your-key-here`
3. Get your key from https://platform.moonshot.cn/

### "401 Unauthorized" or Authentication errors
- Verify API key in `.env` file
- Check base URL is correct (default: `https://api.moonshot.cn/v1`)
- Ensure `.env` file is in the project root

### Frontend won't start
```powershell
cd frontend
npm install
npm run dev
```

### Backend won't start
```powershell
pip install -r requirements.txt
cd backend
python main.py
```

### WebSocket connection issues
- Ensure backend is running on port 8000
- Check browser console for errors
- Refresh the page to reconnect

### Port already in use
- Backend uses port 8000
- Frontend uses port 5173
- Change ports in `backend/main.py` or `frontend/vite.config.js`

## Working in VS Code (Windows)

### Recommended Setup

1. **Install Extensions**:
   - Python (Microsoft)
   - Pylance
   - ESLint
   - Tailwind CSS IntelliSense

2. **Open Terminal in VS Code** (`Ctrl+` `)

3. **Start the System**:
   ```powershell
   python start.py
   ```

4. **Or start servers separately in split terminal**:
   ```powershell
   # Terminal 1
   cd backend
   python main.py

   # Terminal 2
   cd frontend
   npm run dev
   ```

5. **Use VS Code's built-in browser** or open http://localhost:5173

### VS Code Tasks (Optional)

Create `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Kimi Writer",
      "type": "shell",
      "command": "python start.py",
      "problemMatcher": []
    }
  ]
}
```

Then run with `Ctrl+Shift+B` or Terminal → Run Task

## Technical Details

- **Model**: kimi-k2-thinking
- **Temperature**: 1.0 (optimized for this model)
- **Max Tokens per Call**: 65,536 (64K)
- **Context Window**: 200,000 tokens
- **Max Iterations**: 300
- **Compression Threshold**: 180,000 tokens

You can customize this as you please. 

## License

MIT License with Attribution Requirement - see [LICENSE](LICENSE) file for details.

**Commercial Use**: If you use this software in a commercial product, you must provide clear attribution to Pietro Schirano (@Doriandarko).

**API Usage**: This project uses the Moonshot AI API. Please refer to Moonshot AI's terms of service for API usage guidelines.

## Credits

- **Created by**: Pietro Schirano ([@Doriandarko](https://github.com/Doriandarko))
- **Powered by**: Moonshot AI's kimi-k2-thinking model
- **Repository**: https://github.com/Doriandarko/kimi-writer

## Star History

<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="https://api.star-history.com/svg?repos=Doriandarko/kimi-writer&type=Date&theme=dark"
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="https://api.star-history.com/svg?repos=Doriandarko/kimi-writer&type=Date"
  />
  <img
    alt="Star History Chart"
    src="https://api.star-history.com/svg?repos=Doriandarko/kimi-writer&type=Date"
  />
</picture>

