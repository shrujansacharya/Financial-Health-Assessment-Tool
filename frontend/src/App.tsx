import { useState } from 'react'
import Upload from './components/Upload'
import ChatInterface from './components/ChatInterface'; // Import

import Dashboard from './components/Dashboard'
import { Activity, Languages } from 'lucide-react'
import type { FinancialData, Language } from './types'
import { translations } from './translations'
import { Analytics } from "@vercel/analytics/react"

function App() {
  const [data, setData] = useState<FinancialData | null>(null);
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState<Language>('en');

  const t = translations[lang];

  const handleUploadSuccess = (responseData: FinancialData) => {
    setData(responseData);
    setLoading(false);
  };

  const toggleLang = () => {
    setLang(prev => prev === 'en' ? 'hi' : 'en');
  };

  return (
    <div className="min-h-screen font-sans selection:bg-primary selection:text-white">
      <header className="sticky top-0 z-50 backdrop-blur-md border-b border-white/5 bg-background-deep/80">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-gradient-to-br from-primary to-secondary rounded-xl shadow-lg shadow-primary/20">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              FinHealth <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">AI</span>
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={toggleLang}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-white/10 hover:bg-white/5 transition-colors text-sm text-gray-300 font-medium"
            >
              <Languages size={16} />
              {lang === 'en' ? 'English' : 'हिंदी'}
            </button>

            {data && (
              <button
                onClick={() => setData(null)}
                className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors font-medium"
              >
                {t.analyzeNew}
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10">
        {!data ? (
          <Upload onUploadSuccess={handleUploadSuccess} setLoading={setLoading} loading={loading} lang={lang} t={t} />
        ) : (
          <>
            <Dashboard data={data} lang={lang} t={t} />
            <ChatInterface />
          </>
        )}
      </main>

      <footer className="mt-20 border-t border-white/5 py-8 text-center">
        <p className="text-gray-500 text-sm font-medium">
          Financial Health Analysis System
        </p>
      </footer>
      <Analytics />
    </div>
  )
}

export default App
