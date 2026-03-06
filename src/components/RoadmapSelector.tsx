import { useState } from 'react';
import { CURRICULUM_DATA, type Roadmap } from '../data/curriculumData';

export const RoadmapSelector = () => {
    const [selectedRoadmap, setSelectedRoadmap] = useState<Roadmap | null>(null);

    const handleDownloadPDF = async (roadmap: Roadmap) => {
        try {
            const response = await fetch('http://127.0.0.1:8000/download-roadmap-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(roadmap)
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${roadmap.title.replace(/\s+/g, '_')}_Roadmap.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (error) {
            console.error('PDF download failed:', error);
        }
    };

    return (
        <div className="glass-card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '0.9rem', fontWeight: 800, marginBottom: '1rem' }}>📜 LEARNING ROADMAPS</h3>
            
            {!selectedRoadmap ? (
                <div className="flex-col gap-sm">
                    {CURRICULUM_DATA.map((roadmap) => (
                        <button
                            key={roadmap.id}
                            onClick={() => setSelectedRoadmap(roadmap)}
                            className="glass-card flex items-center gap-md hover-lift"
                            style={{
                                padding: '0.75rem 1rem',
                                cursor: 'pointer',
                                border: '1px solid var(--glass-border)',
                                textAlign: 'left'
                            }}
                        >
                            <span style={{ fontSize: '1.2rem' }}>{roadmap.icon}</span>
                            <div style={{ flex: 1 }}>
                                <h4 style={{ fontSize: '0.85rem', marginBottom: '0.2rem' }}>{roadmap.title}</h4>
                                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{roadmap.difficulty} • {roadmap.duration}</span>
                            </div>
                        </button>
                    ))}
                </div>
            ) : (
                <div className="flex-col gap-md">
                    <div style={{ borderLeft: `3px solid ${selectedRoadmap.color}`, paddingLeft: '1rem' }}>
                        <div className="flex items-center gap-sm mb-xs">
                            <span style={{ fontSize: '1.5rem' }}>{selectedRoadmap.icon}</span>
                            <h4 style={{ fontSize: '1rem' }}>{selectedRoadmap.title}</h4>
                        </div>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                            {selectedRoadmap.description}
                        </p>
                        <div className="flex gap-sm">
                            <span className="badge" style={{ fontSize: '0.65rem', padding: '0.2rem 0.6rem' }}>{selectedRoadmap.difficulty}</span>
                            <span className="badge" style={{ fontSize: '0.65rem', padding: '0.2rem 0.6rem' }}>{selectedRoadmap.duration}</span>
                        </div>
                    </div>

                    <div className="flex-col gap-sm" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                        {selectedRoadmap.phases.map((phase, idx) => (
                            <div key={idx} style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.02)', borderRadius: '4px' }}>
                                <h5 style={{ fontSize: '0.75rem', color: selectedRoadmap.color, marginBottom: '0.5rem' }}>
                                    {idx + 1}. {phase.name}
                                </h5>
                                <div className="flex-col gap-xs">
                                    {phase.milestones.map((m, i) => (
                                        <div key={i} style={{ fontSize: '0.7rem', color: 'var(--text-muted)', paddingLeft: '0.5rem' }}>
                                            • {m.title}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="flex gap-sm">
                        <button 
                            className="btn btn-secondary" 
                            style={{ flex: 1, fontSize: '0.75rem', padding: '0.5rem' }}
                            onClick={() => setSelectedRoadmap(null)}
                        >
                            ← Back
                        </button>
                        <button 
                            className="btn btn-primary" 
                            style={{ flex: 1, fontSize: '0.75rem', padding: '0.5rem' }}
                            onClick={() => handleDownloadPDF(selectedRoadmap)}
                        >
                            📥 PDF
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
