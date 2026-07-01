import * as vscode from 'vscode';

export interface DocumentContext {
    fileName: string;
    languageId: string;
    content: string;
    selection?: string;
}

export class ContextManager {
    public static getDocumentContext(editor: vscode.TextEditor): DocumentContext {
        const document = editor.document;
        const selection = editor.selection;
        
        let selectionText = '';
        if (!selection.isEmpty) {
            selectionText = document.getText(selection);
        }

        return {
            fileName: document.fileName,
            languageId: document.languageId,
            content: document.getText(),
            selection: selectionText ? selectionText : undefined
        };
    }

    public static formatContextForPrompt(context: DocumentContext): string {
        let prompt = `File: ${context.fileName}\nLanguage: ${context.languageId}\n`;
        
        if (context.selection) {
            prompt += `\nSelected Code:\n\`\`\`${context.languageId}\n${context.selection}\n\`\`\`\n`;
        } else {
            prompt += `\nFile Content:\n\`\`\`${context.languageId}\n${context.content}\n\`\`\`\n`;
        }
        
        return prompt;
    }
}
