import React, { useEffect, useState } from 'react';

interface Analytics {
    total_students: number;
    active_today: number;
    total_xp: number;
    total_interaction_hits: number;
    total_interviews: number;
    avg_readiness_score: number;
    domain_distribution: Record<string, number>;
    top_skills: { name: string; count: number }[];
}

interface StudentPerf {
    user_id: string;
    email: string;
    full_name: string;
    joined: string;
    xp: number;
    level: number;
    topics_completed: number;
    total_topics_attempted: number;
    domains_studied: string[];
    last_topic: string | null;
    interview_sessions: number;
    latest_readiness: number | null;
    avg_readiness: number | null;
    last_interview_role: string | null;
}

export const AdminDashboard: React.FC = () => {
    const [data, setData] = useState<Analytics | null>(null);
    const [students, setStudents] = useState<StudentPerf[]>([]);
    const [loading, setLoading] = useState(true);
    const [perfLoading, setPerfLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'students'>('overview');
    const [searchQuery, setSearchQuery] = useState('');
    const [expandedStudent, setExpandedStudent] = useState<string | null>(null);

    useEffect(() => {
        const fetchAll = async () => {
            try {
                const [analyticsRes, perfRes] = await Promise.all([
                    fetch('http://127.0.0.1:8000/admin/analytics'),
                    fetch('http://127.0.0.1:8000/admin/student-performance')
                ]);
                if (analyticsRes.ok) setData(await analyticsRes.json());
                if (perfRes.ok) {
                    const perfData = await perfRes.json();
                    setStudents(perfData.students || []);
                }
            } catch (error) {
                console.error('Failed to fetch analytics', error);
            } finally {
                setLoading(false);
                setPerfLoading(false);
            }
        };
        fetchAll();
    }, []);

    if (loading) return (
        <div className="flex-col items-center justify-center fade-in" style={{ minHeight: '80vh', gap: '1rem' }}>
            <div style={{ width: '40px', height: '40px', border: '4px solid rgba(52,160,90,0.1)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
            <h2 style={{ fontSize: '1rem', color: 'var(--text-secondary)', fontWeight: 800, letterSpacing: '2px' }}>LOADING ADMIN ANALYTICS…</h2>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
    );

    const maxHits = data ? Math.max(...Object.values(data.domain_distribution), 1) : 1;
    const filteredStudents = students.filter(s =>
        s.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.full_name?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const readinessColor = (score: number | null) => {
        if (!score) return 'var(--text-muted)';
        if (score >= 70) return 'var(--accent-green)';
        if (score >= 40) return 'var(--accent-orange)';
        return 'var(--accent-red)';
    };

    return (
        <div className="container fade-in" style={{ maxWidth: '1600px', paddingBottom: '5rem' }}>
            {/* Header */}
            <header className="flex justify-between items-center" style={{ marginBottom: '2.5rem', marginTop: '1rem', flexWrap: 'wrap', gap: '1.5rem' }}>
                <div>
                    <div className="flex items-center gap-md">
                        <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'linear-gradient(135deg, var(--primary-500), var(--secondary-500))', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '1.3rem' }}>
                            🏛️
                        </div>
                        <div>
                            <h1 style={{ fontSize: '1.75rem', fontWeight: 900 }}>Admin Console</h1>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Edunovas Learning Intelligence Platform</p>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-md">
                    <span style={{ fontSize: '0.72rem', color: 'var(--accent-green)', fontWeight: 800, background: 'rgba(52,160,90,0.08)', padding: '0.4rem 0.9rem', borderRadius: '20px', border: '1px solid rgba(52,160,90,0.2)' }}>
                        ● SYSTEM OPERATIONAL
                    </span>
                </div>
            </header>

            {/* Stat Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                {[
                    { label: 'TOTAL STUDENTS', value: data?.total_students ?? 0, icon: '👥', color: 'var(--accent-blue)' },
                    { label: 'TOTAL XP EARNED', value: data?.total_xp?.toLocaleString() ?? 0, icon: '⚡', color: 'var(--accent-orange)' },
                    { label: 'TOPICS COMPLETED', value: data?.total_interaction_hits ?? 0, icon: '✅', color: 'var(--accent-green)' },
                    { label: 'INTERVIEW SESSIONS', value: data?.total_interviews ?? 0, icon: '🎤', color: 'var(--primary-500)' },
                    { label: 'AVG READINESS SCORE', value: data?.avg_readiness_score ? `${data.avg_readiness_score}%` : '—', icon: '🎯', color: 'var(--accent-teal)' },
                ].map(stat => (
                    <div key={stat.label} className="glass-card" style={{ padding: '1.25rem' }}>
                        <div className="flex items-center gap-sm" style={{ marginBottom: '0.75rem' }}>
                            <span style={{ fontSize: '1.3rem' }}>{stat.icon}</span>
                            <span style={{ fontSize: '0.6rem', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '0.8px' }}>{stat.label}</span>
                        </div>
                        <p style={{ fontSize: '2rem', fontWeight: 900, color: stat.color, lineHeight: 1 }}>{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-sm" style={{ marginBottom: '1.5rem' }}>
                {(['overview', 'students'] as const).map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={activeTab === tab ? 'btn btn-primary' : 'btn btn-secondary'}
                        style={{ fontSize: '0.85rem', padding: '0.55rem 1.4rem', fontWeight: 700 }}
                    >
                        {tab === 'overview' ? '📊 Platform Overview' : `👥 Student Performance (${students.length})`}
                    </button>
                ))}
            </div>

            {/* OVERVIEW TAB */}
            {activeTab === 'overview' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }} className="admin-grid fade-in">
                    {/* Domain Activity */}
                    <div className="glass-card" style={{ padding: '1.75rem' }}>
                        <h3 style={{ fontSize: '0.85rem', fontWeight: 800, marginBottom: '1.5rem', color: 'var(--primary-600)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                            📚 Domain Activity (Topics Completed)
                        </h3>
                        {Object.keys(data?.domain_distribution || {}).length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '2rem', opacity: 0.5 }}>
                                <p style={{ fontSize: '2rem' }}>📭</p>
                                <p style={{ fontSize: '0.85rem' }}>No activity yet. Students need to use the AI Teacher module.</p>
                            </div>
                        ) : (
                            <div className="flex-col gap-md">
                                {Object.entries(data!.domain_distribution).sort((a, b) => b[1] - a[1]).map(([domain, count]) => (
                                    <div key={domain} className="flex-col gap-xs">
                                        <div className="flex justify-between" style={{ fontSize: '0.82rem' }}>
                                            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{domain}</span>
                                            <span style={{ color: 'var(--accent-blue)', fontWeight: 800 }}>{count} topics</span>
                                        </div>
                                        <div style={{ height: '8px', background: 'rgba(52,160,90,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                                            <div style={{ height: '100%', width: `${(count / maxHits) * 100}%`, background: 'linear-gradient(90deg, var(--primary-500), var(--accent-blue))', borderRadius: '4px', transition: 'width 0.8s ease' }} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Top Skills */}
                    <div className="glass-card" style={{ padding: '1.75rem' }}>
                        <h3 style={{ fontSize: '0.85rem', fontWeight: 800, marginBottom: '1.5rem', color: 'var(--primary-600)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                            🛠️ Top Student Skills (from Profiles)
                        </h3>
                        {(!data?.top_skills || data.top_skills.length === 0) ? (
                            <div style={{ textAlign: 'center', padding: '2rem', opacity: 0.5 }}>
                                <p style={{ fontSize: '2rem' }}>📭</p>
                                <p style={{ fontSize: '0.85rem' }}>No profiles yet. Students need to complete onboarding.</p>
                            </div>
                        ) : (
                            <div className="flex flex-wrap gap-sm">
                                {data!.top_skills.map((skill, i) => (
                                    <div key={skill.name} style={{
                                        padding: '0.5rem 1rem', borderRadius: '20px',
                                        background: i < 3 ? 'rgba(52,160,90,0.08)' : 'transparent',
                                        border: `1px solid ${i < 3 ? 'rgba(52,160,90,0.3)' : 'var(--glass-border)'}`,
                                        display: 'flex', alignItems: 'center', gap: '6px'
                                    }}>
                                        {i < 3 && <span style={{ color: 'var(--primary-500)', fontWeight: 900, fontSize: '0.75rem' }}>#{i + 1}</span>}
                                        <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>{skill.name}</span>
                                        <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.04)', padding: '1px 6px', borderRadius: '10px' }}>{skill.count}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Interview Readiness Summary */}
                    <div className="glass-card" style={{ padding: '1.75rem', border: '1px solid rgba(52,160,90,0.15)' }}>
                        <h3 style={{ fontSize: '0.85rem', fontWeight: 800, marginBottom: '1.5rem', color: 'var(--primary-600)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                            🎤 Interview Readiness Overview
                        </h3>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
                            <div style={{ textAlign: 'center', padding: '1.5rem', background: 'rgba(52,160,90,0.05)', borderRadius: '12px' }}>
                                <p style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--primary-500)', lineHeight: 1 }}>{data?.total_interviews || 0}</p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>Total Sessions</p>
                            </div>
                            <div style={{ textAlign: 'center', padding: '1.5rem', background: 'rgba(56,183,248,0.05)', borderRadius: '12px' }}>
                                <p style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--accent-blue)', lineHeight: 1 }}>
                                    {data?.avg_readiness_score ? `${data.avg_readiness_score}%` : '—'}
                                </p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>Avg Readiness</p>
                            </div>
                        </div>
                        <div style={{ marginTop: '1.25rem', height: '8px', background: 'rgba(52,160,90,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${data?.avg_readiness_score ?? 0}%`, background: `linear-gradient(90deg, ${(data?.avg_readiness_score ?? 0) >= 70 ? 'var(--accent-green)' : (data?.avg_readiness_score ?? 0) >= 40 ? 'var(--accent-orange)' : 'var(--accent-red)'}, var(--accent-blue))`, transition: 'width 1s ease' }} />
                        </div>
                    </div>

                    {/* Quick Summary */}
                    <div className="glass-card" style={{ padding: '1.75rem', border: '1px solid rgba(52,160,90,0.1)', background: 'rgba(52,160,90,0.015)' }}>
                        <h3 style={{ fontSize: '0.85rem', fontWeight: 800, marginBottom: '1rem', color: 'var(--primary-600)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                            🧠 Platform Insight
                        </h3>
                        <div className="flex-col gap-md">
                            {[
                                { icon: '📱', text: `${data?.total_students ?? 0} registered students on the platform` },
                                { icon: '✅', text: `${data?.total_interaction_hits ?? 0} subtopics completed via AI Teacher` },
                                { icon: '🎤', text: `${data?.total_interviews ?? 0} Interview Coach sessions completed` },
                                { icon: '⚡', text: `${data?.total_xp?.toLocaleString() ?? 0} total XP earned by all students` },
                            ].map((item, i) => (
                                <div key={i} className="flex items-center gap-md">
                                    <span style={{ fontSize: '1.1rem' }}>{item.icon}</span>
                                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{item.text}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* STUDENT PERFORMANCE TAB */}
            {activeTab === 'students' && (
                <div className="flex-col gap-lg fade-in">
                    {/* Search */}
                    <div className="flex items-center gap-md">
                        <input
                            type="text"
                            placeholder="Search students by name or email…"
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            className="input-field"
                            style={{ flex: 1, padding: '0.75rem 1rem', fontSize: '0.9rem' }}
                        />
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                            {filteredStudents.length} / {students.length} students
                        </span>
                    </div>

                    {perfLoading ? (
                        <div className="flex-col items-center" style={{ padding: '3rem', gap: '1rem' }}>
                            <div style={{ width: '36px', height: '36px', border: '4px solid rgba(52,160,90,0.1)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                            <p style={{ color: 'var(--text-muted)' }}>Loading student data…</p>
                        </div>
                    ) : filteredStudents.length === 0 ? (
                        <div className="glass-card flex-col items-center" style={{ padding: '4rem', textAlign: 'center', gap: '1rem' }}>
                            <span style={{ fontSize: '3rem' }}>📭</span>
                            <h3 style={{ fontSize: '1.2rem' }}>{searchQuery ? 'No students match your search' : 'No students registered yet'}</h3>
                            <p style={{ color: 'var(--text-muted)', maxWidth: '400px', fontSize: '0.9rem' }}>
                                {searchQuery ? 'Try a different name or email.' : 'Once students sign up and use the platform, their performance will appear here.'}
                            </p>
                        </div>
                    ) : (
                        <div className="flex-col gap-md">
                            {filteredStudents.map(student => {
                                const isExpanded = expandedStudent === student.user_id;
                                const completionRate = student.total_topics_attempted > 0
                                    ? Math.round((student.topics_completed / student.total_topics_attempted) * 100)
                                    : 0;
                                return (
                                    <div key={student.user_id} className="glass-card" style={{ padding: '1.5rem', border: '1px solid var(--glass-border)' }}>
                                        {/* Student Row */}
                                        <div className="flex justify-between items-center" style={{ flexWrap: 'wrap', gap: '1rem', cursor: 'pointer' }} onClick={() => setExpandedStudent(isExpanded ? null : student.user_id)}>
                                            <div className="flex items-center gap-lg">
                                                {/* Avatar */}
                                                <div style={{ width: '44px', height: '44px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--primary-500), var(--secondary-500))', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 800, fontSize: '1rem', flexShrink: 0 }}>
                                                    {(student.full_name || student.email || '?')[0].toUpperCase()}
                                                </div>
                                                <div>
                                                    <p style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text-primary)' }}>{student.full_name || student.email}</p>
                                                    <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{student.email}</p>
                                                    {student.domains_studied.length > 0 && (
                                                        <div className="flex flex-wrap gap-xs" style={{ marginTop: '4px' }}>
                                                            {student.domains_studied.slice(0, 3).map(d => (
                                                                <span key={d} className="badge" style={{ fontSize: '0.6rem', padding: '1px 6px' }}>{d.split(' ')[0]}</span>
                                                            ))}
                                                            {student.domains_studied.length > 3 && <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>+{student.domains_studied.length - 3} more</span>}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Quick Stats */}
                                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, auto)', gap: '1.5rem', alignItems: 'center' }}>
                                                <div style={{ textAlign: 'center' }}>
                                                    <p style={{ fontWeight: 900, fontSize: '1.4rem', color: 'var(--accent-blue)', lineHeight: 1 }}>{student.topics_completed}</p>
                                                    <p style={{ fontSize: '0.62rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.3px' }}>TOPICS DONE</p>
                                                </div>
                                                <div style={{ textAlign: 'center' }}>
                                                    <p style={{ fontWeight: 900, fontSize: '1.4rem', color: 'var(--accent-orange)', lineHeight: 1 }}>{student.interview_sessions}</p>
                                                    <p style={{ fontSize: '0.62rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.3px' }}>INTERVIEWS</p>
                                                </div>
                                                <div style={{ textAlign: 'center' }}>
                                                    <p style={{ fontWeight: 900, fontSize: '1.4rem', color: readinessColor(student.latest_readiness), lineHeight: 1 }}>
                                                        {student.latest_readiness != null ? `${student.latest_readiness}%` : '—'}
                                                    </p>
                                                    <p style={{ fontSize: '0.62rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.3px' }}>READINESS</p>
                                                </div>
                                                <div style={{ textAlign: 'center' }}>
                                                    <p style={{ fontWeight: 900, fontSize: '1.4rem', color: 'var(--accent-green)', lineHeight: 1 }}>{student.xp}</p>
                                                    <p style={{ fontSize: '0.62rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.3px' }}>XP</p>
                                                </div>
                                            </div>

                                            <span style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>{isExpanded ? '▲' : '▼'}</span>
                                        </div>

                                        {/* Expanded Detail */}
                                        {isExpanded && (
                                            <div className="flex-col gap-lg fade-in" style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--glass-border)' }}>
                                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
                                                    {/* Teacher Progress */}
                                                    <div style={{ padding: '1rem', background: 'rgba(52,160,90,0.04)', borderRadius: '12px', border: '1px solid rgba(52,160,90,0.12)' }}>
                                                        <p style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--primary-600)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>🎓 AI Teacher Progress</p>
                                                        <div className="flex-col gap-xs">
                                                            <div className="flex justify-between">
                                                                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Topics Completed</span>
                                                                <strong style={{ color: 'var(--accent-blue)' }}>{student.topics_completed}</strong>
                                                            </div>
                                                            <div className="flex justify-between">
                                                                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Topics Attempted</span>
                                                                <strong style={{ color: 'var(--text-primary)' }}>{student.total_topics_attempted}</strong>
                                                            </div>
                                                            <div className="flex justify-between">
                                                                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Completion Rate</span>
                                                                <strong style={{ color: completionRate >= 70 ? 'var(--accent-green)' : 'var(--accent-orange)' }}>{completionRate}%</strong>
                                                            </div>
                                                            <div style={{ marginTop: '0.5rem', height: '6px', background: 'rgba(52,160,90,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                                                                <div style={{ height: '100%', width: `${completionRate}%`, background: 'var(--primary-500)', borderRadius: '3px' }} />
                                                            </div>
                                                            {student.last_topic && (
                                                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                                                                    Last: <em>{student.last_topic}</em>
                                                                </p>
                                                            )}
                                                        </div>
                                                    </div>

                                                    {/* Interview Performance */}
                                                    <div style={{ padding: '1rem', background: 'rgba(56,183,248,0.04)', borderRadius: '12px', border: '1px solid rgba(56,183,248,0.12)' }}>
                                                        <p style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--accent-blue)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>🎤 Interview Coach</p>
                                                        <div className="flex-col gap-xs">
                                                            <div className="flex justify-between">
                                                                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Sessions</span>
                                                                <strong style={{ color: 'var(--text-primary)' }}>{student.interview_sessions}</strong>
                                                            </div>
                                                            <div className="flex justify-between">
                                                                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Latest Score</span>
                                                                <strong style={{ color: readinessColor(student.latest_readiness) }}>
                                                                    {student.latest_readiness != null ? `${student.latest_readiness}%` : '—'}
                                                                </strong>
                                                            </div>
                                                            <div className="flex justify-between">
                                                                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Avg Score</span>
                                                                <strong style={{ color: readinessColor(student.avg_readiness) }}>
                                                                    {student.avg_readiness != null ? `${student.avg_readiness}%` : '—'}
                                                                </strong>
                                                            </div>
                                                            {student.last_interview_role && (
                                                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                                                                    Target: <em>{student.last_interview_role}</em>
                                                                </p>
                                                            )}
                                                        </div>
                                                    </div>

                                                    {/* Domains Studied */}
                                                    {student.domains_studied.length > 0 && (
                                                        <div style={{ padding: '1rem', background: 'rgba(245,158,11,0.04)', borderRadius: '12px', border: '1px solid rgba(245,158,11,0.12)' }}>
                                                            <p style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--accent-orange)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>📚 Domains Studied</p>
                                                            <div className="flex flex-wrap gap-xs">
                                                                {student.domains_studied.map(d => (
                                                                    <span key={d} className="badge" style={{ fontSize: '0.72rem', borderColor: 'rgba(245,158,11,0.3)', color: 'var(--accent-orange)', background: 'rgba(245,158,11,0.04)' }}>{d}</span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}

            <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                @media (max-width: 900px) { .admin-grid { grid-template-columns: 1fr !important; } }
            `}</style>
        </div>
    );
};
