"use client"

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Globe, Download, CheckCircle, Play, Sparkles, X, Cloud, Monitor, Zap, Info, Settings, AlertTriangle } from 'lucide-react';
import Head from 'next/head';

// Import the results page component
import ResultsPage from '@/app/ResultsPage';

interface TaskStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  message: string;
  result?: CloneResult;
  error?: string;
  error_details?: {
    error_phase: string;
    progress_at_failure: number;
    browserbase_attempted: boolean;
    scraping_method: string;
    context: string;
  };
  files_ready?: boolean;
  browserbase_used?: boolean;
  scraping_method?: string;
  completion_stats?: {
    files_generated: number;
    total_size_bytes: number;
    processing_time: number;
    elements_analyzed: number;
    images_processed: number;
    scraping_method_used: string;
    browserbase_used: boolean;
  };
  processing_duration_seconds?: number;
}

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
    performance_metrics: any;
    responsive_tested: boolean;
    frameworks_detected: string[];
    total_elements: number;
    computed_colors_count: number;
    layout_containers_analyzed: number;
  };
}

interface BrowserbaseStatus {
  browserbase_configured: boolean;
  api_key_set: boolean;
  project_id_set: boolean;
  fallback_available: boolean;
  recommendation: string;
  benefits?: string[];
}

interface ClonePreferences {
  force_browserbase?: boolean;
  performance_priority?: 'speed' | 'quality' | 'balanced';
  capture_screenshots?: boolean;
  analyze_responsive?: boolean;
}

