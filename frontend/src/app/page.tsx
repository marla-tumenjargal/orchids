"use client"

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Globe, Download, CheckCircle, Play, Sparkles, X } from 'lucide-react';
import Head from 'next/head';

// Import the results page component
import ResultsPage from '@/app/ResultsPage';

interface TaskStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  message: string;
  result?: any;
  error?: string;
  files_ready?: boolean;
}

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
  const [toastType, setToastType] = useState<'success' | 'error'>('success');
  const [showResults, setShowResults] = useState<boolean>(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  // Memoize placeholder texts to prevent recreation
  const placeholderTexts = useMemo(() => [
    "https://apple.com",
    "https://stripe.com", 
    "https://vercel.com",
    "https://github.com",
    "https://linear.app",
    "https://figma.com",
    "https://notion.so",
    "https://openai.com"
  ], []);

  // Optimized typing animation with useCallback
  useEffect(() => {
    const currentFullText = placeholderTexts[currentIndex];
    
    if (isTyping) {
      if (currentText.length < currentFullText.length) {
        const timeout = setTimeout(() => {
          setCurrentText(currentFullText.slice(0, currentText.length + 1));
        }, 30); // Reduced from 50ms to 30ms for faster typing
        return () => clearTimeout(timeout);
      } else {
        const timeout = setTimeout(() => {
          setIsTyping(false);
        }, 1500); // Reduced pause time
        return () => clearTimeout(timeout);
      }
    } else {
      if (currentText.length > 0) {
        const timeout = setTimeout(() => {
          setCurrentText(currentText.slice(0, -1));
        }, 20); // Faster deletion
        return () => clearTimeout(timeout);
      } else {
        setCurrentIndex((prev) => (prev + 1) % placeholderTexts.length);
        setIsTyping(true);
      }
    }
  }, [currentText, currentIndex, isTyping, placeholderTexts]);

  // Memoized toast function
  const showToastMessage = useCallback((message: string, type: 'success' | 'error' = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2500); // Reduced toast time
  }, []);

  // Optimized URL validation
  const isValidUrl = useCallback((url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }, []);

  // Optimized polling with shorter intervals
  const pollStatus = useCallback(async (taskId: string) => {
    try {
      const response = await fetch(`${API_URL}/status/${taskId}`, {
        cache: 'no-cache' // Ensure fresh data
      });
      
      if (!response.ok) {
        throw new Error(`Failed to get status: ${response.status}`);
      }
      
      const statusData: TaskStatus = await response.json();
      setCurrentTask(statusData);
      
      if (statusData.status === 'completed') {
        showToastMessage('Website cloned successfully!', 'success');
        setIsLoading(false);
        if (statusData.result) {
          setCloneResult(statusData.result);
          // Auto-navigate to results page
          setTimeout(() => setShowResults(true), 500);
        } else {
          showToastMessage('No result data received', 'error');
        }
      } else if (statusData.status === 'failed') {
        showToastMessage(`Cloning failed: ${statusData.error || statusData.message}`, 'error');
        setIsLoading(false);
      } else if (statusData.status === 'cancelled') {
        showToastMessage('Cloning was cancelled', 'error');
        setIsLoading(false);
      } else {
        // Reduced polling interval for faster updates
        setTimeout(() => pollStatus(taskId), 1000); // 1 second instead of 2
      }
    } catch (error) {
      console.error('Error checking status:', error);
      showToastMessage('Error checking status', 'error');
      setIsLoading(false);
    }
  }, [API_URL, showToastMessage]);

  // Optimized submit handler
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

    setIsLoading(true);
    setCurrentTask(null);
    setCloneResult(null);
    setShowResults(false);
    showToastMessage('Starting website cloning...', 'success');
    
    try {
      const response = await fetch(`${API_URL}/clone`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          url: url.trim(),
          // Add speed optimization preferences
          preferences: {
            fast_mode: true,
            skip_heavy_analysis: true
          }
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.task_id) {
        showToastMessage('Cloning started! Monitoring progress...', 'success');
        pollStatus(data.task_id);
      } else {
        showToastMessage('Failed to start cloning task', 'error');
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error cloning website:', error);
      showToastMessage(error instanceof Error ? error.message : 'Failed to clone website. Please try again.', 'error');
      setIsLoading(false);
    }
  }, [url, isValidUrl, showToastMessage, API_URL, pollStatus]);

  // Handle navigation back from results
  const handleBackFromResults = useCallback(() => {
    setShowResults(false);
    setCloneResult(null);
    setCurrentTask(null);
    setUrl('');
  }, []);

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
          
          {/* Main Headline */}
          <h1 className="text-6xl md:text-7xl font-serif mb-6 leading-tight text-white italic">
            Clone a website in seconds
          </h1>
          
          <p className="text-xl font-grotesk text-gray-300 mb-12 font-normal">
            AI-powered website cloning with clean, modern code
          </p>
          
          {/* Search Interface */}
          <div className="max-w-4xl mx-auto mb-8">
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
                      disabled={isLoading}
                      onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
                    />
                  </div>
                  <button 
                    onClick={handleSubmit}
                    disabled={isLoading || !url.trim()}
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

          {/* Progress Section - Simplified for speed */}
          {currentTask && isLoading && (
            <div className="max-w-2xl mx-auto mb-8">
              <div className="bg-gray-900/50 border border-gray-700 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-white">Cloning Progress</h3>
                  <span className="text-sm text-gray-400">
                    {Math.round(currentTask.progress * 100)}%
                  </span>
                </div>
                
                {/* Simplified Progress Bar */}
                <div className="w-full bg-gray-800 rounded-full h-2 mb-4">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${currentTask.progress * 100}%` }}
                  />
                </div>
                
                <p className="text-sm text-gray-400">{currentTask.message}</p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Optimized Toast Notification */}
      {showToast && (
        <div className="fixed top-4 right-4 z-50">
          <div className={`${
            toastType === 'success' ? 'bg-green-600' : 'bg-red-600'
          } text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-slideIn`}>
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Optimized CSS */}
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
          animation: slideIn 0.2s ease-out;
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

// import React, { useState, useEffect } from 'react';
// import { Globe, Download, CheckCircle, Play, Sparkles } from 'lucide-react';
// import Head from 'next/head'; 
// import orchids_logo from '@/public/orchids_logo.jpeg';

// <Head>
//   <link
//     href="https://fonts.googleapis.com/css2?family=Radley&family=HK+Grotesk:wght@400;500;700&display=swap"
//     rel="stylesheet"
//   />
// </Head>

// interface CloneStatus {
//   task_id: string;
//   status: string;
//   progress: number;
//   message: string;
//   result?: string;
//   error?: string;
//   url?: string;
// }

// export default function HomePage(): React.JSX.Element {
//   const [url, setUrl] = useState<string>('');
//   const [isLoading, setIsLoading] = useState<boolean>(false);
//   const [status, setStatus] = useState<CloneStatus | null>(null);
//   const [showSuccess, setShowSuccess] = useState<boolean>(false);
//   const [currentText, setCurrentText] = useState<string>('');
//   const [currentIndex, setCurrentIndex] = useState<number>(0);
//   const [isTyping, setIsTyping] = useState<boolean>(true);
//   const [showToast, setShowToast] = useState<boolean>(false);
//   const [toastMessage, setToastMessage] = useState<string>('');

//   const placeholderTexts = [
//     "make me a personal website about animation",
//     "make me a personal website for a software engineer", 
//     "make me an online e-store website to sell candles",
//     "make me a portfolio website for a photographer",
//     "make me a restaurant website with online ordering",
//     "make me a blog website about travel adventures",
//     "make me a fitness coaching website",
//     "make me a real estate agency website"
//   ];

//   useEffect(() => {
//     const currentFullText = placeholderTexts[currentIndex];
    
//     if (isTyping) {
//       if (currentText.length < currentFullText.length) {
//         const timeout = setTimeout(() => {
//           setCurrentText(currentFullText.slice(0, currentText.length + 1));
//         }, 50);
//         return () => clearTimeout(timeout);
//       } else {
//         const timeout = setTimeout(() => {
//           setIsTyping(false);
//         }, 2000);
//         return () => clearTimeout(timeout);
//       }
//     } else {
//       if (currentText.length > 0) {
//         const timeout = setTimeout(() => {
//           setCurrentText(currentText.slice(0, -1));
//         }, 30);
//         return () => clearTimeout(timeout);
//       } else {
//         setCurrentIndex((prev) => (prev + 1) % placeholderTexts.length);
//         setIsTyping(true);
//       }
//     }
//   }, [currentText, currentIndex, isTyping, placeholderTexts]);

//   const handleSubmit = async (e: React.FormEvent): Promise<void> => {
//     e.preventDefault();
    
//     if (!url.trim()) {
//       setToastMessage('Please enter a URL');
//       setShowToast(true);
//       setTimeout(() => setShowToast(false), 3000);
//       return;
//     }

//     setIsLoading(true);
//     setToastMessage('Cloning startedd! (Demo)');
//     setShowToast(true);
//     setTimeout(() => setShowToast(false), 3000);
    
//     // Demo functionality
//     setTimeout(() => {
//       setIsLoading(false);
//       setToastMessage('Website cloned successfully!');
//       setShowToast(true);
//       setTimeout(() => setShowToast(false), 3000);
//     }, 2000);
//   };

//   return (
//     <div className="min-h-screen bg-black relative">
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
//             Make a website in seconds
//           </h1>
          
//           <p className="text-xl font-grotesk text-gray-300 mb-12 font-normal">
//             Start, iterate, and launch your website all in one place
//           </p>
          
//           {/* Search Interface */}
//           <form onSubmit={handleSubmit}>
//             <div className="max-w-4xl mx-auto mb-8">
//               <div className="relative">
//                 <div className="bg-gray-900 border border-gray-700 rounded-2xl p-2">
//                   <div className="flex items-center space-x-2">
//                     <div className="flex-1 relative">
//                       <input
//                         type="text"
//                         value={url}
//                         onChange={(e) => setUrl(e.target.value)}
//                         placeholder={currentText + (isTyping && currentText.length < placeholderTexts[currentIndex].length ? '|' : '')}
//                         className="w-full bg-transparent text-white placeholder-gray-400 px-6 py-4 rounded-xl focus:outline-none text-lg font-normal"
//                         disabled={isLoading}
//                       />
//                     </div>
//                     <button 
//                       type="submit"
//                       disabled={isLoading || !url.trim()}
//                       className="bg-gray-600 hover:bg-gray-500 text-white p-4 rounded-xl transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
//                     >
//                       {isLoading ? (
//                         <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
//                       ) : (
//                         <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
//                           <path d="M10 18a7.952 7.952 0 0 0 4.897-1.688l4.396 4.396 1.414-1.414-4.396-4.396A7.952 7.952 0 0 0 18 10c0-4.411-3.589-8-8-8s-8 3.589-8 8 3.589 8 8 8zm0-14c3.309 0 6 2.691 6 6s-2.691 6-6 6-6-2.691-6-6 2.691-6 6-6z"/>
//                         </svg>
//                       )}
//                     </button>
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </form>
//         </div>
//       </main>

//       {/* Toast Notification */}
//       {showToast && (
//         <div className="fixed top-4 right-4 z-50">
//           <div className="bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-slideIn">
//             <CheckCircle className="w-5 h-5" />
//             <span className="font-medium">{toastMessage}</span>
//           </div>
//         </div>
//       )}

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
//           animation: slideIn 0.3s ease-out;
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
// anthropic api key environment variable required