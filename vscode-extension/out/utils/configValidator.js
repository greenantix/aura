"use strict";
/**
 * Configuration Validator
 * =======================
 *
 * Validates Aura extension configuration settings and provides
 * helpful error messages for invalid configurations.
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
exports.ConfigValidator = void 0;
const vscode = __importStar(require("vscode"));
const logger_1 = require("./logger");
class ConfigValidator {
    constructor() {
        this.logger = logger_1.AuraLogger.getInstance();
    }
    validateConfiguration() {
        const result = {
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
    validateServerUrl(config, result) {
        const serverUrl = config.get('serverUrl', '');
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
    validateLLMProvider(config, result) {
        const llmProvider = config.get('llmProvider', '');
        const validProviders = ['lm_studio', 'ollama', 'openai', 'anthropic'];
        if (!llmProvider) {
            result.errors.push('LLM provider is required');
            return;
        }
        if (!validProviders.includes(llmProvider)) {
            result.warnings.push(`Unknown LLM provider: ${llmProvider}. Supported providers: ${validProviders.join(', ')}`);
        }
    }
    validateAnalysisDepth(config, result) {
        const analysisDepth = config.get('analysisDepth', '');
        const validDepths = ['basic', 'detailed', 'comprehensive'];
        if (!analysisDepth) {
            result.warnings.push('Analysis depth not specified, using default');
            return;
        }
        if (!validDepths.includes(analysisDepth)) {
            result.warnings.push(`Unknown analysis depth: ${analysisDepth}. Valid options: ${validDepths.join(', ')}`);
        }
    }
    validateThemeColor(config, result) {
        const themeColor = config.get('themeColor', '');
        const validColors = ['blue', 'green', 'purple', 'orange', 'red'];
        if (themeColor && !validColors.includes(themeColor)) {
            result.warnings.push(`Unknown theme color: ${themeColor}. Valid options: ${validColors.join(', ')}`);
        }
    }
    async showValidationResults(result) {
        if (!result.isValid) {
            const message = `Aura configuration has errors:\n${result.errors.join('\n')}`;
            const action = await vscode.window.showErrorMessage(message, 'Open Settings', 'Ignore');
            if (action === 'Open Settings') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'aura');
            }
        }
        else if (result.warnings.length > 0) {
            const message = `Aura configuration warnings:\n${result.warnings.join('\n')}`;
            vscode.window.showWarningMessage(message, 'Open Settings');
        }
    }
}
exports.ConfigValidator = ConfigValidator;
//# sourceMappingURL=configValidator.js.map