/**
 * Settings View
 * Application settings and preferences
 */
import React, { useState } from 'react';
import Breadcrumbs from '../components/layout/Breadcrumbs';
import { useToast } from '../components/common/Toast';

export default function Settings() {
  const { addToast } = useToast();
  const [settings, setSettings] = useState({
    theme: 'light',
    notifications: true,
    autoProcess: true,
    defaultView: 'dashboard',
    heatmapOpacity: 0.7,
    videoQuality: 'high',
  });

  const handleSave = () => {
    // Save settings logic here
    addToast('Settings saved successfully', 'success');
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Breadcrumbs items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Settings' }
        ]} />

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
          <p className="text-slate-500 mt-1">
            Manage your application preferences
          </p>
        </div>

        <div className="space-y-6">
          {/* Appearance */}
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Appearance</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Theme
                </label>
                <select
                  value={settings.theme}
                  onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark (Coming Soon)</option>
                  <option value="auto">Auto (Coming Soon)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Default View
                </label>
                <select
                  value={settings.defaultView}
                  onChange={(e) => setSettings({ ...settings, defaultView: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
                >
                  <option value="dashboard">Dashboard</option>
                  <option value="matches">Matches List</option>
                  <option value="assistant">AI Assistant</option>
                </select>
              </div>
            </div>
          </div>

          {/* Processing */}
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Processing</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">Auto-process uploads</p>
                  <p className="text-sm text-slate-500">Automatically start processing after upload</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.autoProcess}
                    onChange={(e) => setSettings({ ...settings, autoProcess: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Video Quality
                </label>
                <select
                  value={settings.videoQuality}
                  onChange={(e) => setSettings({ ...settings, videoQuality: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
                >
                  <option value="high">High (slower processing)</option>
                  <option value="medium">Medium (recommended)</option>
                  <option value="low">Low (faster processing)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Notifications</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">Enable notifications</p>
                <p className="text-sm text-slate-500">Get notified about processing status</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications}
                  onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-100 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>

          {/* Visualization */}
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Visualization</h2>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Heatmap Opacity: {Math.round(settings.heatmapOpacity * 100)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={settings.heatmapOpacity}
                onChange={(e) => setSettings({ ...settings, heatmapOpacity: parseFloat(e.target.value) })}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end space-x-4">
            <button
              onClick={handleSave}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
