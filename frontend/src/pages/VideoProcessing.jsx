/**
 * Video Processing View
 * Modern UI for processing uploaded videos with real-time progress
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { processingApi } from '../services/api';
import { useToast } from '../components/common/Toast';

const PROCESSING_STEPS = [
  { id: 1, name: 'Downloading Video', description: 'Fetching video from cloud storage' },
  { id: 2, name: 'Loading AI Model', description: 'Initializing YOLO detection model' },
  { id: 3, name: 'Detecting Players', description: 'Running AI detection on frames' },
  { id: 4, name: 'Tracking Objects', description: 'Building movement paths' },
  { id: 5, name: 'Saving Results', description: 'Storing data to database' },
];

export default function VideoProcessing() {
  const { matchId, videoId } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  const [processing, setProcessing] = useState(false);
  const [status, setStatus] = useState(null);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    if (videoId) {
      fetchStatus();
    }
  }, [videoId]);

  useEffect(() => {
    let interval;
    if (polling && videoId) {
      interval = setInterval(fetchStatus, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [polling, videoId]);

  const fetchStatus = async () => {
    try {
      const response = await processingApi.getSimpleStatus(videoId);
      setStatus(response.data);
      
      if (response.data.status === 'completed' || response.data.status === 'failed') {
        setPolling(false);
        setProcessing(false);
      }
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const handleStartProcessing = async () => {
    if (!videoId) {
      addToast('No video ID provided', 'error');
      return;
    }

    setProcessing(true);
    try {
      await processingApi.processSimple(videoId);
      addToast('Video processing started!', 'success');
      setPolling(true);
      fetchStatus();
    } catch (error) {
      console.error('Error starting processing:', error);
      addToast(error.response?.data?.detail || 'Failed to start processing', 'error');
      setProcessing(false);
    }
  };

  const getCurrentStep = () => {
    if (!status?.result?.step) return 0;
    const step = status.result.step.toLowerCase();
    if (step.includes('download')) return 1;
    if (step.includes('loading') || step.includes('model')) return 2;
    if (step.includes('detect') || step.includes('processing frame')) return 3;
    if (step.includes('track')) return 4;
    if (step.includes('saving') || step.includes('database')) return 5;
    return 0;
  };

  const getStatusConfig = (statusValue) => {
    switch (statusValue) {
      case 'pending':
        return { color: 'slate', icon: '⏸️', label: 'Pending', bg: 'bg-slate-500/20', text: 'text-slate-400' };
      case 'queued':
        return { color: 'amber', icon: '📋', label: 'Queued', bg: 'bg-amber-500/20', text: 'text-amber-400' };
      case 'processing':
        return { color: 'blue', icon: '⚙️', label: 'Processing', bg: 'bg-blue-500/20', text: 'text-blue-400' };
      case 'completed':
        return { color: 'emerald', icon: '✅', label: 'Completed', bg: 'bg-emerald-500/20', text: 'text-emerald-400' };
      case 'failed':
        return { color: 'red', icon: '❌', label: 'Failed', bg: 'bg-red-500/20', text: 'text-red-400' };
      default:
        return { color: 'slate', icon: '❓', label: 'Unknown', bg: 'bg-slate-500/20', text: 'text-slate-400' };
    }
  };

  const statusConfig = getStatusConfig(status?.status);
  const currentStep = getCurrentStep();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
            >
              <span className="text-xl">←</span>
              <span className="font-medium">Back</span>
            </button>
            <div className="h-6 w-px bg-slate-700"></div>
            <div>
              <h1 className="text-xl font-bold text-white">Video Processing</h1>
              <p className="text-sm text-slate-400">AI-powered player detection and tracking</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10">
        {/* Status Card */}
        <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 overflow-hidden mb-8">
          {/* Status Header */}
          <div className="p-8 border-b border-slate-700/50">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-3xl">{statusConfig.icon}</span>
                  <h2 className="text-2xl font-bold text-white">{statusConfig.label}</h2>
                </div>
                <p className="text-slate-400 text-sm font-mono">Video ID: {videoId}</p>
              </div>
              
              {status && (
                <div className={`px-6 py-3 rounded-2xl ${statusConfig.bg}`}>
                  <span className={`text-lg font-bold ${statusConfig.text}`}>
                    {status.progress}%
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Progress Section */}
          {status?.progress !== undefined && (
            <div className="p-8 border-b border-slate-700/50">
              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex justify-between text-sm mb-3">
                  <span className="text-slate-400 font-medium">
                    {status.result?.step || 'Waiting to start...'}
                  </span>
                  <span className="text-white font-bold">{status.progress}%</span>
                </div>
                <div className="h-3 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ease-out ${
                      status.status === 'failed' 
                        ? 'bg-red-500' 
                        : status.status === 'completed'
                          ? 'bg-emerald-500'
                          : 'bg-gradient-to-r from-blue-500 via-blue-400 to-cyan-400'
                    }`}
                    style={{ width: `${status.progress}%` }}
                  />
                </div>
              </div>

              {/* Processing Steps */}
              {status.status === 'processing' && (
                <div className="grid grid-cols-5 gap-2">
                  {PROCESSING_STEPS.map((step) => (
                    <div
                      key={step.id}
                      className={`p-3 rounded-xl text-center transition-all duration-300 ${
                        step.id < currentStep
                          ? 'bg-emerald-500/20'
                          : step.id === currentStep
                            ? 'bg-blue-500/30 ring-2 ring-blue-500/50'
                            : 'bg-slate-900/50'
                      }`}
                    >
                      <div className={`text-lg mb-1 ${
                        step.id < currentStep
                          ? 'text-emerald-400'
                          : step.id === currentStep
                            ? 'text-blue-400 animate-pulse'
                            : 'text-slate-600'
                      }`}>
                        {step.id < currentStep ? '✓' : step.id === currentStep ? '●' : '○'}
                      </div>
                      <div className={`text-xs font-medium ${
                        step.id <= currentStep ? 'text-slate-300' : 'text-slate-600'
                      }`}>
                        {step.name}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Results Section */}
          {status?.status === 'completed' && status?.result && (
            <div className="p-8 border-b border-slate-700/50 bg-emerald-500/5">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span>🎉</span> Processing Complete!
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {status.result.tracks_found !== undefined && (
                  <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                    <div className="text-3xl font-bold text-emerald-400">{status.result.tracks_found}</div>
                    <div className="text-sm text-slate-400">Players Tracked</div>
                  </div>
                )}
                {status.result.frames_processed !== undefined && (
                  <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                    <div className="text-3xl font-bold text-blue-400">{status.result.frames_processed}</div>
                    <div className="text-sm text-slate-400">Frames Processed</div>
                  </div>
                )}
                {status.result.total_detections !== undefined && (
                  <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                    <div className="text-3xl font-bold text-purple-400">{status.result.total_detections}</div>
                    <div className="text-sm text-slate-400">Total Detections</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Error Section */}
          {status?.error && (
            <div className="p-8 border-b border-slate-700/50 bg-red-500/5">
              <h3 className="text-lg font-semibold text-red-400 mb-2 flex items-center gap-2">
                <span>⚠️</span> Error Occurred
              </h3>
              <pre className="text-sm text-red-300 bg-red-900/30 p-4 rounded-xl overflow-auto font-mono">
                {status.error}
              </pre>
            </div>
          )}

          {/* Action Buttons */}
          <div className="p-8">
            <div className="flex flex-wrap gap-4">
              {(!status || status.status === 'pending' || status.status === 'failed') && (
                <button
                  onClick={handleStartProcessing}
                  disabled={processing}
                  className={`flex-1 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${
                    processing
                      ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40'
                  }`}
                >
                  {processing ? (
                    <span className="flex items-center justify-center gap-3">
                      <span className="w-5 h-5 border-2 border-slate-500 border-t-transparent rounded-full animate-spin"></span>
                      Starting...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-3">
                      <span>▶️</span> Start Processing
                    </span>
                  )}
                </button>
              )}

              {status?.status === 'completed' && (
                <>
                  <button
                    onClick={() => navigate(`/videos/${videoId}/overlay`)}
                    className="flex-1 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-xl font-semibold text-lg shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 transition-all duration-300"
                  >
                    <span className="flex items-center justify-center gap-3">
                      <span>🎯</span> Motion Tracking View
                    </span>
                  </button>
                  <button
                    onClick={() => navigate(`/videos/${videoId}/pitch`)}
                    className="flex-1 px-8 py-4 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-500 hover:to-green-500 text-white rounded-xl font-semibold text-lg shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all duration-300"
                  >
                    <span className="flex items-center justify-center gap-3">
                      <span>🏟️</span> View 2D Pitch
                    </span>
                  </button>
                  <button
                    onClick={() => navigate(`/matches/${matchId}`)}
                    className="flex-1 px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-semibold text-lg transition-all duration-300"
                  >
                    <span className="flex items-center justify-center gap-3">
                      <span>📊</span> Match Analytics
                    </span>
                  </button>
                </>
              )}

              <button
                onClick={fetchStatus}
                className="px-6 py-4 bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-xl font-medium transition-all duration-300"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-slate-800/30 backdrop-blur rounded-2xl border border-slate-700/50 p-8">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
            <span className="text-2xl">🤖</span>
            How AI Processing Works
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: '📹', title: 'Frame Extraction', desc: 'Key frames are extracted from the video at optimal intervals for analysis' },
              { icon: '🎯', title: 'YOLO Detection', desc: 'State-of-the-art AI model detects players, ball, and referees in each frame' },
              { icon: '🔗', title: 'Object Tracking', desc: 'Each detected object is tracked across frames with unique IDs' },
              { icon: '📍', title: 'Position Mapping', desc: 'Player positions are mapped to real pitch coordinates for visualization' },
            ].map((item, i) => (
              <div key={i} className="flex gap-4 p-4 bg-slate-900/30 rounded-xl">
                <div className="text-3xl">{item.icon}</div>
                <div>
                  <h4 className="font-semibold text-white mb-1">{item.title}</h4>
                  <p className="text-sm text-slate-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
