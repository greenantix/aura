"use strict";
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
const assert = __importStar(require("assert"));
const vscode = __importStar(require("vscode"));
suite('Aura Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');
    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('aura-ai.aura-autonomous-assistant'));
    });
    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('aura-ai.aura-autonomous-assistant');
        assert.ok(extension);
        if (!extension.isActive) {
            await extension.activate();
        }
        assert.ok(extension.isActive);
    });
    test('Aura commands should be registered', async () => {
        const commands = await vscode.commands.getCommands(true);
        const auraCommands = [
            'aura.analyzeFile',
            'aura.analyzeProject',
            'aura.generateCommit',
            'aura.askQuestion',
            'aura.showDashboard',
            'aura.toggleAutoAnalysis'
        ];
        for (const command of auraCommands) {
            assert.ok(commands.includes(command), `Command ${command} should be registered`);
        }
    });
    test('Configuration should have default values', () => {
        const config = vscode.workspace.getConfiguration('aura');
        assert.strictEqual(config.get('autoAnalysis'), true);
        assert.strictEqual(config.get('serverUrl'), 'tcp://localhost:5559');
        assert.strictEqual(config.get('llmProvider'), 'lm_studio');
        assert.strictEqual(config.get('analysisDepth'), 'detailed');
        assert.strictEqual(config.get('showNotifications'), true);
        assert.strictEqual(config.get('themeColor'), 'purple');
    });
});
//# sourceMappingURL=extension.test.js.map