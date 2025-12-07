/**
 * Video Upload View
 * Modern dark theme with drag-drop and match metadata
 */
import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadApi } from '../services/api';
import { useToast } from '../components/common/Toast';

export default function VideoUpload() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [formData, setFormData] = useState({
    home_team: '',
    away_team: '',
    match_date: '',
    competition: '',
    venue: '',
  });

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile);
    } else {
      addToast('Please upload a video file', 'error');
    }
  }, [addToast]);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      addToast('Please select a video file', 'error');
      return;
    }

    if (!formData.home_team || !formData.away_team) {
      addToast('Please enter team names', 'error');
      return;
    }

    setUploading(true);
    
    try {
      const uploadFormData = new FormData();
      uploadFormData.append('file', file);
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          uploadFormData.append(key, formData[key]);
        }
      });

      const response = await uploadApi.uploadVideo(uploadFormData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      addToast('Video uploaded successfully! 🎉', 'success');
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (response.data.match_id && response.data.video_id) {
        navigate(`/matches/${response.data.match_id}/videos/${response.data.video_id}/process`);
      } else if (response.data.match_id) {
        navigate(`/matches/${response.data.match_id}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      let errorMessage = 'Upload failed';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map(e => e.msg).join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      addToast(errorMessage, 'error');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -right-20 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 -left-20 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6"
          >
            <span className="text-lg">←</span>
            <span>Back</span>
          </button>
          
          <div className="flex items-center gap-4 mb-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
              <span className="text-2xl">📤</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Upload Match Video</h1>
              <p className="text-slate-400 mt-1">
                Upload a video to start AI-powered analysis
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload Area */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700/50 p-8">
            <label className="block text-sm font-medium text-slate-300 mb-4">
              Match Video File
            </label>
            
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
                isDragging
                  ? 'border-blue-500 bg-blue-500/10'
                  : file
                  ? 'border-emerald-500 bg-emerald-500/10'
                  : 'border-slate-600 hover:border-slate-500 bg-slate-900/30'
              }`}
            >
              {file ? (
                <div className="space-y-4">
                  <div className="w-16 h-16 mx-auto bg-emerald-500/20 rounded-full flex items-center justify-center">
                    <span className="text-3xl">✓</span>
                  </div>
                  <div>
                    <p className="text-lg font-medium text-white">{file.name}</p>
                    <p className="text-sm text-slate-400 mt-1">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    className="text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
                  >
                    Change File
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-16 h-16 mx-auto bg-slate-700/50 rounded-full flex items-center justify-center">
                    <span className="text-3xl">📹</span>
                  </div>
                  <div>
                    <p className="text-lg font-medium text-white">
                      Drag and drop your video here
                    </p>
                    <p className="text-sm text-slate-500 mt-1">
                      Supports MP4, MOV, AVI, MKV
                    </p>
                  </div>
                  <div className="text-slate-500 text-sm">or</div>
                  <label className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-xl font-medium cursor-pointer transition-all duration-300 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40">
                    <input
                      type="file"
                      accept="video/*"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <span>📁</span>
                    <span>Browse Files</span>
                  </label>
                </div>
              )}
            </div>

            {/* Upload Progress */}
            {uploading && (
              <div className="mt-6">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Uploading to cloud storage...</span>
                  <span className="text-blue-400 font-medium">{uploadProgress}%</span>
                </div>
                <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Match Details */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700/50 p-8 space-y-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span>⚽</span> Match Details
            </h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Home Team <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.home_team}
                  onChange={(e) => setFormData({ ...formData, home_team: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                  placeholder="e.g., Manchester United"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Away Team <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.away_team}
                  onChange={(e) => setFormData({ ...formData, away_team: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                  placeholder="e.g., Liverpool"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Match Date
                </label>
                <input
                  type="date"
                  value={formData.match_date}
                  onChange={(e) => setFormData({ ...formData, match_date: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Competition
                </label>
                <input
                  type="text"
                  value={formData.competition}
                  onChange={(e) => setFormData({ ...formData, competition: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                  placeholder="e.g., Premier League"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Venue
              </label>
              <input
                type="text"
                value={formData.venue}
                onChange={(e) => setFormData({ ...formData, venue: e.target.value })}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all outline-none"
                placeholder="e.g., Old Trafford"
              />
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-slate-800 text-slate-300 border border-slate-700 rounded-xl hover:bg-slate-700 transition-all font-medium"
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!file || uploading}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-xl font-medium shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
            >
              {uploading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  Uploading... {uploadProgress}%
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <span>🚀</span>
                  Upload & Process
                </span>
              )}
            </button>
          </div>
        </form>

        {/* Info Section */}
        <div className="mt-10 bg-slate-800/30 backdrop-blur-sm rounded-2xl border border-slate-700/50 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span>💡</span> Tips for Best Results
          </h3>
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { icon: '🎥', title: 'Video Quality', desc: 'HD resolution (720p+) recommended for accurate detection' },
              { icon: '📐', title: 'Camera Angle', desc: 'Wide-angle tactical view provides best coverage' },
              { icon: '⏱️', title: 'Duration', desc: 'Full match or highlight clips both supported' },
            ].map((tip, i) => (
              <div key={i} className="flex gap-3 p-4 bg-slate-900/30 rounded-xl">
                <div className="text-2xl">{tip.icon}</div>
                <div>
                  <p className="font-medium text-white text-sm">{tip.title}</p>
                  <p className="text-xs text-slate-400 mt-1">{tip.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
