# Quick Start Guide - Kimi Multi-Agent Novel Writing System

## For First-Time Users

### 1. Set Up Your Environment

**Create `.env` file:**
```powershell
# Copy the example
cp env.example .env

# Edit .env and add your Moonshot API key
MOONSHOT_API_KEY=your-api-key-here
```

Get your API key from: https://platform.moonshot.cn/

### 2. Install Dependencies

**Python dependencies:**
```powershell
pip install -r requirements.txt
```

**Frontend dependencies:**
```powershell
cd frontend
npm install
cd ..
```

### 3. Start the System

**Option A: Single Command (Easiest)**
```powershell
python start.py
```

**Option B: Double-click launcher**
- Double-click `start.bat` in File Explorer

**Option C: Separate terminals**
```powershell
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 4. Open the Web Interface

Open your browser to: **http://localhost:5173**

### 5. Create Your First Novel

1. Click **"Start New Project"**
2. Fill in the form:
   - **Project Name**: "My First Novel"
   - **Theme**: "A detective solving a mysterious case in a small town"
   - **Length**: Choose "Short Story" (3 chapters) for testing
   - **Genre**: "Mystery" (optional)
3. Leave other settings as default
4. Click **"Create Project"**
5. Click **"Start Generation"** on the workspace page
6. Watch the magic happen! 🎉

## What You'll See

### Progress Dashboard (Left Side)
- Current phase (Planning → Plan Review → Writing → Chapter Review)
- Overall progress percentage
- Chapter progress
- Token usage
- Statistics

### Live Output (Main Area)
- Agent reasoning (thinking process)
- Generated content in real-time
- Tool executions

### Files Tab
- Browse all generated materials
- View and download files
- See plan, characters, outline, chapters

## Common First-Time Issues

### "ModuleNotFoundError: No module named 'dotenv'"
```powershell
pip install -r requirements.txt
```

### "MOONSHOT_API_KEY not found"
Make sure you created `.env` file with your API key.

### Frontend shows "Cannot connect to backend"
Make sure backend is running on port 8000:
```powershell
cd backend
python main.py
```

### Port already in use
Kill the process using the port or change ports in config files.

## Next Steps

- **Experiment with different lengths**: Try Flash Fiction (1 chapter) for quick tests
- **Test approval checkpoints**: Enable "Require Plan Approval" to review before writing
- **Try writing samples**: Paste a sample of your favorite author's style
- **Browse your projects**: Use the "Browse Projects" button to see all your work
- **Check the files**: Generated materials are in `output/[project-id]/`

## Need Help?

- See full `README.md` for detailed documentation
- See `UPGRADE.md` if upgrading from old version
- Check `CLAUDE.md` for developer guide
- Check `IMPLEMENTATION_PLAN.md` for architecture details

## Tips for Testing

1. **Start small**: Use Flash Fiction or Short Story for first tests
2. **Watch the output**: The live output shows you exactly what the AI is doing
3. **Check token usage**: You have 200,000 tokens, compression happens at 180,000
4. **Don't panic if it pauses**: It might be waiting for your approval if you enabled checkpoints
5. **Files update in real-time**: Refresh the Files tab to see new content

Enjoy writing with AI! 🚀
