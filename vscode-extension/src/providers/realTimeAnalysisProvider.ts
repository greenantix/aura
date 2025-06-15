/**
 * Real-Time Aura Analysis Provider
 * ================================
 * 
 * Provides real-time code analysis with live feedback as users type.
 * Integrates with VS Code's diagnostic system for inline issue display.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { AuraConnection, FileAnalysis } from '../connection';

export class RealTimeAnalysisProvider {
    private diagnosticsCollection: vscode.DiagnosticCollection;
    private analysisQueue: Map<string, NodeJS.Timeout> = new Map();
    private currentAnalyses: Set<string> = new Set();
    private statusBarItem: vscode.StatusBarItem;
    private outputChannel: vscode.OutputChannel;

    constructor(private connection: AuraConnection) {
        this.diagnosticsCollection = vscode.languages.createDiagnosticCollection('aura-analysis');
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        this.outputChannel = vscode.window.createOutputChannel('Aura Analysis');
        
        this.initializeRealTimeAnalysis();
        this.setupStatusBar();
    }

    private setupStatusBar(): void {
        this.statusBarItem.text = "$(eye) Aura: Ready";
        this.statusBarItem.tooltip = "Aura Analysis Status";
        this.statusBarItem.command = 'aura.showAnalysisOutput';
        this.statusBarItem.show();
    }

    private initializeRealTimeAnalysis(): void {
        // Watch for file changes
        vscode.workspace.onDidChangeTextDocument(async (event) => {
            await this.onDocumentChange(event);
        });

        // Watch for file saves
        vscode.workspace.onDidSaveTextDocument(async (document) => {
            await this.analyzeDocument(document, true);
        });

        // Watch for active editor changes
        vscode.window.onDidChangeActiveTextEditor(async (editor) => {
            if (editor) {
                await this.analyzeDocument(editor.document, false);
            }
        });

        // Analyze current file if any
        if (vscode.window.activeTextEditor) {
            this.analyzeDocument(vscode.window.activeTextEditor.document, false);
        }
    }

    private async onDocumentChange(event: vscode.TextDocumentChangeEvent): Promise<void> {
        const document = event.document;
        
        // Only analyze supported file types
        if (!this.isSupportedFile(document)) {
            return;
        }

        // Skip analysis for very large files to prevent performance issues
        const maxLines = 5000;
        if (document.lineCount > maxLines) {
            this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Skipping real-time analysis for large file (${document.lineCount} lines)`);
            return;
        }

        // Debounce analysis - wait for user to stop typing
        const filePath = document.uri.fsPath;
        
        // Clear existing timeout
        const existingTimeout = this.analysisQueue.get(filePath);
        if (existingTimeout) {
            clearTimeout(existingTimeout);
        }

        // Set new timeout for analysis - longer delay for larger files
        const delayMs = document.lineCount > 1000 ? 5000 : 2000;
        const timeout = setTimeout(() => {
            this.analyzeDocument(document, false);
            this.analysisQueue.delete(filePath);
        }, delayMs);

        this.analysisQueue.set(filePath, timeout);
    }

    private async analyzeDocument(document: vscode.TextDocument, isOnSave: boolean): Promise<void> {
        if (!this.isSupportedFile(document)) {
            return;
        }

        const filePath = document.uri.fsPath;
        
        // Prevent multiple simultaneous analyses of same file
        if (this.currentAnalyses.has(filePath)) {
            return;
        }

        try {
            this.currentAnalyses.add(filePath);
            this.updateStatusBar("Analyzing...", true);
            
            this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Analyzing: ${path.basename(filePath)}`);
            
            // Perform analysis
            const analysis = await this.performAnalysis(document, isOnSave);
            
            if (analysis) {
                // Update diagnostics
                this.updateDiagnostics(document.uri, analysis);
                
                // Update tree view
                this.notifyAnalysisUpdate(filePath, analysis);
                
                this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Analysis complete: ${analysis.issues.length} issues found`);
            }

            this.updateStatusBar("Ready", false);
            
        } catch (error) {
            this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Analysis failed: ${error}`);
            this.updateStatusBar("Error", false);
            
        } finally {
            this.currentAnalyses.delete(filePath);
        }
    }

    private async performAnalysis(document: vscode.TextDocument, isOnSave: boolean): Promise<FileAnalysis | null> {
        try {
            const filePath = document.uri.fsPath;
            const content = document.getText();
            
            // Skip analysis for empty files
            if (content.trim().length === 0) {
                this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Skipping analysis for empty file: ${filePath}`);
                return null;
            }
            
            // Determine file language
            const language = this.getLanguageFromDocument(document);
            
            // Skip analysis for unsupported languages
            if (language === 'unknown') {
                this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Skipping analysis for unsupported language: ${document.languageId}`);
                return null;
            }
            
            // Send analysis request to Aura backend with timeout
            const analysisPromise = this.connection.analyzeFile(filePath, {
                content: content,
                language: language,
                realTime: !isOnSave,
                includeMetrics: isOnSave,
                includeSuggestions: isOnSave
            });
            
            // Set a timeout for analysis
            const timeoutPromise = new Promise<null>((resolve) => {
                setTimeout(() => {
                    this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Analysis timeout for: ${filePath}`);
                    resolve(null);
                }, 15000); // 15 second timeout
            });
            
            const analysis = await Promise.race([analysisPromise, timeoutPromise]);
            return analysis;
            
        } catch (error) {
            this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Analysis error: ${error}`);
            console.error('Analysis failed:', error);
            return null;
        }
    }

    private updateDiagnostics(uri: vscode.Uri, analysis: FileAnalysis): void {
        const diagnostics: vscode.Diagnostic[] = [];

        // Convert analysis issues to VS Code diagnostics
        for (const issue of analysis.issues) {
            const range = new vscode.Range(
                Math.max(0, issue.line - 1), // VS Code is 0-indexed
                0,
                Math.max(0, issue.line - 1),
                1000 // End of line
            );

            const severity = this.getSeverity(issue.severity);
            
            const diagnostic = new vscode.Diagnostic(
                range,
                issue.message,
                severity
            );

            // Add additional information
            diagnostic.source = 'Aura';
            diagnostic.code = issue.type;
            
            if (issue.suggestion) {
                diagnostic.relatedInformation = [
                    new vscode.DiagnosticRelatedInformation(
                        new vscode.Location(uri, range),
                        `Suggestion: ${issue.suggestion}`
                    )
                ];
            }

            diagnostics.push(diagnostic);
        }

        this.diagnosticsCollection.set(uri, diagnostics);
    }

    private getSeverity(severity: string): vscode.DiagnosticSeverity {
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

    private updateStatusBar(text: string, isWorking: boolean): void {
        const icon = isWorking ? "$(sync~spin)" : "$(eye)";
        this.statusBarItem.text = `${icon} Aura: ${text}`;
    }

    private notifyAnalysisUpdate(filePath: string, analysis: FileAnalysis): void {
        // Notify other providers about analysis update
        vscode.commands.executeCommand('aura.analysisUpdated', filePath, analysis);
    }

    private isSupportedFile(document: vscode.TextDocument): boolean {
        const supportedLanguages = [
            'python', 'javascript', 'typescript', 'javascriptreact', 'typescriptreact',
            'go', 'rust', 'java', 'cpp', 'c', 'csharp', 'php', 'ruby'
        ];
        
        const language = document.languageId;
        return supportedLanguages.includes(language) && !document.uri.scheme.startsWith('git');
    }

    private getLanguageFromDocument(document: vscode.TextDocument): string {
        const languageMap: { [key: string]: string } = {
            'python': 'python',
            'javascript': 'javascript',
            'typescript': 'typescript',
            'javascriptreact': 'javascript',
            'typescriptreact': 'typescript',
            'go': 'go',
            'rust': 'rust',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'csharp': 'csharp',
            'php': 'php',
            'ruby': 'ruby'
        };

        return languageMap[document.languageId] || 'unknown';
    }

    public async analyzeWorkspace(): Promise<void> {
        this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Starting workspace analysis...`);
        
        // Find all supported files in workspace
        const files = await vscode.workspace.findFiles(
            '**/*.{py,js,ts,jsx,tsx,go,rs,java,cpp,c,cs,php,rb}',
            '**/node_modules/**'
        );

        this.updateStatusBar(`Analyzing workspace (${files.length} files)`, true);
        
        let analyzed = 0;
        const batchSize = 5; // Analyze 5 files at a time

        for (let i = 0; i < files.length; i += batchSize) {
            const batch = files.slice(i, i + batchSize);
            
            await Promise.all(batch.map(async (file) => {
                try {
                    const document = await vscode.workspace.openTextDocument(file);
                    await this.analyzeDocument(document, true);
                    analyzed++;
                } catch (error) {
                    this.outputChannel.appendLine(`Failed to analyze ${file.fsPath}: ${error}`);
                }
            }));

            // Update progress
            this.updateStatusBar(`Analyzing workspace (${analyzed}/${files.length})`, true);
        }

        this.updateStatusBar("Workspace analysis complete", false);
        this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Workspace analysis complete: ${analyzed} files analyzed`);
    }

    public clearDiagnostics(): void {
        this.diagnosticsCollection.clear();
    }

    public dispose(): void {
        this.diagnosticsCollection.dispose();
        this.statusBarItem.dispose();
        this.outputChannel.dispose();
        
        // Clear all timeouts
        for (const timeout of this.analysisQueue.values()) {
            clearTimeout(timeout);
        }
        this.analysisQueue.clear();
    }
}