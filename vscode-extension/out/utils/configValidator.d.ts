/**
 * Configuration Validator
 * =======================
 *
 * Validates Aura extension configuration settings and provides
 * helpful error messages for invalid configurations.
 */
export interface ValidationResult {
    isValid: boolean;
    errors: string[];
    warnings: string[];
}
export declare class ConfigValidator {
    private logger;
    validateConfiguration(): ValidationResult;
    private validateServerUrl;
    private validateLLMProvider;
    private validateAnalysisDepth;
    private validateThemeColor;
    showValidationResults(result: ValidationResult): Promise<void>;
}
//# sourceMappingURL=configValidator.d.ts.map