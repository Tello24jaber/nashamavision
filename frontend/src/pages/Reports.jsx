/**
 * Reports View
 * Generate and export analytics reports
 */
import React from 'react';
import Breadcrumbs from '../components/layout/Breadcrumbs';

export default function Reports() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Breadcrumbs items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Reports' }
        ]} />

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Reports</h1>
          <p className="text-slate-500 mt-1">
            Generate comprehensive analytics reports
          </p>
        </div>

        {/* Coming Soon Card */}
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <div className="text-6xl mb-6">📊</div>
          <h2 className="text-2xl font-bold text-slate-900 mb-4">Reports Coming Soon</h2>
          <p className="text-slate-600 max-w-md mx-auto mb-8">
            Generate detailed PDF and Excel reports with match analytics, player statistics, 
            and tactical insights. This feature is currently under development.
          </p>
          
          <div className="space-y-3 text-left max-w-md mx-auto mb-8">
            <div className="flex items-center space-x-3 text-slate-700">
              <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span>Match summary reports with key metrics</span>
            </div>
            <div className="flex items-center space-x-3 text-slate-700">
              <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span>Player performance evaluations</span>
            </div>
            <div className="flex items-center space-x-3 text-slate-700">
              <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span>Tactical analysis breakdowns</span>
            </div>
            <div className="flex items-center space-x-3 text-slate-700">
              <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span>Export to PDF, Excel, and CSV formats</span>
            </div>
          </div>

          <div className="inline-flex items-center space-x-2 text-sm text-slate-500">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Expected release: Q2 2025</span>
          </div>
        </div>
      </div>
    </div>
  );
}
