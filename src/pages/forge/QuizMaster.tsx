import { useState, useEffect } from 'react';
import { CURRICULUM_DATA, type Roadmap } from '../../data/curriculumData';

interface Question {
    question: string;
    options: string[];
    answer: string;
    explanation: string;
    topic_tag?: string;
}

export const QuizMaster = ({ onComplete }: any) => {
    const [mode, setMode] = useState<'custom' | 'curriculum'>('curriculum');
    const [config, setConfig] = useState({ subject: 'Full Stack Development', topic: 'React Context API', difficulty: 'Medium' });

    // Curriculum state
    const [selectedRoadmap, setSelectedRoadmap] = useState<Roadmap | null>(null);
    const [selectedPhaseIdx, setSelectedPhaseIdx] = useState(0);
    const [selectedMilestoneIdx, setSelectedMilestoneIdx] = useState(0);

    const [quiz, setQuiz] = useState<Question[] | null>(null);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [isFinished, setIsFinished] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [feedback, setFeedback] = useState<{ gaps: string[], plan: string[] } | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // Auto-detect domain from profile
    useEffect(() => {
        const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
        if (!user.email) return;

        fetch(`http://127.0.0.1:8000/student/profile?user_email=${encodeURIComponent(user.email)}`)
            .then(r => r.json())
            .then(data => {
                if (data.profile?.domain) {
                    const matched = CURRICULUM_DATA.find(r => r.title === data.profile.domain);
                    if (matched) {
                        setSelectedRoadmap(matched);
                        setConfig(prev => ({ ...prev, subject: matched.title }));
                    }
                }
            })
            .catch(err => console.error("Error loading profile context:", err));
    }, []);

    const startQuiz = async () => {
        setIsLoading(true);
        setError(null);
        try {
            localStorage.getItem('edunovas_user'); // Still check if exists if needed, or just remove if unused

            let subject = config.subject;
            let topic = config.topic;
            let subtopic = "";
            let domain = "";

            if (mode === 'curriculum' && selectedRoadmap) {
                const phase = selectedRoadmap.phases[selectedPhaseIdx];
                const milestone = phase?.milestones[selectedMilestoneIdx];
                domain = selectedRoadmap.title;
                subject = selectedRoadmap.title;
                topic = phase?.name || "";
                subtopic = milestone?.title || "";
            }

            const queryParams = new URLSearchParams({
                subject,
                topic,
                difficulty: config.difficulty,
                ...(domain && { domain }),
                ...(subtopic && { subtopic })
            });

            const res = await fetch(`http://127.0.0.1:8000/generate-quiz?${queryParams.toString()}`);
            const data = await res.json();

            if (Array.isArray(data) && data.length > 0) {
                setQuiz(data);
                setCurrentIndex(0);
                setAnswers({});
                setIsFinished(false);
            } else {
                throw new Error("Groq failed to generate unique questions. Please try a different topic.");
            }
        } catch (e: any) {
            setError(e.message || "Failed to generate quiz.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleAnswer = (option: string) => {
        setAnswers(prev => ({ ...prev, [currentIndex]: option }));
    };

    const calculateScore = () => {
        if (!quiz) return 0;
        let correct = 0;
        quiz.forEach((q, i) => {
            if (answers[i] === q.answer) correct++;
        });
        return Math.round((correct / quiz.length) * 100);
    };

    const nextQuestion = async () => {
        if (quiz && currentIndex < quiz.length - 1) {
            setCurrentIndex(currentIndex + 1);
        } else {
            setIsFinished(true);
            setIsAnalyzing(true);
            const score = calculateScore();
            const results = quiz?.map((q, i) => ({
                question: q.question,
                topic_tag: q.topic_tag || 'Core Concept',
                is_correct: answers[i] === q.answer,
                explanation: q.explanation
            }));

            const user = JSON.parse(localStorage.getItem('edunovas_user') || '{}');
            try {
                if (user.email) {
                    await fetch('http://127.0.0.1:8000/submit-quiz', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_email: user.email,
                            topic: mode === 'curriculum' ? `${selectedRoadmap?.title} - ${selectedRoadmap?.phases[selectedPhaseIdx].name}` : config.topic,
                            score: score,
                            weak_areas: results?.filter(r => !r.is_correct).map(r => r.topic_tag) || []
                        })
                    });
                }

                const fbRes = await fetch('http://127.0.0.1:8000/quiz-feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        results: results,
                        subject: mode === 'curriculum' ? selectedRoadmap?.title : config.subject,
                        topic: mode === 'curriculum' ? selectedRoadmap?.phases[selectedPhaseIdx].name : config.topic
                    })
                });
                const fbData = await fbRes.json();
                setFeedback(fbData);
            } catch (e) {
                console.error("Feedback error:", e);
            } finally {
                setIsAnalyzing(false);
            }
            if (onComplete) onComplete();
        }
    };

    if (isFinished && quiz) {
        const score = calculateScore();
        return (
            <div className="flex-col items-center justify-center gap-xl fade-in" style={{ padding: '2rem' }}>
                <div className="glass-card flex-col items-center gap-lg" style={{ padding: '3rem', maxWidth: '800px', width: '100%', textAlign: 'center' }}>
                    <div style={{ fontSize: '4rem' }}>{score >= 70 ? '🎉' : score >= 40 ? '⚖️' : '🧗'}</div>
                    <h2 style={{ fontSize: '2.5rem', fontWeight: 900 }}>{score}% Accuracy</h2>
                    <p style={{ color: 'var(--text-secondary)' }}>Session completed for <strong>{mode === 'curriculum' ? selectedRoadmap?.phases[selectedPhaseIdx].milestones[selectedMilestoneIdx].title : config.topic}</strong>.</p>

                    {isAnalyzing ? (
                        <div className="mt-lg flex-col items-center gap-md">
                            <div style={{ width: '30px', height: '30px', border: '3px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                            <p style={{ fontSize: '0.85rem', color: 'var(--primary-400)', fontWeight: 700 }}>AI MENTOR: ANALYZING PERFORMANCE GAPS...</p>
                        </div>
                    ) : feedback && (
                        <div className="grid-2 gap-md mt-xl w-full" style={{ textAlign: 'left' }}>
                            <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--accent-red)' }}>
                                <h4 style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-red)', marginBottom: '1rem' }}>GAPS IDENTIFIED</h4>
                                <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                    {feedback.gaps?.map((g, i) => <li key={i}>• {g}</li>) || <li>No major gaps identified</li>}
                                </ul>
                            </div>
                            <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--accent-green)' }}>
                                <h4 style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-green)', marginBottom: '1rem' }}>IMPROVEMENT PLAN</h4>
                                <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                    {feedback.plan?.map((p, i) => <li key={i}>• {p}</li>) || <li>Continue your current learning path</li>}
                                </ul>
                            </div>
                        </div>
                    )}

                    <div className="flex gap-md mt-xl">
                        <button className="btn btn-primary" onClick={() => { setIsFinished(false); setFeedback(null); setCurrentIndex(0); setAnswers({}); }}>Retake Quiz</button>
                        <button className="btn btn-secondary" onClick={() => { setQuiz(null); setFeedback(null); }}>New Topic</button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-col gap-xl">
            <header className="flex justify-between items-end">
                <div>
                    <h2 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Quiz Master</h2>
                    <p style={{ color: 'var(--text-secondary)' }}>Adaptive intelligence assessment engine</p>
                </div>
                <div className="flex glass-card" style={{ padding: '4px', borderRadius: '12px' }}>
                    <button
                        onClick={() => setMode('curriculum')}
                        className={`btn ${mode === 'curriculum' ? 'btn-primary' : ''}`}
                        style={{ fontSize: '0.75rem', padding: '0.5rem 1rem', borderRadius: '8px', background: mode === 'curriculum' ? '' : 'transparent' }}
                    >Curriculum</button>
                    <button
                        onClick={() => setMode('custom')}
                        className={`btn ${mode === 'custom' ? 'btn-primary' : ''}`}
                        style={{ fontSize: '0.75rem', padding: '0.5rem 1rem', borderRadius: '8px', background: mode === 'custom' ? '' : 'transparent' }}
                    >Custom Topic</button>
                </div>
            </header>

            {!quiz ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 450px) 1fr', gap: '2rem' }}>
                    <div className="glass-card flex-col gap-lg" style={{ padding: '2rem' }}>
                        <h3 style={{ fontSize: '1.1rem', fontWeight: 800 }}>{mode === 'curriculum' ? 'Select from Roadmap' : 'Define Topic'}</h3>

                        {mode === 'curriculum' ? (
                            <div className="flex-col gap-md">
                                <div className="flex-col gap-xs">
                                    <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)' }}>ROADMAP</label>
                                    <select
                                        className="input-field"
                                        value={selectedRoadmap?.id || ""}
                                        onChange={(e) => {
                                            const r = CURRICULUM_DATA.find(rd => rd.id === e.target.value);
                                            if (r) { setSelectedRoadmap(r); setSelectedPhaseIdx(0); setSelectedMilestoneIdx(0); }
                                        }}
                                    >
                                        <option value="">Select Roadmap</option>
                                        {CURRICULUM_DATA.map(r => <option key={r.id} value={r.id}>{r.icon} {r.title}</option>)}
                                    </select>
                                </div>
                                {selectedRoadmap && (
                                    <>
                                        <div className="flex-col gap-xs">
                                            <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)' }}>PHASE</label>
                                            <select
                                                className="input-field"
                                                value={selectedPhaseIdx}
                                                onChange={(e) => { setSelectedPhaseIdx(Number(e.target.value)); setSelectedMilestoneIdx(0); }}
                                            >
                                                {selectedRoadmap.phases.map((p, i) => <option key={i} value={i}>{i + 1}. {p.name}</option>)}
                                            </select>
                                        </div>
                                        <div className="flex-col gap-xs">
                                            <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)' }}>MILESTONE / SUBTOPIC</label>
                                            <select
                                                className="input-field"
                                                value={selectedMilestoneIdx}
                                                onChange={(e) => setSelectedMilestoneIdx(Number(e.target.value))}
                                            >
                                                {selectedRoadmap.phases[selectedPhaseIdx].milestones.map((m, i) => <option key={i} value={i}>{m.title}</option>)}
                                            </select>
                                        </div>
                                    </>
                                )}
                            </div>
                        ) : (
                            <div className="flex-col gap-md">
                                <div className="flex-col gap-xs">
                                    <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)' }}>SUBJECT / DOMAIN</label>
                                    <input className="input-field" value={config.subject} onChange={(e) => setConfig({ ...config, subject: e.target.value })} placeholder="e.g. Frontend Engineering" />
                                </div>
                                <div className="flex-col gap-xs">
                                    <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)' }}>SPECIFIC TOPIC</label>
                                    <input className="input-field" value={config.topic} onChange={(e) => setConfig({ ...config, topic: e.target.value })} placeholder="e.g. Async/Await in JavaScript" />
                                </div>
                            </div>
                        )}

                        <div className="flex-col gap-xs">
                            <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)' }}>DIFFICULTY LEVEL</label>
                            <div className="flex gap-sm">
                                {['Easy', 'Medium', 'Hard'].map(lvl => (
                                    <button
                                        key={lvl}
                                        onClick={() => setConfig({ ...config, difficulty: lvl })}
                                        className={`btn flex-1 ${config.difficulty === lvl ? 'btn-primary' : 'btn-secondary'}`}
                                        style={{ fontSize: '0.75rem', padding: '0.6rem' }}
                                    >
                                        {lvl}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button className="btn btn-primary w-full" onClick={startQuiz} disabled={isLoading || (mode === 'curriculum' && !selectedRoadmap)}>
                            {isLoading ? (
                                <span className="flex items-center gap-sm">
                                    <span style={{ width: '14px', height: '14px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                                    GENERING ASSESSMENT...
                                </span>
                            ) : 'INITIALIZE ASSESSMENT'}
                        </button>

                        {error && <div className="glass-card" style={{ padding: '0.75rem', border: '1px solid var(--accent-red)', color: 'var(--accent-red)', fontSize: '0.75rem', textAlign: 'center' }}>⚠️ {error}</div>}
                    </div>

                    <div className="glass-card flex-col justify-center items-center gap-md" style={{ padding: '3rem', opacity: 0.8, textAlign: 'center' }}>
                        <span style={{ fontSize: '3rem' }}>🔬</span>
                        <h4 style={{ fontWeight: 800 }}>AI Assessment Mode</h4>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '300px' }}>
                            Groq AI will generate 5 targeted questions based on your selection to measure conceptual depth and practical knowledge.
                        </p>
                    </div>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '2rem' }}>
                    <div className="flex-col gap-lg">
                        <div className="glass-card flex-col gap-xl" style={{ padding: '2.5rem' }}>
                            <div className="flex justify-between items-center">
                                <span style={{ fontSize: '0.72rem', fontWeight: 900, color: 'var(--primary-400)', textTransform: 'uppercase' }}>
                                    {mode === 'curriculum' ? selectedRoadmap?.title : config.topic} ● QUESTION {currentIndex + 1} / {quiz.length}
                                </span>
                                <div style={{ height: '6px', width: '120px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{ height: '100%', width: `${((currentIndex + 1) / quiz.length) * 100}%`, background: 'var(--primary-500)', transition: 'width 0.3s ease' }}></div>
                                </div>
                            </div>

                            <h3 style={{ fontSize: '1.3rem', lineHeight: 1.5, fontWeight: 700 }}>{quiz[currentIndex].question}</h3>

                            <div className="flex-col gap-sm">
                                {quiz[currentIndex].options.map((opt, i) => (
                                    <button
                                        key={i}
                                        className={`glass-card hover-lift ${answers[currentIndex] === opt ? 'active' : ''}`}
                                        style={{
                                            padding: '1.25rem 1.5rem',
                                            textAlign: 'left',
                                            fontSize: '0.95rem',
                                            border: answers[currentIndex] === opt ? '2px solid var(--primary-500)' : '1px solid var(--glass-border)',
                                            background: answers[currentIndex] === opt ? 'rgba(52, 160, 90, 0.08)' : 'var(--glass-bg)',
                                            width: '100%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            transition: 'all 0.2s ease'
                                        }}
                                        onClick={() => handleAnswer(opt)}
                                    >
                                        <span style={{ fontWeight: 900, marginRight: '1rem', color: answers[currentIndex] === opt ? 'var(--primary-400)' : 'var(--text-muted)', width: '20px' }}>
                                            {String.fromCharCode(65 + i)}.
                                        </span>
                                        {opt}
                                    </button>
                                ))}
                            </div>

                            <div className="flex justify-end pt-lg">
                                <button className="btn btn-primary" onClick={nextQuestion} disabled={!answers[currentIndex]} style={{ minWidth: '160px' }}>
                                    {currentIndex === quiz.length - 1 ? 'FINISH ASSESSMENT' : 'NEXT QUESTION →'}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="flex-col gap-md">
                        <div className="glass-card" style={{ padding: '1.5rem' }}>
                            <h4 style={{ fontSize: '0.72rem', fontWeight: 800, letterSpacing: '1px', marginBottom: '1rem', color: 'var(--primary-400)' }}>SENSEI HINT</h4>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                                "This question tests your understanding of <strong>{(quiz[currentIndex] as any).topic_tag || 'core concepts'}</strong>. Think about performance implications."
                            </p>
                        </div>

                        <div className="glass-card" style={{ padding: '1.5rem', background: 'rgba(52, 160, 90, 0.03)' }}>
                            <h4 style={{ fontSize: '0.72rem', fontWeight: 800, letterSpacing: '1px', marginBottom: '1rem', color: 'var(--primary-400)' }}>CURRENT PERFORMANCE</h4>
                            <div className="flex justify-between items-center mb-sm">
                                <span style={{ fontSize: '0.78rem' }}>Accuracy Potential</span>
                                <span style={{ color: 'var(--accent-green)', fontWeight: 800 }}>High</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span style={{ fontSize: '0.78rem' }}>XP Multiplier</span>
                                <span style={{ color: 'var(--accent-blue)', fontWeight: 800 }}>1.5x Active</span>
                            </div>
                        </div>

                        <button className="btn btn-secondary w-full" style={{ fontSize: '0.75rem', opacity: 0.6 }} onClick={() => setQuiz(null)}>
                            Abort Assessment
                        </button>
                    </div>
                </div>
            )}
            <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                .input-field {
                    width: 100%;
                    padding: 0.75rem;
                    background: var(--glass-bg);
                    border: 1px solid var(--glass-border);
                    border-radius: var(--radius-sm);
                    color: var(--text-primary);
                    font-size: 0.85rem;
                    outline: none;
                }
                .input-field:focus {
                    border-color: var(--primary-500);
                }
                option { background: #1a1a1a; color: white; }
            `}</style>
        </div>
    );
};
