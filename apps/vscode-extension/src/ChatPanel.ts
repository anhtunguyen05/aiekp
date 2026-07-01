import * as vscode from 'vscode';
import { DocumentContext, ContextManager } from './ContextManager';
import { ApiClient } from './apiClient';

export class ChatPanel {
    public static currentPanel: ChatPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (ChatPanel.currentPanel) {
            ChatPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'aiekpChat',
            'AIEKP Chat',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this._update();

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'sendMessage':
                        this._handleSendMessage(message.text);
                        return;
                }
            },
            null,
            this._disposables
        );
    }

    public sendContext(context: DocumentContext) {
        const formattedContext = ContextManager.formatContextForPrompt(context);
        this._panel.webview.postMessage({ command: 'injectContext', text: formattedContext });
    }

    private _handleSendMessage(text: string) {
        this._panel.webview.postMessage({ command: 'startStream' });
        
        ApiClient.streamReasoning(
            text,
            (chunk) => {
                this._panel.webview.postMessage({ command: 'streamData', text: chunk });
            },
            (error) => {
                vscode.window.showErrorMessage(`AIEKP Error: ${error}`);
                this._panel.webview.postMessage({ command: 'streamError', text: error });
            },
            () => {
                this._panel.webview.postMessage({ command: 'streamDone' });
            }
        );
    }

    public dispose() {
        ChatPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.css'));

        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="${styleUri}" rel="stylesheet">
                <title>AIEKP Chat</title>
                <!-- Include marked for markdown parsing -->
                <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            </head>
            <body>
                <div id="chat-container">
                    <div id="messages"></div>
                </div>
                <div id="input-container">
                    <textarea id="message-input" rows="3" placeholder="Ask AIEKP a question..."></textarea>
                    <button id="send-button">Send</button>
                </div>
                <script src="${scriptUri}"></script>
            </body>
            </html>`;
    }
}
