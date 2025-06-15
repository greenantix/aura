/**
 * Aura Chat Provider
 * ==================
 * 
 * Provides an interactive chat interface with Aura in VS Code.
 * Allows developers to ask questions and get intelligent responses.
 */

import * as vscode from 'vscode';
import { AuraConnection } from '../connection';

export class AuraChatProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'aura.chat';

    private _view?: vscode.WebviewView;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private connection: AuraConnection
    ) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                this._extensionUri
            ]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async data => {
            switch (data.type) {
                case 'askQuestion':
                    await this.handleQuestion(data.question);
                    break;
                case 'clearChat':
                    this.clearChat();
                    break;
            }
        });
    }

    public async askQuestion(question: string): Promise<void> {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'addUserMessage',
                message: question
            });
            await this.handleQuestion(question);
        }
    }

    private async handleQuestion(question: string): Promise<void> {
        try {
            // Show thinking indicator
            this._view?.webview.postMessage({
                type: 'showThinking',
                show: true
            });

            // Get response from Aura
            const response = await this.connection.askQuestion(question);
            
            // Hide thinking indicator
            this._view?.webview.postMessage({
                type: 'showThinking',
                show: false
            });

            if (response) {
                this._view?.webview.postMessage({
                    type: 'addResponse',
                    response: response
                });
            } else {
                this._view?.webview.postMessage({
                    type: 'addResponse',
                    response: 'Sorry, I could not process your question. Please check the connection to Aura.'
                });
            }
        } catch (error) {
            this._view?.webview.postMessage({
                type: 'showThinking',
                show: false
            });
            
            this._view?.webview.postMessage({
                type: 'addResponse',
                response: `Error: ${error}`
            });
        }
    }

    private clearChat(): void {
        // Chat is cleared via webview messages
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aura Chat</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 10px;
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            margin: 0;
        }
        
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 10px 0;
            margin-bottom: 10px;
        }
        
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
            max-width: 90%;
        }
        
        .message.user {
            background-color: var(--vscode-input-background);
            margin-left: auto;
            border: 1px solid var(--vscode-input-border);
        }
        
        .message.aura {
            background-color: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
        }
        
        .thinking {
            padding: 10px;
            color: var(--vscode-descriptionForeground);
            font-style: italic;
        }
        
        .thinking-dots {
            display: inline-block;
        }
        
        .thinking-dot {
            display: inline-block;
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background-color: var(--vscode-descriptionForeground);
            margin: 0 2px;
            animation: thinking 1.4s infinite ease-in-out both;
        }
        
        .thinking-dot:nth-child(1) { animation-delay: -0.32s; }
        .thinking-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes thinking {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        .input-container {
            display: flex;
            gap: 5px;
            padding: 10px 0;
            border-top: 1px solid var(--vscode-panel-border);
        }
        
        #questionInput {
            flex: 1;
            padding: 8px;
            border: 1px solid var(--vscode-input-border);
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border-radius: 4px;
        }
        
        button {
            padding: 8px 12px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .welcome-message {
            text-align: center;
            color: var(--vscode-descriptionForeground);
            padding: 20px;
        }
        
        pre {
            background-color: var(--vscode-textBlockQuote-background);
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        
        code {
            background-color: var(--vscode-textBlockQuote-background);
            padding: 2px 4px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                <h3>🤖 Aura Chat</h3>
                <p>Ask me anything about your code. I'm here to help!</p>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="questionInput" placeholder="Ask Aura a question..." />
            <button id="sendButton">Send</button>
            <button id="clearButton">Clear</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const chatContainer = document.getElementById('chatMessages');
        const questionInput = document.getElementById('questionInput');
        const sendButton = document.getElementById('sendButton');
        const clearButton = document.getElementById('clearButton');
        
        let isThinking = false;

        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user' : 'aura');
            
            // Simple markdown-like processing
            let processedContent = content
                .replace(/\`\`\`([\\s\\S]*?)\`\`\`/g, '<pre><code>$1</code></pre>')
                .replace(/\`([^\`]+)\`/g, '<code>$1</code>')
                .replace(/\\n/g, '<br>');
            
            messageDiv.innerHTML = processedContent;
            chatContainer.appendChild(messageDiv);
            
            // Remove welcome message if it exists
            const welcomeMessage = chatContainer.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showThinking(show) {
            isThinking = show;
            sendButton.disabled = show;
            
            const existingThinking = chatContainer.querySelector('.thinking');
            if (existingThinking) {
                existingThinking.remove();
            }
            
            if (show) {
                const thinkingDiv = document.createElement('div');
                thinkingDiv.className = 'thinking';
                thinkingDiv.innerHTML = '🤖 Aura is thinking <div class="thinking-dots"><div class="thinking-dot"></div><div class="thinking-dot"></div><div class="thinking-dot"></div></div>';
                chatContainer.appendChild(thinkingDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }

        function sendQuestion() {
            const question = questionInput.value.trim();
            if (question && !isThinking) {
                addMessage(question, true);
                showThinking(true);
                questionInput.value = '';
                
                vscode.postMessage({
                    type: 'askQuestion',
                    question: question
                });
            }
        }

        function clearChat() {
            chatContainer.innerHTML = '<div class="welcome-message"><h3>🤖 Aura Chat</h3><p>Ask me anything about your code. I\\'m here to help!</p></div>';
            vscode.postMessage({ type: 'clearChat' });
        }

        // Event listeners
        sendButton.addEventListener('click', sendQuestion);
        clearButton.addEventListener('click', clearChat);

        questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !isThinking) {
                sendQuestion();
            }
        });

        // Handle messages from the extension
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'addResponse':
                    showThinking(false);
                    addMessage(message.response);
                    break;
                case 'addUserMessage':
                    addMessage(message.message, true);
                    break;
                case 'showThinking':
                    showThinking(message.show);
                    break;
            }
        });

        // Focus input on load
        questionInput.focus();
    </script>
</body>
</html>`;
    }
}