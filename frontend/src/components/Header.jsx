import { FileX2 } from "lucide-react";

export function Header({ currentView, setCurrentView }) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur-md">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2 text-blue-400 font-semibold text-lg hover:text-blue-300 transition-colors cursor-pointer" onClick={() => setCurrentView('upload')}>
          <FileX2 className="w-6 h-6" />
          <span>PlagiarismDetector</span>
        </div>
        <nav className="flex items-center gap-6">
          <button
            onClick={() => setCurrentView('upload')}
            className={`text-sm font-medium transition-colors hover:text-white ${currentView === 'upload' ? 'text-white' : 'text-slate-400'}`}
          >
            New Scan
          </button>
          <button
            onClick={() => setCurrentView('history')}
            className={`text-sm font-medium transition-colors hover:text-white ${currentView === 'history' ? 'text-white' : 'text-slate-400'}`}
          >
            History
          </button>
        </nav>
      </div>
    </header>
  );
}
