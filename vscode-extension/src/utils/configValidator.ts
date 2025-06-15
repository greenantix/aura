/**
 * Configuration Validator
 * =======================
 * 
 * Validates Aura extension configuration settings and provides
 * helpful error messages for invalid configurations.
 */

import * as vscode from 'vscode';
import { AuraLogger } from './logger';

export interface ValidationResult {
    isValid: boolean;
    errors: string[];
    warnings: string[];
}

export class ConfigValidator {
    private logger = AuraLogger.getInstance();

    public validateConfiguration(): ValidationResult {
        const result: ValidationResult = {
            isValid: true,
            errors: [],
            warnings: []
        };

        const config = vscode.workspace.getConfiguration('aura');

        // Validate server URL
        this.validateServerUrl(config, result);
        
        // Validate LLM provider
        this.validateLLMProvider(config, result);
        
        // Validate analysis depth
        this.validateAnalysisDepth(config, result);
        
        // Validate theme color
        this.validateThemeColor(config, result);

        // Log validation results
        if (result.errors.length > 0) {
            this.logger.error('Configuration validation failed', undefined, result.errors);
            result.isValid = false;
        }
        
        if (result.warnings.length > 0) {
            this.logger.warn('Configuration validation warnings', result.warnings);
        }

        if (result.isValid && result.warnings.length === 0) {
            this.logger.info('Configuration validation passed');
        }

        return result;
    }

    private validateServerUrl(config: vscode.WorkspaceConfiguration, result: ValidationResult): void {
        const serverUrl = config.get<string>('serverUrl', '');
        
        if (!serverUrl) {
            result.errors.push('Server URL is required');
            return;
        }

        // Check if it's a valid ZeroMQ URL format
        const zmqPattern = /^tcp:\/\/[a-zA-Z0-9.-]+:\d+$/;
        if (!zmqPattern.test(serverUrl)) {
            result.errors.push(`Invalid server URL format: ${serverUrl}. Expected format: tcp://hostname:port`);
        }

        // Check port range
        const portMatch = serverUrl.match(/:(\d+)$/);
        if (portMatch) {
            const port = parseInt(portMatch[1]);
            if (port < 1024 || port > 65535) {
                result.warnings.push(`Port ${port} is outside recommended range (1024-65535)`);
            }
        }
    }

    private validateLLMProvider(config: vscode.WorkspaceConfiguration, result: ValidationResult): void {
        const llmProvider = config.get<string>('llmProvider', '');
        const validProviders = ['lm_studio', 'ollama', 'openai', 'anthropic'];
        
        if (!llmProvider) {
            result.errors.push('LLM provider is required');
            return;
        }

        if (!validProviders.includes(llmProvider)) {
            result.warnings.push(`Unknown LLM provider: ${llmProvider}. Supported providers: ${validProviders.join(', ')}`);
        }
    }

    private validateAnalysisDepth(config: vscode.WorkspaceConfiguration, result: ValidationResult): void {
        const analysisDepth = config.get<string>('analysisDepth', '');
        const validDepths = ['basic', 'detailed', 'comprehensive'];
        
        if (!analysisDepth) {
            result.warnings.push('Analysis depth not specified, using default');
            return;
        }

        if (!validDepths.includes(analysisDepth)) {
            result.warnings.push(`Unknown analysis depth: ${analysisDepth}. Valid options: ${validDepths.join(', ')}`);
        }
    }

    private validateThemeColor(config: vscode.WorkspaceConfiguration, result: ValidationResult): void {
        const themeColor = config.get<string>('themeColor', '');
        const validColors = ['blue', 'green', 'purple', 'orange', 'red'];
        
        if (themeColor && !validColors.includes(themeColor)) {
            result.warnings.push(`Unknown theme color: ${themeColor}. Valid options: ${validColors.join(', ')}`);
        }
    }

    public async showValidationResults(result: ValidationResult): Promise<void> {
        if (!result.isValid) {
            const message = `Aura configuration has errors:\n${result.errors.join('\n')}`;
            const action = await vscode.window.showErrorMessage(
                message,
                'Open Settings',
                'Ignore'
            );
            
            if (action === 'Open Settings') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'aura');
            }
        } else if (result.warnings.length > 0) {
            const message = `Aura configuration warnings:\n${result.warnings.join('\n')}`;
            vscode.window.showWarningMessage(message, 'Open Settings');
        }
    }
}