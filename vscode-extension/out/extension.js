"use strict";
/**
 * Aura VS Code Extension - Main Entry Point
 * =========================================
 *
 * The vessel through which Aura manifests in the sacred space of the IDE.
 * Real-time intelligence, seamless integration, autonomous assistance.
 *
 * @author Aura - Level 9 Autonomous AI Coding Assistant
 * @date 2025-06-13
 * @phase 2.2 - VS Code Integration
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = exports.AuraExtension = void 0;
const vscode = __importStar(require("vscode"));
const connection_1 = require("./connection");
const dashboardProvider_1 = require("./providers/dashboardProvider");
const codeAnalysisProvider_1 = require("./providers/codeAnalysisProvider");
const suggestionsProvider_1 = require("./providers/suggestionsProvider");
const chatProvider_1 = require("./providers/chatProvider");
const realTimeAnalysisProvider_1 = require("./providers/realTimeAnalysisProvider");
const gitIntegrationProvider_1 = require("./providers/gitIntegrationProvider");
const statusBar_1 = require("./ui/statusBar");
const notifications_1 = require("./ui/notifications");
const logger_1 = require("./utils/logger");
const configValidator_1 = require("./utils/configValidator");
class AuraExtension {
    constructor(context) {
        this.context = context;
        this.disposables = [];
        this.logger = logger_1.AuraLogger.getInstance();
        this.configValidator = new configValidator_1.ConfigValidator();
        // Set debug log level in development
        if (process.env.NODE_ENV === 'development') {
            this.logger.setLogLevel(logger_1.LogLevel.DEBUG);
        }
        this.config = this.loadConfiguration();
        this.initializeComponents();
        this.registerCommands();
        this.setupEventListeners();
    }
    loadConfiguration() {
        const config = vscode.workspace.getConfiguration('aura');
        return {
            autoAnalysis: config.get('autoAnalysis', true),
            serverUrl: config.get('serverUrl', 'tcp://localhost:5559'),
            llmProvider: config.get('llmProvider', 'lm_studio'),
            analysisDepth: config.get('analysisDepth', 'detailed'),
            showNotifications: config.get('showNotifications', true),
            themeColor: config.get('themeColor', 'purple')
        };
    }
    initializeComponents() {
        // Initialize core connection to Aura system
        this.connection = new connection_1.AuraConnection(this.config.serverUrl);
        // Initialize UI components
        this.statusBar = new statusBar_1.AuraStatusBar();
        this.notificationManager = new notifications_1.AuraNotificationManager(this.config.showNotifications);
        // Initialize view providers
        this.dashboardProvider = new dashboardProvider_1.AuraDashboardProvider(this.connection);
        this.codeAnalysisProvider = new codeAnalysisProvider_1.AuraCodeAnalysisProvider(this.connection);
        this.suggestionsProvider = new suggestionsProvider_1.AuraSuggestionsProvider(this.connection);
        this.chatProvider = new chatProvider_1.AuraChatProvider(this.context.extensionUri, this.connection);
        // Initialize real-time analysis and Git integration
        this.realTimeAnalysisProvider = new realTimeAnalysisProvider_1.RealTimeAnalysisProvider(this.connection);
        this.gitIntegrationProvider = new gitIntegrationProvider_1.GitIntegrationProvider(this.connection);
        // Register view providers
        vscode.window.registerTreeDataProvider('aura.dashboard', this.dashboardProvider);
        vscode.window.registerTreeDataProvider('aura.codeAnalysis', this.codeAnalysisProvider);
        vscode.window.registerTreeDataProvider('aura.suggestions', this.suggestionsProvider);
        vscode.window.registerWebviewViewProvider('aura.chat', this.chatProvider);
    }
    registerCommands() {
        // File analysis commands
        this.disposables.push(vscode.commands.registerCommand('aura.analyzeFile', () => {
            this.analyzeCurrentFile();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.analyzeProject', () => {
            this.analyzeProject();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.analyzeWorkspace', () => {
            this.realTimeAnalysisProvider.analyzeWorkspace();
        }));
        // Git integration commands
        this.disposables.push(vscode.commands.registerCommand('aura.generateCommit', () => {
            this.generateSemanticCommit();
        }));
        // Connection management commands
        this.disposables.push(vscode.commands.registerCommand('aura.reconnect', async () => {
            await this.reconnectToBackend();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.showTroubleshooting', () => {
            this.showTroubleshootingPanel();
        }));
        // Enhanced Git commands
        this.disposables.push(vscode.commands.registerCommand('aura.git.generateCommit', () => {
            this.gitIntegrationProvider.generateCommitMessage();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.git.smartCommit', () => {
            this.gitIntegrationProvider.performSmartCommit();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.git.suggestBranch', () => {
            this.gitIntegrationProvider.suggestBranchName();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.git.analyzeChanges', () => {
            this.gitIntegrationProvider.analyzeCurrentChanges();
        }));
        // Real-time analysis commands
        this.disposables.push(vscode.commands.registerCommand('aura.clearDiagnostics', () => {
            this.realTimeAnalysisProvider.clearDiagnostics();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.showAnalysisOutput', () => {
            vscode.commands.executeCommand('workbench.action.output.toggleOutput', 'Aura Analysis');
        }));
        // Chat and query commands
        this.disposables.push(vscode.commands.registerCommand('aura.askQuestion', () => {
            this.showQuickQuestionInput();
        }));
        // Dashboard commands
        this.disposables.push(vscode.commands.registerCommand('aura.showDashboard', () => {
            this.showDashboard();
        }));
        // Settings commands
        this.disposables.push(vscode.commands.registerCommand('aura.toggleAutoAnalysis', () => {
            this.toggleAutoAnalysis();
        }));
        // Refresh commands for views
        this.disposables.push(vscode.commands.registerCommand('aura.refreshDashboard', () => {
            this.dashboardProvider.refresh();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.refreshAnalysis', () => {
            this.codeAnalysisProvider.refresh();
        }));
        // Dashboard utility commands
        this.disposables.push(vscode.commands.registerCommand('aura.checkLLMStatus', async () => {
            this.checkLLMStatus();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.showIssues', () => {
            this.showIssues();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.generateTests', () => {
            this.generateTests();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.optimizeCode', () => {
            this.optimizeCode();
        }));
        this.disposables.push(vscode.commands.registerCommand('aura.showSettings', () => {
            vscode.commands.executeCommand('workbench.action.openSettings', 'aura');
        }));
        // Internal events
        this.disposables.push(vscode.commands.registerCommand('aura.analysisUpdated', (filePath, analysis) => {
            this.codeAnalysisProvider.updateAnalysis(filePath, analysis);
        }));
    }
    setupEventListeners() {
        // File save listener for auto-analysis
        this.disposables.push(vscode.workspace.onDidSaveTextDocument((document) => {
            if (this.config.autoAnalysis && this.isSupportedFile(document)) {
                this.analyzeDocument(document);
            }
        }));
        // Active editor change listener
        this.disposables.push(vscode.window.onDidChangeActiveTextEditor((editor) => {
            if (editor && this.isSupportedFile(editor.document)) {
                this.codeAnalysisProvider.setActiveFile(editor.document.uri.fsPath);
            }
        }));
        // Configuration change listener
        this.disposables.push(vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('aura')) {
                this.config = this.loadConfiguration();
                this.updateComponents();
            }
        }));
        // Connection status listener
        this.connection.onStatusChange((status) => {
            this.statusBar.updateConnectionStatus(status);
            if (status === 'connected') {
                this.notificationManager.showInfo('Aura is now connected and ready');
            }
            else if (status === 'disconnected') {
                this.notificationManager.showWarning('Aura connection lost');
            }
        });
    }
    isSupportedFile(document) {
        const supportedExtensions = ['.py', '.js', '.ts', '.jsx', '.tsx'];
        return supportedExtensions.some(ext => document.fileName.endsWith(ext));
    }
    async analyzeCurrentFile() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active file to analyze');
            return;
        }
        if (!this.isSupportedFile(editor.document)) {
            vscode.window.showErrorMessage('File type not supported for analysis');
            return;
        }
        await this.analyzeDocument(editor.document);
    }
    async analyzeDocument(document) {
        try {
            this.statusBar.showActivity('Analyzing...');
            const analysis = await this.connection.analyzeFile(document.uri.fsPath, this.config.analysisDepth);
            if (analysis) {
                this.codeAnalysisProvider.updateAnalysis(document.uri.fsPath, analysis);
                this.suggestionsProvider.updateSuggestions(analysis.suggestions || []);
                // Show inline diagnostics
                this.showInlineDiagnostics(document, analysis);
                this.notificationManager.showInfo(`Analysis complete: ${analysis.elements?.length || 0} elements analyzed`);
            }
            this.statusBar.hideActivity();
        }
        catch (error) {
            this.statusBar.hideActivity();
            this.notificationManager.showError(`Analysis failed: ${error}`);
        }
    }
    async analyzeProject() {
        try {
            if (!vscode.workspace.workspaceFolders) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }
            this.statusBar.showActivity('Analyzing project...');
            const projectPath = vscode.workspace.workspaceFolders[0].uri.fsPath;
            const analysis = await this.connection.analyzeProject(projectPath);
            if (analysis) {
                this.dashboardProvider.updateProjectAnalysis(analysis);
                this.notificationManager.showInfo(`Project analysis complete: ${analysis.filesAnalyzed} files processed`);
            }
            this.statusBar.hideActivity();
        }
        catch (error) {
            this.statusBar.hideActivity();
            this.notificationManager.showError(`Project analysis failed: ${error}`);
        }
    }
    async generateSemanticCommit() {
        try {
            this.statusBar.showActivity('Generating commit...');
            const commit = await this.connection.generateCommit();
            if (commit) {
                // Show commit message in input box for user approval
                const approved = await vscode.window.showInputBox({
                    prompt: 'Review and approve commit message (or modify)',
                    value: commit.message,
                    placeHolder: 'Semantic commit message',
                    validateInput: (value) => {
                        return value.trim() ? null : 'Commit message cannot be empty';
                    }
                });
                if (approved) {
                    // Execute git commit
                    const terminal = vscode.window.createTerminal('Aura Git');
                    terminal.sendText(`git commit -m "${approved}"`);
                    terminal.show();
                    this.notificationManager.showInfo('Semantic commit message generated and executed');
                }
            }
            this.statusBar.hideActivity();
        }
        catch (error) {
            this.statusBar.hideActivity();
            this.notificationManager.showError(`Commit generation failed: ${error}`);
        }
    }
    async showQuickQuestionInput() {
        const question = await vscode.window.showInputBox({
            prompt: 'Ask Aura a question about your code',
            placeHolder: 'How can I optimize this function?',
        });
        if (question) {
            this.chatProvider.askQuestion(question);
            vscode.commands.executeCommand('aura.chat.focus');
        }
    }
    showDashboard() {
        vscode.commands.executeCommand('aura.dashboard.focus');
    }
    toggleAutoAnalysis() {
        const newValue = !this.config.autoAnalysis;
        vscode.workspace.getConfiguration('aura').update('autoAnalysis', newValue, true);
        this.notificationManager.showInfo(`Auto-analysis ${newValue ? 'enabled' : 'disabled'}`);
    }
    showInlineDiagnostics(document, analysis) {
        // Convert Aura analysis to VS Code diagnostics
        const diagnostics = [];
        if (analysis.issues) {
            for (const issue of analysis.issues) {
                const range = new vscode.Range(issue.line - 1, 0, issue.line - 1, Number.MAX_VALUE);
                const diagnostic = new vscode.Diagnostic(range, issue.message, this.mapSeverity(issue.severity));
                diagnostic.source = 'Aura';
                diagnostic.code = issue.type;
                diagnostics.push(diagnostic);
            }
        }
        // Create diagnostic collection if it doesn't exist
        const collection = vscode.languages.createDiagnosticCollection('aura');
        collection.set(document.uri, diagnostics);
    }
    mapSeverity(severity) {
        switch (severity.toLowerCase()) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Hint;
        }
    }
    updateComponents() {
        this.notificationManager.setEnabled(this.config.showNotifications);
        this.connection.updateServerUrl(this.config.serverUrl);
        // Update other components as needed
    }
    async activate() {
        try {
            this.logger.info('Activating Aura extension...');
            // Validate configuration
            const validationResult = this.configValidator.validateConfiguration();
            await this.configValidator.showValidationResults(validationResult);
            if (!validationResult.isValid) {
                this.logger.error('Extension activation failed due to invalid configuration');
                return;
            }
            // Set context for views
            vscode.commands.executeCommand('setContext', 'aura.enabled', true);
            // Update status bar immediately
            this.statusBar.show();
            // Try to connect to Aura system
            try {
                await this.connection.connect();
                this.notificationManager.showInfo('Aura - Level 9 Autonomous AI Coding Assistant activated');
                this.logger.info('Aura extension activated successfully');
            }
            catch (connectionError) {
                this.logger.warn('Backend connection failed, running in limited mode', connectionError);
                // Show connection error with helpful actions
                const action = await this.notificationManager.showWarning('Could not connect to Aura backend. Extension will run in limited mode.', 'Start Backend', 'Troubleshoot', 'Settings');
                if (action === 'Start Backend') {
                    this.startBackendService();
                }
                else if (action === 'Troubleshoot') {
                    this.showTroubleshootingPanel();
                }
                else if (action === 'Settings') {
                    vscode.commands.executeCommand('workbench.action.openSettings', 'aura');
                }
            }
        }
        catch (error) {
            this.logger.error('Failed to activate Aura extension', error);
            this.notificationManager.showError(`Extension activation failed: ${error}`);
        }
    }
    async checkLLMStatus() {
        try {
            this.statusBar.showActivity('Checking LLM status...');
            // Try to get LLM status from backend
            const status = await this.connection.checkLLMStatus();
            if (status && status.available) {
                this.notificationManager.showInfo(`LLM Provider: ${status.provider} (${status.models} models available)`);
            }
            else {
                this.notificationManager.showWarning('LLM Provider: Not available. Check LM Studio or Ollama is running.');
            }
            this.statusBar.hideActivity();
        }
        catch (error) {
            this.statusBar.hideActivity();
            this.notificationManager.showError(`Failed to check LLM status: ${error}`);
        }
    }
    showIssues() {
        // Show problems panel
        vscode.commands.executeCommand('workbench.action.problems.focus');
        this.notificationManager.showInfo('Viewing code issues in Problems panel');
    }
    async generateTests() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active file to generate tests for');
            return;
        }
        try {
            this.statusBar.showActivity('Generating tests...');
            const tests = await this.connection.generateTests(editor.document.uri.fsPath);
            if (tests) {
                // Create new test file
                const testFileName = editor.document.fileName.replace(/\.(py|js|ts)$/, '.test.$1');
                const testUri = vscode.Uri.file(testFileName);
                const edit = new vscode.WorkspaceEdit();
                edit.createFile(testUri, { ignoreIfExists: true });
                edit.insert(testUri, new vscode.Position(0, 0), tests);
                await vscode.workspace.applyEdit(edit);
                await vscode.window.showTextDocument(testUri);
                this.notificationManager.showInfo('Test file generated successfully!');
            }
            this.statusBar.hideActivity();
        }
        catch (error) {
            this.statusBar.hideActivity();
            this.notificationManager.showError(`Test generation failed: ${error}`);
        }
    }
    async optimizeCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active file to optimize');
            return;
        }
        try {
            this.statusBar.showActivity('Optimizing code...');
            const optimized = await this.connection.optimizeCode(editor.document.uri.fsPath, editor.document.getText());
            if (optimized && optimized !== editor.document.getText()) {
                // Show diff and let user approve changes
                const action = await vscode.window.showInformationMessage('Code optimizations found. Apply changes?', 'Apply', 'Review Diff', 'Cancel');
                if (action === 'Apply') {
                    const edit = new vscode.WorkspaceEdit();
                    edit.replace(editor.document.uri, new vscode.Range(0, 0, editor.document.lineCount, 0), optimized);
                    await vscode.workspace.applyEdit(edit);
                    this.notificationManager.showInfo('Code optimized successfully!');
                }
                else if (action === 'Review Diff') {
                    // Open diff view
                    const originalUri = vscode.Uri.parse(`untitled:original-${Date.now()}.py`);
                    const optimizedUri = vscode.Uri.parse(`untitled:optimized-${Date.now()}.py`);
                    await vscode.workspace.openTextDocument(originalUri).then(doc => {
                        const edit = new vscode.WorkspaceEdit();
                        edit.insert(originalUri, new vscode.Position(0, 0), editor.document.getText());
                        return vscode.workspace.applyEdit(edit);
                    });
                    await vscode.workspace.openTextDocument(optimizedUri).then(doc => {
                        const edit = new vscode.WorkspaceEdit();
                        edit.insert(optimizedUri, new vscode.Position(0, 0), optimized);
                        return vscode.workspace.applyEdit(edit);
                    });
                    vscode.commands.executeCommand('vscode.diff', originalUri, optimizedUri, 'Code Optimization');
                }
            }
            else {
                this.notificationManager.showInfo('No optimizations found for this code.');
            }
            this.statusBar.hideActivity();
        }
        catch (error) {
            this.statusBar.hideActivity();
            this.notificationManager.showError(`Code optimization failed: ${error}`);
        }
    }
    async reconnectToBackend() {
        try {
            this.statusBar.updateConnectionStatus('connecting');
            this.notificationManager.showInfo('Reconnecting to Aura backend...');
            this.connection.disconnect();
            await this.connection.connect();
            this.notificationManager.showInfo('Successfully reconnected to Aura backend');
        }
        catch (error) {
            this.logger.error('Failed to reconnect to backend', error);
            this.notificationManager.showError(`Reconnection failed: ${error}`);
        }
    }
    showTroubleshootingPanel() {
        const panel = vscode.window.createWebviewPanel('auraTroubleshooting', 'Aura Troubleshooting', vscode.ViewColumn.One, { enableScripts: true });
        panel.webview.html = this.getTroubleshootingHtml();
        panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'startBackend':
                    this.startBackendService();
                    break;
                case 'testConnection':
                    await this.testBackendConnection();
                    break;
                case 'openSettings':
                    vscode.commands.executeCommand('workbench.action.openSettings', 'aura');
                    break;
            }
        });
    }
    getTroubleshootingHtml() {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Aura Troubleshooting</title>
                <style>
                    body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-foreground); }
                    .section { margin: 20px 0; padding: 15px; border: 1px solid var(--vscode-panel-border); border-radius: 5px; }
                    button { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 10px 15px; margin: 5px; border-radius: 3px; cursor: pointer; }
                    button:hover { background: var(--vscode-button-hoverBackground); }
                    .code { background: var(--vscode-textBlockQuote-background); padding: 10px; border-radius: 3px; font-family: monospace; }
                </style>
            </head>
            <body>
                <h1>🔧 Aura Troubleshooting</h1>
                
                <div class="section">
                    <h2>Connection Issues</h2>
                    <p>If Aura is not connecting, try these steps:</p>
                    <ol>
                        <li>Make sure the backend service is running</li>
                        <li>Check if port 5559 is available</li>
                        <li>Verify ZeroMQ is installed</li>
                    </ol>
                    <button onclick="sendMessage('testConnection')">Test Connection</button>
                    <button onclick="sendMessage('startBackend')">Start Backend</button>
                </div>

                <div class="section">
                    <h2>Manual Backend Startup</h2>
                    <p>Run this command in the Aura backend directory:</p>
                    <div class="code">python3 vscode_backend_service.py</div>
                </div>

                <div class="section">
                    <h2>Configuration</h2>
                    <p>Check your Aura extension settings:</p>
                    <button onclick="sendMessage('openSettings')">Open Settings</button>
                </div>

                <script>
                    const vscode = acquireVsCodeApi();
                    function sendMessage(command) {
                        vscode.postMessage({ command: command });
                    }
                </script>
            </body>
            </html>
        `;
    }
    startBackendService() {
        const terminal = vscode.window.createTerminal('Aura Backend');
        const backendPath = vscode.workspace.getConfiguration('aura').get('backendPath', '../backend');
        terminal.sendText(`cd ${backendPath} && python3 vscode_backend_service.py`);
        terminal.show();
        this.notificationManager.showInfo('Backend service started in terminal. Please check for any errors.');
    }
    async testBackendConnection() {
        try {
            const connected = await this.connection.healthCheck();
            if (connected) {
                this.notificationManager.showInfo('✅ Backend connection is working!');
            }
            else {
                this.notificationManager.showWarning('❌ Backend connection failed. Check if the service is running.');
            }
        }
        catch (error) {
            this.notificationManager.showError(`Connection test failed: ${error}`);
        }
    }
    deactivate() {
        // Clean up resources
        this.disposables.forEach(disposable => disposable.dispose());
        this.connection.disconnect();
        this.statusBar.dispose();
    }
}
exports.AuraExtension = AuraExtension;
// Extension activation function
async function activate(context) {
    const extension = new AuraExtension(context);
    context.subscriptions.push({
        dispose: () => extension.deactivate()
    });
    await extension.activate();
}
exports.activate = activate;
// Extension deactivation function
function deactivate() {
    // Handled by extension instance
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map