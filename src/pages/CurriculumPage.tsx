import { useState } from 'react';
import { CURRICULUM_DATA, type Roadmap } from '../data/curriculumData';

export const CurriculumPage = () => {
    const [selectedRoadmap, setSelectedRoadmap] = useState<Roadmap>(CURRICULUM_DATA[0]);

    const handleDownloadPDF = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/download-roadmap-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(selectedRoadmap)
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${selectedRoadmap.title.replace(/\s+/g, '_')}_Roadmap.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (error) {
            console.error('PDF download failed:', error);
            alert('Failed to download PDF. Please try again.');
        }
    };

    return (
        <div className="fade-in" style={{ padding: '2rem 0 6rem' }}>
            <div className="text-center mb-2xl">
                <div className="badge mb-sm" style={{ padding: '0.6rem 1.2rem', color: 'var(--primary-400)' }}>
                    📜 Industry-Certified Curriculums
                </div>
                <h1 style={{ marginBottom: '1rem' }}>Accelerated <span className="gradient-text">Roadmaps</span></h1>
                <p style={{ color: 'var(--text-secondary)', maxWidth: '650px', margin: '0 auto 2.5rem', fontSize: '1.1rem' }}>
                    Standardized learning paths designed by industry experts to take you from foundational logic to professional mastery.
                </p>
            </div>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(250px, 300px) 1fr',
                gap: '2rem',
                alignItems: 'start',
                maxWidth: '1600px',
                margin: '0 auto'
            }} className="curriculum-layout">

                {/* Discovery Sidebar */}
                <div className="flex-col gap-md">
                    <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '2px', paddingLeft: '0.5rem' }}>Select Domain</h3>
                    <div className="flex-col gap-sm">
                        {CURRICULUM_DATA.map((roadmap) => (
                            <button
                                key={roadmap.id}
                                onClick={() => setSelectedRoadmap(roadmap)}
                                className="glass-card flex items-center gap-md"
                                style={{
                                    padding: '1.25rem 1.5rem',
                                    cursor: 'pointer',
                                    border: selectedRoadmap.id === roadmap.id ? `1px solid ${roadmap.color}` : '1px solid var(--glass-border)',
                                    background: selectedRoadmap.id === roadmap.id ? `${roadmap.color}15` : 'var(--glass-bg)',
                                    textAlign: 'left',
                                    transition: 'all 0.3s ease',
                                    transform: selectedRoadmap.id === roadmap.id ? 'translateX(10px)' : 'none'
                                }}
                            >
                                <span style={{ fontSize: '1.5rem' }}>{roadmap.icon}</span>
                                <div>
                                    <h4 style={{ fontSize: '0.95rem', color: selectedRoadmap.id === roadmap.id ? 'var(--primary-600)' : 'var(--text-secondary)' }}>{roadmap.title}</h4>
                                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>{roadmap.difficulty} • {roadmap.duration}</span>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Animated Roadmap View */}
                <div className="flex-col gap-lg" style={{ minWidth: 0 }}>
                    <div className="glass-card" style={{
                        padding: '2.5rem',
                        borderTop: `4px solid ${selectedRoadmap.color}`,
                        background: `linear-gradient(180deg, ${selectedRoadmap.color}08 0%, transparent 100%)`,
                        position: 'relative'
                    }}>
                        <div className="roadmap-header">
                            <div className="flex-col gap-sm" style={{ flex: 1, minWidth: 0 }}>
                                <div className="flex items-center gap-md" style={{ flexWrap: 'wrap' }}>
                                    <span style={{ fontSize: '2.5rem' }}>{selectedRoadmap.icon}</span>
                                    <h2 style={{ fontSize: '2rem', fontWeight: 900, letterSpacing: '-1.5px', margin: 0 }}>{selectedRoadmap.title}</h2>
                                </div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: 1.6, marginTop: '0.5rem' }}>{selectedRoadmap.description}</p>
                            </div>
                            <div className="roadmap-meta">
                                <span className="badge" style={{ borderColor: `${selectedRoadmap.color}40`, color: selectedRoadmap.color, padding: '0.5rem 1rem', whiteSpace: 'nowrap', background: `${selectedRoadmap.color}10` }}>
                                    Certified Curriculum
                                </span>
                                <button onClick={handleDownloadPDF} className="btn btn-secondary" style={{ padding: '0.6rem 1rem', fontSize: '0.8rem', border: '1px solid var(--glass-border)', whiteSpace: 'nowrap' }}>
                                    📥 Download PDF Roadmap
                                </button>
                                <div className="duration-box" style={{ textAlign: 'right', marginTop: '1rem', borderTop: '1px solid var(--glass-border)', paddingTop: '1rem' }}>
                                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', display: 'block', fontWeight: 800, letterSpacing: '1.5px', textTransform: 'uppercase' }}>ESTIMATED TIME</span>
                                    <span style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--text-primary)' }}>{selectedRoadmap.duration}</span>
                                </div>
                            </div>
                        </div>

                        {/* Interactive Timeline */}
                        <div className="flex-col gap-3xl" style={{ position: 'relative', paddingLeft: '3rem', marginTop: '4rem' }}>
                            {/* Connector Line */}
                            <div style={{
                                position: 'absolute',
                                left: '20px',
                                top: '0',
                                bottom: '0',
                                width: '2px',
                                background: `linear-gradient(180deg, ${selectedRoadmap.color} 0%, ${selectedRoadmap.color}40 50%, rgba(255,255,255,0.05) 100%)`,
                                opacity: 0.3,
                                zIndex: 1
                            }}></div>

                            {selectedRoadmap.phases.map((phase, pIdx) => (
                                <div key={phase.name} className="flex-col gap-xl" style={{ position: 'relative' }}>
                                    {/* Phase Header */}
                                    <div className="flex items-center gap-lg" style={{ marginLeft: '-3rem', marginBottom: '1rem' }}>
                                        <div style={{
                                            width: '40px',
                                            height: '40px',
                                            minWidth: '40px',
                                            borderRadius: '50%',
                                            background: selectedRoadmap.color,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            fontWeight: 900,
                                            fontSize: '1.1rem',
                                            color: '#fff',
                                            boxShadow: `0 0 30px ${selectedRoadmap.color}60`,
                                            zIndex: 2,
                                            border: '4px solid var(--bg-primary)'
                                        }}>{pIdx + 1}</div>
                                        <h3 style={{ fontSize: '1.4rem', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 900, margin: 0 }}>{phase.name}</h3>
                                    </div>

                                    {/* Milestone Cards */}
                                    <div className="milestone-grid" style={{ paddingLeft: '0.5rem' }}>
                                        {phase.milestones.map((m) => (
                                            <div key={m.title} className="glass-card hover-lift" style={{
                                                padding: '1.75rem',
                                                background: 'rgba(255,255,255,0.03)',
                                                border: '1px solid var(--glass-border)',
                                                display: 'flex',
                                                flexDirection: 'column',
                                                gap: '1rem',
                                                borderRadius: '1.25rem'
                                            }}>
                                                <div>
                                                    <h4 style={{ marginBottom: '0.6rem', fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>{m.title}</h4>
                                                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>{m.description}</p>
                                                </div>
                                                <div className="flex flex-wrap gap-xs mt-auto" style={{ paddingTop: '0.75rem' }}>
                                                    {m.skills.map(skill => (
                                                        <span key={skill} className="badge" style={{
                                                            fontSize: '0.72rem',
                                                            padding: '0.35rem 0.8rem',
                                                            background: `${selectedRoadmap.color}08`,
                                                            borderColor: `${selectedRoadmap.color}20`,
                                                            color: 'var(--text-secondary)',
                                                            fontWeight: 600
                                                        }}>{skill}</span>
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-4xl flex justify-center" style={{ marginTop: '5rem' }}>
                            <button className="btn btn-primary" style={{ padding: '1.25rem 5rem', fontSize: '1.2rem', fontWeight: 900, boxShadow: `0 10px 40px ${selectedRoadmap.color}40`, borderRadius: '1rem' }}>
                                Start This Journey 🚀
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
                .roadmap-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    gap: 2rem;
                    margin-bottom: 2rem;
                }
                .roadmap-meta {
                    display: flex;
                    flex-direction: column;
                    align-items: flex-end;
                    gap: 0.75rem;
                    min-width: 220px;
                    flex-shrink: 0;
                }
                .milestone-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 1rem;
                }
                @media (max-width: 1200px) {
                    .curriculum-layout {
                        grid-template-columns: 1fr !important;
                    }
                    .curriculum-layout > :first-child {
                        display: flex;
                        flex-direction: row !important;
                        overflow-x: auto;
                        padding-bottom: 1rem;
                    }
                    .curriculum-layout > :first-child::-webkit-scrollbar { height: 4px; }
                    .curriculum-layout > :first-child > div {
                        flex-direction: row !important;
                    }
                    .curriculum-layout > :first-child button {
                        white-space: nowrap;
                        flex-shrink: 0;
                    }
                }
                @media (max-width: 768px) {
                    .roadmap-header {
                        flex-direction: column;
                        gap: 1.5rem;
                    }
                    .roadmap-meta {
                        width: 100%;
                        align-items: stretch;
                    }
                    .roadmap-meta > div {
                        text-align: left !important;
                    }
                    .milestone-grid {
                        grid-template-columns: 1fr !important;
                    }
                }
                .hover-lift { transition: all 0.3s ease; }
                .hover-lift:hover { transform: translateY(-5px); border-color: rgba(52, 160, 90, 0.25) !important; background: rgba(52, 160, 90, 0.05) !important; }
            `}</style>
        </div>
    );
};
