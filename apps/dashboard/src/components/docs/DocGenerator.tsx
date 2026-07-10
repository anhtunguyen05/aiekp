'use client';

import React, { useState } from 'react';
import { FileText, Download, Copy, Play, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { DocType } from '@/lib/api-types';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';

const DOC_TYPES: { type: DocType; label: string; description: string }[] = [
  {
    type: 'architecture_overview',
    label: 'Architecture Overview',
    description: 'High-level structure, core layers, and inferred design patterns.',
  },
  {
    type: 'onboarding_guide',
    label: 'Onboarding Guide',
    description: 'Entry points and recommended reading order for new developers.',
  },
  {
    type: 'key_entry_points',
    label: 'Key Entry Points',
    description: 'Hotspots and highly connected files in the codebase.',
  },
  {
    type: 'module_dependencies',
    label: 'Module Dependencies',
    description: 'File-to-file relationships with Mermaid diagram.',
  },
];

export function DocGenerator() {
  const [selectedType, setSelectedType] = useState<DocType>('architecture_overview');
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusText, setStatusText] = useState<string>('');
  const [generatedDoc, setGeneratedDoc] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const token = useSelector((state: RootState) => state.auth.token);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGeneratedDoc('');
    setError(null);
    setStatusText('Initializing...');

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs/generate`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ doc_type: selectedType, session_id: 'doc-gen' }),
      });

      if (!response.ok) {
        throw new Error('Failed to connect to API');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (!reader) throw new Error('No reader available');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          if (part.startsWith('data: ')) {
            const dataStr = part.replace('data: ', '').trim();
            if (dataStr === '[DONE]') {
              setIsGenerating(false);
              setStatusText('Completed.');
              return;
            }

            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'status') {
                setStatusText(data.content);
              } else if (data.type === 'message') {
                setGeneratedDoc((prev) => prev + data.content);
              } else if (data.type === 'error') {
                setError(data.content);
                setIsGenerating(false);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE json:', e, dataStr);
            }
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'An unknown error occurred');
      } else {
        setError('An unknown error occurred');
      }
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!generatedDoc) return;
    const blob = new Blob([generatedDoc], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedType}-${new Date().toISOString().split('T')[0]}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCopy = async () => {
    if (!generatedDoc) return;
    await navigator.clipboard.writeText(generatedDoc);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full bg-zinc-950 text-zinc-100 overflow-hidden">
      {/* Header */}
      <header className="flex items-center gap-4 px-6 py-4 border-b border-white/10 bg-zinc-900/60 backdrop-blur-md shrink-0">
        <div className="p-2.5 rounded-xl bg-blue-500/15 text-blue-400">
          <FileText size={22} />
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-tight">Onboarding Doc Generator</h1>
          <p className="text-xs text-zinc-500">
            Automatically generate grounded architecture and onboarding documents from the Knowledge Graph.
          </p>
        </div>
      </header>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar: Controls */}
        <aside className="w-80 shrink-0 border-r border-white/10 overflow-y-auto p-5 bg-zinc-900/30 flex flex-col gap-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-3">
              Document Type
            </p>
            <div className="space-y-2">
              {DOC_TYPES.map((dt) => (
                <button
                  key={dt.type}
                  onClick={() => !isGenerating && setSelectedType(dt.type)}
                  disabled={isGenerating}
                  className={`w-full text-left p-3 rounded-xl border transition-all ${
                    selectedType === dt.type
                      ? 'border-blue-500/50 bg-blue-500/10'
                      : 'border-white/5 bg-zinc-800/40 hover:bg-zinc-800/80'
                  } ${isGenerating ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <p className={`text-sm font-medium ${selectedType === dt.type ? 'text-blue-400' : 'text-zinc-300'}`}>
                    {dt.label}
                  </p>
                  <p className="text-xs text-zinc-500 mt-1">{dt.description}</p>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-500 transition-colors font-medium text-sm"
          >
            {isGenerating ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Play size={16} fill="currentColor" />
                Generate Document
              </>
            )}
          </button>
        </aside>

        {/* Right Pane: Preview */}
        <main className="flex-1 flex flex-col overflow-hidden bg-zinc-950">
          {/* Action bar */}
          <div className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-zinc-900/20 shrink-0">
            <div className="flex items-center gap-3">
              {isGenerating && (
                <span className="flex items-center gap-2 text-xs text-blue-400 animate-pulse">
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                  {statusText}
                </span>
              )}
              {!isGenerating && generatedDoc && (
                <span className="text-xs text-emerald-400 flex items-center gap-1">
                  <CheckCircle size={14} /> {statusText}
                </span>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                disabled={!generatedDoc || isGenerating}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 hover:bg-white/5 text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {copied ? <CheckCircle size={14} className="text-emerald-400" /> : <Copy size={14} />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
              <button
                onClick={handleDownload}
                disabled={!generatedDoc || isGenerating}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 hover:bg-white/5 text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Download size={14} /> Download .md
              </button>
            </div>
          </div>

          {/* Markdown Content */}
          <div className="flex-1 overflow-y-auto p-8">
            {error && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 mb-6 text-sm">
                <strong>Error:</strong> {error}
              </div>
            )}

            {!generatedDoc && !isGenerating && !error && (
              <div className="h-full flex flex-col items-center justify-center text-zinc-500 opacity-60">
                <FileText size={48} strokeWidth={1} className="mb-4" />
                <p>Select a document type and click Generate.</p>
              </div>
            )}

            <article className="prose prose-invert prose-blue max-w-4xl mx-auto">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {generatedDoc}
              </ReactMarkdown>
            </article>
          </div>
        </main>
      </div>
    </div>
  );
}
