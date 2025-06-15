import * as assert from 'assert';
import * as vscode from 'vscode';
import { AuraExtension } from '../../extension';

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