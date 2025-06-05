import React, { useState, useEffect } from 'react';
import { Eye, Code, Download, Copy, ArrowLeft, ExternalLink } from 'lucide-react';

interface CloneResult {
  original_url: string;
  files: {
    [filename: string]: {
      content: string;
      size: number;
      type: string;
      description: string;
    };
  };
  clone_metadata: {
    title: string;
    description: string;
    generation_timestamp: string;
    ai_model_used: string;
  };
}

interface ResultsPageProps {
  result: CloneResult;
  taskId: string;
  onBack: () => void;
}

export default function ResultsPage({ result, taskId, onBack }: ResultsPageProps) {
  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');
  const [selectedFile, setSelectedFile] = useState<string>('index.html');
  const [copiedFile, setCopiedFile] = useState<string | null>(null);
  const [previewHtml, setPreviewHtml] = useState<string>('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  // Safe access to result properties with defaults
  const safeResult = {
    original_url: result?.original_url || 'Unknown URL',
    files: result?.files || {},
    clone_metadata: {
      title: result?.clone_metadata?.title || 'Cloned Website',
      description: result?.clone_metadata?.description || 'AI-generated website clone',
      generation_timestamp: result?.clone_metadata?.generation_timestamp || new Date().toISOString(),
      ai_model_used: result?.clone_metadata?.ai_model_used || 'AI Model'
    }
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
        const response = await fetch(`${API_URL}/download/${taskId}?format=zip`);
        
        if (!response.ok) {
          throw new Error('Failed to download files');
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `website_clone_${taskId.slice(0, 8)}.zip`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);
      }
    } catch (error) {
      console.error('Error downloading files:', error);
    }
  };

  const copyToClipboard = async (content: string, filename: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedFile(filename);
      setTimeout(() => setCopiedFile(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
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
    return '📋';
  };

  const getLanguage = (filename: string) => {
    if (filename.endsWith('.html')) return 'html';
    if (filename.endsWith('.css')) return 'css';
    if (filename.endsWith('.js')) return 'javascript';
    return 'markdown';
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
                <h1 className="text-xl font-semibold">{safeResult.clone_metadata.title}</h1>
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
        {/* Sidebar - File List (only show in code mode) */}
        {viewMode === 'code' && (
          <div className="w-80 border-r border-gray-800 bg-gray-900/30">
            <div className="p-4">
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
                        <div className="text-xs text-gray-400">{formatFileSize(fileInfo?.size || 0)}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
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

      {/* Footer Info */}
      <div className="border-t border-gray-800 bg-gray-900/50 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center space-x-6">
            <span>🤖 {safeResult.clone_metadata.ai_model_used}</span>
            <span>⏰ {new Date(safeResult.clone_metadata.generation_timestamp).toLocaleString()}</span>
            <span>📦 {Object.keys(safeResult.files).length} files generated</span>
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
    </div>
  );
}