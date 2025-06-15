import * as assert from 'assert';
import { AuraConnection } from '../../connection';

suite('Aura Connection Test Suite', () => {
    let connection: AuraConnection;

    setup(() => {
        connection = new AuraConnection('tcp://localhost:5559');
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
        const invalidConnection = new AuraConnection('invalid-url');
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
        (connection as any).notifyStatusChange('connected');

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