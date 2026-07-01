const vscode = acquireVsCodeApi();

const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

let currentAiMessageDiv = null;
let currentAiRawText = '';

function addMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user' : 'ai'}`;
    
    if (isUser) {
        msgDiv.textContent = text;
    } else {
        msgDiv.innerHTML = marked.parse(text);
    }
    
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return msgDiv;
}

function sendMessage() {
    const text = messageInput.value.trim();
    if (text) {
        addMessage(text, true);
        messageInput.value = '';
        vscode.postMessage({
            command: 'sendMessage',
            text: text
        });
        sendButton.disabled = true;
    }
}

sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Handle messages from the extension
window.addEventListener('message', event => {
    const message = event.data;
    switch (message.command) {
        case 'injectContext':
            messageInput.value = message.text + '\n\n' + messageInput.value;
            break;
        case 'startStream':
            currentAiRawText = '';
            currentAiMessageDiv = addMessage('', false);
            break;
        case 'streamData':
            currentAiRawText += message.text;
            if (currentAiMessageDiv) {
                currentAiMessageDiv.innerHTML = marked.parse(currentAiRawText);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            break;
        case 'streamError':
            if (currentAiMessageDiv) {
                currentAiMessageDiv.innerHTML += `<br><span style="color: red;">Error: ${message.text}</span>`;
            } else {
                addMessage(`Error: ${message.text}`, false);
            }
            sendButton.disabled = false;
            break;
        case 'streamDone':
            sendButton.disabled = false;
            currentAiMessageDiv = null;
            break;
    }
});
