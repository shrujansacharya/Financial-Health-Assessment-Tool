import { useRef, useState } from 'react';
import { Upload as UploadIcon, FileSpreadsheet, Loader2, AlertCircle } from 'lucide-react';
import type { Language } from '../types';

interface UploadProps {
    onUploadSuccess: (data: any) => void;
    setLoading: (loading: boolean) => void;
    loading: boolean;
    lang: Language;
    t: any;
}

export default function Upload({ onUploadSuccess, setLoading, loading, lang, t }: UploadProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [error, setError] = useState<string | null>(null);
    const [dragActive, setDragActive] = useState(false);

    const [industry, setIndustry] = useState('');

    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const handleFileSelect = (file: File) => {
        if (!file) return;

        if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx') && !file.name.endsWith('.pdf')) {
            setError("Only .csv, .xlsx, or .pdf files are allowed.");
            return;
        }

        setError(null);
        setSelectedFile(file);
    };

    const handleAnalyze = async () => {
        if (!selectedFile) return;

        if (!industry) {
            setError("Please select an industry to continue.");
            return;
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('language', lang);
        formData.append('industry', industry);

        try {
            const apiUrl = import.meta.env.VITE_API_URL;
            const response = await fetch(`${apiUrl}/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Upload failed');
            }

            const data = await response.json();
            onUploadSuccess(data);
        } catch (err: any) {
            setError(err.message);
            setLoading(false);
        }
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
            <div className="text-center mb-12 max-w-2xl px-4">
                <h2 className="text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent mb-6 leading-tight">
                    {t.title}
                </h2>
                <p className="text-gray-400 text-lg leading-relaxed font-light">
                    {t.subtitle}
                </p>
            </div>

            {/* Industry Selector */}
            <div className="mb-8 w-full max-w-xs space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">
                    Select Industry <span className="text-red-400">*</span>
                </label>
                <div className="relative bg-background-card rounded-lg border border-white/10 group hover:border-primary/50 transition-colors">
                    <select
                        value={industry}
                        onChange={(e) => setIndustry(e.target.value)}
                        className="w-full appearance-none bg-transparent text-white border-0 py-3 px-4 pr-8 rounded-lg outline-none focus:ring-2 focus:ring-primary/50 cursor-pointer"
                    >
                        <option value="" disabled className="bg-background-card text-gray-400">Select your industry...</option>
                        <option value="Retail" className="bg-background-card">Retail</option>
                        <option value="E-commerce" className="bg-background-card">E-commerce</option>
                        <option value="Manufacturing" className="bg-background-card">Manufacturing</option>
                        <option value="Services" className="bg-background-card">Services</option>
                        <option value="Agriculture" className="bg-background-card">Agriculture</option>
                        <option value="Logistics" className="bg-background-card">Logistics & Supply Chain</option>
                        <option value="Technology" className="bg-background-card">Technology & SaaS</option>
                        <option value="Healthcare" className="bg-background-card">Healthcare</option>
                        <option value="Construction" className="bg-background-card">Construction</option>
                        <option value="Other" className="bg-background-card">Other</option>
                    </select>
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                </div>
            </div>

            <div
                className={`relative w-full max-w-xl glass-panel p-12 transition-all duration-300 ${dragActive
                    ? 'border-primary bg-primary/10 ring-2 ring-primary/20 scale-[1.02]'
                    : 'border-white/5 hover:border-white/10'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <div className="flex flex-col items-center gap-8">
                    <div className={`p-6 rounded-2xl transition-all duration-500 ${loading ? 'bg-primary/20 shadow-[0_0_30px_rgba(79,70,229,0.3)]' : 'bg-background-card border border-white/5'}`}>
                        {loading ? (
                            <Loader2 className="w-12 h-12 text-primary animate-spin" />
                        ) : (
                            <UploadIcon className="w-12 h-12 text-primary" />
                        )}
                    </div>

                    <div className="text-center space-y-4">
                        {loading ? (
                            <div className="space-y-2">
                                <h3 className="text-xl font-semibold text-white tracking-wide">{t.analyzing}</h3>
                                <div className="h-1 w-32 bg-gray-800 rounded-full overflow-hidden mx-auto">
                                    <div className="h-full bg-primary animate-[loading_1s_ease-in-out_infinite]"></div>
                                </div>
                            </div>
                        ) : selectedFile ? (
                            <div className="space-y-4 animate-fade-in">
                                <div>
                                    <h3 className="text-lg font-bold text-white mb-1">File Selected</h3>
                                    <p className="text-emerald-400 font-medium bg-emerald-500/10 px-3 py-1 rounded-full inline-block border border-emerald-500/20">{selectedFile.name}</p>
                                    <p className="text-gray-500 text-xs mt-2">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                                </div>
                                <div className="flex gap-3 justify-center">
                                    <button
                                        onClick={() => setSelectedFile(null)}
                                        className="px-4 py-2 rounded-lg border border-white/10 hover:bg-white/5 text-gray-300 text-sm transition-colors"
                                    >
                                        Change File
                                    </button>
                                    <button
                                        onClick={handleAnalyze}
                                        className="btn-primary"
                                    >
                                        Analyze Financials
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-2">{t.dragDrop}</h3>
                                    <p className="text-gray-400">{t.browse}</p>
                                </div>
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="btn-primary mt-2"
                                >
                                    {t.selectFile}
                                </button>
                            </>
                        )}
                    </div>

                    {!loading && !selectedFile && (
                        <div className="flex gap-6 text-xs font-medium text-gray-500 mt-2 border-t border-white/5 pt-6 w-full justify-center opacity-80">
                            <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 transition-colors"><FileSpreadsheet size={14} className="text-emerald-400" /> CSV</span>
                            <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 transition-colors"><FileSpreadsheet size={14} className="text-emerald-400" /> XLSX</span>
                            <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 transition-colors"><FileSpreadsheet size={14} className="text-red-400" /> PDF</span>
                        </div>
                    )}
                </div>

                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                    accept=".csv,.xlsx,.pdf"
                />
            </div>

            {error && (
                <div className="mt-8 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-200 animate-fade-in backdrop-blur-sm">
                    <AlertCircle size={20} className="shrink-0" />
                    <span className="font-medium">{error}</span>
                </div>
            )}

            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-center max-w-5xl w-full">
                <div className="px-6 py-8 glass-panel border-white/5 hover:bg-white/[0.02]">
                    <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
                        <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                    </div>
                    <strong className="text-white block mb-2 text-lg">{t.secure}</strong>
                    <p className="text-gray-400 text-sm leading-relaxed">{t.secureDesc}</p>
                </div>
                <div className="px-6 py-8 glass-panel border-white/5 hover:bg-white/[0.02]">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
                        <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    </div>
                    <strong className="text-white block mb-2 text-lg">{t.instant}</strong>
                    <p className="text-gray-400 text-sm leading-relaxed">{t.instantDesc}</p>
                </div>
                <div className="px-6 py-8 glass-panel border-white/5 hover:bg-white/[0.02]">
                    <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center mx-auto mb-4">
                        <svg className="w-5 h-5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                    </div>
                    <strong className="text-white block mb-2 text-lg">{t.ai}</strong>
                    <p className="text-gray-400 text-sm leading-relaxed">{t.aiDesc}</p>
                </div>
            </div>
        </div>
    );
}
