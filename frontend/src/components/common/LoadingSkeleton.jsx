/**
 * Loading Skeleton Component
 * Shows placeholder content while data loads
 */
import React from 'react';

export function MatchListSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="h-6 bg-slate-200 rounded w-48 mb-4"></div>
              <div className="h-4 bg-slate-200 rounded w-32"></div>
            </div>
            <div className="h-10 bg-slate-200 rounded w-24"></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function MetricsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
          <div className="h-4 bg-slate-200 rounded w-24 mb-4"></div>
          <div className="h-8 bg-slate-200 rounded w-32 mb-2"></div>
          <div className="h-3 bg-slate-200 rounded w-16"></div>
        </div>
      ))}
    </div>
  );
}

export function PlayerListSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <div className="animate-pulse">
        <div className="h-12 bg-slate-100 border-b"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center justify-between p-4 border-b border-slate-100">
            <div className="flex items-center space-x-4 flex-1">
              <div className="h-10 w-10 bg-slate-200 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 bg-slate-200 rounded w-32 mb-2"></div>
                <div className="h-3 bg-slate-200 rounded w-24"></div>
              </div>
            </div>
            <div className="h-6 bg-slate-200 rounded w-20"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ReplaySkeleton() {
  return (
    <div className="space-y-4">
      <div className="bg-slate-900 rounded-xl aspect-video animate-pulse"></div>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
          <div className="h-4 bg-slate-200 rounded w-24 mb-4"></div>
          <div className="h-8 bg-slate-200 rounded w-32"></div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
          <div className="h-4 bg-slate-200 rounded w-24 mb-4"></div>
          <div className="h-8 bg-slate-200 rounded w-32"></div>
        </div>
      </div>
    </div>
  );
}

export default function LoadingSkeleton({ variant = 'matchList' }) {
  const skeletons = {
    matchList: MatchListSkeleton,
    metrics: MetricsSkeleton,
    playerList: PlayerListSkeleton,
    replay: ReplaySkeleton,
  };

  const SkeletonComponent = skeletons[variant] || MatchListSkeleton;
  return <SkeletonComponent />;
}
