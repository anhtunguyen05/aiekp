'use client';

import React from 'react';
import { ChatBox } from '@/components/chat/ChatBox';
import { KnowledgeGraph } from '@/components/graph/KnowledgeGraph';
import { Provider } from 'react-redux';
import { store } from '@/store';

export default function ChatPage() {
  return (
    <Provider store={store}>
      <div className="flex h-full w-full">
        {/* Left Column: Chat Interface */}
        <div className="w-[60%] flex flex-col border-r border-zinc-800 bg-zinc-950">
          <ChatBox />
        </div>
        
        {/* Right Column: Mini Graph */}
        <div className="w-[40%] flex flex-col bg-zinc-900 relative">
          <KnowledgeGraph />
        </div>
      </div>
    </Provider>
  );
}
