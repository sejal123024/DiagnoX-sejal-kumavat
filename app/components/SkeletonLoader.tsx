'use client';

import React from 'react';

/**
 * Reusable Skeleton Loader for asynchronous data fetching states.
 * Useful for the dashboard while loading ML results.
 */
export const SkeletonLoader = () => {
  return (
    <div className="animate-pulse flex space-x-4 p-4 mb-4 border border-slate-800 rounded-lg bg-slate-900/50">
      <div className="rounded-full bg-slate-700 h-12 w-12 flex-shrink-0"></div>
      <div className="flex-1 space-y-6 py-1 w-full">
        <div className="h-2 bg-slate-700 rounded w-3/4"></div>
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-4">
            <div className="h-2 bg-slate-700 rounded col-span-2"></div>
            <div className="h-2 bg-slate-700 rounded col-span-1"></div>
          </div>
          <div className="h-2 bg-slate-700 rounded w-5/6"></div>
        </div>
      </div>
    </div>
  );
};

export default SkeletonLoader;
