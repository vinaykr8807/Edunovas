import { useEffect, useState } from 'react';

interface JobMarketItem {
    title: string;
    source: string;
    link: string;
    snippet: string;
    skills: string[];
}

interface CareerReport {
    role: string;
    level: string;
    city: string;
    readiness_score: number;
    resume_skills: string[];
    market_required_skills: string[];
    matched_skills: string[];
    missing_skills: string[];
    job_market: JobMarketItem[];
    proceed_guide: {
        immediate: string[];
        short_term: string[];
        mid_term: string[];
        long_term: string[];
    };
    roadmap: {
        foundation: string[];
        job_readiness: string[];
        interview_prep: string[];
        projects: string[];
    };
}

export const CareerPathfinder = () => {
    const [file, setFile] = useState<File | null>(null);
    const [role, setRole] = useState('Fullstack Developer');
    const [level, setLevel] = useState('Junior');
    const [city, setCity] = useState('Bengaluru');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [report, setReport] = useState<CareerReport | null>(null);
    const [hasStoredResume, setHasStoredResume] = useState(false);

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
        if (!user.email) return;
        fetch(`http://127.0.0.1:8000/resume-status?user_email=${encodeURIComponent(user.email)}`)
            .then((r) => r.json())
            .then((d) => setHasStoredResume(Boolean(d?.has_stored_resume)))
            .catch(() => setHasStoredResume(false));
    }, []);

    const analyzeCareerPath = async () => {
        if (!file && !hasStoredResume) return;
        setIsLoading(true);
        setError('');
        setReport(null);

        const formData = new FormData();
        if (file) formData.append('file', file);
        formData.append('role', role);
        formData.append('level', level);
        formData.append('city', city);
        const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
        if (user.email) formData.append('user_email', user.email);

        try {
            const res = await fetch('http://127.0.0.1:8000/career-pathfinder', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (!res.ok || data.error) {
                setError(data.error || 'Career analysis failed.');
            } else {
                setReport(data);
            }
        } catch {
            setError('Unable to connect to backend.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex-col gap-xl">
            <header>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Career Pathfinder</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Resume-driven roadmap, market demand, and city-specific role guidance</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 320px) minmax(0, 1fr)', gap: '1.5rem' }} className="career-grid">
                <div className="glass-card flex-col gap-lg" style={{ padding: '1.5rem', height: 'fit-content' }}>
                    <h3 style={{ fontSize: '1rem', color: 'var(--primary-400)' }}>Career Inputs</h3>

                    <div className="flex-col gap-xs">
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>Target Role</span>
                        <select value={role} onChange={(e) => setRole(e.target.value)} className="btn btn-secondary" style={{ padding: '0.6rem', textAlign: 'left' }}>
                            <option>Fullstack Developer</option>
                            <option>Frontend Engineer</option>
                            <option>Data Scientist</option>
                            <option>DevOps Engineer</option>
                        </select>
                    </div>

                    <div className="flex-col gap-xs">
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>Experience Level</span>
                        <select value={level} onChange={(e) => setLevel(e.target.value)} className="btn btn-secondary" style={{ padding: '0.6rem', textAlign: 'left' }}>
                            <option>Junior</option>
                            <option>Mid-Level</option>
                            <option>Senior</option>
                        </select>
                    </div>

                    <div className="flex-col gap-xs">
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>Target City</span>
                        <input
                            value={city}
                            onChange={(e) => setCity(e.target.value)}
                            className="btn btn-secondary"
                            style={{ padding: '0.65rem', textAlign: 'left' }}
                            placeholder="e.g., Bengaluru, Hyderabad, Mumbai"
                        />
                    </div>

                    <div
                        style={{ border: '2px dashed var(--glass-border)', padding: '1.25rem', textAlign: 'center', borderRadius: 'var(--radius-md)' }}
                        onDrop={(e) => { e.preventDefault(); setFile(e.dataTransfer.files[0]); }}
                        onDragOver={(e) => e.preventDefault()}
                    >
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            {file ? `Resume: ${file.name}` : 'Upload Resume PDF/DOCX'}
                        </p>
                        <input type="file" hidden id="career-resume-upload" onChange={(e) => setFile(e.target.files?.[0] || null)} />
                        <label htmlFor="career-resume-upload" className="btn btn-primary" style={{ marginTop: '1rem', cursor: 'pointer', display: 'inline-block' }}>
                            Browse Resume
                        </label>
                    </div>

                    <button className="btn btn-primary w-full" disabled={(!file && !hasStoredResume) || isLoading} onClick={analyzeCareerPath}>
                        {isLoading ? 'ANALYZING MARKET...' : file ? 'BUILD CAREER STRATEGY' : 'USE STORED RESUME STRATEGY'}
                    </button>
                    {hasStoredResume && !file && (
                        <p style={{ fontSize: '0.72rem', color: 'var(--accent-green)', textAlign: 'center' }}>
                            Stored resume found. You can run Career Pathfinder directly.
                        </p>
                    )}

                    {error && (
                        <div style={{ color: 'var(--accent-red)', fontSize: '0.8rem' }}>{error}</div>
                    )}
                </div>

                <div className="flex-col gap-lg">

                    {!report && !isLoading && (
                        <div className="glass-card flex-col items-center justify-center" style={{ minHeight: '420px', textAlign: 'center' }}>
                            <h3 style={{ fontSize: '1.2rem' }}>Your career strategy will appear here</h3>
                            <p style={{ color: 'var(--text-muted)', maxWidth: '540px' }}>
                                Upload your resume and target city to get role demand, skill gaps, job links, and a step-by-step guide to proceed.
                            </p>
                        </div>
                    )}

                    {report && (
                        <>
                            <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid var(--accent-blue)', background: 'rgba(0,100,255,0.05)' }}>
                                <div className="flex justify-between items-start" style={{ gap: '1rem', flexWrap: 'wrap' }}>
                                    <div>
                                        <h3 style={{ fontSize: '1.1rem' }}>{report.role} in {report.city}</h3>
                                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{report.level} market readiness</p>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <span style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-blue)' }}>{report.readiness_score}%</span>
                                        <p style={{ fontSize: '0.65rem', textTransform: 'uppercase', opacity: 0.7 }}>Readiness</p>
                                    </div>
                                </div>
                                <div className="flex flex-wrap gap-xs mt-md" style={{ maxWidth: '100%', alignItems: 'flex-start' }}>
                                    {report.resume_skills.slice(0, 14).map((s) => (
                                        <span key={s} className="badge" style={{ fontSize: '0.75rem', padding: '0.35rem 0.7rem', lineHeight: 1.2 }}>{s}</span>
                                    ))}
                                </div>
                            </div>

                            <div className="glass-card" style={{ padding: '1.5rem' }}>
                                <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Skill Gap Summary</h3>
                                <div className="flex-col gap-sm">
                                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                                        Top skills demanded in {report.city} listings for {report.role}:
                                    </p>
                                    <div className="flex flex-wrap gap-xs">
                                        {report.market_required_skills.map((s) => (
                                            <span key={s} className="badge" style={{ fontSize: '0.72rem' }}>{s}</span>
                                        ))}
                                    </div>
                                    <p style={{ fontSize: '0.82rem', color: 'var(--accent-red)', marginTop: '0.5rem' }}>
                                        Missing in your resume:
                                    </p>
                                    <div className="flex flex-wrap gap-xs">
                                        {report.missing_skills.length > 0 ? report.missing_skills.map((s) => (
                                            <span key={s} className="badge" style={{ fontSize: '0.72rem', borderColor: 'var(--accent-red)', color: 'var(--accent-red)' }}>{s}</span>
                                        )) : <span style={{ fontSize: '0.8rem', color: 'var(--accent-green)' }}>No major critical gaps detected.</span>}
                                    </div>
                                </div>
                            </div>

                            <div className="glass-card" style={{ padding: '1.5rem' }}>
                                <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Guide To Proceed</h3>
                                {[
                                    { title: 'Immediate (This Week)', items: report.proceed_guide.immediate, color: 'var(--primary-400)' },
                                    { title: 'Short Term (2-4 Weeks)', items: report.proceed_guide.short_term, color: 'var(--accent-blue)' },
                                    { title: 'Mid Term (1-2 Months)', items: report.proceed_guide.mid_term, color: 'var(--accent-orange)' },
                                    { title: 'Long Term (Quarterly)', items: report.proceed_guide.long_term, color: 'var(--accent-green)' },
                                ].map((section) => (
                                    <div key={section.title} style={{ marginBottom: '1rem' }}>
                                        <p style={{ fontSize: '0.76rem', color: section.color, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{section.title}</p>
                                        <ul style={{ margin: '0.4rem 0 0.2rem 1rem', padding: 0, fontSize: '0.85rem', lineHeight: 1.5 }}>
                                            {section.items.map((item) => <li key={item}>{item}</li>)}
                                        </ul>
                                    </div>
                                ))}
                            </div>

                            <div className="glass-card" style={{ padding: '1.5rem' }}>
                                <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Roadmap Aligned To Job Demand</h3>
                                {[
                                    { label: 'Foundation', items: report.roadmap.foundation },
                                    { label: 'Job Readiness', items: report.roadmap.job_readiness },
                                    { label: 'Interview Prep', items: report.roadmap.interview_prep },
                                    { label: 'Projects', items: report.roadmap.projects }
                                ].map((phase) => (
                                    <div key={phase.label} style={{ marginBottom: '1rem' }}>
                                        <p style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>{phase.label}</p>
                                        <ul style={{ margin: '0.4rem 0 0.2rem 1rem', padding: 0, fontSize: '0.85rem', lineHeight: 1.5 }}>
                                            {phase.items.map((item) => <li key={item}>{item}</li>)}
                                        </ul>
                                    </div>
                                ))}
                            </div>

                            <div className="glass-card" style={{ padding: '1.5rem' }}>
                                <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Live Job Demand Signals ({report.job_market.length})</h3>
                                <div className="flex-col gap-sm">
                                    {report.job_market.length > 0 ? report.job_market.map((job) => (
                                        <a
                                            key={`${job.link}-${job.title}`}
                                            href={job.link}
                                            target="_blank"
                                            rel="noreferrer"
                                            style={{ display: 'block', border: '1px solid var(--glass-border)', borderRadius: '10px', padding: '0.9rem', textDecoration: 'none' }}
                                        >
                                            <p style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-primary)', wordBreak: 'break-word' }}>{job.title}</p>
                                            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{job.source}</p>
                                            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.5rem', wordBreak: 'break-word' }}>{job.snippet}</p>
                                            <div className="flex flex-wrap gap-xs" style={{ marginTop: '0.55rem' }}>
                                                {job.skills.slice(0, 8).map((s) => (
                                                    <span key={s} className="badge" style={{ fontSize: '0.66rem', padding: '0.2rem 0.5rem' }}>{s}</span>
                                                ))}
                                            </div>
                                        </a>
                                    )) : (
                                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                            No live listings found for the exact query right now. Try a nearby metro city or broader role title.
                                        </p>
                                    )}
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            <style>{`
                @media (max-width: 980px) {
                    .career-grid {
                        grid-template-columns: 1fr !important;
                    }
                }
            `}</style>
        </div>
    );
};
