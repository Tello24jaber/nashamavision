/**
 * Sidebar Navigation Component
 * Secondary navigation for match-specific actions
 */
import React from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';

export default function Sidebar({ matchId }) {
  const location = useLocation();
  const params = useParams();
  const currentMatchId = matchId || params.matchId;

  if (!currentMatchId) return null;

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-screen p-4">
      <div className="space-y-1">
        <SidebarSection title="Overview">
          <SidebarLink
            to={`/matches/${currentMatchId}`}
            active={location.pathname === `/matches/${currentMatchId}`}
            icon="📊"
          >
            Match Details
          </SidebarLink>
          <SidebarLink
            to={`/matches/${currentMatchId}/players`}
            active={location.pathname.includes('/players')}
            icon="👥"
          >
            Players
          </SidebarLink>
        </SidebarSection>

        <SidebarSection title="Analytics">
          <SidebarLink
            to={`/matches/${currentMatchId}/heatmap`}
            active={location.pathname.includes('/heatmap')}
            icon="🎯"
          >
            Heatmaps
          </SidebarLink>
          <SidebarLink
            to={`/matches/${currentMatchId}/tactics`}
            active={location.pathname.includes('/tactics')}
            icon="🎖️"
          >
            Tactical
          </SidebarLink>
          <SidebarLink
            to={`/matches/${currentMatchId}/xt`}
            active={location.pathname.includes('/xt')}
            icon="⚡"
          >
            xT Analysis
          </SidebarLink>
          <SidebarLink
            to={`/matches/${currentMatchId}/events`}
            active={location.pathname.includes('/events')}
            icon="📍"
          >
            Events
          </SidebarLink>
        </SidebarSection>

        <SidebarSection title="Replay">
          <SidebarLink
            to={`/matches/${currentMatchId}/replay`}
            active={location.pathname.includes('/replay')}
            icon="▶️"
          >
            Match Replay
          </SidebarLink>
        </SidebarSection>
      </div>
    </aside>
  );
}

function SidebarSection({ title, children }) {
  return (
    <div className="mb-6">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-3">
        {title}
      </h3>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

function SidebarLink({ to, active, icon, children }) {
  return (
    <Link
      to={to}
      className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
        active
          ? 'bg-blue-50 text-blue-600 font-medium'
          : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900'
      }`}
    >
      <span className="text-lg">{icon}</span>
      <span className="text-sm">{children}</span>
    </Link>
  );
}
