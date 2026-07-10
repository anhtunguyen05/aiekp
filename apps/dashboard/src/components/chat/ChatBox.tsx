import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, ThumbsUp, ThumbsDown } from 'lucide-react';
import { EvidencePanel } from './EvidencePanel';
import { AffectedNode } from '@/lib/api-types'; // Reuse type for sources
import { useSelector } from 'react-redux';
import { RootState } from '@/store';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: AffectedNode[];
  isStreaming?: boolean;
  traceId?: string;
  feedback?: number;
}

const SUGGESTED_QUESTIONS = [
  "Các file nào được import nhiều nhất trong project?",
  "Hãy giải thích kiến trúc tổng thể của codebase này.",
  "Hàm nào có nhiều dependencies nhất?",
  "Nếu tôi thay đổi file main.py, những file nào sẽ bị ảnh hưởng?",
];

export function ChatBox() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const token = useSelector((state: RootState) => state.auth.token);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFeedback = async (messageId: string, traceId: string, score: number) => {
    // Optimistic update
    setMessages(prev => prev.map(m => m.id === messageId ? { ...m, feedback: score } : m));
    
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/feedback/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ trace_id: traceId, score })
      });
    } catch (error) {
      console.error("Failed to submit feedback", error);
    }
  };

  const handleSubmit = async (text: string = input) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const assistantMessageId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      { id: assistantMessageId, role: 'assistant', content: '', isStreaming: true },
    ]);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/reason/stream`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ query: text, session_id: 'default' }),
      });

      if (!response.ok) {
        throw new Error('API Error');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let currentContent = '';
      let sources: AffectedNode[] = [];

      if (reader) {
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          
          // Process SSE lines
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer
          
          for (const line of lines) {
            if (line.startsWith('data: ') && line !== 'data: [DONE]') {
              const data = line.slice(6);
              try {
                const parsed = JSON.parse(data);
                if (parsed.type === 'message' || parsed.type === 'status' || parsed.type === 'error') {
                  currentContent += (currentContent ? '\n' : '') + parsed.content;
                } else if (parsed.type === 'evidence') {
                  sources = parsed.data.map((s: { node_id: string; type: string; label: string; snippet: string }) => ({
                    id: s.node_id,
                    type: s.type,
                    label: s.label,
                    snippet: s.snippet,
                    depth: 1,
                    via_relation: 'CONTEXT'
                  }));
                } else if (parsed.type === 'trace') {
                  const traceId = parsed.trace_id;
                  setMessages((prev) => 
                    prev.map((m) => 
                      m.id === assistantMessageId 
                        ? { ...m, traceId } 
                        : m
                    )
                  );
                }
                
                const nextContent = currentContent;
                const nextSources = sources;
                setMessages((prev) => 
                  prev.map((m) => 
                    m.id === assistantMessageId 
                      ? { ...m, content: nextContent, sources: nextSources } 
                      : m
                  )
                );
              } catch {
                console.error("Failed to parse SSE data", data);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
      setMessages((prev) => 
        prev.map((m) => 
          m.id === assistantMessageId 
            ? { ...m, content: "Sorry, I encountered an error while processing your request.", isStreaming: false } 
            : m
        )
      );
    } finally {
      setIsLoading(false);
      setMessages((prev) => 
        prev.map((m) => 
          m.id === assistantMessageId 
            ? { ...m, isStreaming: false } 
            : m
        )
      );
    }
  };

  return (
    <div className="flex flex-col h-full bg-zinc-950">
      {/* Chat Header */}
      <div className="p-4 border-b border-zinc-800 bg-zinc-900/50 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Sparkles className="text-blue-400" size={20} />
          <h2 className="text-lg font-semibold text-white">AI Knowledge Assistant</h2>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
            <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center mb-4">
              <Bot size={32} className="text-blue-400" />
            </div>
            <h3 className="text-xl font-medium text-zinc-200">How can I help you today?</h3>
            <p className="text-sm text-zinc-400 max-w-md">
              Ask me questions about the codebase structure, dependencies, or impact analysis. I will consult the Knowledge Graph and provide evidence.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl mt-8">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSubmit(q)}
                  className="p-3 text-sm text-left bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 hover:border-zinc-700 transition-colors text-zinc-300 flex items-center gap-2"
                >
                  <Sparkles size={14} className="text-blue-500 shrink-0" />
                  <span>{q}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
                  <Bot size={16} className="text-blue-400" />
                </div>
              )}
              
              <div className={`max-w-[80%] flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`p-3 rounded-xl ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-tr-sm' 
                    : 'bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-tl-sm'
                }`}>
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {msg.content}
                    {msg.isStreaming && (
                      <span className="inline-block w-2 h-4 ml-1 bg-zinc-400 animate-pulse align-middle"></span>
                    )}
                  </div>
                </div>
                
                {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                  <div className="w-full mt-2">
                    <EvidencePanel sources={msg.sources} />
                  </div>
                )}
                
                {msg.role === 'assistant' && !msg.isStreaming && msg.traceId && (
                  <div className="flex gap-2 mt-2 ml-1">
                    <button 
                      onClick={() => handleFeedback(msg.id, msg.traceId!, 1)}
                      className={`p-1.5 rounded-md hover:bg-zinc-800 transition-colors ${msg.feedback === 1 ? 'text-green-400 bg-green-400/10' : 'text-zinc-500'}`}
                      title="Good response"
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button 
                      onClick={() => handleFeedback(msg.id, msg.traceId!, -1)}
                      className={`p-1.5 rounded-md hover:bg-zinc-800 transition-colors ${msg.feedback === -1 ? 'text-red-400 bg-red-400/10' : 'text-zinc-500'}`}
                      title="Bad response"
                    >
                      <ThumbsDown size={14} />
                    </button>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center shrink-0">
                  <User size={16} className="text-zinc-400" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}
          className="relative max-w-4xl mx-auto flex items-end gap-2"
        >
          <div className="relative flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              placeholder="Ask a question about your codebase..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-4 pr-12 py-3 text-sm text-zinc-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none overflow-hidden max-h-32 min-h-[48px]"
              rows={1}
              style={{
                height: 'auto',
              }}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-3 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-xl transition-colors shrink-0 flex items-center justify-center"
          >
            <Send size={18} className={input.trim() && !isLoading ? 'ml-0.5' : ''} />
          </button>
        </form>
        <div className="text-center mt-2">
          <span className="text-[10px] text-zinc-500">AI can make mistakes. Verify critical code structure.</span>
        </div>
      </div>
    </div>
  );
}
