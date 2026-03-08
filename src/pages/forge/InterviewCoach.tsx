import { useEffect, useState, useRef } from 'react';

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
    trend_analytics?: { skill: string; demand_score: number }[];
}

interface BeginnerGuide {
    guide_title: string;
    summary: string;
    phases: { phase: string; focus: string }[];
    soft_skills: string[];
    trends: string[];
}

interface HistoricalTrends {
    trend_line: { year: string; count: number }[];
    top_historical_companies: { name: string; count: number }[];
    total_historical_records: number;
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

const playInterviewSound = (type: 'next' | 'finish') => {
    try {
        const url = type === 'next' 
            ? 'https://cdn.pixabay.com/download/audio/2021/08/04/audio_3aa2204c3c.mp3?filename=pop-up-something-160353.mp3' // gentle pop
            : 'https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c1539c.mp3?filename=success-1-6297.mp3'; // success chime
        const audio = new Audio(url);
        audio.volume = 0.5;
        audio.play().catch(() => {});
    } catch (e) { console.error(e) }
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
    const [activeTab, setActiveTab] = useState<'gap' | 'roadmap' | 'trends' | 'mentor' | 'mock'>('gap');
    const [beginnerGuide, setBeginnerGuide] = useState<BeginnerGuide | null>(null);
    const [historicalTrends, setHistoricalTrends] = useState<HistoricalTrends | null>(null);
    const [guideLoading, setGuideLoading] = useState(false);

    // Mock Interview State
    const [mockPlan, setMockPlan] = useState<any[]>([]);
    const [mockQuestions, setMockQuestions] = useState<string[]>([]);
    const [mockIndex, setMockIndex] = useState(0);
    const [mockDifficulty, setMockDifficulty] = useState('Medium');
    const [currentQuestion, setCurrentQuestion] = useState<any>(null);
    const [mockEvals, setMockEvals] = useState<any[]>([]);
    const [userMockAnswer, setUserMockAnswer] = useState('');
    const [isMockLoading, setIsMockLoading] = useState(false);
    const [mockComplete, setMockComplete] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const recognitionRef = useRef<any>(null);

    // Initialize Speech Recognition
    useEffect(() => {
        const SpeechRecognitionInfo = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognitionInfo) {
            const recognition = new SpeechRecognitionInfo();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            // Re-vamped speech handler for live updates without erasing old text
            recognition.onresult = (event: any) => {
                let finalSegment = '';
                let interimSegment = '';
                
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalSegment += event.results[i][0].transcript + ' ';
                    } else {
                        interimSegment += event.results[i][0].transcript;
                    }
                }
                
                // Append final segments permanently
                if (finalSegment) {
                    setUserMockAnswer(prev => prev + finalSegment);
                }
                // (We could show interimSegment in a separate state, but for simplicity we'll just wait for final chunks)
            };

            recognition.onerror = (e: any) => {
                console.error("Speech recognition error", e);
                setIsListening(false);
            };

            recognition.onend = () => {
                setIsListening(false);
            };

            recognitionRef.current = recognition;
        }
    }, []);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
            setIsListening(false);
        } else {
            if (recognitionRef.current) {
                recognitionRef.current.start();
                setIsListening(true);
            } else {
                alert("Speech recognition isn't supported in your browser.");
            }
        }
    };

    // Start Mock Interview Session
    const startMockInterview = async () => {
        setIsMockLoading(true);
        setActiveTab('mock');
        try {
            const res = await fetch('http://127.0.0.1:8000/coach/mock-interview/plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role,
                    domain,
                    extracted_skills: result?.extracted_skills || []
                })
            });
            const data = await res.json();
            setMockPlan(data.plan);
            setMockDifficulty(data.difficulty);
            setMockIndex(0);
            setMockQuestions([]);
            setMockEvals([]);
            setMockComplete(false);
            fetchNextQuestion(data.plan[0], []);
        } catch (e) {
            console.error('Failed to start mock', e);
        }
        setIsMockLoading(false);
    };

    const fetchNextQuestion = async (planItem: any, asked: string[]) => {
        setIsMockLoading(true);
        try {
            const res = await fetch('http://127.0.0.1:8000/coach/mock-interview/question', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role,
                    domain,
                    plan_item: planItem,
                    asked_questions: asked,
                    difficulty: mockDifficulty
                })
            });
            const data = await res.json();
            setCurrentQuestion(data);
            setMockQuestions([...asked, data.question]);
            setUserMockAnswer('');
            
            // Audio Feedback for new question
            playInterviewSound('next');
            
            // Wait slightly before speaking to allow the pop sound to play
            setTimeout(() => {
                speakText(data.question);
            }, 600);
            
        } catch (e) {
            console.error(e);
        }
        setIsMockLoading(false);
    };

    const submitMockAnswer = async () => {
        setIsMockLoading(true);
        try {
            const res = await fetch('http://127.0.0.1:8000/coach/mock-interview/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role,
                    domain,
                    question: currentQuestion.question,
                    answer: userMockAnswer
                })
            });
            const ev = await res.json();
            const newEvals = [...mockEvals, ev];
            setMockEvals(newEvals);
            
            const nextIdx = mockIndex + 1;
            if (nextIdx < (mockPlan?.length || 0)) {
                setMockIndex(nextIdx);
                const nextDiff = ev.overall_score >= 8 ? 'Hard' : (ev.overall_score >= 5 ? 'Medium' : 'Easy');
                setMockDifficulty(nextDiff);
                fetchNextQuestion(mockPlan[nextIdx], mockQuestions);
            } else {
                setMockComplete(true);
                playInterviewSound('finish');
            }
        } catch (e) {
            console.error(e);
        }
        setIsMockLoading(false);
    };

    const speakText = (text: string) => {
        if ('speechSynthesis' in window) {
            const msg = new SpeechSynthesisUtterance(text);
            msg.lang = 'en-US';
            window.speechSynthesis.speak(msg);
        }
    };

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

    const fetchMarketSkills = async () => {
        setMarketLoading(true);
        setActiveTab('trends');
        try {
            const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
            const response = await fetch('http://127.0.0.1:8000/teacher/market-skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role, domain, user_email: user.email })
            });
            const data = await response.json();
            setMarketSkills(data);
        } catch {
            setMarketSkills(null);
        } finally {
            setMarketLoading(false);
        }
    };

    const fetchBeginnerGuide = async () => {
        setGuideLoading(true);
        setActiveTab('mentor');
        try {
            const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
            const response = await fetch('http://127.0.0.1:8000/coach/beginner-guide', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role, domain, user_email: user.email })
            });
            const data = await response.json();
            setBeginnerGuide(data);
        } catch {
            setBeginnerGuide(null);
        } finally {
            setGuideLoading(false);
        }
    };

    const fetchHistoricalTrends = async () => {
        try {
            const res = await fetch('http://127.0.0.1:8000/coach/historical-trends', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role, domain })
            });
            const data = await res.json();
            setHistoricalTrends(data);
        } catch {
            setHistoricalTrends(null);
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
                fetchMarketSkills()
            ]);
            fetchHistoricalTrends(); // Background load
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

    // Historical and Market Intelligence ready

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
                        style={{ border: '2px dashed rgba(100,130,255,0.3)', padding: '1.25rem', textAlign: 'center', borderRadius: 'var(--radius-md)', background: 'rgba(100,130,255,0.03)', cursor: 'pointer' }}
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

                    {/* Pro Mentor Feature */}
                    <button
                        className="btn btn-primary w-full"
                        onClick={() => fetchBeginnerGuide()}
                        disabled={guideLoading}
                        style={{ background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)', border: 'none', color: 'white', fontWeight: 800 }}
                    >
                        {guideLoading ? '⏳ Crafting Beginner Roadmap…' : '👨‍🏫 Pro Mentor: Zero-to-Hero Guide'}
                    </button>

                    <button
                        className="btn btn-secondary w-full"
                        onClick={() => fetchMarketSkills()}
                        disabled={marketLoading}
                        style={{ fontSize: '0.8rem' }}
                    >
                        {marketLoading ? '⏳ Loading market trends…' : '📉 Visual Market Analytics'}
                    </button>
                    
                    <button
                        className="btn btn-primary w-full"
                        onClick={startMockInterview}
                        disabled={isMockLoading}
                        style={{ background: 'linear-gradient(135deg, var(--primary-500), #059669)', border: 'none', color: 'white', fontWeight: 800, marginTop: '0.5rem' }}
                    >
                        {isMockLoading ? '⏳ Starting Simulator…' : '🎙️ Start AI Mock Interview'}
                    </button>
                </div>

                {/* Results Panel */}
                <div className="flex-col gap-lg">
                    {!result && !marketSkills && !isAnalyzing && !marketLoading && !isMockLoading && (mockPlan?.length || 0) === 0 && !mockComplete && (
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
                            <div style={{ width: '48px', height: '48px', border: '4px solid rgba(100,130,255,0.15)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                            <p style={{ color: 'var(--text-secondary)' }}>Fetching market intelligence + parsing resume…</p>
                        </div>
                    )}

                        {/* Main Content Area */}
                    <div className="flex-col gap-lg">
                        {/* Tab Navigation (Always show if we have data) */}
                        {(result || marketSkills || beginnerGuide || (mockPlan?.length || 0) > 0 || isMockLoading || mockComplete) && (
                            <div className="flex gap-sm flex-wrap">
                                {(['gap', 'roadmap', 'trends', 'mentor', 'mock'] as const).map(tab => {
                                    const isAvailable = (tab === 'gap' || tab === 'roadmap') ? !!result :
                                                        (tab === 'trends') ? !!marketSkills :
                                                        (tab === 'mentor') ? !!beginnerGuide : 
                                                        (tab === 'mock') ? ((mockPlan?.length || 0) > 0 || isMockLoading) : false;
                                    if (!isAvailable) return null;

                                    return (
                                        <button
                                            key={tab}
                                            onClick={() => setActiveTab(tab)}
                                            className={activeTab === tab ? 'btn btn-primary' : 'btn btn-secondary'}
                                            style={{ fontSize: '0.82rem', padding: '0.5rem 1.2rem' }}
                                        >
                                            {tab === 'gap' ? '🎯 Skill Gap' : 
                                             tab === 'roadmap' ? '📋 Roadmap' : 
                                             tab === 'trends' ? '📊 Market Trends' : 
                                             tab === 'mock' ? '🎙️ Mock Interview' : '👨‍🏫 Pro Mentor'}
                                        </button>
                                    );
                                })}
                            </div>
                        )}

                        {/* Gap Analysis & Resume Insights */}
                        {activeTab === 'gap' && result && (
                            <div className="flex-col gap-lg fade-in">
                                <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid rgba(56,183,248,0.2)', background: 'rgba(56,183,248,0.03)' }}>
                                    <div className="flex justify-between items-center flex-wrap gap-md">
                                        <div>
                                            <p style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '1px', marginBottom: '4px' }}>INTERVIEW READINESS SCORE</p>
                                            <h3 style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--accent-blue)' }}>{result.readiness_score}%</h3>
                                        </div>
                                        <div style={{ flex: 1, maxWidth: '400px' }}>
                                            <div style={{ height: '10px', background: 'rgba(100,130,255,0.10)', borderRadius: '5px', overflow: 'hidden' }}>
                                                <div style={{ height: '100%', width: `${result.readiness_score}%`, background: result.readiness_score >= 70 ? 'var(--primary-500)' : result.readiness_score >= 40 ? 'var(--accent-orange)' : 'var(--accent-red)', borderRadius: '5px', transition: 'width 1s ease' }} />
                                            </div>
                                            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>{result.readiness_score >= 70 ? '🟢 Ready for interviews!' : '🟡 Solid base — bridge gaps.'}</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="glass-card" style={{ padding: '1.5rem' }}>
                                    <h4 style={{ fontSize: '0.9rem', fontWeight: 800, marginBottom: '1rem' }}>📋 Skills Found in Your Resume</h4>
                                    <div className="flex flex-wrap gap-xs">
                                        {result.extracted_skills.map(s => {
                                            const matched = marketSkills?.required_skills.some(r => r.toLowerCase().includes(s.toLowerCase()));
                                            return <span key={s} className="badge" style={{ fontSize: '0.78rem', borderColor: matched ? 'rgba(100,130,255,0.5)' : 'var(--glass-border)', color: matched ? 'var(--primary-500)' : 'var(--text-primary)' }}>{s}</span>;
                                        })}
                                    </div>
                                </div>

                                {marketSkills && (
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                        <div className="glass-card" style={{ padding: '1.25rem', border: '1px solid rgba(100,130,255,0.2)' }}>
                                            <h5 style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--primary-500)', marginBottom: '0.75rem' }}>✅ Matching Market Skills</h5>
                                            <div className="flex flex-wrap gap-xs">
                                                {marketSkills.required_skills.filter(s => result.extracted_skills.some(r => r.toLowerCase().includes(s.toLowerCase()))).map(s => <span key={s} className="badge" style={{ fontSize: '0.72rem', color: 'var(--primary-500)', borderColor: 'rgba(100,130,255,0.3)' }}>{s}</span>)}
                                            </div>
                                        </div>
                                        <div className="glass-card" style={{ padding: '1.25rem', border: '1px solid rgba(239,68,68,0.2)' }}>
                                            <h5 style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-red)', marginBottom: '0.75rem' }}>❌ Missing Critical Skills</h5>
                                            <div className="flex flex-wrap gap-xs">
                                                {marketSkills.required_skills.filter(s => !result.extracted_skills.some(r => r.toLowerCase().includes(s.toLowerCase()))).slice(0, 10).map(s => <span key={s} className="badge" style={{ fontSize: '0.72rem', color: 'var(--accent-red)', borderColor: 'rgba(239,68,68,0.3)' }}>{s}</span>)}
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Strong Domains */}
                                {result.strong_domains.length > 0 && (
                                    <div className="glass-card" style={{ padding: '1.25rem' }}>
                                        <h4 style={{ fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.75rem' }}>🌟 Your Strongest Areas</h4>
                                        <div className="flex flex-wrap gap-xs">
                                            {result.strong_domains.map(s => <span key={s} className="badge" style={{ fontSize: '0.78rem', borderColor: 'rgba(100,130,255,0.4)', color: 'var(--primary-500)', background: 'rgba(100,130,255,0.06)' }}>{s}</span>)}
                                        </div>
                                    </div>
                                )}

                                {/* Missing skills from resume analysis */}
                                {result.missing_skills.length > 0 && (
                                    <div className="glass-card" style={{ padding: '1.25rem', border: '1px solid rgba(239,68,68,0.15)', background: 'rgba(239,68,68,0.02)' }}>
                                        <h4 style={{ fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.75rem' }}>⚠️ Skills to Develop (Resume Analysis)</h4>
                                        <div className="flex-col gap-sm">
                                            {result.missing_skills.map(s => (
                                                <div key={s} className="flex items-center gap-sm" style={{ padding: '0.6rem 1rem', background: 'rgba(100,130,255,0.04)', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.15)' }}>
                                                    <span style={{ color: 'var(--accent-red)' }}>!</span>
                                                    <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>{s}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Roadmap */}
                        {activeTab === 'roadmap' && result && (
                            <div className="glass-card fade-in" style={{ padding: '1.5rem' }}>
                                <h4 style={{ fontSize: '0.9rem', fontWeight: 800, marginBottom: '1.25rem' }}>📋 Personalized Learning Roadmap</h4>
                                {[
                                    { label: 'PHASE 1: FOUNDATION', color: 'var(--primary-500)', items: result.roadmap.beginner },
                                    { label: 'PHASE 2: INTERMEDIATE', color: 'var(--accent-blue)', items: result.roadmap.intermediate },
                                    { label: 'PHASE 3: ADVANCED', color: 'var(--accent-orange)', items: result.roadmap.advanced },
                                    { label: 'PHASE 4: PROJECTS', color: 'var(--primary-500)', items: result.roadmap.projects }
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
                                                                {subs.map(s => <span key={s} style={{ fontSize: '0.65rem', padding: '0.1rem 0.5rem', background: 'rgba(100,130,255,0.08)', borderRadius: '4px', color: 'var(--text-secondary)' }}>{s}</span>)}
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

                        {/* Trends */}
                        {activeTab === 'trends' && marketSkills && (
                            <div className="flex-col gap-lg fade-in">
                                <div className="glass-card" style={{ padding: '1.5rem' }}>
                                    <h4 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '1.5rem', color: 'var(--primary-500)' }}>📈 Live Market Skill Demand</h4>
                                    <div className="flex-col gap-md">
                                        {(marketSkills.trend_analytics || [
                                            { skill: 'Core Tech Stack', demand_score: 95 },
                                            { skill: 'Cloud & DevOps', demand_score: 82 },
                                            { skill: 'AI Integration', demand_score: 75 },
                                            { skill: 'Soft Skills', demand_score: 65 }
                                        ]).map((trend, i) => (
                                            <div key={i} className="flex-col gap-xs">
                                                <div className="flex justify-between" style={{ fontSize: '0.8rem' }}>
                                                    <span style={{ fontWeight: 700 }}>{trend.skill}</span>
                                                    <span style={{ color: 'var(--text-muted)' }}>{trend.demand_score}% Demand</span>
                                                </div>
                                                <div style={{ height: '10px', background: 'var(--glass-border)', borderRadius: '5px', overflow: 'hidden' }}>
                                                    <div style={{ height: '100%', width: `${trend.demand_score}%`, background: i === 0 ? 'var(--primary-500)' : 'var(--accent-blue)', transition: 'width 1s ease' }} />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '1.5rem', fontStyle: 'italic' }}>
                                        *Data periodically scraped from live tech job portals and industry reports for 2026 outlook.
                                    </p>
                                </div>
                                <div className="glass-card" style={{ padding: '1.5rem' }}>
                                    <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--accent-orange)', marginBottom: '0.5rem' }}>💼 Market Pulse</h4>
                                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{marketSkills.growth_trend}</p>
                                    <div className="flex-col gap-sm" style={{ marginTop: '1rem' }}>
                                        <p style={{ fontSize: '0.75rem', fontWeight: 800 }}>Average Salary: <span style={{ color: 'var(--primary-500)' }}>{marketSkills.avg_salary_india}</span></p>
                                        <div className="flex flex-wrap gap-xs">
                                            {marketSkills.top_tools.map(t => <span key={t} className="badge" style={{ fontSize: '0.7rem' }}>{t}</span>)}
                                        </div>
                                    </div>
                                </div>

                                {historicalTrends && historicalTrends.total_historical_records > 0 && (
                                    <div className="glass-card fade-in" style={{ padding: '1.5rem', background: 'rgba(100,130,255,0.02)', border: '1px solid rgba(100,130,255,0.1)' }}>
                                        <h4 style={{ fontSize: '0.9rem', fontWeight: 900, color: 'var(--accent-teal)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: 'sm' }}>
                                            📜 Historical Market Context (2021-2025)
                                        </h4>
                                        <div className="flex-col gap-lg">
                                            <div className="flex gap-lg" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', height: '100px', padding: '0 1rem' }}>
                                                {historicalTrends.trend_line.map((item, i) => {
                                                    const maxCount = Math.max(...historicalTrends.trend_line.map(t => t.count), 1);
                                                    const barHeight = (item.count / maxCount) * 100;
                                                    return (
                                                        <div key={item.year} className="flex-col items-center gap-xs" style={{ flex: 1, height: '100%', justifyContent: 'flex-end' }}>
                                                            <div 
                                                                style={{ 
                                                                    width: '100%', 
                                                                    borderRadius: '4px 4px 0 0', 
                                                                    height: `${barHeight}%`, 
                                                                    background: i === 4 ? 'var(--accent-teal)' : 'rgba(20,184,166,0.3)',
                                                                    transition: 'height 1s ease-out',
                                                                    minHeight: item.count > 0 ? '4px' : '0'
                                                                }} 
                                                                title={`${item.count} Jobs Recorded`}
                                                            />
                                                            <span style={{ fontSize: '0.65rem', fontWeight: 800, color: 'var(--text-muted)' }}>{item.year.slice(2)}</span>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                            <div className="flex-col gap-sm" style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '1rem' }}>
                                                <p style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-secondary)' }}>Top Historical Recruiters:</p>
                                                <div className="flex flex-wrap gap-xs">
                                                    {historicalTrends.top_historical_companies.map(c => (
                                                        <span key={c.name} className="badge" style={{ fontSize: '0.68rem', background: 'transparent', borderColor: 'rgba(100,130,255,0.3)' }}>{c.name} ({c.count})</span>
                                                    ))}
                                                </div>
                                            </div>
                                            <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                                                Analyzed {historicalTrends.total_historical_records} past job postings from project data artifacts.
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Mentor */}
                        {activeTab === 'mentor' && beginnerGuide && (
                            <div className="flex-col gap-lg fade-in">
                                <div className="glass-card" style={{ padding: '2rem', border: '1px solid #8b5cf633', background: 'linear-gradient(135deg, rgba(139,92,246,0.05) 0%, transparent 100%)' }}>
                                    <h3 style={{ fontSize: '1.4rem', fontWeight: 900, marginBottom: '1rem', color: '#8b5cf6' }}>🚀 {beginnerGuide.guide_title}</h3>
                                    <div style={{ fontSize: '0.95rem', lineHeight: 1.7, color: 'var(--text-primary)', marginBottom: '2rem' }} dangerouslySetInnerHTML={{ __html: beginnerGuide.summary.replace(/\n/g, '<br/>') }} />
                                    <div className="flex-col gap-lg">
                                        {beginnerGuide.phases.map((p, i) => (
                                            <div key={i} className="flex gap-md">
                                                <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#8b5cf6', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: '0.75rem', flexShrink: 0 }}>{i + 1}</div>
                                                <div>
                                                    <h4 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '0.2rem' }}>{p.phase}</h4>
                                                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{p.focus}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                                    <div className="glass-card" style={{ padding: '1.25rem' }}>
                                        <h4 style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-teal)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>Essential Soft Skills</h4>
                                        <div className="flex flex-wrap gap-xs">
                                            {beginnerGuide.soft_skills.map(s => <span key={s} className="badge" style={{ fontSize: '0.72rem', borderColor: 'rgba(20,184,166,0.2)', color: 'var(--accent-teal)' }}>{s}</span>)}
                                        </div>
                                    </div>
                                    <div className="glass-card" style={{ padding: '1.25rem' }}>
                                        <h4 style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-orange)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>2026 Trends</h4>
                                        <div className="flex flex-wrap gap-xs">
                                            {beginnerGuide.trends.map(t => <span key={t} className="badge" style={{ fontSize: '0.72rem', borderColor: 'rgba(245,158,11,0.2)', color: 'var(--accent-orange)' }}>{t}</span>)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        
                        {/* Mock Interview */}
                        {activeTab === 'mock' && (
                            <div className="flex-col gap-lg fade-in">
                                {!mockComplete ? (
                                    <div className="glass-card" style={{ padding: '2rem' }}>
                                        <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--glass-border)' }}>
                                            <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>🤖 Live Interview Simulator</h3>
                                            <span className="badge" style={{ background: 'var(--primary-500)', color: 'white' }}>Question {mockIndex + 1} / {mockPlan?.length || 0}</span>
                                        </div>
                                        
                                        {currentQuestion ? (
                                            <div className="flex-col gap-lg">
                                                <div style={{ background: 'rgba(56,183,248,0.05)', border: '1px solid rgba(56,183,248,0.2)', padding: '1.5rem', borderRadius: '12px' }}>
                                                    <p style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-blue)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.5rem' }}>Scenario / Question ({mockDifficulty})</p>
                                                    <p style={{ fontSize: '1.1rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{currentQuestion.question}</p>
                                                </div>
                                                
                                                <div className="flex-col gap-sm">
                                                    <div className="flex justify-between items-center">
                                                        <label style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--text-secondary)' }}>Your Answer:</label>
                                                        <button 
                                                            onClick={toggleListening}
                                                            className={`btn ${isListening ? 'btn-danger' : 'btn-secondary'}`}
                                                            style={{ 
                                                                padding: '0.4rem 1rem', 
                                                                fontSize: '0.8rem',
                                                                background: isListening ? '#EF4444' : 'var(--glass-border)',
                                                                color: isListening ? 'white' : 'var(--text-primary)',
                                                                border: 'none',
                                                                animation: isListening ? 'pulse 2s infinite' : 'none'
                                                            }}
                                                        >
                                                            {isListening ? '⏹️ Stop Recording' : '🎤 Speak Answer'}
                                                        </button>
                                                    </div>
                                                    <textarea 
                                                        value={userMockAnswer}
                                                        onChange={(e) => setUserMockAnswer(e.target.value)}
                                                        className="input-field" 
                                                        style={{ 
                                                            minHeight: '150px', 
                                                            padding: '1rem',
                                                            background: isListening ? 'rgba(239, 68, 68, 0.05)' : 'rgba(0,0,0,0.2)',
                                                            border: isListening ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid var(--glass-border)'
                                                        }}
                                                        placeholder="Type your answer here or click 'Speak Answer'... (Tip: Use the STAR method)"
                                                    />
                                                </div>
                                                
                                                <button 
                                                    className="btn btn-primary" 
                                                    onClick={submitMockAnswer}
                                                    disabled={isMockLoading || userMockAnswer.trim().length === 0}
                                                    style={{ alignSelf: 'flex-start', padding: '0.8rem 2rem' }}
                                                >
                                                    {isMockLoading ? 'Evaluating...' : 'Submit Answer'}
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="flex-col items-center justify-center py-xl">
                                                <div style={{ width: '40px', height: '40px', border: '3px solid rgba(100,130,255,0.2)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                                                <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>AI generating custom scenario...</p>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="glass-card" style={{ padding: '2rem' }}>
                                        <h3 style={{ fontSize: '1.5rem', fontWeight: 900, marginBottom: '2rem', textAlign: 'center', color: 'var(--primary-500)' }}>📊 Final Interview Performance</h3>
                                        
                                        <div className="flex-col gap-lg mt-xl">
                                            {mockEvals.map((ev, i) => (
                                                <div key={i} style={{ border: '1px solid var(--glass-border)', padding: '1.5rem', borderRadius: '12px', background: 'rgba(255,255,255,0.02)' }}>
                                                    <div className="flex justify-between" style={{ marginBottom: '1rem' }}>
                                                        <h4 style={{ fontSize: '1rem', fontWeight: 800 }}>Q{i+1}: {mockQuestions[i]}</h4>
                                                        <span className="badge" style={{ background: ev.overall_score >= 8 ? 'var(--primary-500)' : (ev.overall_score >= 5 ? 'var(--accent-orange)' : 'var(--accent-red)'), color: 'white', alignSelf: 'flex-start' }}>Score: {ev.overall_score}/10</span>
                                                    </div>
                                                    
                                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                                                        <div style={{ background: 'rgba(100,130,255,0.05)', padding: '1rem', borderRadius: '8px' }}>
                                                            <strong style={{ color: 'var(--primary-500)', fontSize: '0.8rem' }}>Strengths:</strong>
                                                            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>{ev.strengths}</p>
                                                        </div>
                                                        <div style={{ background: 'rgba(239,68,68,0.05)', padding: '1rem', borderRadius: '8px' }}>
                                                            <strong style={{ color: 'var(--accent-red)', fontSize: '0.8rem' }}>Weaknesses:</strong>
                                                            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>{ev.weaknesses}</p>
                                                        </div>
                                                    </div>
                                                    
                                                    <div style={{ background: 'rgba(56,183,248,0.05)', padding: '1rem', borderRadius: '8px' }}>
                                                        <strong style={{ color: 'var(--accent-blue)', fontSize: '0.8rem' }}>Senior Expert Answer:</strong>
                                                        <p style={{ fontSize: '0.85rem', marginTop: '0.5rem', fontStyle: 'italic' }}>"{ev.improved_answer}"</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        
                                        <div className="flex justify-center" style={{ marginTop: '2rem' }}>
                                            <button className="btn btn-primary" onClick={startMockInterview} style={{ padding: '0.8rem 2rem' }}>🔄 Take Another Mock Interview</button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                @keyframes pulse { 0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); } 70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); } 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } }
                @media (max-width: 900px) { .coach-grid { grid-template-columns: 1fr !important; } }
            `}</style>
        </div>
    );
};
