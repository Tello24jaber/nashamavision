/**
 * Top Navigation Bar Component
 * Modern dark theme with glass morphism effect
 */
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function TopNav() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 transform group-hover:scale-105 transition-transform">
              <span className="text-white text-xl">⚽</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors">Nashama Vision</h1>
              <p className="text-xs text-slate-500">Football Analytics</p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            <NavLink to="/" active={isActive('/')}>
              <span className="mr-1.5">🏠</span> Dashboard
            </NavLink>
            <NavLink to="/matches" active={isActive('/matches')}>
              <span className="mr-1.5">⚽</span> Matches
            </NavLink>
            <NavLink to="/upload" active={isActive('/upload')}>
              <span className="mr-1.5">📤</span> Upload
            </NavLink>
            <NavLink to="/assistant" active={isActive('/assistant')} highlight>
              <span className="mr-1.5">🤖</span> AI Assistant
            </NavLink>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-2">
            {/* Settings Button */}
            <Link
              to="/settings"
              className="hidden md:flex p-2.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Settings"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </Link>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              {mobileMenuOpen ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-800">
            <div className="flex flex-col space-y-2">
              <MobileNavLink to="/" active={isActive('/')} onClick={() => setMobileMenuOpen(false)}>
                🏠 Dashboard
              </MobileNavLink>
              <MobileNavLink to="/matches" active={isActive('/matches')} onClick={() => setMobileMenuOpen(false)}>
                ⚽ Matches
              </MobileNavLink>
              <MobileNavLink to="/upload" active={isActive('/upload')} onClick={() => setMobileMenuOpen(false)}>
                📤 Upload
              </MobileNavLink>
              <MobileNavLink to="/assistant" active={isActive('/assistant')} onClick={() => setMobileMenuOpen(false)}>
                🤖 AI Assistant
              </MobileNavLink>
              <MobileNavLink to="/settings" active={isActive('/settings')} onClick={() => setMobileMenuOpen(false)}>
                ⚙️ Settings
              </MobileNavLink>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

function NavLink({ to, active, highlight, children }) {
  return (
    <Link
      to={to}
      className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
        active
          ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
          : highlight
            ? 'text-purple-400 hover:text-purple-300 hover:bg-purple-500/10'
            : 'text-slate-400 hover:text-white hover:bg-slate-800'
      }`}
    >
      {children}
    </Link>
  );
}

function MobileNavLink({ to, active, onClick, children }) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className={`px-4 py-3 rounded-lg font-medium transition-colors ${
        active
          ? 'bg-blue-500/20 text-blue-400'
          : 'text-slate-400 hover:text-white hover:bg-slate-800'
      }`}
    >
      {children}
    </Link>
  );
}
