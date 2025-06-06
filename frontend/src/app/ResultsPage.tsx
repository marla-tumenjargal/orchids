import React, { useState, useEffect } from 'react';
import { 
  Eye, Code, Download, Copy, ArrowLeft, ExternalLink, 
  Cloud, Monitor, Zap, Clock, FileText, Image, 
  Smartphone, Tablet, Info, CheckCircle 
} from 'lucide-react';

interface CloneResult {
  original_url: string;
  files: {
    [filename: string]: {
      content: string;
      size: number;
      type: string;
      description: string;
      enhanced_with_browserbase?: boolean;
    };
  };
  clone_metadata: {
    title: string;
    description: string;
    generation_timestamp: string;
    ai_model_used: string;
    browserbase_used?: boolean;
    scraping_method?: string;
    responsive_design_detected?: boolean;
    frameworks_detected?: string[];
    performance_score?: number;
    task_id?: string;
    processing_time_seconds?: number;
    browserbase_session_used?: boolean;
    scraping_method_final?: string;
    total_progress_steps?: number;
    user_preferences_applied?: boolean;
    total_elements_analyzed?: number;
  };
  browserbase_insights?: {
    browserbase_used: boolean;
    scraping_method: string;
    screenshots_captured: string[];
    performance_metrics: {
      loadTime?: number;
      firstPaint?: number;
      firstContentfulPaint?: number;
      resourceCount?: number;
      totalResourceSize?: number;
    };
    responsive_tested: boolean;
    frameworks_detected: string[];
    total_elements: number;
    computed_colors_count: number;
    layout_containers_analyzed: number;
  };
}

interface ResultsPageProps {
  result: CloneResult;
  taskId: string;
  onBack: () => void;
}

