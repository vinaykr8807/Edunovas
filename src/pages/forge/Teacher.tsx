import { useState } from 'react';
import { CURRICULUM_DATA, type Roadmap } from '../../data/curriculumData';

const getUser = () => JSON.parse(localStorage.getItem('edunovas_user') || '{}');

const saveProgress = async (payload: object) => {
    try {
        const user = getUser();
        if (!user?.email) return;
        await fetch('http://127.0.0.1:8000/save-teacher-progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_email: user.email, ...payload })
        });
    } catch { /* silent fail — progress saved locally via status state */ }
};


interface TopicStatus {
    [key: string]: 'pending' | 'learning' | 'done';
}

interface Explanation {
    explanation: string;
    topic: string;
    subtopic: string;
}

export const Teacher = () => {
    // Step 1: pick domain
    const [selectedRoadmap, setSelectedRoadmap] = useState<Roadmap | null>(null);
    // Step 2: pick phase
    const [phaseIdx, setPhaseIdx] = useState(0);
    // Step 3: active milestone
    const [milestoneIdx, setMilestoneIdx] = useState(0);

    const [status, setStatus] = useState<TopicStatus>({});
    const [explanation, setExplanation] = useState<Explanation | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [showDoubt, setShowDoubt] = useState(false);
    const [doubtText, setDoubtText] = useState('');
    const [doubtAnswer, setDoubtAnswer] = useState<string | null>(null);
    const [isDownloading, setIsDownloading] = useState(false);
    const [doubtLoading, setDoubtLoading] = useState(false);
    const [savedNotes, setSavedNotes] = useState<{ name: string; display_name: string; signed_url: string; created_at: string }[]>([]);
    const [notesLoading, setNotesLoading] = useState(false);
    const [showNotes, setShowNotes] = useState(false);

    const loadSavedNotes = async () => {
        const user = getUser();
        if (!user?.email) return;
        setNotesLoading(true);
        try {
            const res = await fetch(`http://127.0.0.1:8000/student/notes?user_email=${encodeURIComponent(user.email)}`);
            const data = await res.json();
            setSavedNotes(data.notes || []);
        } catch { setSavedNotes([]); }
        finally { setNotesLoading(false); }
    };

    useState(() => {
        // Run once on init
        const user = getUser();
        if (!user.email) return;
        fetch(`http://127.0.0.1:8000/student/profile?user_email=${encodeURIComponent(user.email)}`)
            .then(r => r.json())
            .then(data => {
                if (data.profile?.domain) {
                    const matched = CURRICULUM_DATA.find(r => r.title === data.profile.domain);
                    if (matched) {
                        console.log("Auto-selecting roadmap:", matched.title);
                        setSelectedRoadmap(matched);
                    }
                }
            })
            .catch(err => console.error("Error loading profile:", err));
    });

    const phase = selectedRoadmap?.phases[phaseIdx];
    const milestone = phase?.milestones[milestoneIdx];
    const totalMilestones = selectedRoadmap?.phases.reduce((acc, p) => acc + p.milestones.length, 0) || 0;
    const doneCount = Object.values(status).filter(s => s === 'done').length;
    const overallProgress = totalMilestones > 0 ? Math.round((doneCount / totalMilestones) * 100) : 0;

    const milestoneKey = milestone ? `${phaseIdx}-${milestoneIdx}` : '';

    const loadExplanation = async (roadmap: Roadmap, pIdx: number, mIdx: number) => {
        const ph = roadmap.phases[pIdx];
        const ms = ph?.milestones[mIdx];
        if (!ms) return;
        const key = `${pIdx}-${mIdx}`;
        setExplanation(null);
        setDoubtAnswer(null);
        setShowDoubt(false);
        setDoubtText('');
        setIsLoading(true);
        setStatus(prev => ({ ...prev, [key]: 'learning' }));
        // Save "learning" status to Supabase
        saveProgress({
            domain: roadmap.title,
            roadmap_id: roadmap.id,
            phase_name: ph.name,
            phase_index: pIdx,
            milestone_title: ms.title,
            milestone_index: mIdx,
            status: 'learning'
        });
        try {
            const res = await fetch('http://127.0.0.1:8000/teacher/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: ph.name,
                    subtopic: ms.title,
                    domain: roadmap.title,
                    has_doubt: false
                })
            });
            const data = await res.json();
            setExplanation(data);
        } catch {
            setExplanation({ explanation: 'Failed to load explanation. Please check if backend is running.', topic: ph.name, subtopic: ms.title });
        } finally {
            setIsLoading(false);
        }
    };

    const handleAskDoubt = async () => {
        if (!doubtText.trim() || !milestone || !phase || !selectedRoadmap) return;
        setDoubtLoading(true);
        try {
            const res = await fetch('http://127.0.0.1:8000/teacher/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: phase.name,
                    subtopic: milestone.title,
                    domain: selectedRoadmap.title,
                    has_doubt: true,
                    doubt_text: doubtText
                })
            });
            const data = await res.json();
            setDoubtAnswer(data.explanation);
        } catch {
            setDoubtAnswer('Could not get answer. Please try again.');
        } finally {
            setDoubtLoading(false);
        }
    };

    const handleMarkDone = () => {
        setStatus(prev => ({ ...prev, [milestoneKey]: 'done' }));
        // Save "done" status to Supabase
        if (phase && milestone && selectedRoadmap) {
            saveProgress({
                domain: selectedRoadmap.title,
                roadmap_id: selectedRoadmap.id,
                phase_name: phase.name,
                phase_index: phaseIdx,
                milestone_title: milestone.title,
                milestone_index: milestoneIdx,
                status: 'done'
            });
        }
        // Auto-advance
        if (phase && milestoneIdx < phase.milestones.length - 1) {
            const nextMIdx = milestoneIdx + 1;
            setMilestoneIdx(nextMIdx);
            if (selectedRoadmap) loadExplanation(selectedRoadmap, phaseIdx, nextMIdx);
        } else if (selectedRoadmap && phaseIdx < selectedRoadmap.phases.length - 1) {
            const nextPIdx = phaseIdx + 1;
            setPhaseIdx(nextPIdx);
            setMilestoneIdx(0);
            loadExplanation(selectedRoadmap, nextPIdx, 0);
        }
    };

    const handleDownloadNotes = async () => {
        if (!milestone || !phase || !selectedRoadmap) return;
        setIsDownloading(true);
        try {
            const user = getUser();
            const res = await fetch('http://127.0.0.1:8000/teacher/generate-notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: phase.name,
                    subtopic: milestone.title,
                    domain: selectedRoadmap.title,
                    user_email: user?.email || null
                })
            });
            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${milestone.title.replace(/\s+/g, '_')}_Notes.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                // Refresh saved notes list — backend just uploaded it
                if (user?.email) setTimeout(() => loadSavedNotes(), 1500);
            }
        } catch (e) {
            console.error('Notes download failed', e);
        } finally {
            setIsDownloading(false);
        }
    };

    // Render inline markdown: **bold**, `code`, mixed text
    const renderInline = (text: string) => {
        const parts: React.ReactNode[] = [];
        // Split on **bold** and `code`
        const regex = /(\*\*[^*]+\*\*|`[^`]+`)/g;
        let last = 0, m;
        let key = 0;
        while ((m = regex.exec(text)) !== null) {
            if (m.index > last) parts.push(<span key={key++}>{text.slice(last, m.index)}</span>);
            const token = m[0];
            if (token.startsWith('**')) {
                parts.push(<strong key={key++} style={{ color: 'var(--text-primary)', fontWeight: 700 }}>{token.slice(2, -2)}</strong>);
            } else {
                parts.push(<code key={key++} style={{ background: 'rgba(52,160,90,0.12)', color: 'var(--primary-700)', padding: '1px 5px', borderRadius: '4px', fontSize: '0.85em', fontFamily: 'monospace' }}>{token.slice(1, -1)}</code>);
            }
            last = m.index + token.length;
        }
        if (last < text.length) parts.push(<span key={key++}>{text.slice(last)}</span>);
        return parts;
    };

    const formatExplanation = (text: string) => {
        const lines = text.split('\n');
        const elements: React.ReactNode[] = [];
        let i = 0;

        while (i < lines.length) {
            const line = lines[i];

            // --- Headings ---
            if (line.startsWith('### ')) {
                elements.push(<h5 key={i} style={{ color: 'var(--primary-600)', fontSize: '0.95rem', fontWeight: 800, margin: '1rem 0 0.4rem' }}>{renderInline(line.slice(4))}</h5>);
                i++; continue;
            }
            if (line.startsWith('## ')) {
                elements.push(<h4 key={i} style={{ color: 'var(--primary-600)', fontSize: '1rem', fontWeight: 800, margin: '1.25rem 0 0.5rem', borderBottom: '1px solid rgba(52,160,90,0.15)', paddingBottom: '4px' }}>{renderInline(line.slice(3))}</h4>);
                i++; continue;
            }
            if (line.startsWith('# ')) {
                elements.push(<h3 key={i} style={{ color: 'var(--primary-700)', fontSize: '1.1rem', fontWeight: 900, margin: '1rem 0 0.5rem' }}>{renderInline(line.slice(2))}</h3>);
                i++; continue;
            }

            // --- Markdown table: collect all table rows ---
            if (line.trim().startsWith('|') && line.includes('|')) {
                const tableLines: string[] = [];
                while (i < lines.length && lines[i].trim().startsWith('|')) {
                    tableLines.push(lines[i]);
                    i++;
                }
                const isSeparator = (l: string) => /^\|[-|: ]+\|$/.test(l.trim());
                const rows = tableLines.filter(l => !isSeparator(l));
                const parseCells = (l: string) => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim());

                if (rows.length > 0) {
                    const headerCells = parseCells(rows[0]);
                    const bodyRows = rows.slice(1);
                    elements.push(
                        <div key={`table-${i}`} style={{ overflowX: 'auto', margin: '0.75rem 0' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.87rem' }}>
                                <thead>
                                    <tr style={{ background: 'rgba(52,160,90,0.12)' }}>
                                        {headerCells.map((c, ci) => (
                                            <th key={ci} style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 700, color: 'var(--primary-700)', borderBottom: '2px solid rgba(52,160,90,0.3)', whiteSpace: 'nowrap' }}>
                                                {renderInline(c)}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {bodyRows.map((row, ri) => (
                                        <tr key={ri} style={{ background: ri % 2 === 0 ? 'transparent' : 'rgba(52,160,90,0.04)' }}>
                                            {parseCells(row).map((c, ci) => (
                                                <td key={ci} style={{ padding: '7px 12px', borderBottom: '1px solid rgba(52,160,90,0.08)', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                                                    {renderInline(c)}
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    );
                }
                continue;
            }

            // --- Bullets: * or - or • ---
            if (/^[*\-•]\s/.test(line)) {
                const content = line.replace(/^[*\-•]\s+/, '');
                elements.push(<p key={i} style={{ margin: '3px 0 3px 16px', fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.65, display: 'flex', gap: '8px' }}>
                    <span style={{ color: 'var(--primary-500)', flexShrink: 0, fontWeight: 700 }}>•</span>
                    <span>{renderInline(content)}</span>
                </p>);
                i++; continue;
            }

            // --- Numbered list: 1. 2. etc ---
            if (/^\d+\.\s/.test(line)) {
                const [num, ...rest] = line.split(/\.\s(.*)/);
                elements.push(<p key={i} style={{ margin: '3px 0 3px 16px', fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.65, display: 'flex', gap: '8px' }}>
                    <span style={{ color: 'var(--primary-500)', flexShrink: 0, fontWeight: 700, minWidth: '1.4em' }}>{num}.</span>
                    <span>{renderInline(rest[0] || '')}</span>
                </p>);
                i++; continue;
            }

            // --- Empty line ---
            if (line.trim() === '') {
                elements.push(<div key={i} style={{ height: '6px' }} />);
                i++; continue;
            }

            // --- Standalone bold line ---
            if (/^\*\*[^*]+\*\*\s*:?$/.test(line.trim())) {
                elements.push(<strong key={i} style={{ display: 'block', color: 'var(--primary-600)', margin: '8px 0 2px', fontSize: '0.93rem' }}>{line.replace(/\*\*/g, '').replace(/:$/, '')}</strong>);
                i++; continue;
            }

            // --- Normal paragraph ---
            elements.push(<p key={i} style={{ margin: '4px 0', fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.65 }}>{renderInline(line)}</p>);
            i++;
        }
        return elements;
    };


    // ── Domain Picker ───────────────────────────────────────
    if (!selectedRoadmap) {
        return (
            <div className="flex-col gap-xl fade-in">
                <header>
                    <h2 style={{ fontSize: '2rem', fontWeight: 900 }}>🎓 AI Teacher</h2>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                        Select your learning domain to begin your guided journey
                    </p>
                </header>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1.25rem' }}>
                    {CURRICULUM_DATA.map(roadmap => (
                        <button
                            key={roadmap.id}
                            onClick={() => {
                                setSelectedRoadmap(roadmap);
                                setPhaseIdx(0);
                                setMilestoneIdx(0);
                                loadExplanation(roadmap, 0, 0);
                            }}
                            className="glass-card"
                            style={{
                                padding: '1.5rem',
                                cursor: 'pointer',
                                border: `1px solid ${roadmap.color}30`,
                                textAlign: 'left',
                                transition: 'all 0.3s ease',
                                background: `linear-gradient(135deg, ${roadmap.color}06 0%, transparent 100%)`
                            }}
                        >
                            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>{roadmap.icon}</div>
                            <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.3rem' }}>{roadmap.title}</h3>
                            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', lineHeight: 1.5 }}>{roadmap.description.slice(0, 90)}…</p>
                            <div className="flex gap-sm">
                                <span className="badge" style={{ fontSize: '0.65rem', borderColor: roadmap.color, color: roadmap.color }}>{roadmap.difficulty}</span>
                                <span className="badge" style={{ fontSize: '0.65rem' }}>{roadmap.duration}</span>
                                <span className="badge" style={{ fontSize: '0.65rem' }}>{roadmap.phases.length} Phases</span>
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        );
    }

    // ── Main Teacher View ───────────────────────────────────
    return (
        <div className="flex-col gap-xl fade-in">
            {/* Header */}
            <header className="flex justify-between items-start" style={{ flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <div className="flex items-center gap-md">
                        <button onClick={() => setSelectedRoadmap(null)} className="btn btn-secondary" style={{ padding: '0.4rem 0.9rem', fontSize: '0.75rem' }}>← Domains</button>
                        <span style={{ fontSize: '1.5rem' }}>{selectedRoadmap.icon}</span>
                        <h2 style={{ fontSize: '1.6rem', fontWeight: 900 }}>{selectedRoadmap.title}</h2>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.4rem', fontSize: '0.9rem' }}>AI-Guided Learning · Phase {phaseIdx + 1} of {selectedRoadmap.phases.length}</p>
                </div>
                {/* Overall Progress */}
                <div className="glass-card" style={{ padding: '0.75rem 1.5rem', minWidth: '200px' }}>
                    <div className="flex justify-between items-center mb-xs">
                        <span style={{ fontSize: '0.65rem', fontWeight: 800, color: 'var(--text-muted)' }}>OVERALL PROGRESS</span>
                        <span style={{ fontWeight: 900, color: 'var(--primary-500)', fontSize: '1rem' }}>{overallProgress}%</span>
                    </div>
                    <div style={{ height: '6px', background: 'rgba(52,160,90,0.12)', borderRadius: '3px' }}>
                        <div style={{ height: '100%', width: `${overallProgress}%`, background: 'var(--primary-500)', borderRadius: '3px', transition: 'width 0.5s ease' }} />
                    </div>
                    <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>{doneCount} / {totalMilestones} topics completed</p>
                </div>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '1.5rem', alignItems: 'start' }} className="teacher-grid">
                {/* Left: Phase + Milestone Nav */}
                <div className="flex-col gap-md" style={{ position: 'sticky', top: '110px' }}>
                    {selectedRoadmap.phases.map((ph, pIdx) => (
                        <div key={pIdx} className="glass-card" style={{ padding: '1rem', border: phaseIdx === pIdx ? `1px solid ${selectedRoadmap.color}` : '1px solid var(--glass-border)' }}>
                            <h4 style={{ fontSize: '0.78rem', fontWeight: 800, color: phaseIdx === pIdx ? selectedRoadmap.color : 'var(--text-muted)', marginBottom: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                Phase {pIdx + 1}: {ph.name}
                            </h4>
                            <div className="flex-col gap-xs">
                                {ph.milestones.map((ms, mIdx) => {
                                    const k = `${pIdx}-${mIdx}`;
                                    const s = status[k];
                                    const isActive = phaseIdx === pIdx && milestoneIdx === mIdx;
                                    return (
                                        <button
                                            key={mIdx}
                                            onClick={() => {
                                                setPhaseIdx(pIdx);
                                                setMilestoneIdx(mIdx);
                                                loadExplanation(selectedRoadmap, pIdx, mIdx);
                                            }}
                                            style={{
                                                display: 'flex', alignItems: 'center', gap: '8px',
                                                padding: '0.5rem 0.75rem', borderRadius: '8px', border: 'none',
                                                cursor: 'pointer', textAlign: 'left', width: '100%',
                                                background: isActive ? `${selectedRoadmap.color}15` : 'transparent',
                                                transition: 'all 0.2s ease'
                                            }}
                                        >
                                            <span style={{ fontSize: '0.9rem', flexShrink: 0 }}>
                                                {s === 'done' ? '✅' : s === 'learning' ? '📖' : '⬜'}
                                            </span>
                                            <span style={{ fontSize: '0.78rem', color: isActive ? 'var(--primary-600)' : 'var(--text-secondary)', fontWeight: isActive ? 700 : 400, lineHeight: 1.3 }}>
                                                {ms.title}
                                            </span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Right: Content Panel */}
                <div className="flex-col gap-lg">
                    {/* Topic header */}
                    {milestone && (
                        <div className="glass-card" style={{ padding: '1.5rem', borderTop: `3px solid ${selectedRoadmap.color}` }}>
                            <div className="flex justify-between items-start" style={{ flexWrap: 'wrap', gap: '1rem' }}>
                                <div>
                                    <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 800, letterSpacing: '1px', marginBottom: '4px' }}>
                                        {phase?.name}
                                    </p>
                                    <h3 style={{ fontSize: '1.4rem', fontWeight: 900, color: 'var(--text-primary)' }}>{milestone.title}</h3>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: '0.4rem' }}>{milestone.description}</p>
                                    <div className="flex flex-wrap gap-xs" style={{ marginTop: '0.75rem' }}>
                                        {milestone.skills.map(s => (
                                            <span key={s} className="badge" style={{ fontSize: '0.68rem', background: `${selectedRoadmap.color}10`, borderColor: `${selectedRoadmap.color}40`, color: selectedRoadmap.color }}>{s}</span>
                                        ))}
                                    </div>
                                </div>
                                <div className="flex-col gap-sm">
                                    <button
                                        className="btn btn-primary"
                                        style={{ fontSize: '0.8rem', padding: '0.6rem 1.2rem', whiteSpace: 'nowrap' }}
                                        onClick={handleMarkDone}
                                        disabled={status[milestoneKey] === 'done'}
                                    >
                                        {status[milestoneKey] === 'done' ? '✅ Completed' : '✓ Mark Done & Next'}
                                    </button>
                                    <button
                                        className="btn btn-secondary"
                                        style={{ fontSize: '0.75rem', padding: '0.5rem 1rem', whiteSpace: 'nowrap' }}
                                        onClick={handleDownloadNotes}
                                        disabled={isDownloading}
                                    >
                                        {isDownloading ? '⏳ Generating...' : '📄 Download Notes PDF'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* AI Explanation */}
                    <div className="glass-card" style={{ padding: '1.75rem', minHeight: '300px' }}>
                        <div className="flex justify-between items-center" style={{ marginBottom: '1.25rem' }}>
                            <h4 style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--primary-500)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                                🤖 AI Teacher Explanation
                            </h4>
                            {explanation && (
                                <button
                                    className="btn btn-secondary"
                                    style={{ fontSize: '0.72rem', padding: '0.35rem 0.8rem' }}
                                    onClick={() => selectedRoadmap && loadExplanation(selectedRoadmap, phaseIdx, milestoneIdx)}
                                >
                                    ↻ Regenerate
                                </button>
                            )}
                        </div>

                        {isLoading ? (
                            <div className="flex-col items-center justify-center" style={{ padding: '3rem', gap: '1rem' }}>
                                <div style={{ width: '40px', height: '40px', border: '3px solid rgba(52,160,90,0.2)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Teacher AI is preparing your lesson…</p>
                            </div>
                        ) : explanation ? (
                            <div style={{ lineHeight: 1.7 }}>
                                {formatExplanation(explanation.explanation)}
                            </div>
                        ) : (
                            <div className="flex-col items-center" style={{ padding: '3rem', opacity: 0.5 }}>
                                <p>Select a topic from the left to start learning</p>
                            </div>
                        )}
                    </div>

                    {/* Doubt Section */}
                    {explanation && (
                        <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid rgba(52,160,90,0.2)' }}>
                            <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
                                <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--primary-600)' }}>
                                    🙋 Have a Doubt?
                                </h4>
                                <button
                                    className="btn btn-secondary"
                                    style={{ fontSize: '0.72rem', padding: '0.4rem 0.9rem' }}
                                    onClick={() => setShowDoubt(!showDoubt)}
                                >
                                    {showDoubt ? 'Hide' : 'Ask AI Teacher'}
                                </button>
                            </div>

                            {showDoubt && (
                                <div className="flex-col gap-md fade-in">
                                    <textarea
                                        value={doubtText}
                                        onChange={e => setDoubtText(e.target.value)}
                                        placeholder="Type your doubt or question about this topic…"
                                        className="input-field"
                                        style={{ minHeight: '80px', resize: 'vertical', fontSize: '0.9rem', padding: '0.9rem' }}
                                    />
                                    <button
                                        className="btn btn-primary"
                                        style={{ alignSelf: 'flex-start', padding: '0.6rem 1.5rem' }}
                                        onClick={handleAskDoubt}
                                        disabled={!doubtText.trim() || doubtLoading}
                                    >
                                        {doubtLoading ? '⏳ Thinking…' : '🤖 Get Answer'}
                                    </button>

                                    {doubtAnswer && (
                                        <div style={{ padding: '1.25rem', background: 'rgba(52,160,90,0.05)', borderRadius: '8px', border: '1px solid rgba(52,160,90,0.15)', marginTop: '0.5rem' }}>
                                            <p style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--primary-600)', marginBottom: '0.75rem', letterSpacing: '0.5px' }}>AI TEACHER RESPONSE</p>
                                            <div style={{ lineHeight: 1.7 }}>
                                                {formatExplanation(doubtAnswer)}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── Notes Library ── */}
                    {selectedRoadmap && (
                        <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid rgba(52,160,90,0.15)' }}>
                            <div className="flex justify-between items-center">
                                <div className="flex items-center gap-md">
                                    <span style={{ fontSize: '1.2rem' }}>📁</span>
                                    <div>
                                        <h4 style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--text-primary)' }}>My Notes Library</h4>
                                        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>All PDFs saved to your Supabase account</p>
                                    </div>
                                </div>
                                <button
                                    className="btn btn-secondary"
                                    style={{ fontSize: '0.78rem', padding: '0.45rem 1rem' }}
                                    onClick={() => {
                                        const next = !showNotes;
                                        setShowNotes(next);
                                        if (next && savedNotes.length === 0) loadSavedNotes();
                                    }}
                                >
                                    {showNotes ? '▲ Hide' : '▼ View Saved Notes'}
                                </button>
                            </div>

                            {showNotes && (
                                <div className="fade-in" style={{ marginTop: '1.25rem', borderTop: '1px solid var(--glass-border)', paddingTop: '1.25rem' }}>
                                    {notesLoading ? (
                                        <div className="flex items-center gap-md" style={{ padding: '1rem' }}>
                                            <div style={{ width: '20px', height: '20px', border: '3px solid rgba(52,160,90,0.15)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                                            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading your saved notes…</p>
                                        </div>
                                    ) : savedNotes.length === 0 ? (
                                        <div style={{ textAlign: 'center', padding: '2rem', opacity: 0.6 }}>
                                            <p style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>📭</p>
                                            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No saved notes yet. Generate notes for a topic and they'll appear here.</p>
                                        </div>
                                    ) : (
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '0.75rem' }}>
                                            {savedNotes.map((note, i) => (
                                                <div key={i} style={{
                                                    padding: '1rem 1.25rem',
                                                    background: 'rgba(52,160,90,0.04)',
                                                    border: '1px solid rgba(52,160,90,0.15)',
                                                    borderRadius: '10px',
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center',
                                                    gap: '0.75rem'
                                                }}>
                                                    <div style={{ overflow: 'hidden' }}>
                                                        <p style={{ fontWeight: 700, fontSize: '0.82rem', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                            📄 {note.display_name || note.name}
                                                        </p>
                                                        {note.created_at && (
                                                            <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                                                                {new Date(note.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                                                            </p>
                                                        )}
                                                    </div>
                                                    {note.signed_url ? (
                                                        <a
                                                            href={note.signed_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            download
                                                            style={{
                                                                flexShrink: 0,
                                                                padding: '0.4rem 0.8rem',
                                                                background: 'var(--primary-500)',
                                                                color: 'white',
                                                                borderRadius: '8px',
                                                                fontSize: '0.72rem',
                                                                fontWeight: 700,
                                                                textDecoration: 'none',
                                                                whiteSpace: 'nowrap'
                                                            }}
                                                        >
                                                            ⬇ PDF
                                                        </a>
                                                    ) : (
                                                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Link expired</span>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    <button
                                        className="btn btn-secondary"
                                        style={{ marginTop: '1rem', fontSize: '0.75rem', padding: '0.4rem 0.9rem' }}
                                        onClick={loadSavedNotes}
                                        disabled={notesLoading}
                                    >
                                        {notesLoading ? '⏳ Refreshing…' : '🔄 Refresh List'}
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>


            <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                @media (max-width: 900px) {
                    .teacher-grid { grid-template-columns: 1fr !important; }
                }
                .glass-card button:hover { opacity: 0.85; }
            `}</style>
        </div>
    );
};
