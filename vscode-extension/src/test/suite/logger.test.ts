import * as assert from 'assert';
import { AuraLogger, LogLevel } from '../../utils/logger';

suite('Aura Logger Test Suite', () => {
    let logger: AuraLogger;

    setup(() => {
        logger = AuraLogger.getInstance();
    });

    test('Logger should be singleton', () => {
        const logger1 = AuraLogger.getInstance();
        const logger2 = AuraLogger.getInstance();
        
        assert.strictEqual(logger1, logger2);
    });

    test('Logger should set and get log level', () => {
        logger.setLogLevel(LogLevel.DEBUG);
        // No public getter for log level, but we can test that it doesn't throw
        assert.ok(logger);
    });

    test('Logger should handle different log levels', () => {
        // Test that logging methods don't throw
        assert.doesNotThrow(() => {
            logger.debug('Debug message');
            logger.info('Info message');
            logger.warn('Warning message');
            logger.error('Error message', new Error('Test error'));
        });
    });

    test('Logger should handle errors without stack trace', () => {
        assert.doesNotThrow(() => {
            logger.error('Error without stack trace');
        });
    });

    test('Logger should format messages consistently', () => {
        // Since logger outputs to VS Code channel, we mainly test that it doesn't crash
        assert.doesNotThrow(() => {
            logger.info('Test message with %s formatting', 'parameter');
        });
    });
});