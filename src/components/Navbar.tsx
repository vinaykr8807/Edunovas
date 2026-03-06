import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export const Navbar: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const userStr = localStorage.getItem('edunovas_user');
    let user = null;
    if (userStr) {
        try {
            user = JSON.parse(userStr);
        } catch (e) {
            localStorage.removeItem('edunovas_user');
        }
    }

    const navLinks = [
        { name: 'Home', path: '/' },
        { name: 'Curriculum', path: '/curriculum' },
    ];

    if (user?.role === 'student') {
        navLinks.push({ name: 'Career Forge', path: '/assistant' });
    }

    if (user?.role === 'admin') {
        navLinks.push({ name: 'Dashboard', path: '/admin' });
    }

    const handleLogout = () => {
        localStorage.removeItem('edunovas_user');
        localStorage.removeItem('edunovas_profile');
        navigate('/login');
    };

    return (
        <nav style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            zIndex: 100,
            background: 'rgba(255, 255, 255, 0.85)',
            backdropFilter: 'blur(20px)',
            borderBottom: '1px solid var(--glass-border)',
            padding: '1rem 0'
        }}>
            <div className="container flex items-center justify-between" style={{ padding: '0 var(--spacing-lg)' }}>
                <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{
                        width: '38px',
                        height: '38px',
                        background: 'linear-gradient(135deg, var(--primary-500), var(--secondary-500))',
                        borderRadius: '10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 800,
                        color: 'white',
                        fontSize: '1.1rem'
                    }}>E</div>
                    <span style={{
                        fontSize: '1.4rem',
                        fontWeight: 800,
                        color: 'var(--text-primary)',
                        letterSpacing: '-0.5px'
                    }}>Edunovas</span>
                </Link>

                <div className="flex items-center flex-wrap" style={{ gap: '1.5rem' }}>
                    <div className="flex items-center gap-lg">
                        {navLinks.map((link) => (
                            <Link
                                key={link.path}
                                to={link.path}
                                style={{
                                    textDecoration: 'none',
                                    color: location.pathname === link.path ? 'var(--primary-400)' : 'var(--text-secondary)',
                                    fontWeight: 600,
                                    fontSize: '0.9rem',
                                    transition: 'color var(--transition-fast)'
                                }}
                            >
                                {link.name}
                            </Link>
                        ))}
                    </div>

                    <div style={{ borderLeft: '1px solid var(--glass-border)', height: '24px', opacity: 0.5 }} className="mobile-hide"></div>

                    {!user ? (
                        <Link to="/login" className="btn btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.85rem' }}>
                            Login
                        </Link>
                    ) : (
                        <div className="flex items-center gap-md">
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }} className="mobile-hide">{user.email}</span>
                            <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>
                                Logout
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};
