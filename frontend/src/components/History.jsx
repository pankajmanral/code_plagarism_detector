import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Clock, AlertCircle, CheckCircle, ShieldAlert, Trash2, Loader2 } from 'lucide-react';
import { cn } from '../utils';

const API_URL = 'http://localhost:8000';

export function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/history?limit=50`);
      setHistory(res.data.items);
      setError(null);
    } catch (err) {
      setError('Failed to fetch history.');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (!window.confirm("Are you sure you want to clear all history?")) return;
    try {
      await axios.delete(`${API_URL}/history`);
      setHistory([]);
    } catch (err) {
      alert("Failed to clear history.");
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-5xl mx-auto w-full"
    >
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3 mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
            <Clock className="w-8 h-8 text-blue-500" /> Analysis History
          </h2>
          <p className="text-slate-400">Past code plagiarism checks and similarity scores.</p>
        </div>
        <button
          onClick={clearHistory}
          disabled={history.length === 0}
          className="flex items-center gap-2 text-red-400 hover:text-red-300 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 rounded-lg transition-colors disabled:opacity-50"
        >
          <Trash2 className="w-4 h-4" /> Clear All
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-20 text-slate-400 gap-3">
          <Loader2 className="w-6 h-6 animate-spin" /> Loading history...
        </div>
      ) : error ? (
        <div className="glass-panel p-6 text-center text-red-400 border-red-500/20 bg-red-500/5">
          {error}
        </div>
      ) : history.length === 0 ? (
        <div className="glass-panel p-16 text-center border-slate-700/50 bg-slate-800/20">
          <ShieldAlert className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2 text-slate-300">No History Found</h3>
          <p className="text-slate-500">Run a code comparison to see the results here.</p>
        </div>
      ) : (
        <div className="glass-panel overflow-hidden bg-slate-800/30 border-slate-700">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-700 bg-slate-800/80">
                  <th className="p-4 text-sm font-semibold tracking-wide text-slate-300">Date</th>
                  <th className="p-4 text-sm font-semibold tracking-wide text-slate-300">Files Compared</th>
                  <th className="p-4 text-sm font-semibold tracking-wide text-center text-slate-300">Similarity</th>
                  <th className="p-4 text-sm font-semibold tracking-wide text-center text-slate-300">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="p-4 text-slate-400 text-sm whitespace-nowrap">
                      {new Date(item.timestamp).toLocaleString(undefined, { 
                        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
                      })}
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className="bg-slate-800 px-2 py-1 rounded text-xs border border-slate-700 font-mono text-slate-300 max-w-[150px] truncate">
                          {item.file1_name || 'Snippet 1'}
                        </span>
                        <span className="text-slate-500 text-xs">vs</span>
                        <span className="bg-slate-800 px-2 py-1 rounded text-xs border border-slate-700 font-mono text-slate-300 max-w-[150px] truncate">
                          {item.file2_name || 'Snippet 2'}
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <span className="font-mono font-medium text-white">
                        {Math.round(item.similarity_score * 100)}%
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex justify-center">
                        <span className={cn(
                          "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border",
                          item.plagiarism 
                            ? "bg-red-500/10 text-red-400 border-red-500/20" 
                            : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        )}>
                          {item.plagiarism ? <AlertCircle className="w-3.5 h-3.5" /> : <CheckCircle className="w-3.5 h-3.5" />}
                          {item.plagiarism ? 'High Risk' : 'Low Risk'}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </motion.div>
  );
}
