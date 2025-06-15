/**
 * Git Integration Provider
 * ========================
 *
 * Provides intelligent Git operations with semantic commit generation,
 * automated branch naming, and change analysis.
 */
import { AuraConnection } from '../connection';
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
export declare class GitIntegrationProvider {
    private connection;
    private outputChannel;
    private statusBarItem;
    constructor(connection: AuraConnection);
    private setupStatusBar;
    private setupCommands;
    generateCommitMessage(): Promise<void>;
    analyzeCurrentChanges(): Promise<GitChangeAnalysis | null>;
    performSmartCommit(): Promise<void>;
    suggestBranchName(): Promise<void>;
    private createBranch;
    private executeGitCommit;
    private executeGitCommand;
    private parseGitStatus;
    private showGitPanel;
    private getGitPanelHtml;
    dispose(): void;
}
//# sourceMappingURL=gitIntegrationProvider.d.ts.map