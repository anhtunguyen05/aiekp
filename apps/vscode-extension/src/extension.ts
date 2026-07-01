import * as vscode from 'vscode';
import { ChatPanel } from './ChatPanel';
import { ContextManager } from './ContextManager';

export function activate(context: vscode.ExtensionContext) {
    console.log('AIEKP VSCode Extension is now active!');

    // Command to open the chat panel
    const startChatCommand = vscode.commands.registerCommand('aiekp.startChat', () => {
        ChatPanel.createOrShow(context.extensionUri);
    });

    // Command to ask about the current selection or file
    const askSelectionCommand = vscode.commands.registerCommand('aiekp.askAboutSelection', () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const documentContext = ContextManager.getDocumentContext(editor);
            ChatPanel.createOrShow(context.extensionUri);
            // Send the context to the chat panel to pre-fill or automatically send
            ChatPanel.currentPanel?.sendContext(documentContext);
        } else {
            vscode.window.showInformationMessage('No active editor found to extract context.');
        }
    });

    context.subscriptions.push(startChatCommand, askSelectionCommand);
}

export function deactivate() {}
