import { useEffect, useState } from 'react';

interface AnalysisResult {
    extracted_skills: string[];
    strong_domains: string[];
    missing_skills: string[];
    readiness_score: number;
    roadmap: {
        beginner: string[];
        intermediate: string[];
        advanced: string[];
        projects: string[];
    };
}

interface MarketSkills {
    required_skills: string[];
    nice_to_have_skills: string[];
    top_tools: string[];
    avg_salary_india: string;
    demand_level: string;
    growth_trend: string;
}

const ROLES = ['Frontend Engineer', 'Fullstack Developer', 'Data Scientist', 'DevOps Engineer', 'ML Engineer', 'Backend Engineer', 'Cloud Architect', 'Cyber Security Analyst'];
const DOMAINS = ['Full Stack Development', 'Generative AI & Machine Learning', 'Cyber Security', 'DevOps & Cloud Engineering', 'Cloud Solutions Architecture', 'Core CS & Algorithms', 'Data Engineering & MLOps'];

const saveInterviewSession = async (payload: object) => {
    try {
        const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
        if (!user?.email) return;
        await fetch('http://127.0.0.1:8000/save-interview-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_email: user.email, ...payload })
        });
    } catch { /* silent fail */ }
};

export const InterviewCoach = ({ onComplete }: any) => {
    const [file, setFile] = useState<File | null>(null);
    const [role, setRole] = useState('Frontend Engineer');
    const [domain, setDomain] = useState('Full Stack Development');
    const [level, setLevel] = useState('Junior');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [hasStoredResume, setHasStoredResume] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [marketSkills, setMarketSkills] = useState<MarketSkills | null>(null);
    const [marketLoading, setMarketLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<'gap' | 'roadmap'>('gap');

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
        if (!user.email) return;

        // Fetch both resume status and student profile (which contains domain)
        fetch(`http://127.0.0.1:8000/student/profile?user_email=${encodeURIComponent(user.email)}`)
            .then((r) => r.json())
            .then((data) => {
                if (data.has_stored_resume) setHasStoredResume(true);
                if (data.profile?.domain) {
                    console.log("Auto-selecting domain from profile:", data.profile.domain);
                    setDomain(data.profile.domain);
                }
            })
            .catch((err) => console.error("Error fetching profile context:", err));
    }, []);

    const fetchMarketSkills = async (r: string, d: string) => {
        setMarketLoading(true);
        try {
            const res = await fetch('http://127.0.0.1:8000/teacher/market-skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: r, domain: d })
            });
            const data = await res.json();
            setMarketSkills(data);
        } catch {
            setMarketSkills(null);
        } finally {
            setMarketLoading(false);
        }
    };

    const handleUpload = async () => {
        if (!file && !hasStoredResume) return;
        setIsAnalyzing(true);
        setResult(null);
        setMarketSkills(null);

        const formData = new FormData();
        if (file) formData.append('file', file);
        formData.append('role', role);
        formData.append('level', level);
        const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
        if (user.email) formData.append('user_email', user.email);

        try {
            const [resumeRes] = await Promise.all([
                fetch('http://127.0.0.1:8000/analyze-resume', { method: 'POST', body: formData }),
                fetchMarketSkills(role, domain)
            ]);
            const data = await resumeRes.json();
            setResult(data);
            // Save session to Supabase after state update (300ms allows setMarketSkills to propagate)
            setTimeout(() => {
                const stateSnapshot = marketSkills;
                saveInterviewSession({
                    role,
                    domain,
                    level,
                    readiness_score: data.readiness_score || 0,
                    extracted_skills: data.extracted_skills || [],
                    matched_skills: (data.extracted_skills || []).filter((s: string) =>
                        (stateSnapshot?.required_skills || []).some((r: string) =>
                            r.toLowerCase().includes(s.toLowerCase()) || s.toLowerCase().includes(r.toLowerCase())
                        )
                    ),
                    missing_skills: data.missing_skills || [],
                    market_skills: stateSnapshot?.required_skills || [],
                    strong_domains: data.strong_domains || []
                });
            }, 300);
            if (onComplete) onComplete();
        } catch (e) {
            console.error(e);
        } finally {
            setIsAnalyzing(false);
        }
    };

    // Compute skill gap when both result and market data are available
    const matchedSkills = result && marketSkills
        ? result.extracted_skills.filter(s => marketSkills.required_skills.some(r => r.toLowerCase().includes(s.toLowerCase()) || s.toLowerCase().includes(r.toLowerCase())))
        : [];
    const gapSkills = result && marketSkills
        ? marketSkills.required_skills.filter(r => !result.extracted_skills.some(s => s.toLowerCase().includes(r.toLowerCase()) || r.toLowerCase().includes(s.toLowerCase())))
        : [];

    const demandColor: Record<string, string> = {
        'Very High': 'var(--accent-green)', 'High': 'var(--accent-blue)',
        'Moderate': 'var(--accent-orange)', 'Low': 'var(--accent-red)'
    };

    return (
        <div className="flex-col gap-xl fade-in">
            <header>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 900 }}>🎤 Interview Coach</h2>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.3rem' }}>Resume analysis · Market skill gap detection · Personalized roadmap</p>
            </header>

            {/* Config Panel */}
            <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem', alignItems: 'start' }} className="coach-grid">
                <div className="glass-card flex-col gap-lg" style={{ padding: '1.5rem' }}>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--primary-600)', textTransform: 'uppercase', letterSpacing: '1px' }}>Setup</h3>

                    <div className="flex-col gap-xs">
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700 }}>Target Role</span>
                        <select value={role} onChange={e => setRole(e.target.value)} className="input-field" style={{ padding: '0.65rem' }}>
                            {ROLES.map(r => <option key={r}>{r}</option>)}
                        </select>
                    </div>

                    <div className="flex-col gap-xs">
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700 }}>Learning Domain</span>
                        <select value={domain} onChange={e => setDomain(e.target.value)} className="input-field" style={{ padding: '0.65rem' }}>
                            {DOMAINS.map(d => <option key={d}>{d}</option>)}
                        </select>
                    </div>

                    <div className="flex-col gap-xs">
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700 }}>Experience Level</span>
                        <select value={level} onChange={e => setLevel(e.target.value)} className="input-field" style={{ padding: '0.65rem' }}>
                            {['Fresher', 'Junior', 'Mid-Level', 'Senior'].map(l => <option key={l}>{l}</option>)}
                        </select>
                    </div>

                    {/* Resume Upload */}
                    <div
                        style={{ border: '2px dashed rgba(52,160,90,0.3)', padding: '1.25rem', textAlign: 'center', borderRadius: 'var(--radius-md)', background: 'rgba(52,160,90,0.03)', cursor: 'pointer' }}
                        onDrop={e => { e.preventDefault(); setFile(e.dataTransfer.files[0]); }}
                        onDragOver={e => e.preventDefault()}
                    >
                        <p style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{file ? '📄' : '📎'}</p>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                            {file ? file.name : hasStoredResume ? '✅ Stored resume ready' : 'Upload Resume PDF/DOCX'}
                        </p>
                        <input type="file" hidden id="coach-resume" accept=".pdf,.doc,.docx" onChange={e => setFile(e.target.files?.[0] || null)} />
                        <label htmlFor="coach-resume" className="btn btn-secondary" style={{ cursor: 'pointer', fontSize: '0.78rem', padding: '0.5rem 1rem', display: 'inline-block' }}>
                            Browse
                        </label>
                    </div>

                    <button
                        className="btn btn-primary w-full"
                        disabled={(!file && !hasStoredResume) || isAnalyzing}
                        onClick={handleUpload}
                        style={{ height: '48px', fontSize: '0.9rem', fontWeight: 700 }}
                    >
                        {isAnalyzing ? (
                            <span className="flex items-center justify-center gap-md">
                                <span style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.8s linear infinite', display: 'inline-block' }} />
                                Analyzing…
                            </span>
                        ) : '🔍 Analyze Resume'}
                    </button>

                    {/* Market Pulse Button */}
                    <button
                        className="btn btn-secondary w-full"
                        onClick={() => fetchMarketSkills(role, domain)}
                        disabled={marketLoading}
                        style={{ fontSize: '0.8rem' }}
                    >
                        {marketLoading ? '⏳ Loading market data…' : '📡 Fetch Market Skills (no resume)'}
                    </button>
                </div>

                {/* Results Panel */}
                <div className="flex-col gap-lg">
                    {!result && !marketSkills && !isAnalyzing && !marketLoading && (
                        <div className="glass-card flex-col items-center justify-center fade-in" style={{ minHeight: '420px', textAlign: 'center', gap: '1rem' }}>
                            <span style={{ fontSize: '4rem' }}>🎯</span>
                            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)' }}>Your skill analysis will appear here</h3>
                            <p style={{ color: 'var(--text-muted)', maxWidth: '400px', fontSize: '0.9rem', lineHeight: 1.6 }}>
                                Upload your resume and click Analyze to see your skill gap versus today's market demand, powered by Groq AI.
                            </p>
                        </div>
                    )}

                    {(isAnalyzing || marketLoading) && (
                        <div className="glass-card flex-col items-center justify-center" style={{ minHeight: '200px', gap: '1rem' }}>
                            <div style={{ width: '48px', height: '48px', border: '4px solid rgba(52,160,90,0.15)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                            <p style={{ color: 'var(--text-secondary)' }}>Fetching market intelligence + parsing resume…</p>
                        </div>
                    )}

                    {/* Market Skills Card */}
                    {marketSkills && (
                        <div className="glass-card fade-in" style={{ padding: '1.5rem', border: '1px solid rgba(52,160,90,0.2)' }}>
                            <div className="flex justify-between items-start" style={{ marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                                <div>
                                    <h3 style={{ fontSize: '1.1rem', fontWeight: 800 }}>📡 Market Intelligence: {role}</h3>
                                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '3px' }}>{domain}</p>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <span style={{ fontWeight: 900, color: demandColor[marketSkills.demand_level] || 'var(--primary-500)', fontSize: '0.9rem' }}>
                                        ● {marketSkills.demand_level} Demand
                                    </span>
                                    <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>💰 {marketSkills.avg_salary_india}</p>
                                </div>
                            </div>

                            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem', fontStyle: 'italic', lineHeight: 1.5 }}>
                                📈 {marketSkills.growth_trend}
                            </p>

                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                                <div>
                                    <p style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--accent-red)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Must-Have Skills</p>
                                    <div className="flex flex-wrap gap-xs">
                                        {marketSkills.required_skills.map(s => <span key={s} className="badge" style={{ fontSize: '0.72rem', borderColor: 'rgba(239,68,68,0.3)', color: 'var(--accent-red)', background: 'rgba(239,68,68,0.04)' }}>{s}</span>)}
                                    </div>
                                </div>
                                <div>
                                    <p style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--accent-blue)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Nice to Have</p>
                                    <div className="flex flex-wrap gap-xs">
                                        {marketSkills.nice_to_have_skills.map(s => <span key={s} className="badge" style={{ fontSize: '0.72rem' }}>{s}</span>)}
                                    </div>
                                </div>
                                <div>
                                    <p style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--accent-green)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Top Tools</p>
                                    <div className="flex flex-wrap gap-xs">
                                        {marketSkills.top_tools.map(s => <span key={s} className="badge" style={{ fontSize: '0.72rem', borderColor: 'rgba(52,160,90,0.3)', color: 'var(--accent-green)', background: 'rgba(52,160,90,0.04)' }}>{s}</span>)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Resume Analysis */}
                    {result && (
                        <>
                            {/* Readiness Score */}
                            <div className="glass-card fade-in" style={{ padding: '1.5rem', border: '1px solid rgba(56,183,248,0.2)', background: 'rgba(56,183,248,0.03)' }}>
                                <div className="flex justify-between items-center" style={{ flexWrap: 'wrap', gap: '1rem' }}>
                                    <div>
                                        <p style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '1px', marginBottom: '4px' }}>INTERVIEW READINESS SCORE</p>
                                        <h3 style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--accent-blue)' }}>{result.readiness_score}%</h3>
                                    </div>
                                    <div style={{ flex: 1, maxWidth: '400px' }}>
                                        <div style={{ height: '10px', background: 'rgba(52,160,90,0.10)', borderRadius: '5px', overflow: 'hidden' }}>
                                            <div style={{ height: '100%', width: `${result.readiness_score}%`, background: result.readiness_score >= 70 ? 'var(--accent-green)' : result.readiness_score >= 40 ? 'var(--accent-orange)' : 'var(--accent-red)', borderRadius: '5px', transition: 'width 1s ease' }} />
                                        </div>
                                        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                                            {result.readiness_score >= 70 ? '🟢 Ready for interviews! Keep refining.' : result.readiness_score >= 40 ? '🟡 Solid base — bridge the skill gaps below.' : '🔴 Focus on the missing skills first.'}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Tab Navigation */}
                            <div className="flex gap-sm">
                                {(['gap', 'roadmap'] as const).map(tab => (
                                    <button
                                        key={tab}
                                        onClick={() => setActiveTab(tab)}
                                        className={activeTab === tab ? 'btn btn-primary' : 'btn btn-secondary'}
                                        style={{ fontSize: '0.82rem', padding: '0.5rem 1.2rem' }}
                                    >
                                        {tab === 'gap' ? '🎯 Skill Gap Analysis' : '📋 Personalized Roadmap'}
                                    </button>
                                ))}
                            </div>

                            {activeTab === 'gap' && (
                                <div className="flex-col gap-lg fade-in">
                                    {/* Your Skills */}
                                    <div className="glass-card" style={{ padding: '1.5rem' }}>
                                        <h4 style={{ fontSize: '0.9rem', fontWeight: 800, marginBottom: '1rem', color: 'var(--text-primary)' }}>📋 Skills Found in Your Resume</h4>
                                        <div className="flex flex-wrap gap-xs">
                                            {result.extracted_skills.map(s => {
                                                const matched = marketSkills?.required_skills.some(r => r.toLowerCase().includes(s.toLowerCase()) || s.toLowerCase().includes(r.toLowerCase()));
                                                return (
                                                    <span key={s} className="badge" style={{
                                                        fontSize: '0.78rem', padding: '0.4rem 0.8rem',
                                                        borderColor: matched ? 'rgba(52,160,90,0.5)' : 'var(--glass-border)',
                                                        color: matched ? 'var(--accent-green)' : 'var(--text-primary)',
                                                        background: matched ? 'rgba(52,160,90,0.06)' : 'transparent'
                                                    }}>{matched ? '✓ ' : ''}{s}</span>
                                                );
                                            })}
                                        </div>
                                        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>✓ Green = matched with market demand</p>
                                    </div>

                                    {/* Gap Analysis */}
                                    {marketSkills && (
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                            <div className="glass-card" style={{ padding: '1.25rem', border: '1px solid rgba(52,160,90,0.2)' }}>
                                                <h5 style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-green)', marginBottom: '0.75rem' }}>✅ Matching Market Skills ({matchedSkills.length})</h5>
                                                <div className="flex flex-wrap gap-xs">
                                                    {matchedSkills.length > 0 ? matchedSkills.map(s => <span key={s} className="badge" style={{ fontSize: '0.72rem', color: 'var(--accent-green)', borderColor: 'rgba(52,160,90,0.3)', background: 'rgba(52,160,90,0.05)' }}>{s}</span>)
                                                        : <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No direct matches yet</p>}
                                                </div>
                                            </div>
                                            <div className="glass-card" style={{ padding: '1.25rem', border: '1px solid rgba(239,68,68,0.2)' }}>
                                                <h5 style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-red)', marginBottom: '0.75rem' }}>❌ Missing Critical Skills ({gapSkills.length})</h5>
                                                <div className="flex flex-wrap gap-xs">
                                                    {gapSkills.length > 0 ? gapSkills.map(s => <span key={s} className="badge" style={{ fontSize: '0.72rem', color: 'var(--accent-red)', borderColor: 'rgba(239,68,68,0.3)', background: 'rgba(239,68,68,0.04)' }}>{s}</span>)
                                                        : <p style={{ fontSize: '0.8rem', color: 'var(--accent-green)' }}>🎉 No major gaps found!</p>}
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Strong Domains */}
                                    {result.strong_domains.length > 0 && (
                                        <div className="glass-card" style={{ padding: '1.25rem' }}>
                                            <h4 style={{ fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.75rem' }}>🌟 Your Strongest Areas</h4>
                                            <div className="flex flex-wrap gap-xs">
                                                {result.strong_domains.map(s => <span key={s} className="badge" style={{ fontSize: '0.78rem', borderColor: 'rgba(52,160,90,0.4)', color: 'var(--accent-green)', background: 'rgba(52,160,90,0.06)' }}>{s}</span>)}
                                            </div>
                                        </div>
                                    )}

                                    {/* Missing skills from resume analysis */}
                                    {result.missing_skills.length > 0 && (
                                        <div className="glass-card" style={{ padding: '1.25rem', border: '1px solid rgba(239,68,68,0.15)', background: 'rgba(239,68,68,0.02)' }}>
                                            <h4 style={{ fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.75rem' }}>⚠️ Skills to Develop (Resume Analysis)</h4>
                                            <div className="flex-col gap-sm">
                                                {result.missing_skills.map(s => (
                                                    <div key={s} className="flex items-center gap-sm" style={{ padding: '0.6rem 1rem', background: 'rgba(52,160,90,0.04)', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.15)' }}>
                                                        <span style={{ color: 'var(--accent-red)' }}>!</span>
                                                        <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>{s}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {activeTab === 'roadmap' && (
                                <div className="glass-card fade-in" style={{ padding: '1.5rem' }}>
                                    <h4 style={{ fontSize: '0.9rem', fontWeight: 800, marginBottom: '1.25rem' }}>📋 Personalized Learning Roadmap</h4>
                                    {[
                                        { label: 'PHASE 1: FOUNDATION', color: 'var(--primary-500)', items: result.roadmap.beginner },
                                        { label: 'PHASE 2: INTERMEDIATE', color: 'var(--accent-blue)', items: result.roadmap.intermediate },
                                        { label: 'PHASE 3: ADVANCED', color: 'var(--accent-orange)', items: result.roadmap.advanced },
                                        { label: 'PHASE 4: PROJECTS', color: 'var(--accent-green)', items: result.roadmap.projects }
                                    ].map(phase => (
                                        <div key={phase.label} style={{ marginBottom: '1.25rem', paddingLeft: '1rem', borderLeft: `3px solid ${phase.color}` }}>
                                            <p style={{ fontSize: '0.7rem', color: phase.color, fontWeight: 900, letterSpacing: '1px', marginBottom: '0.5rem' }}>{phase.label}</p>
                                            <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                                                {phase.items.map((item, i) => {
                                                    const parts = item.split(': [');
                                                    if (parts.length > 1) {
                                                        const subs = parts[1].replace(']', '').split(', ');
                                                        return (
                                                            <li key={i} style={{ marginBottom: '0.6rem' }}>
                                                                <strong style={{ color: 'var(--text-primary)', fontSize: '0.85rem' }}>{parts[0]}</strong>
                                                                <div className="flex flex-wrap gap-xs" style={{ marginTop: '4px' }}>
                                                                    {subs.map(s => <span key={s} style={{ fontSize: '0.65rem', padding: '0.1rem 0.5rem', background: 'rgba(52,160,90,0.08)', borderRadius: '4px', color: 'var(--text-secondary)' }}>{s}</span>)}
                                                                </div>
                                                            </li>
                                                        );
                                                    }
                                                    return <li key={i} style={{ fontSize: '0.85rem', color: 'var(--text-primary)', marginBottom: '4px' }}>— {item}</li>;
                                                })}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

            <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                @media (max-width: 900px) { .coach-grid { grid-template-columns: 1fr !important; } }
            `}</style>
        </div>
    );
};
