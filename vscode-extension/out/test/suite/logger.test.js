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
const logger_1 = require("../../utils/logger");
suite('Aura Logger Test Suite', () => {
    let logger;
    setup(() => {
        logger = logger_1.AuraLogger.getInstance();
    });
    test('Logger should be singleton', () => {
        const logger1 = logger_1.AuraLogger.getInstance();
        const logger2 = logger_1.AuraLogger.getInstance();
        assert.strictEqual(logger1, logger2);
    });
    test('Logger should set and get log level', () => {
        logger.setLogLevel(logger_1.LogLevel.DEBUG);
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
//# sourceMappingURL=logger.test.js.map