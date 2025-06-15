/**
 * Real-Time Aura Analysis Provider
 * ================================
 *
 * Provides real-time code analysis with live feedback as users type.
 * Integrates with VS Code's diagnostic system for inline issue display.
 */
import { AuraConnection } from '../connection';
export declare class RealTimeAnalysisProvider {
    private connection;
    private diagnosticsCollection;
    private analysisQueue;
    private currentAnalyses;
    private statusBarItem;
    private outputChannel;
    constructor(connection: AuraConnection);
    private setupStatusBar;
    private initializeRealTimeAnalysis;
    private onDocumentChange;
    private analyzeDocument;
    private performAnalysis;
    private updateDiagnostics;
    private getSeverity;
    private updateStatusBar;
    private notifyAnalysisUpdate;
    private isSupportedFile;
    private getLanguageFromDocument;
    analyzeWorkspace(): Promise<void>;
    clearDiagnostics(): void;
    dispose(): void;
}
//# sourceMappingURL=realTimeAnalysisProvider.d.ts.map