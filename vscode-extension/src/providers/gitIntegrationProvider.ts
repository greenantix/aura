/**
 * Git Integration Provider
 * ========================
 * 
 * Provides intelligent Git operations with semantic commit generation,
 * automated branch naming, and change analysis.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { AuraConnection, CommitGeneration } from '../connection';

export interface GitChangeAnalysis {
    files_changed: string[];
    additions: number;
    deletions: number;
    change_type: 'feature' | 'fix' | 'docs' | 'style' | 'refactor' | 'test' | 'chore';
    scope?: string;
    breaking_change: boolean;
    description: string;
    detailed_changes: Array<{
        file: string;
        type: 'added' | 'modified' | 'deleted';
        changes: string[];
    }>;
}

export class GitIntegrationProvider {
    private outputChannel: vscode.OutputChannel;
    private statusBarItem: vscode.StatusBarItem;

    constructor(private connection: AuraConnection) {
        this.outputChannel = vscode.window.createOutputChannel('Aura Git');
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 99);
        this.setupCommands();
        this.setupStatusBar();
    }

    private setupStatusBar(): void {
        this.statusBarItem.text = "$(git-branch) Aura Git";
        this.statusBarItem.tooltip = "Aura Git Integration";
        this.statusBarItem.command = 'aura.git.showPanel';
        this.statusBarItem.show();
    }

    private setupCommands(): void {
        // Register Git-related commands
        vscode.commands.registerCommand('aura.git.generateCommit', () => this.generateCommitMessage());
        vscode.commands.registerCommand('aura.git.analyzeChanges', () => this.analyzeCurrentChanges());
        vscode.commands.registerCommand('aura.git.smartCommit', () => this.performSmartCommit());
        vscode.commands.registerCommand('aura.git.suggestBranch', () => this.suggestBranchName());
        vscode.commands.registerCommand('aura.git.showPanel', () => this.showGitPanel());
    }

    public async generateCommitMessage(): Promise<void> {
        try {
            this.outputChannel.appendLine('[Git] Generating semantic commit message...');
            
            // Get current changes
            const changes = await this.analyzeCurrentChanges();
            if (!changes) {
                vscode.window.showWarningMessage('No changes detected to analyze.');
                return;
            }

            // Generate commit message
            const commit = await this.connection.generateCommit(false);
            if (!commit) {
                vscode.window.showErrorMessage('Failed to generate commit message.');
                return;
            }

            // Show commit message in input box for editing
            const finalMessage = await vscode.window.showInputBox({
                prompt: 'Review and edit the generated commit message',
                value: commit.message,
                placeHolder: 'feat: add new feature',
                validateInput: (value) => {
                    if (!value || value.trim().length === 0) {
                        return 'Commit message cannot be empty';
                    }
                    return null;
                }
            });

            if (finalMessage) {
                // Copy to clipboard
                await vscode.env.clipboard.writeText(finalMessage);
                
                // Show notification with options
                const action = await vscode.window.showInformationMessage(
                    'Commit message generated and copied to clipboard!',
                    'Commit Now',
                    'Open Git Panel'
                );

                if (action === 'Commit Now') {
                    await this.executeGitCommit(finalMessage);
                } else if (action === 'Open Git Panel') {
                    vscode.commands.executeCommand('workbench.view.scm');
                }
            }

        } catch (error) {
            this.outputChannel.appendLine(`[Git] Error: ${error}`);
            vscode.window.showErrorMessage(`Git operation failed: ${error}`);
        }
    }

    public async analyzeCurrentChanges(): Promise<GitChangeAnalysis | null> {
        try {
            this.outputChannel.appendLine('[Git] Analyzing current changes...');
            
            // Execute git status to get changed files
            const gitStatus = await this.executeGitCommand(['status', '--porcelain']);
            if (!gitStatus) {
                return null;
            }

            const changedFiles = this.parseGitStatus(gitStatus);
            if (changedFiles.length === 0) {
                return null;
            }

            // Get detailed diff for analysis
            const gitDiff = await this.executeGitCommand(['diff', '--cached', '--unified=3']);
            const gitDiffUnstaged = await this.executeGitCommand(['diff', '--unified=3']);
            
            const fullDiff = [gitDiff, gitDiffUnstaged].filter(d => d).join('\n');

            // Send to Aura for analysis
            const response = await this.connection.sendMessage('git_semantic', 'analyze_changes', {
                files: changedFiles,
                diff: fullDiff,
                include_analysis: true
            });

            if (response.success && response.analysis) {
                this.outputChannel.appendLine(`[Git] Analysis complete: ${response.analysis.change_type} change detected`);
                return response.analysis;
            }

            return null;

        } catch (error) {
            this.outputChannel.appendLine(`[Git] Analysis error: ${error}`);
            return null;
        }
    }

    public async performSmartCommit(): Promise<void> {
        try {
            // Analyze changes first
            const changes = await this.analyzeCurrentChanges();
            if (!changes) {
                vscode.window.showWarningMessage('No changes to commit.');
                return;
            }

            // Generate commit message
            const commit = await this.connection.generateCommit(false);
            if (!commit) {
                vscode.window.showErrorMessage('Failed to generate commit message.');
                return;
            }

            // Show preview of what will be committed
            const previewMessage = `
**Change Type**: ${changes.change_type}
**Files**: ${changes.files_changed.length} file(s)
**Breaking Change**: ${changes.breaking_change ? 'Yes' : 'No'}

**Proposed Commit Message**:
${commit.message}

**Files to be committed**:
${changes.files_changed.map(f => `• ${f}`).join('\n')}
            `;

            const action = await vscode.window.showInformationMessage(
                'Smart Commit Preview',
                { 
                    modal: true, 
                    detail: previewMessage 
                },
                'Commit',
                'Edit Message',
                'Cancel'
            );

            if (action === 'Commit') {
                await this.executeGitCommit(commit.message);
            } else if (action === 'Edit Message') {
                await this.generateCommitMessage();
            }

        } catch (error) {
            this.outputChannel.appendLine(`[Git] Smart commit error: ${error}`);
            vscode.window.showErrorMessage(`Smart commit failed: ${error}`);
        }
    }

    public async suggestBranchName(): Promise<void> {
        try {
            this.outputChannel.appendLine('[Git] Suggesting branch name...');
            
            // Get current changes for context
            const changes = await this.analyzeCurrentChanges();
            
            // Ask user for feature description if no changes
            let description = '';
            if (changes) {
                description = changes.description;
            } else {
                const userInput = await vscode.window.showInputBox({
                    prompt: 'Describe the feature or change you\'re working on',
                    placeHolder: 'Add user authentication system'
                });
                if (!userInput) {return;}
                description = userInput;
            }

            // Generate branch name
            const response = await this.connection.sendMessage('git_semantic', 'suggest_branch_name', {
                description: description,
                change_type: changes?.change_type || 'feature'
            });

            if (response.success && response.branch_name) {
                const branchName = response.branch_name;
                
                const action = await vscode.window.showInformationMessage(
                    `Suggested branch name: ${branchName}`,
                    'Create Branch',
                    'Copy Name',
                    'Edit Name'
                );

                if (action === 'Create Branch') {
                    await this.createBranch(branchName);
                } else if (action === 'Copy Name') {
                    await vscode.env.clipboard.writeText(branchName);
                    vscode.window.showInformationMessage('Branch name copied to clipboard!');
                } else if (action === 'Edit Name') {
                    const editedName = await vscode.window.showInputBox({
                        value: branchName,
                        prompt: 'Edit the branch name'
                    });
                    if (editedName) {
                        await this.createBranch(editedName);
                    }
                }
            }

        } catch (error) {
            this.outputChannel.appendLine(`[Git] Branch suggestion error: ${error}`);
            vscode.window.showErrorMessage(`Branch suggestion failed: ${error}`);
        }
    }

    private async createBranch(branchName: string): Promise<void> {
        try {
            const result = await this.executeGitCommand(['checkout', '-b', branchName]);
            if (result !== null) {
                vscode.window.showInformationMessage(`Created and switched to branch: ${branchName}`);
                this.outputChannel.appendLine(`[Git] Created branch: ${branchName}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create branch: ${error}`);
        }
    }

    private async executeGitCommit(message: string): Promise<void> {
        try {
            // Add all staged files or stage modified files
            const statusResult = await this.executeGitCommand(['status', '--porcelain']);
            if (statusResult) {
                const hasStaged = statusResult.split('\n').some(line => line.startsWith('M ') || line.startsWith('A '));
                if (!hasStaged) {
                    // Stage modified files
                    await this.executeGitCommand(['add', '-u']);
                }
            }

            // Commit with the generated message
            const result = await this.executeGitCommand(['commit', '-m', message]);
            if (result !== null) {
                vscode.window.showInformationMessage('Successfully committed changes!');
                this.outputChannel.appendLine(`[Git] Committed: ${message}`);
            }

        } catch (error) {
            vscode.window.showErrorMessage(`Commit failed: ${error}`);
        }
    }

    private async executeGitCommand(args: string[]): Promise<string | null> {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                throw new Error('No workspace folder found');
            }

            const { spawn } = require('child_process');
            
            return new Promise((resolve, reject) => {
                const git = spawn('git', args, {
                    cwd: workspaceFolder.uri.fsPath,
                    stdio: ['pipe', 'pipe', 'pipe'],
                    timeout: 30000 // 30 second timeout
                });

                let stdout = '';
                let stderr = '';

                git.stdout.on('data', (data: any) => {
                    stdout += data.toString();
                });

                git.stderr.on('data', (data: any) => {
                    stderr += data.toString();
                });

                git.on('close', (code: number) => {
                    if (code === 0) {
                        resolve(stdout.trim());
                    } else {
                        const errorMessage = stderr || `Git command failed with code ${code}`;
                        this.outputChannel.appendLine(`[Git] Command failed: git ${args.join(' ')} - ${errorMessage}`);
                        reject(new Error(errorMessage));
                    }
                });

                git.on('error', (error: any) => {
                    this.outputChannel.appendLine(`[Git] Process error: ${error.message}`);
                    reject(error);
                });

                // Handle timeout
                setTimeout(() => {
                    if (!git.killed) {
                        git.kill();
                        reject(new Error(`Git command timeout: git ${args.join(' ')}`));
                    }
                }, 30000);
            });

        } catch (error) {
            this.outputChannel.appendLine(`[Git] Command error: ${error}`);
            return null;
        }
    }

    private parseGitStatus(statusOutput: string): string[] {
        return statusOutput
            .split('\n')
            .filter(line => line.trim().length > 0)
            .map(line => line.substring(3)) // Remove status prefix
            .filter(file => file.length > 0);
    }

    private async showGitPanel(): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'auraGit',
            'Aura Git Assistant',
            vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        // Get current git status
        const changes = await this.analyzeCurrentChanges();
        
        panel.webview.html = this.getGitPanelHtml(changes);

        // Handle messages from webview
        panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'generateCommit':
                    await this.generateCommitMessage();
                    break;
                case 'smartCommit':
                    await this.performSmartCommit();
                    break;
                case 'suggestBranch':
                    await this.suggestBranchName();
                    break;
                case 'refresh': {
                    const newChanges = await this.analyzeCurrentChanges();
                    panel.webview.html = this.getGitPanelHtml(newChanges);
                    break;
                }
            }
        });
    }

    private getGitPanelHtml(changes: GitChangeAnalysis | null): string {
        const changesHtml = changes ? `
            <div class="change-analysis">
                <h3>Current Changes Analysis</h3>
                <div class="change-info">
                    <p><strong>Type:</strong> ${changes.change_type}</p>
                    <p><strong>Files:</strong> ${changes.files_changed.length}</p>
                    <p><strong>Breaking Change:</strong> ${changes.breaking_change ? 'Yes' : 'No'}</p>
                    ${changes.scope ? `<p><strong>Scope:</strong> ${changes.scope}</p>` : ''}
                </div>
                <div class="files-list">
                    <h4>Changed Files:</h4>
                    <ul>
                        ${changes.files_changed.map(file => `<li>${file}</li>`).join('')}
                    </ul>
                </div>
            </div>
        ` : '<p>No changes detected</p>';

        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Aura Git Assistant</title>
                <style>
                    body { 
                        font-family: var(--vscode-font-family);
                        color: var(--vscode-foreground);
                        background: var(--vscode-editor-background);
                        padding: 20px;
                    }
                    .section {
                        margin-bottom: 20px;
                        padding: 15px;
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 5px;
                    }
                    button {
                        background: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        padding: 10px 15px;
                        margin: 5px;
                        border-radius: 3px;
                        cursor: pointer;
                    }
                    button:hover {
                        background: var(--vscode-button-hoverBackground);
                    }
                    .change-analysis {
                        background: var(--vscode-editor-background);
                        padding: 15px;
                        border-radius: 5px;
                    }
                    .change-info p {
                        margin: 5px 0;
                    }
                    ul {
                        margin: 10px 0;
                        padding-left: 20px;
                    }
                </style>
            </head>
            <body>
                <h1>🤖 Aura Git Assistant</h1>
                
                <div class="section">
                    <h2>Quick Actions</h2>
                    <button onclick="sendMessage('generateCommit')">Generate Commit Message</button>
                    <button onclick="sendMessage('smartCommit')">Smart Commit</button>
                    <button onclick="sendMessage('suggestBranch')">Suggest Branch Name</button>
                    <button onclick="sendMessage('refresh')">Refresh</button>
                </div>

                <div class="section">
                    ${changesHtml}
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

    public dispose(): void {
        this.outputChannel.dispose();
        this.statusBarItem.dispose();
    }
}