import { PieChart, Pie, Cell, ResponsiveContainer, AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts';
import { TrendingUp, AlertTriangle, CheckCircle, Activity, Building2, Wallet, FileText, BadgeCheck, Zap } from 'lucide-react';
import type { FinancialData, Language } from '../types';

export default function Dashboard({ data, lang, t }: { data: FinancialData, lang: Language, t: any }) {
    const getScoreColor = (score: number) => {
        if (score >= 80) return '#10b981';
        if (score >= 50) return '#f59e0b';
        return '#ef4444';
    };

    const scoreColor = getScoreColor(data.score);

    const gaugeData = [
        { name: 'Score', value: data.score },
        { name: 'Remaining', value: 100 - data.score },
    ];

    const aiInsights = (lang === 'hi' && (data as any).ai_insights_hi) ? (data as any).ai_insights_hi : data.ai_insights;

    return (
        <div className="animate-fade-in pb-10 space-y-8">
            {/* Top Stats Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">

                {/* Health Score Card */}
                <div className="glass-panel p-8 flex flex-col items-center justify-center relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-50"></div>
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-secondary/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                    <h2 className="text-gray-400 font-medium mb-6 uppercase tracking-widest text-xs flex items-center gap-2 relative z-10">
                        <Activity size={14} className="text-primary" /> {t.score}
                    </h2>

                    <div className="relative w-56 h-56 z-10">
                        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                            <PieChart>
                                <Pie
                                    data={gaugeData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={75}
                                    outerRadius={95}
                                    startAngle={180}
                                    endAngle={0}
                                    paddingAngle={0}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    <Cell key="score" fill={scoreColor} className="drop-shadow-[0_0_10px_rgba(0,0,0,0.5)]" />
                                    <Cell key="remaining" fill="rgba(255,255,255,0.05)" />
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex flex-col items-center justify-center mt-8">
                            <span className="text-6xl font-bold text-white tracking-tighter drop-shadow-lg">{data.score}</span>
                            <span className="text-sm text-gray-400 font-medium">/ 100</span>
                        </div>
                    </div>
                    <div className="mt-[-24px] text-center relative z-10">
                        <span className={`px-4 py-1.5 rounded-full text-xs font-bold border ${data.score >= 80 ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-amber-500/10 border-amber-500/20 text-amber-400'}`}>
                            {data.score >= 80 ? 'EXCELLENT' : data.score >= 50 ? 'FAIR' : 'CRITICAL'}
                        </span>
                    </div>
                </div>

                {/* Risk Assessment */}
                <div className="glass-panel p-6 flex flex-col">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-gray-400 font-medium uppercase tracking-widest text-xs flex items-center gap-2">
                            <AlertTriangle size={14} className="text-amber-400" /> {t.risk}
                        </h2>
                        <span className="text-[10px] bg-white/5 px-2 py-1 rounded text-gray-500">{data.flags.length} Issues</span>
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
                        {data.flags.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-gray-500 text-sm py-10">
                                <CheckCircle className="text-emerald-500 w-10 h-10 mb-3 opacity-80" />
                                <span className="font-medium">No critical risks identified.</span>
                            </div>
                        ) : (
                            data.flags.map((flag, idx) => (
                                <div key={idx} className="group bg-red-500/5 border border-red-500/10 hover:border-red-500/20 hover:bg-red-500/10 transition-colors p-4 rounded-xl flex justify-between items-center">
                                    <span className="text-red-200 text-sm font-medium pr-4">{flag.type}</span>
                                    <span className="text-[10px] bg-red-500/20 text-red-300 px-2.5 py-1 rounded-md uppercase tracking-wide font-bold shadow-sm">{flag.severity}</span>
                                </div>
                            ))
                        )}
                    </div>

                    <div className="mt-auto pt-4 border-t border-white/5 grid grid-cols-2 gap-4">
                        <div className="bg-white/5 rounded-lg p-3 text-center">
                            <span className="text-[10px] text-gray-500 block uppercase tracking-wide mb-1">Expense Ratio</span>
                            <span className={`text-xl font-bold ${data.metrics.expense_ratio > 0.8 ? 'text-red-400' : 'text-emerald-400'}`}>
                                {(data.metrics.expense_ratio * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div className="bg-white/5 rounded-lg p-3 text-center">
                            <span className="text-[10px] text-gray-500 block uppercase tracking-wide mb-1">Debt Burden</span>
                            <span className={`text-xl font-bold ${data.metrics.debt_burden_ratio > 0.3 ? 'text-red-400' : 'text-emerald-400'}`}>
                                {(data.metrics.debt_burden_ratio * 100).toFixed(0)}%
                            </span>
                        </div>
                    </div>
                </div>

                {/* Advanced Integrations (New Panel) */}
                <div className="glass-panel p-6 flex flex-col gap-5">
                    <div className="flex justify-between items-center">
                        <h2 className="text-gray-400 font-medium uppercase tracking-widest text-xs flex items-center gap-2">
                            <Zap size={14} className="text-yellow-400" /> {t.advanced}
                        </h2>
                        <button
                            onClick={() => alert("Mock Integration: Successfully connected to XYZ Bank API (Sandbox Mode).")}
                            className="text-[10px] bg-primary/20 hover:bg-primary/30 text-primary px-2 py-1 rounded border border-primary/20 transition-colors uppercase font-bold tracking-wide"
                        >
                            + Connect Bank
                        </button>
                    </div>

                    {/* Credit Score */}
                    <div className="bg-white/5 p-4 rounded-xl flex flex-col gap-3 border border-white/5 hover:border-white/10 transition-colors">
                        <div className="flex justify-between items-center">
                            <div className="text-xs text-gray-400 uppercase tracking-wide">{t.creditScore}</div>
                            <div className="text-2xl font-bold text-white font-mono tracking-tight">{data.credit_score || 'N/A'}</div>
                        </div>
                        <div className="h-1.5 w-full bg-gray-700/50 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-blue-600 to-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.5)]" style={{ width: `${((data.credit_score || 300) - 300) / 6}%` }}></div>
                        </div>
                        <div className="text-[9px] text-gray-500 leading-tight">
                            *300–900 range, non-bureau, indicative only. Not a CIBIL score.
                        </div>
                    </div>

                    {/* Tax Status */}
                    <div className="bg-white/5 p-4 rounded-xl flex flex-col gap-2 border border-white/5 hover:border-white/10 transition-colors">
                        <div className="flex justify-between items-start">
                            <div className="flex flex-col">
                                <div className="text-xs text-gray-400 uppercase tracking-wide mb-1 flex items-center gap-1">{t.taxStatus}</div>
                                <div className={`text-base font-bold flex items-center gap-2 ${data.tax_status === 'Compliant' ? 'text-emerald-400' : 'text-amber-400'}`}>
                                    {data.tax_status || 'Pending'}
                                </div>
                            </div>
                            <div className={`p-2 rounded-full ${data.tax_status === 'Compliant' ? 'bg-emerald-500/10' : 'bg-gray-700/30'}`}>
                                <BadgeCheck size={20} className={data.tax_status === 'Compliant' ? 'text-emerald-500' : 'text-gray-500'} />
                            </div>
                        </div>
                        <div className="text-[9px] text-gray-500 leading-tight mt-1">
                            *Based on financial ratios only. Not a statutory compliance check.
                        </div>
                    </div>

                    {/* Forecasting */}
                    <div className="bg-gradient-to-br from-emerald-500/10 to-transparent p-4 rounded-xl border border-emerald-500/20 hover:border-emerald-500/30 transition-colors">
                        <div className="text-xs text-gray-400 uppercase tracking-wide mb-1 flex justify-between">
                            <span>{t.forecast}</span>
                            <span className="bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded text-[10px] font-bold">+5.2%</span>
                        </div>
                        <div className="text-2xl font-bold text-white flex items-baseline gap-1 mt-2">
                            ₹{(data.forecast_next_month || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                            <span className="text-xs font-normal text-gray-500 uppercase tracking-wide">est.</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content Grid: AI & Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">

                {/* AI Insight Panel */}
                <div className="lg:col-span-1 glass-panel p-8 border-primary/20 shadow-[0_0_40px_-10px_rgba(79,70,229,0.15)] flex flex-col">
                    <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5">
                        <div className="relative">
                            <div className="absolute inset-0 bg-primary blur-md opacity-50 animate-pulse"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-primary relative z-10"></div>
                        </div>
                        <h2 className="font-bold text-lg text-transparent bg-clip-text bg-gradient-to-r from-primary to-white tracking-tight">
                            {t.insightEngine}
                        </h2>
                    </div>
                    <div className="prose prose-invert prose-sm text-gray-300 leading-relaxed max-h-[500px] overflow-y-auto custom-scrollbar flex-1">
                        <div className="whitespace-pre-line text-base leading-relaxed font-normal text-gray-200">
                            {aiInsights}
                        </div>
                    </div>
                    <div className="mt-6 pt-6 border-t border-white/5 flex justify-between items-center text-[10px]">
                        <span className="text-gray-600 font-mono uppercase tracking-wider">{t.mockGPT}</span>
                        <button
                            onClick={() => {
                                const reportId = (data as any).report_id;
                                if (reportId) {
                                    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                                    window.open(`${apiUrl}/report/${reportId}`, '_blank');
                                } else {
                                    alert("Report generation failed or not available.");
                                }
                            }}
                            className="flex items-center gap-2 text-primary hover:text-white transition-colors text-xs font-medium group cursor-pointer"
                        >
                            <FileText size={14} className="group-hover:scale-110 transition-transform" /> {t.investorReport}
                        </button>
                    </div>
                </div>

                {/* Charts Section */}
                <div className="lg:col-span-2 space-y-8 flex flex-col">

                    {/* Revenue vs Expenses */}
                    <div className="glass-panel p-8">
                        <h3 className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-6 flex items-center gap-2">
                            <TrendingUp size={14} className="text-emerald-400" /> {t.revExp}
                        </h3>
                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                                <AreaChart data={data.charts_data}>
                                    <defs>
                                        <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorExp" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                    <XAxis dataKey="Month" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value / 1000}k`} dx={-10} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1E2330', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.5)', color: '#fff' }}
                                        itemStyle={{ fontSize: '13px', fontWeight: 500 }}
                                        cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }}
                                    />
                                    <Area type="monotone" dataKey="Revenue" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" activeDot={{ r: 6, strokeWidth: 0 }} />
                                    <Area type="monotone" dataKey="Operating Expenses" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorExp)" activeDot={{ r: 6, strokeWidth: 0 }} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {/* Cash Flow */}
                        <div className="glass-panel p-6">
                            <h3 className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-6 flex items-center gap-2">
                                <Wallet size={14} className="text-primary" /> {t.cashFlow}
                            </h3>
                            <div className="h-[200px] w-full">
                                <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                                    <BarChart data={data.charts_data}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                        <XAxis dataKey="Month" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} dy={8} />
                                        <Tooltip
                                            cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                                            contentStyle={{ backgroundColor: '#1E2330', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                                        />
                                        <Bar dataKey="Net Cash Flow" fill="#6366f1" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Expense Breakdown */}
                        <div className="glass-panel p-6">
                            <h3 className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-6 flex items-center gap-2">
                                <Building2 size={14} className="text-secondary" /> {t.outflow}
                            </h3>
                            <div className="h-[200px] w-full flex items-center justify-center relative">
                                <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                                    <PieChart>
                                        <Pie
                                            data={[
                                                { name: 'Operating', value: data.metrics.expense_ratio },
                                                { name: 'Debt Repayment', value: data.metrics.debt_burden_ratio }
                                            ]}
                                            innerRadius={60}
                                            outerRadius={80}
                                            paddingAngle={4}
                                            dataKey="value"
                                            stroke="none"
                                        >
                                            <Cell fill="#f59e0b" />
                                            <Cell fill="#ef4444" />
                                        </Pie>
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#1E2330', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                    <div className="w-20 h-20 rounded-full bg-white/5 blur-xl"></div>
                                </div>
                            </div>
                            <div className="flex justify-center gap-4 text-xs mt-[-10px]">
                                <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-white/5">
                                    <div className="w-2 h-2 rounded-full bg-amber-500"></div> <span className="text-gray-300 font-medium">Operating</span>
                                </div>
                                <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-white/5">
                                    <div className="w-2 h-2 rounded-full bg-red-500"></div> <span className="text-gray-300 font-medium">Debt</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Anomaly Detection Panel (NEW) */}
                    <div className="glass-panel p-8 mt-8 border-red-500/20">
                        <div className="flex items-center gap-3 mb-6">
                            <AlertTriangle size={20} className="text-red-400" />
                            <h3 className="text-gray-200 text-lg font-bold tracking-tight">
                                {t.anomalies || "Anomaly Detection (Beta)"}
                            </h3>
                            <span className="px-2 py-0.5 rounded text-[10px] bg-red-500/10 text-red-400 uppercase font-bold tracking-wider border border-red-500/20">
                                AI Guard
                            </span>
                        </div>

                        {!data.anomalies || data.anomalies.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-10 text-gray-500 gap-3 border border-dashed border-white/5 rounded-xl bg-white/5">
                                <BadgeCheck size={32} className="text-emerald-500/50" />
                                <span className="text-sm font-medium">{t.noAnomalies || "No operational anomalies detected."}</span>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <p className="text-xs text-gray-400 mb-4">{t.anomaliesDesc || "The AI flagged the following unusual transactions:"}</p>
                                <div className="space-y-2 max-h-[250px] overflow-y-auto custom-scrollbar pr-2">
                                    {data.anomalies.map((item, idx) => (
                                        <div key={idx} className="flex justify-between items-center bg-red-500/5 hover:bg-red-500/10 border border-red-500/10 rounded-lg p-3 transition-colors group">
                                            <div className="flex flex-col">
                                                <span className="text-xs text-gray-400 font-mono">{item.Date}</span>
                                                <span className="text-sm text-red-200 font-medium">Unusual Cash Flow</span>
                                            </div>
                                            <div className="text-right">
                                                <span className="block text-red-400 font-bold font-mono">
                                                    {item["Net Cash Flow"] < 0 ? "-" : "+"}₹{Math.abs(item["Net Cash Flow"]).toLocaleString()}
                                                </span>
                                                <span className="text-[10px] text-gray-500 uppercase tracking-wider">
                                                    Rev: {item.Revenue} | Exp: {item["Operating Expenses"]}
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
}
