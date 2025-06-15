# Aura VS Code Extension

**Level 9 Autonomous AI Coding Assistant**

Aura is a comprehensive AI-powered coding assistant that provides real-time code analysis, intelligent suggestions, semantic commit generation, and much more.

## 🚀 Features

### Core Functionality
- **Real-time Code Analysis**: Get instant feedback as you type
- **Intelligent Suggestions**: AI-powered recommendations for code improvements
- **Semantic Commit Generation**: Automatically generate conventional commit messages
- **Interactive Chat**: Ask Aura questions about your code
- **Test Generation**: Automatically create unit tests for your functions
- **Code Optimization**: Get AI-powered refactoring suggestions

### Language Support
- Python
- JavaScript/TypeScript
- Go, Rust, Java, C++, C#, PHP, Ruby

### VS Code Integration
- Sidebar panels for dashboard, analysis, and suggestions
- Status bar integration with connection status
- Real-time diagnostics integration
- Context menus and keyboard shortcuts
- Git integration with smart commit workflows

## 📦 Installation

### Prerequisites
1. **Python 3.8+** with the following packages:
   ```bash
   pip install zmq asyncio
   ```

2. **LLM Provider** (choose one):
   - **LM Studio**: Download and run from [lmstudio.ai](https://lmstudio.ai)
   - **Ollama**: Install from [ollama.ai](https://ollama.ai)

### Extension Installation
1. Download the `.vsix` file
2. Open VS Code
3. Run `Extensions: Install from VSIX...` command
4. Select the downloaded `.vsix` file

### Backend Setup
1. Navigate to the Aura backend directory
2. Start the backend service:
   ```bash
   cd backend
   python3 vscode_backend_service.py
   ```

The backend will start listening on `tcp://localhost:5559`.

## ⚙️ Configuration

Open VS Code Settings and search for "Aura" to configure:

- **Server URL**: Backend connection URL (default: `tcp://localhost:5559`)
- **LLM Provider**: Choose between `lm_studio`, `ollama`, etc.
- **Analysis Depth**: `basic`, `detailed`, or `comprehensive`
- **Auto Analysis**: Enable/disable automatic analysis on file save
- **Backend Path**: Path to backend directory (for auto-start features)

## 🎮 Usage

### Quick Start
1. Open a Python/JavaScript project
2. Press `Ctrl+Alt+A` (or `Cmd+Alt+A` on Mac) to analyze current file
3. View results in the Aura sidebar panels
4. Use `Ctrl+Alt+Q` to ask questions about your code
5. Use `Ctrl+Alt+C` to generate semantic commit messages

### Commands
- **Aura: Analyze Current File** - Analyze the active file
- **Aura: Analyze Entire Project** - Analyze all supported files
- **Aura: Ask Aura** - Open quick question input
- **Aura: Generate Semantic Commit** - Create commit message
- **Aura: Show Dashboard** - Open Aura dashboard
- **Aura: Toggle Auto-Analysis** - Enable/disable auto-analysis

### Sidebar Panels
- **Dashboard**: System status and quick actions
- **Code Analysis**: Detailed analysis of current file
- **Suggestions**: AI-powered improvement recommendations
- **Chat**: Interactive conversation with Aura

## 🔧 Troubleshooting

### Connection Issues

If Aura shows "Connection Error":

1. **Check Backend Service**:
   ```bash
   cd backend
   python3 vscode_backend_service.py
   ```

2. **Verify Dependencies**:
   ```bash
   python3 -c "import zmq; print('ZMQ OK')"
   ```

3. **Check Port Availability**:
   ```bash
   netstat -an | grep 5559
   ```

4. **Use Built-in Troubleshooter**:
   - Command Palette → "Aura: Show Troubleshooting"
   - Or click "Troubleshoot" when connection fails

### Common Issues

**Extension won't activate:**
- Check VS Code developer console for errors
- Ensure all configuration values are valid
- Try reloading VS Code window

**Backend connection fails:**
- Ensure Python backend is running
- Check firewall/antivirus settings
- Verify ZeroMQ installation
- Try different port in settings

**Analysis not working:**
- Check file type is supported
- Ensure LLM provider is running
- Check backend logs for errors
- Try manual analysis command

**LLM provider issues:**
- Ensure LM Studio/Ollama is running
- Check provider URLs in settings
- Verify models are loaded
- Check provider health status

### Debug Mode

Enable debug logging:
1. Open VS Code Settings
2. Search for "Aura"
3. Enable debug logging
4. Check "Aura Extension" output channel

### Support

1. **Check Logs**: View "Aura Extension" output channel
2. **Test Connection**: Use built-in connection test
3. **Reset Settings**: Clear Aura configuration and reconfigure
4. **Manual Backend**: Run backend service manually to check for errors

## 🔗 Architecture

```
VS Code Extension (ZeroMQ Client)
        ↓
Backend Service (ZeroMQ Server :5559)
        ↓
┌─────────────────────────────────────┐
│  LLM Provider (LM Studio/Ollama)    │
│  Code Analysis Engine              │
│  Git Integration                   │
│  Test Generator                    │
│  Refactoring Engine               │
└─────────────────────────────────────┘
```

## 📝 Development

### Building from Source
```bash
cd vscode-extension
npm install
npm run compile
```

### Packaging
```bash
npm install -g vsce
vsce package
```

### Testing
```bash
npm test
```

---

**Aura - Level 9 Autonomous AI Coding Assistant**  
*Making code perfect, one suggestion at a time.*