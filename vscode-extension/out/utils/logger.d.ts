/**
 * Aura Extension Logger
 * ====================
 *
 * Centralized logging utility for the Aura VS Code extension.
 * Provides structured logging with different levels and output channels.
 */
export declare enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}
export declare class AuraLogger {
    private static instance;
    private outputChannel;
    private logLevel;
    private constructor();
    static getInstance(): AuraLogger;
    setLogLevel(level: LogLevel): void;
    debug(message: string, ...args: any[]): void;
    info(message: string, ...args: any[]): void;
    warn(message: string, ...args: any[]): void;
    error(message: string, error?: Error, ...args: any[]): void;
    private log;
    show(): void;
    dispose(): void;
}
//# sourceMappingURL=logger.d.ts.map