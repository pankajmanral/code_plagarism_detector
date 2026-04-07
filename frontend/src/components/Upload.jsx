import { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { UploadCloud, Code, FileText, CheckCircle2, ChevronRight, Loader2 } from 'lucide-react';
import { cn } from '../utils';

const API_URL = 'http://localhost:8000';

export function Upload({ onAnalysisComplete }) {
    const [method, setMethod] = useState('text'); // text or file
    const [language, setLanguage] = useState('python');
    const [code1, setCode1] = useState('');
    const [code2, setCode2] = useState('');
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleTextSubmit = async () => {
        if (!code1.trim() || !code2.trim()) {
            setError('Please provide code for both inputs.');
            return;
        }
        setLoading(true);
        setError('');
        try {
            const response = await axios.post(`${API_URL}/compare`, {
                code1,
                code2,
                language
            });
            onAnalysisComplete(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred during analysis.');
        } finally {
            setLoading(false);
        }
    };

    const handleFileSubmit = async () => {
        if (files.length < 2) {
            setError('Please select at least 2 python files.');
            return;
        }
        setLoading(true);
        setError('');
        const formData = new FormData();
        Array.from(files).forEach((file) => {
            formData.append('files', file);
        });

        try {
            const response = await axios.post(`${API_URL}/upload?language=${language}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            // For simplicity, we just pass the first pairwise result
            const firstResult = response.data.results[0];
            if (firstResult) {
                onAnalysisComplete({
                    ...firstResult,
                    isMultiple: response.data.results.length > 1,
                    allResults: response.data.results
                });
            } else {
                setError('No results returned.');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred during file upload.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto w-full"
        >
            <div className="text-center mb-10">
                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
                    Source Code Analysis
                </h1>
                <p className="text-slate-400 text-lg">
                    Detect structural similarity and code plagiarism using advanced AST parsing and ML analysis.
                </p>
            </div>

            <div className="glass-panel p-2 flex bg-slate-800/50 mb-8 rounded-xl max-w-sm mx-auto">
                <button
                    onClick={() => setMethod('text')}
                    className={cn(
                        "flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-lg font-medium transition-all",
                        method === 'text' ? "bg-blue-600 text-white shadow-lg" : "text-slate-400 hover:text-white"
                    )}
                >
                    <Code className="w-4 h-4" /> Paste Code
                </button>
                <button
                    onClick={() => setMethod('file')}
                    className={cn(
                        "flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-lg font-medium transition-all",
                        method === 'file' ? "bg-blue-600 text-white shadow-lg" : "text-slate-400 hover:text-white"
                    )}
                >
                    <UploadCloud className="w-4 h-4" /> Upload Files
                </button>
            </div>

            <div className="max-w-sm mx-auto mb-8">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 text-center">
                    Programming Language
                </label>
                <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg py-2 px-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                </select>
            </div>

            <div className="glass-panel p-6 md:p-8">
                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 flex items-start gap-3">
                        <div className="mt-0.5">⚠️</div>
                        <div>{error}</div>
                    </div>
                )}

                {method === 'text' ? (
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="flex flex-col h-64 md:h-96">
                            <label className="text-sm font-semibold text-slate-300 mb-2 flex justify-between items-center">
                                <span>Code Snippet 1</span>
                                <span className="text-xs text-slate-500 font-normal uppercase">{language}</span>
                            </label>
                            <textarea
                                value={code1}
                                onChange={(e) => setCode1(e.target.value)}
                                className="flex-1 w-full bg-slate-900 border border-slate-700 rounded-lg p-4 font-mono text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none hide-scrollbar"
                                placeholder="def hello_world():..."
                                spellCheck="false"
                            />
                        </div>
                        <div className="flex flex-col h-64 md:h-96">
                            <label className="text-sm font-semibold text-slate-300 mb-2 flex justify-between items-center">
                                <span>Code Snippet 2</span>
                                <span className="text-xs text-slate-500 font-normal uppercase">{language}</span>
                            </label>
                            <textarea
                                value={code2}
                                onChange={(e) => setCode2(e.target.value)}
                                className="flex-1 w-full bg-slate-900 border border-slate-700 rounded-lg p-4 font-mono text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none hide-scrollbar"
                                placeholder="def another_function():..."
                                spellCheck="false"
                            />
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-slate-700 rounded-xl bg-slate-900/50 hover:bg-slate-800/50 transition-colors">
                        <FileText className="w-16 h-16 text-slate-500 mb-4" />
                        <p className="text-slate-300 font-medium mb-2 text-center text-lg">Drag & drop files here</p>
                        <p className="text-slate-500 text-sm mb-6 text-center">or click below to select files from your computer</p>

                        <input
                            type="file"
                            id="file-upload"
                            multiple
                            accept={
                                language === 'python' ? '.py' :
                                    language === 'javascript' ? '.js,.jsx' :
                                        language === 'java' ? '.java' :
                                            language === 'cpp' ? '.cpp,.h,.hpp' : '.py'
                            }
                            className="hidden"
                            onChange={(e) => {
                                const selectedFiles = Array.from(e.target.files);
                                if (selectedFiles.length > 2) {
                                    setError('Please select exactly 2 files for comparison.');
                                    setFiles(selectedFiles.slice(0, 2));
                                } else {
                                    setError('');
                                    setFiles(selectedFiles);
                                }
                            }}
                        />
                        <label
                            htmlFor="file-upload"
                            className="px-6 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg font-medium cursor-pointer transition-colors shadow-sm text-white"
                        >
                            Select Files
                        </label>

                        {files.length > 0 && (
                            <div className="mt-8 w-full max-w-md">
                                <h4 className="text-sm font-medium text-slate-400 mb-3">{files.length} files selected:</h4>
                                <div className="space-y-2">
                                    {Array.from(files).map((f, i) => (
                                        <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                            <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                                            <span className="text-sm font-medium truncate">{f.name}</span>
                                            <span className="text-xs text-slate-500 ml-auto">{(f.size / 1024).toFixed(1)} KB</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                <div className="mt-8 flex justify-center">
                    <button
                        onClick={method === 'text' ? handleTextSubmit : handleFileSubmit}
                        disabled={loading || (method === 'text' && (!code1.trim() || !code2.trim())) || (method === 'file' && files.length !== 2)}
                        className="group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-full bg-blue-600 px-8 py-3.5 font-medium text-white shadow-lg shadow-blue-600/30 transition-all hover:bg-blue-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span>Analyzing AST Structure...</span>
                            </>
                        ) : (
                            <>
                                <span>Analyze Similarity</span>
                                <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                            </>
                        )}
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
