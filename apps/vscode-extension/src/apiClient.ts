import * as vscode from 'vscode';
import * as http from 'http';
import * as https from 'https';
import { URL } from 'url';

export class ApiClient {
    public static async streamReasoning(
        prompt: string, 
        onData: (chunk: string) => void, 
        onError: (error: string) => void,
        onDone: () => void
    ) {
        const config = vscode.workspace.getConfiguration('aiekp');
        const apiUrl = config.get<string>('apiUrl', 'http://127.0.0.1:8000');
        const apiKey = config.get<string>('apiKey', '');

        if (!apiKey) {
            onError('API Key is missing. Please configure aiekp.apiKey in settings.');
            onDone();
            return;
        }

        const endpoint = `${apiUrl}/reason/stream`;
        const payload = JSON.stringify({
            query: prompt,
            session_id: "vscode-ext-" + Math.random().toString(36).substring(7)
        });

        const parsedUrl = new URL(endpoint);
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey,
                'Content-Length': Buffer.byteLength(payload)
            }
        };

        const client = parsedUrl.protocol === 'https:' ? https : http;

        const req = client.request(parsedUrl, options, (res) => {
            if (res.statusCode !== 200) {
                onError(`Server returned status code ${res.statusCode}`);
                onDone();
                return;
            }

            res.setEncoding('utf8');
            let buffer = '';
            res.on('data', (chunk: string) => {
                buffer += chunk;
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // keep the incomplete line in the buffer
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6).trim();
                        if (data === '[DONE]') {
                            onDone();
                        } else if (data.length > 0) {
                            try {
                                const parsed = JSON.parse(data);
                                if (parsed.content) {
                                    onData(parsed.content);
                                }
                            } catch (e) {
                                // Ignore parse errors for incomplete JSON
                            }
                        }
                    }
                }
            });

            res.on('end', () => {
                onDone();
            });
        });

        req.on('error', (e) => {
            onError(`Request failed: ${e.message}`);
            onDone();
        });

        req.write(payload);
        req.end();
    }
}
