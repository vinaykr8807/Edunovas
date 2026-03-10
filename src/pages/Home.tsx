import { Link } from 'react-router-dom';


export const Home = () => {
    return (
        <div className="fade-in" style={{ background: 'var(--bg-primary)', minHeight: '100vh', paddingBottom: '100px' }}>
            {/* 🚀 High-Energy Hero Section */}
            <section style={{
                padding: '180px 0 120px',
                textAlign: 'center',
                position: 'relative',
                overflow: 'hidden',
                background: 'radial-gradient(circle at top, rgba(52, 160, 90, 0.08) 0%, transparent 60%)'
            }}>
                <div style={{
                    position: 'absolute',
                    top: '-10%',
                    right: '-5%',
                    width: '600px',
                    height: '600px',
                    background: 'radial-gradient(circle, rgba(100, 130, 255, 0.05) 0%, transparent 70%)',
                    filter: 'blur(100px)',
                    zIndex: 0
                }} />
                
                <div className="container" style={{ position: 'relative', zIndex: 1 }}>
                    <div className="badge mb-md" style={{ 
                        padding: '0.7rem 1.6rem', 
                        background: 'rgba(52, 160, 90, 0.05)', 
                        border: '1px solid var(--primary-500)',
                        fontSize: '0.75rem',
                        letterSpacing: '3px',
                        fontWeight: 900,
                        color: 'var(--primary-400)'
                    }}>
                        NEXT-GEN TECHNICAL CO-PILOT
                    </div>
                    <h1 style={{ 
                        marginBottom: '1.5rem', 
                        lineHeight: 0.95, 
                        fontSize: 'clamp(3.5rem, 8vw, 6rem)', 
                        fontWeight: 900,
                        letterSpacing: '-3px'
                    }}>
                        Master Systems <br />
                        <span className="gradient-text">Not Just Syntax.</span>
                    </h1>
                    <p style={{
                        fontSize: '1.35rem',
                        color: 'var(--text-secondary)',
                        maxWidth: '850px',
                        margin: '0 auto 3.5rem',
                        lineHeight: 1.5,
                        fontWeight: 500
                    }}>
                        The first AI ecosystem that bridges the gap between basic coding and senior system engineering. 
                        Experience master-grade mentorship with automated architecture visualization and real-time skill gaps analysis.
                    </p>
                    <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center' }}>
                        <Link to="/assistant" className="btn btn-primary" style={{ padding: '1.4rem 4rem', fontSize: '1.1rem', fontWeight: 800, borderRadius: '12px' }}>
                            Initialize Forge ⚡
                        </Link>
                        <Link to="/curriculum" className="btn btn-secondary" style={{ padding: '1.4rem 4rem', fontSize: '1.1rem', fontWeight: 800, borderRadius: '12px' }}>
                            Browse Curriculums
                        </Link>
                    </div>
                </div>
            </section>

            {/* 🛠️ Specialized Technical Pillars */}
            <section className="container" style={{ marginBottom: '160px' }}>
                <div style={{ textAlign: 'center', marginBottom: '5rem' }}>
                    <h2 style={{ fontSize: '3rem', fontWeight: 900, letterSpacing: '-1.5px' }}>Engineered for Professional Excellence</h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem', maxWidth: '700px', margin: '1rem auto 0' }}>Specialized AI agents designed to handle specific stages of your career growth.</p>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
                    gap: '2rem'
                }}>
                    {[
                        {
                            title: 'AI Technical Teacher',
                            icon: '🏗️',
                            desc: 'Architectural deep-dives with D2 System Diagram generation. Master the "why" behind distributed systems, concurrency, and DB persistence.',
                            color: 'var(--primary-500)',
                            tag: 'ARCHITECTURE'
                        },
                        {
                            title: 'Quiz Master 2.0',
                            icon: '🔬',
                            desc: 'Adaptive recovery quizzes that detect weak areas. "Teach the AI" mode evaluates your explanation clarity against senior standards.',
                            color: 'var(--accent-pink)',
                            tag: 'DIAGNOSTICS'
                        },
                        {
                            title: 'Career Pathfinder',
                            icon: '🎯',
                            desc: 'Live Market-Skill syncing. AI scans your resume vs active industry demand to provide a personalized roadmap to high-paying roles.',
                            color: 'var(--accent-teal)',
                            tag: 'STRATEGY'
                        },
                        {
                            title: 'Interview Simulation',
                            icon: '💼',
                            desc: 'High-fidelity technical interviews. Role-based behavioral and system design sessions with immediate actionable feedback scorecards.',
                            color: 'var(--accent-blue)',
                            tag: 'SIMULATION'
                        }
                    ].map((feature, i) => (
                        <div key={i} className="glass-card hover-glow" style={{ padding: '4rem 3rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div style={{ fontSize: '3rem' }}>{feature.icon}</div>
                                <span style={{ fontSize: '0.65rem', fontWeight: 900, color: feature.color, letterSpacing: '2px', border: `1px solid ${feature.color}44`, background: `${feature.color}11`, padding: '6px 12px', borderRadius: '6px' }}>{feature.tag}</span>
                            </div>
                            <h3 style={{ fontSize: '1.8rem', fontWeight: 900, margin: 0 }}>{feature.title}</h3>
                            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: '1.05rem', flex: 1 }}>{feature.desc}</p>
                            <Link to="/assistant" style={{ color: feature.color, textDecoration: 'none', fontWeight: 800, fontSize: '0.8rem', letterSpacing: '1px' }} className="flex items-center gap-xs">
                                LAUNCH MODULE <span style={{ fontSize: '1.2rem' }}>→</span>
                            </Link>
                        </div>
                    ))}
                </div>
            </section>


            {/* 🌀 The Hyper-Learning Loop Section */}
            <section style={{ padding: '140px 0', position: 'relative' }}>
                <div className="container">
                     <div style={{ textAlign: 'center', marginBottom: '6rem' }}>
                        <div className="badge mb-sm" style={{ color: 'var(--accent-pink)', borderColor: 'var(--accent-pink)33' }}>METHODOLOGY</div>
                        <h2 style={{ fontSize: '3.5rem', fontWeight: 900, letterSpacing: '-2px' }}>The Hyper-Learning <span style={{ color: 'var(--accent-pink)' }}>Path</span></h2>
                        <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem', maxWidth: '600px', margin: '1.5rem auto 0' }}>Our AI doesn't just teach. It evolves your technical foundation through a continuous feedback loop.</p>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem' }}>
                        {[
                            { step: '01', title: 'Deep Ingestion', desc: 'AI Teacher breaks down high-level concepts into granular subtopics with architectural context.', color: 'var(--primary-500)' },
                            { step: '02', title: 'Adaptive Stress', desc: 'Quiz Master 2.0 identifies exactly where your mental model breaks under technical pressure.', color: 'var(--accent-pink)' },
                            { step: '03', title: 'Actionable Recovery', desc: 'Personalized improvement plans Bridge your specific skill gaps with precision training.', color: 'var(--accent-teal)' }
                        ].map((item, i) => (
                            <div key={i} className="glass-card" style={{ padding: '3.5rem 2.5rem', position: 'relative', overflow: 'hidden' }}>
                                <div style={{ position: 'absolute', top: '-20px', right: '-20px', fontSize: '8rem', fontWeight: 900, opacity: 0.03, color: item.color }}>{item.step}</div>
                                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: item.color, display: 'grid', placeItems: 'center', color: '#fff', fontWeight: 900, marginBottom: '2rem' }}>{item.step}</div>
                                <h3 style={{ fontSize: '1.5rem', fontWeight: 900, marginBottom: '1rem' }}>{item.title}</h3>
                                <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* 🛠️ Integrated Tech Stack Section */}
            <section style={{ padding: '100px 0', background: 'var(--bg-primary)' }}>
                <div className="container">
                    <div style={{ textAlign: 'center', marginBottom: '5rem' }}>
                        <h2 style={{ fontSize: '3rem', fontWeight: 900, letterSpacing: '-1.5px' }}>The Core <span className="gradient-text">Engine</span></h2>
                        <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem', marginTop: '1rem' }}>High-performance tools powering your learning journey.</p>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem' }}>
                        {[
                            { name: 'Kroki Rendering', icon: '🎨', desc: 'Enterprise-grade visualization engine.' },
                            { name: 'Groq Inference', icon: '⚡', desc: 'Sub-second AI response latency.' },
                            { name: 'PostgreSQL', icon: '💾', desc: 'Secure, relational data persistence.' },
                            { name: 'Supabase OSS', icon: '☁️', desc: 'Cloud-native infrastructure.' }
                        ].map((tech, i) => (
                            <div key={i} className="glass-card text-center" style={{ padding: '2.5rem 1.5rem' }}>
                                <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{tech.icon}</div>
                                <h4 style={{ fontWeight: 800, marginBottom: '0.5rem' }}>{tech.name}</h4>
                                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{tech.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* 🤖 AI Mentorship & Global Standards Section */}
            <section style={{ padding: '120px 0', background: 'var(--bg-secondary)' }}>
                <div className="container">
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5rem', alignItems: 'center' }}>
                        <div className="glass-card" style={{ padding: '3rem', border: '1px solid var(--accent-blue)33' }}>
                             <div style={{ fontSize: '3rem', marginBottom: '2rem' }}>👨‍💻</div>
                             <h3 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: '1.5rem', letterSpacing: '-1px' }}>24/7 AI Mentorship</h3>
                             <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', lineHeight: 1.7, marginBottom: '2rem' }}>
                                 Never get stuck again. Our AI Mentor understands your progress, remembers your past mistakes, and guides you through complex debugging sessions with the patience of a senior lead.
                             </p>
                             <div className="flex-col gap-md">
                                 {[
                                     'Context-Aware Doubt Resolution',
                                     'Personalized Debugging Support',
                                     'Senior-Level Code Optimizations',
                                     'Mental Model Alignment'
                                 ].map(point => (
                                     <div key={point} className="flex gap-sm items-center">
                                         <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent-blue)' }} />
                                         <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{point}</span>
                                     </div>
                                 ))}
                             </div>
                        </div>
                        <div>
                            <div className="badge mb-sm" style={{ color: 'var(--accent-blue)', borderColor: 'var(--accent-blue)33' }}>GLOBAL STANDARDS</div>
                            <h2 style={{ fontSize: '3.5rem', fontWeight: 900, marginBottom: '2rem', letterSpacing: '-2px' }}>Built for the <br /><span style={{ color: 'var(--accent-blue)' }}>FAANG Era</span></h2>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', lineHeight: 1.6, marginBottom: '3rem' }}>
                                Our curriculum and evaluations are mapped against the engineering standards of top-tier tech companies. We don't just teach you to code; we teach you to engineer.
                            </p>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                                <div className="glass-card" style={{ padding: '1.5rem' }}>
                                    <h4 style={{ fontWeight: 800, color: 'var(--accent-blue)' }}>99.9%</h4>
                                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>AI Technical Accuracy</p>
                                </div>
                                <div className="glass-card" style={{ padding: '1.5rem' }}>
                                    <h4 style={{ fontWeight: 800, color: 'var(--accent-green)' }}>500+</h4>
                                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Technical Subtopics</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 🔥 Final CTA Section */}
            <section className="container" style={{ padding: '160px 0' }}>
                <div className="glass-card text-center" style={{
                    padding: '8rem 2rem',
                    background: 'radial-gradient(circle at top right, rgba(160, 100, 255, 0.15), transparent), radial-gradient(circle at bottom center, rgba(52, 160, 90, 0.15), transparent)',
                    border: '1px solid var(--primary-500)',
                    borderRadius: '40px'
                }}>
                    <h2 style={{ fontSize: 'max(3.5rem, 5vw)', marginBottom: '1.5rem', fontWeight: 900, letterSpacing: '-2px' }}>Stop Learning.<br />Start <span className="gradient-text">Mastering.</span></h2>
                    <p style={{ fontSize: '1.4rem', color: 'var(--text-secondary)', maxWidth: '750px', margin: '0 auto 4rem', fontWeight: 500 }}>
                        The future of technical education is specialized AI. Forge your career with tools that actually understand the engineering standard.
                    </p>
                    <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center' }}>
                        <Link to="/assistant" className="btn btn-primary" style={{ padding: '1.6rem 5rem', fontSize: '1.2rem', borderRadius: '100px', fontWeight: 900 }}>
                            Access The Forge Now ⚡
                        </Link>
                    </div>
                </div>
            </section>

            {/* Custom Global CSS Additions */}
            <style>{`
                .hover-glow:hover {
                    box-shadow: 0 0 60px rgba(52, 160, 90, 0.18);
                    transform: translateY(-8px);
                    border-color: var(--primary-500)88 !important;
                }
                .gradient-text {
                    background: linear-gradient(135deg, var(--primary-400), var(--accent-teal), var(--secondary-500));
                    -webkit-background-clip: text;
                    background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .diagram-full svg {
                    width: 100% !important;
                    height: 100% !important;
                    max-width: none !important;
                    display: block;
                    background: transparent !important;
                    position: absolute;
                    top: 0;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    object-fit: cover;
                }
                .diagram-full svg rect, .diagram-full svg path {
                    vector-effect: non-scaling-stroke;
                }
                .diagram-full svg * {
                    transition: all 0.5s ease;
                }
                .diagram-full .mermaid-loader {
                    border: 3px solid rgba(52, 160, 90, 0.1);
                    border-top: 3px solid var(--primary-500);
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    animation: spin 1s linear infinite;
                }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            `}</style>
        </div>
    );
};