export default function ResultsPage({ result, taskId, onBack }: ResultsPageProps) {
  const [viewMode, setViewMode] = useState<'preview' | 'code' | 'insights'>('preview');
  const [selectedFile, setSelectedFile] = useState<string>('index.html');
  const [copiedFile, setCopiedFile] = useState<string | null>(null);
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [showToast, setShowToast] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string>('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  // Safe access to result properties with defaults
  const safeResult = {
    original_url: result?.original_url || 'Unknown URL',
    files: result?.files || {},
    clone_metadata: {
      title: result?.clone_metadata?.title || 'Cloned Website',
      description: result?.clone_metadata?.description || 'AI-generated website clone',
      generation_timestamp: result?.clone_metadata?.generation_timestamp || new Date().toISOString(),
      ai_model_used: result?.clone_metadata?.ai_model_used || 'AI Model',
      browserbase_used: result?.clone_metadata?.browserbase_used || false,
      scraping_method: result?.clone_metadata?.scraping_method || 'unknown',
      responsive_design_detected: result?.clone_metadata?.responsive_design_detected || false,
      frameworks_detected: result?.clone_metadata?.frameworks_detected || [],
      performance_score: result?.clone_metadata?.performance_score || 0,
      processing_time_seconds: result?.clone_metadata?.processing_time_seconds || 0,
      total_elements_analyzed: result?.clone_metadata?.total_elements_analyzed || 0
    },
    browserbase_insights: result?.browserbase_insights || null
  };

  // Show toast message
  const showToastMessage = (message: string) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Prepare preview HTML by combining all files
  useEffect(() => {
    if (safeResult.files && Object.keys(safeResult.files).length > 0) {
      const htmlContent = safeResult.files['index.html']?.content || '';
      const cssContent = safeResult.files['styles.css']?.content || '';
      const jsContent = safeResult.files['script.js']?.content || '';

      if (htmlContent) {
        // Inject CSS and JS into HTML for preview
        const previewContent = htmlContent
          .replace('</head>', `<style>${cssContent}</style>\n</head>`)
          .replace('</body>', `<script>${jsContent}</script>\n</body>`);

        setPreviewHtml(previewContent);
      } else {
        setPreviewHtml('<html><body><h1>No HTML content available</h1></body></html>');
      }
    }
  }, [safeResult.files]);

  // Set default selected file if index.html doesn't exist
  useEffect(() => {
    const availableFiles = Object.keys(safeResult.files);
    if (availableFiles.length > 0 && !availableFiles.includes('index.html')) {
      setSelectedFile(availableFiles[0]);
    }
  }, [safeResult.files]);

  const downloadFiles = async (format: 'zip' | 'individual' = 'zip') => {
    try {
      if (format === 'zip') {
        showToastMessage('Preparing download...');
        
        const response = await fetch(`${API_URL}/download/${taskId}?format=zip`);
        
        if (!response.ok) {
          throw new Error('Failed to download files');
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        
        // Enhanced filename with method indicator
        const method = safeResult.clone_metadata.browserbase_used ? 'browserbase' : 'local';
        link.download = `website_clone_${taskId.slice(0, 8)}_${method}.zip`;
        
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);
        
        showToastMessage('Download started successfully!');
      }
    } catch (error) {
      console.error('Error downloading files:', error);
      showToastMessage('Failed to download files. Please try again.');
    }
  };

  const copyToClipboard = async (content: string, filename: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedFile(filename);
      setTimeout(() => setCopiedFile(null), 2000);
      showToastMessage(`${filename} copied to clipboard!`);
    } catch (error) {
      console.error('Failed to copy:', error);
      showToastMessage('Failed to copy to clipboard');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename: string) => {
    if (filename.endsWith('.html')) return '📄';
    if (filename.endsWith('.css')) return '🎨';
    if (filename.endsWith('.js')) return '⚡';
    if (filename.endsWith('.md')) return '📝';
    return '📋';
  };

  const getLanguage = (filename: string) => {
    if (filename.endsWith('.html')) return 'html';
    if (filename.endsWith('.css')) return 'css';
    if (filename.endsWith('.js')) return 'javascript';
    return 'markdown';
  };

  const getScrapingMethodDisplay = () => {
    const method = safeResult.clone_metadata.scraping_method;
    if (method === 'browserbase') {
      return {
        icon: <Cloud className="w-4 h-4" />,
        text: 'Cloud Browser',
        color: 'text-blue-400',
        bgColor: 'bg-blue-500/20',
        borderColor: 'border-blue-500/30'
      };
    } else if (method === 'local_playwright') {
      return {
        icon: <Monitor className="w-4 h-4" />,
        text: 'Local Browser',
        color: 'text-green-400',
        bgColor: 'bg-green-500/20',
        borderColor: 'border-green-500/30'
      };
    }
    return {
      icon: <Monitor className="w-4 h-4" />,
      text: 'Unknown Method',
      color: 'text-gray-400',
      bgColor: 'bg-gray-500/20',
      borderColor: 'border-gray-500/30'
    };
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(1)}s`;
  };

  const getPerformanceScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back</span>
              </button>
              <div>
                <div className="flex items-center space-x-3">
                  <h1 className="text-xl font-semibold">{safeResult.clone_metadata.title}</h1>
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs border ${getScrapingMethodDisplay().bgColor} ${getScrapingMethodDisplay().color} ${getScrapingMethodDisplay().borderColor}`}>
                    {getScrapingMethodDisplay().icon}
                    <span>{getScrapingMethodDisplay().text}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-400">{safeResult.original_url}</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* View Toggle */}
              <div className="flex items-center bg-gray-800 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('preview')}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-all ${
                    viewMode === 'preview'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <Eye className="w-4 h-4" />
                  <span>Preview</span>
                </button>
                <button
                  onClick={() => setViewMode('code')}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-all ${
                    viewMode === 'code'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <Code className="w-4 h-4" />
                  <span>Code</span>
                </button>
                {safeResult.browserbase_insights && (
                  <button
                    onClick={() => setViewMode('insights')}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-all ${
                      viewMode === 'insights'
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    <Info className="w-4 h-4" />
                    <span>Insights</span>
                  </button>
                )}
              </div>

              {/* Download Button */}
              <button
                onClick={() => downloadFiles('zip')}
                className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Download</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-80px)]">
        {/* Sidebar - File List or Insights Panel */}
        {(viewMode === 'code' || viewMode === 'insights') && (
          <div className="w-80 border-r border-gray-800 bg-gray-900/30">
            <div className="p-4">
              {viewMode === 'code' ? (
                // File List
                <>
                  <h3 className="text-sm font-medium text-gray-300 mb-4">Generated Files</h3>
                  <div className="space-y-2">
                    {Object.entries(safeResult.files).map(([filename, fileInfo]) => (
                      <button
                        key={filename}
                        onClick={() => setSelectedFile(filename)}
                        className={`w-full text-left p-3 rounded-lg transition-colors ${
                          selectedFile === filename
                            ? 'bg-blue-600/20 border border-blue-500/50'
                            : 'bg-gray-800/50 hover:bg-gray-700/50'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <span className="text-xl">{getFileIcon(filename)}</span>
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-white truncate">{filename}</div>
                            <div className="text-xs text-gray-400 flex items-center space-x-2">
                              <span>{formatFileSize(fileInfo?.size || 0)}</span>
                              {fileInfo?.enhanced_with_browserbase && (
                                <span className="text-blue-400">✨ Enhanced</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </>
              ) : (
                // Insights Panel
                <div className="space-y-6">
                  <h3 className="text-sm font-medium text-gray-300 mb-4">Browserbase Insights</h3>
                  
                  {/* Processing Summary */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-white mb-3">Processing Summary</h4>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Processing Time:</span>
                        <span className="text-white">{formatTime(safeResult.clone_metadata.processing_time_seconds)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Elements Analyzed:</span>
                        <span className="text-white">{safeResult.browserbase_insights?.total_elements?.toLocaleString() || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Files Generated:</span>
                        <span className="text-white">{Object.keys(safeResult.files).length}</span>
                      </div>
                      {safeResult.clone_metadata.performance_score && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Performance Score:</span>
                          <span className={getPerformanceScoreColor(safeResult.clone_metadata.performance_score)}>
                            {safeResult.clone_metadata.performance_score.toFixed(1)}/100
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Features Detected */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-white mb-3">Features Detected</h4>
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <Smartphone className="w-4 h-4 text-gray-400" />
                        <span className="text-xs text-gray-300">
                          Responsive Design: {safeResult.clone_metadata.responsive_design_detected ? 'Yes' : 'No'}
                        </span>
                      </div>
                      {safeResult.browserbase_insights?.screenshots_captured && safeResult.browserbase_insights.screenshots_captured.length > 0 && (
                        <div className="flex items-center space-x-2">
                          <Image className="w-4 h-4 text-gray-400" />
                          <span className="text-xs text-gray-300">
                            Screenshots: {safeResult.browserbase_insights.screenshots_captured.length} captured
                          </span>
                        </div>
                      )}
                      {safeResult.clone_metadata.frameworks_detected && safeResult.clone_metadata.frameworks_detected.length > 0 && (
                        <div className="flex items-center space-x-2">
                          <Zap className="w-4 h-4 text-gray-400" />
                          <span className="text-xs text-gray-300">
                            Frameworks: {safeResult.clone_metadata.frameworks_detected.join(', ')}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  {safeResult.browserbase_insights?.performance_metrics && (
                    <div className="bg-gray-800/50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-white mb-3">Performance Metrics</h4>
                      <div className="space-y-2 text-xs">
                        {safeResult.browserbase_insights.performance_metrics.loadTime && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">Load Time:</span>
                            <span className="text-white">{safeResult.browserbase_insights.performance_metrics.loadTime}ms</span>
                          </div>
                        )}
                        {safeResult.browserbase_insights.performance_metrics.firstContentfulPaint && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">First Paint:</span>
                            <span className="text-white">{safeResult.browserbase_insights.performance_metrics.firstContentfulPaint}ms</span>
                          </div>
                        )}
                        {safeResult.browserbase_insights.performance_metrics.resourceCount && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">Resources:</span>
                            <span className="text-white">{safeResult.browserbase_insights.performance_metrics.resourceCount}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Color Analysis */}
                  {safeResult.browserbase_insights?.computed_colors_count && (
                    <div className="bg-gray-800/50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-white mb-3">Design Analysis</h4>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Colors Extracted:</span>
                          <span className="text-white">{safeResult.browserbase_insights.computed_colors_count}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Layout Containers:</span>
                          <span className="text-white">{safeResult.browserbase_insights.layout_containers_analyzed}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {viewMode === 'preview' ? (
            // Preview Mode
            <div className="flex-1 bg-white">
              <iframe
                srcDoc={previewHtml}
                className="w-full h-full border-0"
                title="Website Preview"
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
          ) : viewMode === 'insights' ? (
            // Insights Main View
            <div className="flex-1 p-6 overflow-auto">
              <div className="max-w-4xl mx-auto space-y-8">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-white mb-2">Clone Analysis Report</h2>
                  <p className="text-gray-400">Detailed insights from your website cloning process</p>
                </div>

                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                    <div className="flex items-center space-x-3 mb-2">
                      <Clock className="w-5 h-5 text-blue-400" />
                      <h3 className="font-medium text-white">Processing Time</h3>
                    </div>
                    <p className="text-2xl font-bold text-white">
                      {formatTime(safeResult.clone_metadata.processing_time_seconds)}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Using {getScrapingMethodDisplay().text}
                    </p>
                  </div>

                  <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                    <div className="flex items-center space-x-3 mb-2">
                      <FileText className="w-5 h-5 text-green-400" />
                      <h3 className="font-medium text-white">Files Generated</h3>
                    </div>
                    <p className="text-2xl font-bold text-white">
                      {Object.keys(safeResult.files).length}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Total size: {formatFileSize(Object.values(safeResult.files).reduce((sum, file) => sum + file.size, 0))}
                    </p>
                  </div>

                  <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                    <div className="flex items-center space-x-3 mb-2">
                      <Zap className="w-5 h-5 text-purple-400" />
                      <h3 className="font-medium text-white">Elements Analyzed</h3>
                    </div>
                    <p className="text-2xl font-bold text-white">
                      {safeResult.browserbase_insights?.total_elements?.toLocaleString() || 'N/A'}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      DOM elements processed
                    </p>
                  </div>
                </div>

                {/* Technology Stack */}
                {safeResult.clone_metadata.frameworks_detected && safeResult.clone_metadata.frameworks_detected.length > 0 && (
                  <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                    <h3 className="font-medium text-white mb-4">Technology Stack Detected</h3>
                    <div className="flex flex-wrap gap-2">
                      {safeResult.clone_metadata.frameworks_detected.map((framework, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-600/20 border border-blue-500/30 text-blue-400 rounded-full text-sm"
                        >
                          {framework}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Performance Analysis */}
                {safeResult.clone_metadata.performance_score && (
                  <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                    <h3 className="font-medium text-white mb-4">Performance Analysis</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-gray-300">Overall Score</span>
                          <span className={`font-bold ${getPerformanceScoreColor(safeResult.clone_metadata.performance_score)}`}>
                            {safeResult.clone_metadata.performance_score.toFixed(1)}/100
                          </span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              safeResult.clone_metadata.performance_score >= 80 ? 'bg-green-500' :
                              safeResult.clone_metadata.performance_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${safeResult.clone_metadata.performance_score}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            // Code Mode
            <div className="flex-1 flex flex-col">
              {/* Code Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-800 bg-gray-900/30">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{getFileIcon(selectedFile)}</span>
                  <div>
                    <h3 className="font-medium">{selectedFile}</h3>
                    <p className="text-xs text-gray-400">
                      {safeResult.files[selectedFile]?.description || 'Generated file'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => copyToClipboard(safeResult.files[selectedFile]?.content || '', selectedFile)}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                      copiedFile === selectedFile
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                    }`}
                  >
                    <Copy className="w-4 h-4" />
                    <span>{copiedFile === selectedFile ? 'Copied!' : 'Copy'}</span>
                  </button>
                </div>
              </div>

              {/* Code Content */}
              <div className="flex-1 overflow-auto">
                <pre className="p-4 text-sm font-mono leading-relaxed">
                  <code className={`language-${getLanguage(selectedFile)}`}>
                    {safeResult.files[selectedFile]?.content || 'No content available'}
                  </code>
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Footer Info */}
      <div className="border-t border-gray-800 bg-gray-900/50 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center space-x-6">
            <span>🤖 {safeResult.clone_metadata.ai_model_used}</span>
            <span>⏰ {new Date(safeResult.clone_metadata.generation_timestamp).toLocaleString()}</span>
            <span>📦 {Object.keys(safeResult.files).length} files generated</span>
            {safeResult.browserbase_insights?.browserbase_used && (
              <span className="text-blue-400">☁️ Cloud Enhanced</span>
            )}
          </div>
          <div className="flex items-center space-x-4">
            <a
              href={safeResult.original_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 hover:text-white transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Original Site</span>
            </a>
          </div>
        </div>
      </div>

      {/* Toast Notification */}
      {showToast && (
        <div className="fixed top-4 right-4 z-50">
          <div className="bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-slideIn">
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">{toastMessage}</span>
          </div>
        </div>
      )}

      {/* CSS for animations */}
      <style jsx>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        .animate-slideIn {
          animation: slideIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

// import React, { useState, useEffect } from 'react';
// import { Eye, Code, Download, Copy, ArrowLeft, ExternalLink } from 'lucide-react';

// interface CloneResult {
//   original_url: string;
//   files: {
//     [filename: string]: {
//       content: string;
//       size: number;
//       type: string;
//       description: string;
//     };
//   };
//   clone_metadata: {
//     title: string;
//     description: string;
//     generation_timestamp: string;
//     ai_model_used: string;
//   };
// }

// interface ResultsPageProps {
//   result: CloneResult;
//   taskId: string;
//   onBack: () => void;
// }

// export default function ResultsPage({ result, taskId, onBack }: ResultsPageProps) {
//   const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');
//   const [selectedFile, setSelectedFile] = useState<string>('index.html');
//   const [copiedFile, setCopiedFile] = useState<string | null>(null);
//   const [previewHtml, setPreviewHtml] = useState<string>('');

//   const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

//   // Safe access to result properties with defaults
//   const safeResult = {
//     original_url: result?.original_url || 'Unknown URL',
//     files: result?.files || {},
//     clone_metadata: {
//       title: result?.clone_metadata?.title || 'Cloned Website',
//       description: result?.clone_metadata?.description || 'AI-generated website clone',
//       generation_timestamp: result?.clone_metadata?.generation_timestamp || new Date().toISOString(),
//       ai_model_used: result?.clone_metadata?.ai_model_used || 'AI Model'
//     }
//   };

//   // Prepare preview HTML by combining all files
//   useEffect(() => {
//     if (safeResult.files && Object.keys(safeResult.files).length > 0) {
//       const htmlContent = safeResult.files['index.html']?.content || '';
//       const cssContent = safeResult.files['styles.css']?.content || '';
//       const jsContent = safeResult.files['script.js']?.content || '';

//       if (htmlContent) {
//         // Inject CSS and JS into HTML for preview
//         const previewContent = htmlContent
//           .replace('</head>', `<style>${cssContent}</style>\n</head>`)
//           .replace('</body>', `<script>${jsContent}</script>\n</body>`);

//         setPreviewHtml(previewContent);
//       } else {
//         setPreviewHtml('<html><body><h1>No HTML content available</h1></body></html>');
//       }
//     }
//   }, [safeResult.files]);

//   // Set default selected file if index.html doesn't exist
//   useEffect(() => {
//     const availableFiles = Object.keys(safeResult.files);
//     if (availableFiles.length > 0 && !availableFiles.includes('index.html')) {
//       setSelectedFile(availableFiles[0]);
//     }
//   }, [safeResult.files]);

//   const downloadFiles = async (format: 'zip' | 'individual' = 'zip') => {
//     try {
//       if (format === 'zip') {
//         const response = await fetch(`${API_URL}/download/${taskId}?format=zip`);
        
//         if (!response.ok) {
//           throw new Error('Failed to download files');
//         }

//         const blob = await response.blob();
//         const downloadUrl = window.URL.createObjectURL(blob);
//         const link = document.createElement('a');
//         link.href = downloadUrl;
//         link.download = `website_clone_${taskId.slice(0, 8)}.zip`;
//         document.body.appendChild(link);
//         link.click();
//         link.remove();
//         window.URL.revokeObjectURL(downloadUrl);
//       }
//     } catch (error) {
//       console.error('Error downloading files:', error);
//     }
//   };

//   const copyToClipboard = async (content: string, filename: string) => {
//     try {
//       await navigator.clipboard.writeText(content);
//       setCopiedFile(filename);
//       setTimeout(() => setCopiedFile(null), 2000);
//     } catch (error) {
//       console.error('Failed to copy:', error);
//     }
//   };

//   const formatFileSize = (bytes: number): string => {
//     if (bytes === 0) return '0 B';
//     const k = 1024;
//     const sizes = ['B', 'KB', 'MB', 'GB'];
//     const i = Math.floor(Math.log(bytes) / Math.log(k));
//     return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
//   };

//   const getFileIcon = (filename: string) => {
//     if (filename.endsWith('.html')) return '📄';
//     if (filename.endsWith('.css')) return '🎨';
//     if (filename.endsWith('.js')) return '⚡';
//     return '📋';
//   };

//   const getLanguage = (filename: string) => {
//     if (filename.endsWith('.html')) return 'html';
//     if (filename.endsWith('.css')) return 'css';
//     if (filename.endsWith('.js')) return 'javascript';
//     return 'markdown';
//   };

//   return (
//     <div className="min-h-screen bg-black text-white">
//       {/* Header */}
//       <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
//         <div className="max-w-7xl mx-auto px-6 py-4">
//           <div className="flex items-center justify-between">
//             <div className="flex items-center space-x-4">
//               <button
//                 onClick={onBack}
//                 className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
//               >
//                 <ArrowLeft className="w-5 h-5" />
//                 <span>Back</span>
//               </button>
//               <div>
//                 <h1 className="text-xl font-semibold">{safeResult.clone_metadata.title}</h1>
//                 <p className="text-sm text-gray-400">{safeResult.original_url}</p>
//               </div>
//             </div>

//             <div className="flex items-center space-x-4">
//               {/* View Toggle */}
//               <div className="flex items-center bg-gray-800 rounded-lg p-1">
//                 <button
//                   onClick={() => setViewMode('preview')}
//                   className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-all ${
//                     viewMode === 'preview'
//                       ? 'bg-blue-600 text-white'
//                       : 'text-gray-400 hover:text-white'
//                   }`}
//                 >
//                   <Eye className="w-4 h-4" />
//                   <span>Preview</span>
//                 </button>
//                 <button
//                   onClick={() => setViewMode('code')}
//                   className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-all ${
//                     viewMode === 'code'
//                       ? 'bg-blue-600 text-white'
//                       : 'text-gray-400 hover:text-white'
//                   }`}
//                 >
//                   <Code className="w-4 h-4" />
//                   <span>Code</span>
//                 </button>
//               </div>

//               {/* Download Button */}
//               <button
//                 onClick={() => downloadFiles('zip')}
//                 className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg transition-colors"
//               >
//                 <Download className="w-4 h-4" />
//                 <span>Download</span>
//               </button>
//             </div>
//           </div>
//         </div>
//       </header>

//       <div className="flex h-[calc(100vh-80px)]">
//         {/* Sidebar - File List (only show in code mode) */}
//         {viewMode === 'code' && (
//           <div className="w-80 border-r border-gray-800 bg-gray-900/30">
//             <div className="p-4">
//               <h3 className="text-sm font-medium text-gray-300 mb-4">Generated Files</h3>
//               <div className="space-y-2">
//                 {Object.entries(safeResult.files).map(([filename, fileInfo]) => (
//                   <button
//                     key={filename}
//                     onClick={() => setSelectedFile(filename)}
//                     className={`w-full text-left p-3 rounded-lg transition-colors ${
//                       selectedFile === filename
//                         ? 'bg-blue-600/20 border border-blue-500/50'
//                         : 'bg-gray-800/50 hover:bg-gray-700/50'
//                     }`}
//                   >
//                     <div className="flex items-center space-x-3">
//                       <span className="text-xl">{getFileIcon(filename)}</span>
//                       <div className="flex-1 min-w-0">
//                         <div className="font-medium text-white truncate">{filename}</div>
//                         <div className="text-xs text-gray-400">{formatFileSize(fileInfo?.size || 0)}</div>
//                       </div>
//                     </div>
//                   </button>
//                 ))}
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Main Content */}
//         <div className="flex-1 flex flex-col">
//           {viewMode === 'preview' ? (
//             // Preview Mode
//             <div className="flex-1 bg-white">
//               <iframe
//                 srcDoc={previewHtml}
//                 className="w-full h-full border-0"
//                 title="Website Preview"
//                 sandbox="allow-scripts allow-same-origin"
//               />
//             </div>
//           ) : (
//             // Code Mode
//             <div className="flex-1 flex flex-col">
//               {/* Code Header */}
//               <div className="flex items-center justify-between p-4 border-b border-gray-800 bg-gray-900/30">
//                 <div className="flex items-center space-x-3">
//                   <span className="text-xl">{getFileIcon(selectedFile)}</span>
//                   <div>
//                     <h3 className="font-medium">{selectedFile}</h3>
//                     <p className="text-xs text-gray-400">
//                       {safeResult.files[selectedFile]?.description || 'Generated file'}
//                     </p>
//                   </div>
//                 </div>
                
//                 <div className="flex items-center space-x-2">
//                   <button
//                     onClick={() => copyToClipboard(safeResult.files[selectedFile]?.content || '', selectedFile)}
//                     className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
//                       copiedFile === selectedFile
//                         ? 'bg-green-600 text-white'
//                         : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
//                     }`}
//                   >
//                     <Copy className="w-4 h-4" />
//                     <span>{copiedFile === selectedFile ? 'Copied!' : 'Copy'}</span>
//                   </button>
//                 </div>
//               </div>

//               {/* Code Content */}
//               <div className="flex-1 overflow-auto">
//                 <pre className="p-4 text-sm font-mono leading-relaxed">
//                   <code className={`language-${getLanguage(selectedFile)}`}>
//                     {safeResult.files[selectedFile]?.content || 'No content available'}
//                   </code>
//                 </pre>
//               </div>
//             </div>
//           )}
//         </div>
//       </div>

//       {/* Footer Info */}
//       <div className="border-t border-gray-800 bg-gray-900/50 p-4">
//         <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-gray-400">
//           <div className="flex items-center space-x-6">
//             <span>🤖 {safeResult.clone_metadata.ai_model_used}</span>
//             <span>⏰ {new Date(safeResult.clone_metadata.generation_timestamp).toLocaleString()}</span>
//             <span>📦 {Object.keys(safeResult.files).length} files generated</span>
//           </div>
//           <div className="flex items-center space-x-4">
//             <a
//               href={safeResult.original_url}
//               target="_blank"
//               rel="noopener noreferrer"
//               className="flex items-center space-x-1 hover:text-white transition-colors"
//             >
//               <ExternalLink className="w-4 h-4" />
//               <span>Original Site</span>
//             </a>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }