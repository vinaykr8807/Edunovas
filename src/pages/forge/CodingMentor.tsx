import { useState } from 'react';
import { RoadmapSelector } from '../../components/RoadmapSelector';
export const CodingMentor = ({ onComplete }: any) => {
    const [code, setCode] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysis, setAnalysis] = useState<any>(null);

    const handleAnalyze = async () => {
        setIsAnalyzing(true);
        const formData = new FormData();
        formData.append('code', code);
        formData.append('language', 'python'); // Hardcoded for demo
        const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
        if (user.email) formData.append('user_email', user.email);

        try {
            const res = await fetch('http://127.0.0.1:8000/analyze-code', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            setAnalysis(data);
            if (onComplete) onComplete();
        } catch (error) {
            console.error('Analysis failed:', error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="flex-col gap-xl">
            <header>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Coding Mentor</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Advanced code analysis and architectural mentoring</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '1.5rem', alignItems: 'stretch' }}>
                <div className="flex-col gap-md">
                    <div className="glass-card" style={{ padding: '0', background: '#0d1117', border: '1px solid #30363d', minHeight: '500px', position: 'relative', overflow: 'hidden' }}>
                        <div style={{ background: '#161b22', padding: '0.75rem 1.5rem', borderBottom: '1px solid #30363d', display: 'flex', gap: '1rem' }}>
                            <div className="flex gap-xs">
                                <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ff5f56' }}></span>
                                <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ffbd2e' }}></span>
                                <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#27c93f' }}></span>
                            </div>
                            <span style={{ fontSize: '0.75rem', color: '#8b949e', fontWeight: 700 }}>main.py</span>
                        </div>
                        <textarea
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            style={{
                                width: '100%',
                                minHeight: '440px',
                                background: 'transparent',
                                color: '#e6edf3',
                                border: 'none',
                                outline: 'none',
                                padding: '1.5rem',
                                fontSize: '0.95rem',
                                fontFamily: 'monospace',
                                resize: 'none'
                            }}
                            spellCheck={false}
                        />
                        <div style={{ position: 'absolute', bottom: '1.5rem', right: '1.5rem' }}>
                            <button className="btn btn-primary" onClick={handleAnalyze} disabled={isAnalyzing}>
                                {isAnalyzing ? '⚡ ANALYZING...' : 'RUN ANALYTICS'}
                            </button>
                        </div>
                    </div>

                    <div className="glass-card" style={{ padding: '1.5rem' }}>
                        <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem', fontWeight: 800 }}>COMMON MISTAKE PATTERNS</h3>
                        <div className="flex flex-wrap gap-sm">
                            {(analysis?.mistakes || ['Variable Naming', 'Complexity O(n^2)', 'Edge Cases']).map((m: string) => (
                                <span key={m} className="badge" style={{ borderColor: 'var(--accent-red)', color: 'var(--accent-red)', background: 'rgba(255,100,100,0.05)' }}>{m}</span>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="flex-col gap-md">
                    <RoadmapSelector />
                    {analysis ? (
                        <>
                            <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid var(--accent-red)', background: 'rgba(255,0,0,0.02)' }}>
                                <h4 style={{ fontSize: '0.75rem', color: 'var(--accent-red)', fontWeight: 800, textTransform: 'uppercase', marginBottom: '1rem' }}>Bug Detection</h4>
                                <ul style={{ fontSize: '0.85rem', color: '#e6edf3', listStyle: 'none', padding: 0 }} className="flex-col gap-sm">
                                    {analysis.bugs.map((b: string, i: number) => <li key={i}>• {b}</li>)}
                                    {analysis.bugs.length === 0 && <li>✅ No syntax errors detected.</li>}
                                </ul>
                            </div>

                            <div className="glass-card" style={{ padding: '1.5rem' }}>
                                <h4 style={{ fontSize: '0.75rem', color: 'var(--primary-400)', fontWeight: 800, textTransform: 'uppercase', marginBottom: '1rem' }}>Mentor Explanation</h4>
                                <p style={{ fontSize: '0.85rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                                    {analysis.explanation}
                                </p>
                            </div>

                            <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid var(--accent-green)', background: 'rgba(0,255,128,0.02)' }}>
                                <h4 style={{ fontSize: '0.75rem', color: 'var(--accent-green)', fontWeight: 800, textTransform: 'uppercase', marginBottom: '1rem' }}>Optimized Recommendation</h4>
                                <pre style={{
                                    background: 'rgba(255,255,255,0.02)',
                                    padding: '1rem',
                                    borderRadius: '4px',
                                    fontSize: '0.75rem',
                                    margin: 0,
                                    overflowX: 'auto',
                                    color: 'var(--accent-green)'
                                }}>
                                    <code>{analysis.optimized || analysis.fix}</code>
                                </pre>
                            </div>
                        </>
                    ) : (
                        <div className="glass-card flex-col items-center justify-center" style={{ flex: 1, minHeight: '400px', opacity: 0.5 }}>
                            <span style={{ fontSize: '3rem' }}>🛠️</span>
                            <p>Write or paste code to analyze</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