export default function HomePage(): React.JSX.Element {
  const [url, setUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentTask, setCurrentTask] = useState<TaskStatus | null>(null);
  const [cloneResult, setCloneResult] = useState<CloneResult | null>(null);
  const [currentText, setCurrentText] = useState<string>('');
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isTyping, setIsTyping] = useState<boolean>(true);
  const [showToast, setShowToast] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string>('');
  const [toastType, setToastType] = useState<'success' | 'error' | 'info' | 'warning'>('success');
  const [showResults, setShowResults] = useState<boolean>(false);
  
  // New Browserbase-related state
  const [browserbaseStatus, setBrowserbaseStatus] = useState<BrowserbaseStatus | null>(null);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState<boolean>(false);
  const [preferences, setPreferences] = useState<ClonePreferences>({
    force_browserbase: false, // Default to false until we check status
    performance_priority: 'balanced',
    capture_screenshots: true,
    analyze_responsive: true
  });
  const [apiConnected, setApiConnected] = useState<boolean>(false);
  const [connectionChecked, setConnectionChecked] = useState<boolean>(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  // Enhanced placeholder texts with more modern examples
  const placeholderTexts = useMemo(() => [
    "https://stripe.com",
    "https://linear.app", 
    "https://vercel.com",
    "https://figma.com",
    "https://notion.so",
    "https://anthropic.com",
    "https://openai.com",
    "https://github.com"
  ], []);

  // Check API connection and Browserbase status on component mount
  useEffect(() => {
    const checkApiConnection = async () => {
      try {
        console.log('Checking API connection to:', API_URL);
        
        // First check if API is reachable with a simple health check
        const healthResponse = await fetch(`${API_URL}/health`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        });
        
        if (healthResponse.ok) {
          setApiConnected(true);
          console.log('API connection successful');
          
          // Now check Browserbase status
          try {
            const statusResponse = await fetch(`${API_URL}/browserbase-status`);
            if (statusResponse.ok) {
              const status = await statusResponse.json();
              setBrowserbaseStatus(status);
              console.log('Browserbase status:', status);
              
              // Update default preference based on availability
              if (status.browserbase_configured) {
                setPreferences(prev => ({ ...prev, force_browserbase: true }));
                showToastMessage('✨ Enhanced cloud browser automation available!', 'info');
              }
            } else {
              console.warn('Browserbase status endpoint not available, using defaults');
              // Set default status for backward compatibility
              setBrowserbaseStatus({
                browserbase_configured: false,
                api_key_set: false,
                project_id_set: false,
                fallback_available: true,
                recommendation: 'Using local browser automation'
              });
            }
          } catch (statusError) {
            console.warn('Could not fetch Browserbase status:', statusError);
            // Set default status for backward compatibility
            setBrowserbaseStatus({
              browserbase_configured: false,
              api_key_set: false,
              project_id_set: false,
              fallback_available: true,
              recommendation: 'Using local browser automation'
            });
          }
        } else {
          throw new Error(`API health check failed: ${healthResponse.status}`);
        }
      } catch (error) {
        console.error('API connection failed:', error);
        setApiConnected(false);
        showToastMessage('⚠️ Cannot connect to backend API. Please check if the server is running.', 'warning');
      } finally {
        setConnectionChecked(true);
      }
    };

    checkApiConnection();
  }, [API_URL]);

  // Optimized typing animation
  useEffect(() => {
    const currentFullText = placeholderTexts[currentIndex];
    
    if (isTyping) {
      if (currentText.length < currentFullText.length) {
        const timeout = setTimeout(() => {
          setCurrentText(currentFullText.slice(0, currentText.length + 1));
        }, 40);
        return () => clearTimeout(timeout);
      } else {
        const timeout = setTimeout(() => {
          setIsTyping(false);
        }, 2000);
        return () => clearTimeout(timeout);
      }
    } else {
      if (currentText.length > 0) {
        const timeout = setTimeout(() => {
          setCurrentText(currentText.slice(0, -1));
        }, 30);
        return () => clearTimeout(timeout);
      } else {
        setCurrentIndex((prev) => (prev + 1) % placeholderTexts.length);
        setIsTyping(true);
      }
    }
  }, [currentText, currentIndex, isTyping, placeholderTexts]);

  // Enhanced toast function with warning type
  const showToastMessage = useCallback((message: string, type: 'success' | 'error' | 'info' | 'warning' = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), type === 'warning' ? 6000 : 4000);
  }, []);

  // URL validation
  const isValidUrl = useCallback((url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }, []);

  // Enhanced polling with better error handling
  const pollStatus = useCallback(async (taskId: string) => {
    try {
      const response = await fetch(`${API_URL}/status/${taskId}`, {
        cache: 'no-cache'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to get status: ${response.status}`);
      }
      
      const statusData: TaskStatus = await response.json();
      setCurrentTask(statusData);
      
      console.log('Task status update:', statusData);
      
      // Enhanced completion handling
      if (statusData.status === 'completed') {
        const method = statusData.scraping_method || 'unknown';
        const methodText = method === 'browserbase' ? 'cloud browsers' : 'local browser';
        const stats = statusData.completion_stats;
        
        let successMessage = `✅ Website cloned successfully using ${methodText}!`;
        if (stats) {
          successMessage += ` Generated ${stats.files_generated} files in ${stats.processing_time?.toFixed(1)}s`;
        }
        
        showToastMessage(successMessage, 'success');
        setIsLoading(false);
        
        if (statusData.result) {
          setCloneResult(statusData.result);
          setTimeout(() => setShowResults(true), 800);
        }
      } else if (statusData.status === 'failed') {
        let errorMessage = '❌ Cloning failed';
        
        // Enhanced error messaging based on phase
        if (statusData.error_details) {
          const { error_phase, scraping_method } = statusData.error_details;
          const methodText = scraping_method === 'browserbase' ? 'cloud browser' : 'local browser';
          errorMessage = `${error_phase} failed using ${methodText}: ${statusData.error || statusData.message}`;
        } else {
          errorMessage = `Cloning failed: ${statusData.error || statusData.message}`;
        }
        
        showToastMessage(errorMessage, 'error');
        setIsLoading(false);
      } else if (statusData.status === 'cancelled') {
        showToastMessage('Cloning was cancelled', 'error');
        setIsLoading(false);
      } else {
        // Continue polling with shorter interval for better UX
        setTimeout(() => pollStatus(taskId), 1500);
      }
    } catch (error) {
      console.error('Error checking status:', error);
      showToastMessage('Error checking status - please check your connection', 'error');
      setIsLoading(false);
    }
  }, [API_URL, showToastMessage]);

  // Enhanced submit handler with better error handling
  const handleSubmit = useCallback(async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    
    if (!url.trim()) {
      showToastMessage('Please enter a URL', 'error');
      return;
    }

    if (!isValidUrl(url.trim())) {
      showToastMessage('Please enter a valid URL (e.g., https://example.com)', 'error');
      return;
    }

    if (!apiConnected) {
      showToastMessage('Cannot connect to backend API. Please check if the server is running.', 'error');
      return;
    }

    setIsLoading(true);
    setCurrentTask(null);
    setCloneResult(null);
    setShowResults(false);
    
    // Enhanced starting message based on Browserbase availability
    const startingMethod = preferences.force_browserbase && browserbaseStatus?.browserbase_configured 
      ? 'cloud browsers' : 'local browser';
    showToastMessage(`🚀 Starting website cloning with ${startingMethod}...`, 'info');
    
    try {
      const requestBody = {
        url: url.trim(),
        preferences: {
          ...preferences,
          // Map performance priority to backend preferences
          fast_mode: preferences.performance_priority === 'speed',
          high_quality: preferences.performance_priority === 'quality'
        },
        force_browserbase: preferences.force_browserbase && browserbaseStatus?.browserbase_configured
      };

      console.log('Sending clone request:', requestBody);

      const response = await fetch(`${API_URL}/clone`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        throw new Error(errorData.detail?.message || errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Clone response:', data);
      
      if (data.task_id) {
        const method = data.browserbase_enabled ? 'cloud automation' : 'local browser';
        showToastMessage(`🎯 Cloning started with ${method}! Monitoring progress...`, 'success');
        pollStatus(data.task_id);
      } else {
        showToastMessage('Failed to start cloning task', 'error');
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error cloning website:', error);
      
      // Enhanced error messaging
      let errorMessage = 'Failed to clone website. Please try again.';
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMessage = 'Cannot connect to the server. Please check if the backend is running.';
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      showToastMessage(errorMessage, 'error');
      setIsLoading(false);
    }
  }, [url, isValidUrl, showToastMessage, API_URL, pollStatus, preferences, browserbaseStatus, apiConnected]);

  // Handle navigation back from results
  const handleBackFromResults = useCallback(() => {
    setShowResults(false);
    setCloneResult(null);
    setCurrentTask(null);
    setUrl('');
  }, []);

  // Get the status indicator color and text
  const getScrapingMethodDisplay = useCallback(() => {
    if (!currentTask) return null;
    
    const method = currentTask.scraping_method;
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
    return null;
  }, [currentTask]);

  // If showing results, render the results page
  if (showResults && cloneResult && currentTask) {
    return (
      <ResultsPage 
        result={cloneResult} 
        taskId={currentTask.task_id}
        onBack={handleBackFromResults}
      />
    );
  }

  return (
    <div className="min-h-screen bg-black relative">
      <Head>
        <link
          href="https://fonts.googleapis.com/css2?family=Radley&family=HK+Grotesk:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </Head>

      {/* Header */}
      <header className="relative z-20 px-6 py-6">
        <nav className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-3">
            <img 
              src="/orchids_logo.jpeg" 
              alt="Orchids Logo" 
              className="w-10 h-10 rounded-xl"
            />
            <span className="text-2xl font-bold text-white">
              orchids
            </span>
            {/* API Connection Status */}
            {connectionChecked && (
              <div className={`hidden md:flex items-center space-x-1 px-3 py-1 rounded-full text-sm ${
                apiConnected 
                  ? browserbaseStatus?.browserbase_configured 
                    ? 'bg-blue-500/20 border border-blue-500/30 text-blue-400'
                    : 'bg-green-500/20 border border-green-500/30 text-green-400'
                  : 'bg-red-500/20 border border-red-500/30 text-red-400'
              }`}>
                {apiConnected ? (
                  browserbaseStatus?.browserbase_configured ? (
                    <>
                      <Cloud className="w-3 h-3" />
                      <span>Enhanced</span>
                    </>
                  ) : (
                    <>
                      <Monitor className="w-3 h-3" />
                      <span>Ready</span>
                    </>
                  )
                ) : (
                  <>
                    <AlertTriangle className="w-3 h-3" />
                    <span>Offline</span>
                  </>
                )}
              </div>
            )}
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">Product</a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">How it works</a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">Features</a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">Mission</a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">Company</a>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="text-gray-300 hover:text-white transition-colors duration-300 font-medium px-4 py-2">
              Log in
            </button>
            <button className="bg-white text-black px-6 py-2 rounded-full hover:bg-gray-100 transition-all duration-300 font-medium">
              Sign up
            </button>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-120px)] px-6">
        <div className="text-center max-w-5xl mx-auto">
          {/* Orchids Logo */}
          <div className="mb-8">
            <div className="w-40 h-40 mx-auto mb-4">
              <img 
                src="/orchids_logo.jpeg" 
                alt="Orchids" 
                className="w-full h-full rounded-2xl"
              />
            </div>
          </div>
          
          {/* Main Headline with Browserbase enhancement note */}
          <h1 className="text-6xl md:text-7xl font-serif mb-6 leading-tight text-white italic">
            Clone a website in seconds
          </h1>
          
          <p className="text-xl font-grotesk text-gray-300 mb-4 font-normal">
            AI-powered website cloning with clean, modern code
          </p>

          {/* API Status Badge */}
          {connectionChecked && (
            <div className="mb-8">
              {!apiConnected ? (
                <div className="inline-flex items-center space-x-2 bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-2 rounded-full text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Backend API offline - Please start your server</span>
                </div>
              ) : browserbaseStatus?.browserbase_configured ? (
                <div className="inline-flex items-center space-x-2 bg-blue-500/20 border border-blue-500/30 text-blue-400 px-4 py-2 rounded-full text-sm">
                  <Cloud className="w-4 h-4" />
                  <span>Enhanced with cloud browser automation</span>
                </div>
              ) : (
                <div className="inline-flex items-center space-x-2 bg-amber-500/20 border border-amber-500/30 text-amber-400 px-4 py-2 rounded-full text-sm">
                  <Monitor className="w-4 h-4" />
                  <span>Using local browser • <a href="#" className="underline">cloud upgrade available</a></span>
                </div>
              )}
            </div>
          )}
          
          {/* Search Interface */}
          <div className="max-w-4xl mx-auto mb-6">
            <div className="relative">
              <div className="bg-gray-900 border border-gray-700 rounded-2xl p-2">
                <div className="flex items-center space-x-2">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder={currentText + (isTyping && currentText.length < placeholderTexts[currentIndex].length ? '|' : '')}
                      className="w-full bg-transparent text-white placeholder-gray-400 px-6 py-4 rounded-xl focus:outline-none text-lg font-normal"
                      disabled={isLoading || !apiConnected}
                      onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
                    />
                  </div>
                  
                  {/* Settings Button */}
                  <button
                    onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                    className="bg-gray-700 hover:bg-gray-600 text-white p-4 rounded-xl transition-colors duration-300 disabled:opacity-50"
                    title="Advanced Options"
                    disabled={!apiConnected}
                  >
                    <Settings className="w-5 h-5" />
                  </button>
                  
                  {/* Submit Button */}
                  <button 
                    onClick={handleSubmit}
                    disabled={isLoading || !url.trim() || !apiConnected}
                    className="bg-gray-600 hover:bg-gray-500 text-white p-4 rounded-xl transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    ) : (
                      <Sparkles className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Advanced Options Panel */}
          {showAdvancedOptions && apiConnected && (
            <div className="max-w-2xl mx-auto mb-8 bg-gray-900/50 border border-gray-700 rounded-2xl p-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-white">Advanced Options</h3>
                  <button 
                    onClick={() => setShowAdvancedOptions(false)}
                    className="text-gray-400 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Performance Priority */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">Performance Priority</label>
                  <div className="flex space-x-3">
                    {(['speed', 'balanced', 'quality'] as const).map((priority) => (
                      <button
                        key={priority}
                        onClick={() => setPreferences(prev => ({ ...prev, performance_priority: priority }))}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-300 ${
                          preferences.performance_priority === priority
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                      >
                        {priority === 'speed' ? '🚀 Speed' : priority === 'balanced' ? '⚖️ Balanced' : '💎 Quality'}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    {preferences.performance_priority === 'speed' && 'Prioritizes fast cloning with essential features'}
                    {preferences.performance_priority === 'balanced' && 'Good balance of speed and comprehensive analysis'}
                    {preferences.performance_priority === 'quality' && 'Maximum analysis depth and feature extraction'}
                  </p>
                </div>

                {/* Cloud Browser Option */}
                {browserbaseStatus?.browserbase_configured && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Cloud className="w-4 h-4 text-blue-400" />
                      <div>
                        <label className="text-sm font-medium text-gray-300">Use Cloud Browsers</label>
                        <p className="text-xs text-gray-400">Enhanced reliability and bypass anti-bot measures</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setPreferences(prev => ({ ...prev, force_browserbase: !prev.force_browserbase }))}
                      className={`relative w-12 h-6 rounded-full transition-colors duration-300 ${
                        preferences.force_browserbase ? 'bg-blue-600' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`absolute w-5 h-5 bg-white rounded-full top-0.5 transition-transform duration-300 ${
                        preferences.force_browserbase ? 'translate-x-6' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </div>
                )}

                {/* Feature Toggles */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-300">Capture Screenshots</label>
                      <p className="text-xs text-gray-400">Multi-viewport screenshots for analysis</p>
                    </div>
                    <button
                      onClick={() => setPreferences(prev => ({ ...prev, capture_screenshots: !prev.capture_screenshots }))}
                      className={`relative w-12 h-6 rounded-full transition-colors duration-300 ${
                        preferences.capture_screenshots ? 'bg-blue-600' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`absolute w-5 h-5 bg-white rounded-full top-0.5 transition-transform duration-300 ${
                        preferences.capture_screenshots ? 'translate-x-6' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-300">Responsive Analysis</label>
                      <p className="text-xs text-gray-400">Test across multiple device sizes</p>
                    </div>
                    <button
                      onClick={() => setPreferences(prev => ({ ...prev, analyze_responsive: !prev.analyze_responsive }))}
                      className={`relative w-12 h-6 rounded-full transition-colors duration-300 ${
                        preferences.analyze_responsive ? 'bg-blue-600' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`absolute w-5 h-5 bg-white rounded-full top-0.5 transition-transform duration-300 ${
                        preferences.analyze_responsive ? 'translate-x-6' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Enhanced Progress Section */}
          {currentTask && isLoading && (
            <div className="max-w-2xl mx-auto mb-8">
              <div className="bg-gray-900/50 border border-gray-700 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-medium text-white">Cloning Progress</h3>
                    {getScrapingMethodDisplay() && (
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs border ${getScrapingMethodDisplay()!.bgColor} ${getScrapingMethodDisplay()!.color} ${getScrapingMethodDisplay()!.borderColor}`}>
                        {getScrapingMethodDisplay()!.icon}
                        <span>{getScrapingMethodDisplay()!.text}</span>
                      </div>
                    )}
                  </div>
                  <span className="text-sm text-gray-400">
                    {Math.round(currentTask.progress * 100)}%
                  </span>
                </div>
                
                {/* Enhanced Progress Bar */}
                <div className="w-full bg-gray-800 rounded-full h-3 mb-4">
                  <div
                    className={`h-3 rounded-full transition-all duration-500 ease-out ${
                      currentTask.scraping_method === 'browserbase' 
                        ? 'bg-gradient-to-r from-blue-500 to-cyan-500'
                        : 'bg-gradient-to-r from-green-500 to-emerald-500'
                    }`}
                    style={{ width: `${currentTask.progress * 100}%` }}
                  />
                </div>
                
                <div className="space-y-2">
                  <p className="text-sm text-gray-300">{currentTask.message}</p>
                  
                  {/* Show completion stats in real-time if available */}
                  {currentTask.completion_stats && (
                    <div className="text-xs text-gray-400 grid grid-cols-2 gap-2 pt-2 border-t border-gray-700">
                      <div>Elements: {currentTask.completion_stats.elements_analyzed?.toLocaleString()}</div>
                      <div>Images: {currentTask.completion_stats.images_processed}</div>
                      {currentTask.processing_duration_seconds && (
                        <>
                          <div>Time: {currentTask.processing_duration_seconds.toFixed(1)}s</div>
                          <div>Method: {currentTask.completion_stats.scraping_method_used}</div>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Enhanced Toast Notification with different types */}
      {showToast && (
        <div className="fixed top-4 right-4 z-50">
          <div className={`${
            toastType === 'success' ? 'bg-green-600' : 
            toastType === 'error' ? 'bg-red-600' : 
            toastType === 'warning' ? 'bg-amber-600' : 'bg-blue-600'
          } text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-slideIn max-w-sm`}>
            {toastType === 'success' && <CheckCircle className="w-5 h-5 flex-shrink-0" />}
            {toastType === 'error' && <X className="w-5 h-5 flex-shrink-0" />}
            {toastType === 'info' && <Info className="w-5 h-5 flex-shrink-0" />}
            {toastType === 'warning' && <AlertTriangle className="w-5 h-5 flex-shrink-0" />}
            <span className="font-medium text-sm">{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Enhanced CSS */}
      <style jsx>{`
        .font-serif {
          font-family: 'Times New Roman', serif;
        }
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slideIn {
          animation: slideIn 0.3s ease-out;
        }
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
        .animate-spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}

// "use client"

// import React, { useState, useEffect, useCallback, useMemo } from 'react';
// import { Globe, Download, CheckCircle, Play, Sparkles, X } from 'lucide-react';
// import Head from 'next/head';

// // Import the results page component
// import ResultsPage from '@/app/ResultsPage';

// interface TaskStatus {
//   task_id: string;
//   status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
//   progress: number;
//   message: string;
//   result?: any;
//   error?: string;
//   files_ready?: boolean;
// }

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

// export default function HomePage(): React.JSX.Element {
//   const [url, setUrl] = useState<string>('');
//   const [isLoading, setIsLoading] = useState<boolean>(false);
//   const [currentTask, setCurrentTask] = useState<TaskStatus | null>(null);
//   const [cloneResult, setCloneResult] = useState<CloneResult | null>(null);
//   const [currentText, setCurrentText] = useState<string>('');
//   const [currentIndex, setCurrentIndex] = useState<number>(0);
//   const [isTyping, setIsTyping] = useState<boolean>(true);
//   const [showToast, setShowToast] = useState<boolean>(false);
//   const [toastMessage, setToastMessage] = useState<string>('');
//   const [toastType, setToastType] = useState<'success' | 'error'>('success');
//   const [showResults, setShowResults] = useState<boolean>(false);

//   const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

//   // Memoize placeholder texts to prevent recreation
//   const placeholderTexts = useMemo(() => [
//     "https://apple.com",
//     "https://stripe.com", 
//     "https://vercel.com",
//     "https://github.com",
//     "https://linear.app",
//     "https://figma.com",
//     "https://notion.so",
//     "https://openai.com"
//   ], []);

//   // Optimized typing animation with useCallback
//   useEffect(() => {
//     const currentFullText = placeholderTexts[currentIndex];
    
//     if (isTyping) {
//       if (currentText.length < currentFullText.length) {
//         const timeout = setTimeout(() => {
//           setCurrentText(currentFullText.slice(0, currentText.length + 1));
//         }, 30); // Reduced from 50ms to 30ms for faster typing
//         return () => clearTimeout(timeout);
//       } else {
//         const timeout = setTimeout(() => {
//           setIsTyping(false);
//         }, 1500); // Reduced pause time
//         return () => clearTimeout(timeout);
//       }
//     } else {
//       if (currentText.length > 0) {
//         const timeout = setTimeout(() => {
//           setCurrentText(currentText.slice(0, -1));
//         }, 20); // Faster deletion
//         return () => clearTimeout(timeout);
//       } else {
//         setCurrentIndex((prev) => (prev + 1) % placeholderTexts.length);
//         setIsTyping(true);
//       }
//     }
//   }, [currentText, currentIndex, isTyping, placeholderTexts]);

//   // Memoized toast function
//   const showToastMessage = useCallback((message: string, type: 'success' | 'error' = 'success') => {
//     setToastMessage(message);
//     setToastType(type);
//     setShowToast(true);
//     setTimeout(() => setShowToast(false), 2500); // Reduced toast time
//   }, []);

//   // Optimized URL validation
//   const isValidUrl = useCallback((url: string): boolean => {
//     try {
//       new URL(url);
//       return true;
//     } catch {
//       return false;
//     }
//   }, []);

//   // Optimized polling with shorter intervals
//   const pollStatus = useCallback(async (taskId: string) => {
//     try {
//       const response = await fetch(`${API_URL}/status/${taskId}`, {
//         cache: 'no-cache' // Ensure fresh data
//       });

//       console.log('Polling status for task:', API_URL);
//       console.log('Response:', response);
      
//       if (!response.ok) {
//         throw new Error(`Failed to get status: ${response.status}`);
//       }
      
//       const statusData: TaskStatus = await response.json();
//       setCurrentTask(statusData);
      
//       if (statusData.status === 'completed') {
//         showToastMessage('Website cloned successfully!', 'success');
//         setIsLoading(false);
//         if (statusData.result) {
//           setCloneResult(statusData.result);
//           // Auto-navigate to results page
//           setTimeout(() => setShowResults(true), 500);
//         } else {
//           showToastMessage('No result data received', 'error');
//         }
//       } else if (statusData.status === 'failed') {
//         showToastMessage(`Cloning failed 11: ${statusData.error || statusData.message}`, 'error');
//         setIsLoading(false);
//       } else if (statusData.status === 'cancelled') {
//         showToastMessage('Cloning was cancelled', 'error');
//         setIsLoading(false);
//       } else {
//         // Reduced polling interval for faster updates
//         setTimeout(() => pollStatus(taskId), 1000); // 1 second instead of 2
//       }
//     } catch (error) {
//       console.error('Error checking status:', error);
//       showToastMessage('Error checking status', 'error');
//       setIsLoading(false);
//     }
//   }, [API_URL, showToastMessage]);

//   // Optimized submit handler
//   const handleSubmit = useCallback(async (e: React.FormEvent): Promise<void> => {
//     e.preventDefault();
    
//     if (!url.trim()) {
//       showToastMessage('Please enter a URL', 'error');
//       return;
//     }

//     if (!isValidUrl(url.trim())) {
//       showToastMessage('Please enter a valid URL (e.g., https://example.com)', 'error');
//       return;
//     }

//     setIsLoading(true);
//     setCurrentTask(null);
//     setCloneResult(null);
//     setShowResults(false);
//     showToastMessage('Starting website cloning...', 'success');
    
//     try {
//       const response = await fetch(`${API_URL}/clone`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ 
//           url: url.trim(),
//           // Add speed optimization preferences
//           preferences: {
//             fast_mode: true,
//             skip_heavy_analysis: true
//           }
//         }),
//       });

//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail?.message || `HTTP error! status: ${response.status}`);
//       }

//       const data = await response.json();
      
//       if (data.task_id) {
//         showToastMessage('Cloning started! Monitoring progress...', 'success');
//         pollStatus(data.task_id);
//       } else {
//         showToastMessage('Failed to start cloning task', 'error');
//         setIsLoading(false);
//       }
//     } catch (error) {
//       console.error('Error cloning website:', error);
//       showToastMessage(error instanceof Error ? error.message : 'Failed to clone website. Please try again.', 'error');
//       setIsLoading(false);
//     }
//   }, [url, isValidUrl, showToastMessage, API_URL, pollStatus]);

//   // Handle navigation back from results
//   const handleBackFromResults = useCallback(() => {
//     setShowResults(false);
//     setCloneResult(null);
//     setCurrentTask(null);
//     setUrl('');
//   }, []);

//   // If showing results, render the results page
//   if (showResults && cloneResult && currentTask) {
//     return (
//       <ResultsPage 
//         result={cloneResult} 
//         taskId={currentTask.task_id}
//         onBack={handleBackFromResults}
//       />
//     );
//   }

//   return (
//     <div className="min-h-screen bg-black relative">
//       <Head>
//         <link
//           href="https://fonts.googleapis.com/css2?family=Radley&family=HK+Grotesk:wght@400;500;700&display=swap"
//           rel="stylesheet"
//         />
//       </Head>

//       {/* Header */}
//       <header className="relative z-20 px-6 py-6">
//         <nav className="flex items-center justify-between max-w-7xl mx-auto">
//           <div className="flex items-center space-x-3">
//             <img 
//               src="/orchids_logo.jpeg" 
//               alt="Orchids Logo" 
//               className="w-10 h-10 rounded-xl"
//             />
//             <span className="text-2xl font-bold text-white">
//               orchids
//             </span>
//           </div>
          
//           <div className="hidden md:flex items-center space-x-8">
//             <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">Product</a>
//             <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">How it works</a>
//             <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">Features</a>
//             <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">Mission</a>
//             <a href="#" className="text-gray-300 hover:text-white transition-colors duration-300 font-medium">Company</a>
//           </div>
          
//           <div className="flex items-center space-x-4">
//             <button className="text-gray-300 hover:text-white transition-colors duration-300 font-medium px-4 py-2">
//               Log in
//             </button>
//             <button className="bg-white text-black px-6 py-2 rounded-full hover:bg-gray-100 transition-all duration-300 font-medium">
//               Sign up
//             </button>
//           </div>
//         </nav>
//       </header>

//       {/* Main Content */}
//       <main className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-120px)] px-6">
//         <div className="text-center max-w-5xl mx-auto">
//           {/* Orchids Logo */}
//           <div className="mb-8">
//             <div className="w-40 h-40 mx-auto mb-4">
//               <img 
//                 src="/orchids_logo.jpeg" 
//                 alt="Orchids" 
//                 className="w-full h-full rounded-2xl"
//               />
//             </div>
//           </div>
          
//           {/* Main Headline */}
//           <h1 className="text-6xl md:text-7xl font-serif mb-6 leading-tight text-white italic">
//             Clone a website in seconds
//           </h1>
          
//           <p className="text-xl font-grotesk text-gray-300 mb-12 font-normal">
//             AI-powered website cloning with clean, modern code
//           </p>
          
//           {/* Search Interface */}
//           <div className="max-w-4xl mx-auto mb-8">
//             <div className="relative">
//               <div className="bg-gray-900 border border-gray-700 rounded-2xl p-2">
//                 <div className="flex items-center space-x-2">
//                   <div className="flex-1 relative">
//                     <input
//                       type="text"
//                       value={url}
//                       onChange={(e) => setUrl(e.target.value)}
//                       placeholder={currentText + (isTyping && currentText.length < placeholderTexts[currentIndex].length ? '|' : '')}
//                       className="w-full bg-transparent text-white placeholder-gray-400 px-6 py-4 rounded-xl focus:outline-none text-lg font-normal"
//                       disabled={isLoading}
//                       onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
//                     />
//                   </div>
//                   <button 
//                     onClick={handleSubmit}
//                     disabled={isLoading || !url.trim()}
//                     className="bg-gray-600 hover:bg-gray-500 text-white p-4 rounded-xl transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
//                   >
//                     {isLoading ? (
//                       <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
//                     ) : (
//                       <Sparkles className="w-5 h-5" />
//                     )}
//                   </button>
//                 </div>
//               </div>
//             </div>
//           </div>

//           {/* Progress Section - Simplified for speed */}
//           {currentTask && isLoading && (
//             <div className="max-w-2xl mx-auto mb-8">
//               <div className="bg-gray-900/50 border border-gray-700 rounded-2xl p-6">
//                 <div className="flex items-center justify-between mb-4">
//                   <h3 className="text-lg font-medium text-white">Cloning Progress</h3>
//                   <span className="text-sm text-gray-400">
//                     {Math.round(currentTask.progress * 100)}%
//                   </span>
//                 </div>
                
//                 {/* Simplified Progress Bar */}
//                 <div className="w-full bg-gray-800 rounded-full h-2 mb-4">
//                   <div
//                     className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300 ease-out"
//                     style={{ width: `${currentTask.progress * 100}%` }}
//                   />
//                 </div>
                
//                 <p className="text-sm text-gray-400">{currentTask.message}</p>
//               </div>
//             </div>
//           )}
//         </div>
//       </main>

//       {/* Optimized Toast Notification */}
//       {showToast && (
//         <div className="fixed top-4 right-4 z-50">
//           <div className={`${
//             toastType === 'success' ? 'bg-green-600' : 'bg-red-600'
//           } text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-slideIn`}>
//             <CheckCircle className="w-5 h-5" />
//             <span className="font-medium">{toastMessage}</span>
//           </div>
//         </div>
//       )}

//       {/* Optimized CSS */}
//       <style jsx>{`
//         .font-serif {
//           font-family: 'Times New Roman', serif;
//         }
//         @keyframes slideIn {
//           from {
//             transform: translateX(100%);
//             opacity: 0;
//           }
//           to {
//             transform: translateX(0);
//             opacity: 1;
//           }
//         }
//         .animate-slideIn {
//           animation: slideIn 0.2s ease-out;
//         }
//         @keyframes spin {
//           to {
//             transform: rotate(360deg);
//           }
//         }
//         .animate-spin {
//           animation: spin 1s linear infinite;
//         }
//       `}</style>
//     </div>
//   );
// }
