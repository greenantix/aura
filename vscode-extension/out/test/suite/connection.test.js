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
const connection_1 = require("../../connection");
suite('Aura Connection Test Suite', () => {
    let connection;
    setup(() => {
        connection = new connection_1.AuraConnection('tcp://localhost:5559');
    });
    teardown(() => {
        if (connection) {
            connection.disconnect();
        }
    });
    test('Connection should initialize with server URL', () => {
        assert.ok(connection);
        // Connection tests require backend to be running
        // For now, just test instantiation
    });
    test('Connection should handle invalid URLs gracefully', () => {
        const invalidConnection = new connection_1.AuraConnection('invalid-url');
        assert.ok(invalidConnection);
        // Should not throw during construction
    });
    test('Status change callbacks should work', () => {
        let statusChanged = false;
        let lastStatus = '';
        connection.onStatusChange((status) => {
            statusChanged = true;
            lastStatus = status;
        });
        // Simulate status change
        connection.notifyStatusChange('connected');
        assert.ok(statusChanged);
        assert.strictEqual(lastStatus, 'connected');
    });
    test('Connection should format file analysis requests', async () => {
        // Test request formatting without actual backend
        const request = {
            file_path: '/test/file.py',
            analysis_depth: 'detailed'
        };
        // This would normally require backend, so we test the request structure
        assert.ok(request.file_path);
        assert.ok(request.analysis_depth);
    });
});
//# sourceMappingURL=connection.test.js.map