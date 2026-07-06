'use client';

import React from 'react';
import { Search } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { setSearchQuery, setSelectedNodeId } from '@/store/graphSlice';
import { RootState } from '@/store';


export function SearchBar() {
  const dispatch = useDispatch();
  const query = useSelector((state: RootState) => state.graph.searchQuery);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(setSearchQuery(e.target.value));
    if (e.target.value === '') {
      dispatch(setSelectedNodeId(null));
    }
  };

  return (
    <div className="relative">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search className="h-4 w-4 text-zinc-400" />
      </div>
      <input
        type="text"
        className="block w-full pl-10 pr-3 py-2 border border-zinc-800 rounded-md leading-5 bg-zinc-900 text-zinc-300 placeholder-zinc-500 focus:outline-none focus:bg-zinc-800 focus:border-zinc-700 sm:text-sm"
        placeholder="Search nodes by name..."
        value={query}
        onChange={handleSearch}
      />
    </div>
  );
}
