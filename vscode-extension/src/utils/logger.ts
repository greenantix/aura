/**
 * Aura Extension Logger
 * ====================
 * 
 * Centralized logging utility for the Aura VS Code extension.
 * Provides structured logging with different levels and output channels.
 */

import * as vscode from 'vscode';

export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}

export class AuraLogger {
    private static instance: AuraLogger;
    private outputChannel: vscode.OutputChannel;
    private logLevel: LogLevel = LogLevel.INFO;

    private constructor() {
        this.outputChannel = vscode.window.createOutputChannel('Aura Extension');
    }

    public static getInstance(): AuraLogger {
        if (!AuraLogger.instance) {
            AuraLogger.instance = new AuraLogger();
        }
        return AuraLogger.instance;
    }

    public setLogLevel(level: LogLevel): void {
        this.logLevel = level;
    }

    public debug(message: string, ...args: any[]): void {
        if (this.logLevel <= LogLevel.DEBUG) {
            this.log('DEBUG', message, ...args);
        }
    }

    public info(message: string, ...args: any[]): void {
        if (this.logLevel <= LogLevel.INFO) {
            this.log('INFO', message, ...args);
        }
    }

    public warn(message: string, ...args: any[]): void {
        if (this.logLevel <= LogLevel.WARN) {
            this.log('WARN', message, ...args);
        }
    }

    public error(message: string, error?: Error, ...args: any[]): void {
        if (this.logLevel <= LogLevel.ERROR) {
            const errorMessage = error ? `${message}: ${error.message}` : message;
            this.log('ERROR', errorMessage, ...args);
            if (error && error.stack) {
                this.outputChannel.appendLine(`Stack trace: ${error.stack}`);
            }
        }
    }

    private log(level: string, message: string, ...args: any[]): void {
        const timestamp = new Date().toISOString();
        const formattedMessage = `[${timestamp}] [${level}] ${message}`;
        
        this.outputChannel.appendLine(formattedMessage);
        
        if (args.length > 0) {
            this.outputChannel.appendLine(`Additional data: ${JSON.stringify(args, null, 2)}`);
        }

        // Also log to console for development
        console.log(formattedMessage, ...args);
    }

    public show(): void {
        this.outputChannel.show();
    }

    public dispose(): void {
        this.outputChannel.dispose();
    }
}