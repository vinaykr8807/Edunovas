import { Link } from 'react-router-dom';
import { PERSONAS } from '../data/personas';

export const Home = () => {
    return (
        <div className="fade-in">
            {/* Hero Section */}
            <section style={{
                padding: '120px 0 80px',
                textAlign: 'center',
                position: 'relative'
            }}>
                <div className="badge mb-sm" style={{ padding: '0.6rem 1.2rem' }}>
                    🚀 The Future of Technical Education
                </div>
                <h1 style={{ marginBottom: '1.5rem', lineHeight: 1.1 }}>
                    Master Your Career with <br />
                    <span className="gradient-text">Personalized AI Mentorship</span>
                </h1>
                <p style={{
                    fontSize: '1.25rem',
                    color: 'var(--text-secondary)',
                    maxWidth: '800px',
                    margin: '0 auto 2.5rem',
                    lineHeight: 1.6
                }}>
                    Edunovas AI adapts to your learning pace, identifies your skill gaps, and prepares you for your dream technical role through immersive simulation and expert guidance.
                </p>
                <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center' }}>
                    <Link to="/assistant" className="btn btn-primary" style={{ padding: '1rem 3rem' }}>
                        Start Learning Now
                    </Link>
                    <a href="#features" className="btn btn-secondary" style={{ padding: '1rem 3rem' }}>
                        Explore Features
                    </a>
                </div>
            </section>

            {/* Stats Section */}
            <section className="container" style={{ marginBottom: '100px' }}>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '2rem'
                }}>
                    {[
                        { label: 'Active Students', value: '15,000+' },
                        { label: 'Success Rate', value: '94%' },
                        { label: 'Expert Personas', value: '5+' },
                        { label: 'Mock Interviews', value: '50k+' }
                    ].map((stat, i) => (
                        <div key={i} className="glass-card text-center" style={{ padding: '2rem' }}>
                            <h2 className="gradient-text" style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{stat.value}</h2>
                            <p style={{ color: 'var(--text-muted)', fontWeight: 600 }}>{stat.label}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Persona Showcase */}
            <section id="features" className="container" style={{ paddingBottom: '100px' }}>
                <div className="text-center mb-xl">
                    <h2 style={{ marginBottom: '1rem' }}>Meet Your AI Learning Team</h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '2.5rem' }}>Switch between specialized modes designed for every stage of your journey.</p>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '2rem'
                }}>
                    {Object.values(PERSONAS).map((persona) => (
                        <div key={persona.id} className="glass-card flex-col" style={{ padding: '2.5rem' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1.5rem' }}>{persona.icon}</div>
                            <h3 style={{ marginBottom: '1rem' }}>{persona.name}</h3>
                            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', flex: 1 }}>
                                {persona.prompt.split('.')[0]}. Experience a tailored approach to {persona.name.toLowerCase()} that adapts to your needs.
                            </p>
                            <Link
                                to="/assistant"
                                className="btn btn-secondary"
                                style={{ justifyContent: 'center', borderColor: persona.color, color: 'var(--text-primary)' }}
                            >
                                Launch {persona.name}
                            </Link>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="container" style={{ paddingBottom: '120px' }}>
                <div className="glass-card text-center" style={{
                    padding: '5rem 2rem',
                    background: 'linear-gradient(135deg, rgba(160, 100, 255, 0.1) 0%, rgba(255, 100, 150, 0.1) 100%)',
                    border: '1px solid var(--primary-500)'
                }}>
                    <h2 style={{ fontSize: '3rem', marginBottom: '1.5rem' }}>Ready to transform your future?</h2>
                    <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 3rem' }}>
                        Join thousands of professional developers who started their journey with Edunovas AI.
                    </p>
                    <Link to="/assistant" className="btn btn-primary" style={{ padding: '1.2rem 4rem', fontSize: '1.1rem' }}>
                        Get Career Ready ⚡
                    </Link>
                </div>
            </section>
        </div>
    );
};
