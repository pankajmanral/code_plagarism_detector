import { useState } from 'react';
import { Header } from './components/Header';
import { Upload } from './components/Upload';
import { Results } from './components/Results';
import { History } from './components/History';
import { Shield } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState('upload'); // 'upload', 'results', 'history'
  const [analysisData, setAnalysisData] = useState(null);

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    setCurrentView('results');
  };

  const clearResults = () => {
    setAnalysisData(null);
    setCurrentView('upload');
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-50 selection:bg-blue-500/30">
      <div className="fixed inset-0 z-[-1] pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] opacity-20 blur-[120px] bg-gradient-to-r from-blue-600 to-emerald-600 rounded-full"></div>
      </div>

      <Header currentView={currentView} setCurrentView={setCurrentView} />

      <main className="container mx-auto px-4 py-12 md:py-20 relative z-10">
        {currentView === 'upload' && (
          <Upload onAnalysisComplete={handleAnalysisComplete} />
        )}
        
        {currentView === 'results' && (
          <Results data={analysisData} onBack={clearResults} />
        )}

        {currentView === 'history' && (
          <History />
        )}
      </main>

      <footer className="mt-20 py-8 border-t border-slate-800 text-center text-slate-500">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Shield className="w-5 h-5 text-slate-400" />
          <span className="font-semibold text-slate-400">CodePlagiarism Detector</span>
        </div>
        <p className="text-sm">Powered by AST + ML Analysis</p>
      </footer>
    </div>
  );
}

export default App;
