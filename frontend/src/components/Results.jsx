import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, ChevronLeft, Percent, Info } from 'lucide-react';
import { cn } from '../utils';

export function Results({ data, onBack }) {
  if (!data) return null;

  const isPlagiarism = data.plagiarism;
  const score = Math.round(data.similarity_score * 100);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-4xl mx-auto w-full"
    >
      <button 
        onClick={onBack}
        className="flex items-center gap-2 text-slate-400 hover:text-white mb-6 transition-colors"
      >
        <ChevronLeft className="w-4 h-4" /> Back to Upload
      </button>

      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold mb-2">Analysis Results</h2>
        <p className="text-slate-400">Detailed breakdown of the similarity comparison.</p>
      </div>

      <div className={cn(
        "glass-panel p-8 mb-8 text-center",
        isPlagiarism ? "border-red-500/30 shadow-red-500/10" : "border-emerald-500/30 shadow-emerald-500/10"
      )}>
        <div className="flex justify-center mb-6">
          <div className="relative">
            <svg className="w-40 h-40 transform -rotate-90">
              <circle
                className="text-slate-800"
                strokeWidth="12"
                stroke="currentColor"
                fill="transparent"
                r="70"
                cx="80"
                cy="80"
              />
              <circle
                className={isPlagiarism ? "text-red-500" : "text-emerald-500"}
                strokeWidth="12"
                strokeDasharray={440}
                strokeDashoffset={440 - (440 * score) / 100}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="70"
                cx="80"
                cy="80"
                style={{ transition: 'stroke-dashoffset 1.5s ease-out' }}
              />
            </svg>
            <div className="absolute top-0 left-0 w-full h-full flex flex-col justify-center items-center">
              <span className="text-4xl font-bold">{score}</span>
              <Percent className="w-5 h-5 text-slate-400" />
            </div>
          </div>
        </div>

        <h3 className="text-2xl font-bold mb-2 flex items-center justify-center gap-2">
          {isPlagiarism ? (
            <><AlertTriangle className="text-red-500 w-6 h-6" /> <span className="text-red-400">Plagiarism Detected</span></>
          ) : (
            <><CheckCircle className="text-emerald-500 w-6 h-6" /> <span className="text-emerald-400">Low Similarity</span></>
          )}
        </h3>
        <p className="text-slate-400 max-w-lg mx-auto">
          {isPlagiarism 
            ? "The scanned code shows significant structural similarities suggesting potential plagiarism."
            : "The scanned code appears structurally distinct with low risk of plagiarism."}
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 bg-slate-800/40">
          <h4 className="text-lg font-semibold mb-4 border-b border-slate-700 pb-2 flex items-center gap-2">
            <Info className="w-5 h-5 text-blue-400" /> Similarity Metrics
          </h4>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Cosine Similarity</span>
              <span className="font-mono text-white text-lg">{(data.details.cosine_similarity * 100).toFixed(1)}%</span>
            </div>
            {data.details.jaccard_similarity !== undefined && (
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Jaccard Similarity</span>
                <span className="font-mono text-white text-lg">{(data.details.jaccard_similarity * 100).toFixed(1)}%</span>
              </div>
            )}
            <div className="flex justify-between items-center">
              <span className="text-slate-400">AST Nodes (Code 1)</span>
              <span className="font-mono text-white">{data.details.ast_nodes_1}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">AST Nodes (Code 2)</span>
              <span className="font-mono text-white">{data.details.ast_nodes_2}</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 bg-slate-800/40">
          <h4 className="text-lg font-semibold mb-4 border-b border-slate-700 pb-2 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-blue-400" /> Machine Learning Analysis
          </h4>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">KNN Distance</span>
              <span className="font-mono text-white text-lg">{data.details.knn_distance?.toFixed(4) ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Risk Assessment</span>
              <span className={cn(
                "px-2 py-1 rounded text-sm font-medium",
                data.plagiarism ? "bg-red-500/20 text-red-400" : "bg-emerald-500/20 text-emerald-400"
              )}>
                {data.plagiarism ? "HIGH" : "LOW"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
