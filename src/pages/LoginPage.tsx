import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const LoginPage: React.FC = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [role, setRole] = useState<'student' | 'admin'>('student');
    const [email, setEmail] = useState('');
    const [fullName, setFullName] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [welcomeName, setWelcomeName] = useState('');
    const [showPopup, setShowPopup] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const userStr = localStorage.getItem('edunovas_user');
        if (userStr) {
            try {
                const user = JSON.parse(userStr);
                if (user.full_name) {
                    setWelcomeName(user.full_name);
                    setShowPopup(true);
                    setTimeout(() => setShowPopup(false), 4000);

                    // Already logged in, redirect to dashboard
                    setTimeout(() => {
                        navigate(user.role === 'admin' ? '/admin' : '/assistant');
                    }, 1500);
                }
            } catch (e) {
                localStorage.removeItem('edunovas_user');
            }
        }
    }, [navigate]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!isLogin && password !== confirmPassword) {
            setError("Passwords don't match");
            return;
        }

        setIsLoading(true);
        console.log(`Attempting ${isLogin ? 'login' : 'signup'} for ${email}...`);

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

            const response = await fetch(`http://127.0.0.1:8000${isLogin ? '/login' : '/signup'}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    password,
                    role,
                    full_name: isLogin ? undefined : fullName
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            const data = await response.json();
            console.log("Response received:", data);

            if (response.ok) {
                localStorage.setItem('edunovas_user', JSON.stringify({
                    email: data.email,
                    role: data.role,
                    token: data.access_token,
                    full_name: data.full_name
                }));

                setWelcomeName(data.full_name || data.email);
                setShowPopup(true);

                // Small delay to show popup before navigation
                setTimeout(() => {
                    navigate(data.role === 'admin' ? '/admin' : '/assistant');
                }, 1000);
            } else {
                setError(data.detail || 'Authentication failed. Check your credentials.');
                setIsLoading(false);
            }
        } catch (err: any) {
            console.error("Fetch error:", err);
            const targetUrl = `http://127.0.0.1:8000${isLogin ? '/login' : '/signup'}`;
            if (err.name === 'AbortError') {
                setError(`Connection timed out at ${targetUrl}. Is the backend slow?`);
            } else {
                setError(`Failed to connect to ${targetUrl}. Error: ${err.message || 'Unknown network error'}`);
            }
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center bg-dark" style={{ minHeight: '100vh', padding: 'var(--spacing-xl)', position: 'relative' }}>
            {/* Success Popup */}
            {showPopup && (
                <div style={{
                    position: 'fixed', top: '40px', left: '50%', transform: 'translateX(-50%)',
                    background: 'linear-gradient(135deg, var(--primary-500), var(--secondary-500))',
                    padding: '1.25rem 2.5rem', borderRadius: 'var(--radius-md)', color: 'white',
                    fontWeight: 800, fontSize: '1.2rem', boxShadow: '0 10px 40px rgba(160, 100, 255, 0.4)',
                    zIndex: 10000, animation: 'slideDown 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28)'
                }}>
                    ✨ Hello, {welcomeName}!
                </div>
            )}

            <div className="glass-card fade-in" style={{ maxWidth: '480px', width: '100%', padding: 'var(--spacing-xl)' }}>
                <div className="text-center mb-xl">
                    <h1 className="gradient-text" style={{ fontSize: '3rem', marginBottom: '0.5rem', fontWeight: 900 }}>Edunovas</h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
                        {isLogin ? 'Enter the AI Mentor Ecosystem' : 'Join the technical elite'}
                    </p>
                </div>

                <div style={{ marginBottom: '2.5rem' }}>
                    <div className="flex" style={{
                        background: 'rgba(52, 160, 90, 0.05)', padding: '4px', borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--glass-border)', position: 'relative', height: '52px'
                    }}>
                        <div style={{
                            position: 'absolute', top: '4px', left: role === 'student' ? '4px' : 'calc(50% + 2px)',
                            width: 'calc(50% - 6px)', height: 'calc(100% - 8px)',
                            background: 'linear-gradient(135deg, var(--primary-500), var(--secondary-500))',
                            borderRadius: 'var(--radius-sm)', transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)', zIndex: 0
                        }}></div>

                        <button type="button" onClick={() => setRole('student')} style={{ flex: 1, border: 'none', background: 'none', color: role === 'student' ? 'white' : 'var(--text-secondary)', cursor: 'pointer', fontWeight: 700, fontSize: '0.95rem', zIndex: 1 }}>Student</button>
                        <button type="button" onClick={() => setRole('admin')} style={{ flex: 1, border: 'none', background: 'none', color: role === 'admin' ? 'white' : 'var(--text-secondary)', cursor: 'pointer', fontWeight: 700, fontSize: '0.95rem', zIndex: 1 }}>Admin</button>
                    </div>
                </div>

                <form className="flex-col gap-lg" onSubmit={handleSubmit}>
                    {!isLogin && (
                        <div className="flex-col gap-xs">
                            <label style={{ fontSize: '0.8rem', color: 'var(--primary-400)', fontWeight: 700, letterSpacing: '0.5px' }}>FULL NAME</label>
                            <input type="text" className="input-field" placeholder="John Doe" value={fullName} onChange={(e) => setFullName(e.target.value)} required={!isLogin} style={{ padding: '0.9rem 1.25rem' }} />
                        </div>
                    )}

                    <div className="flex-col gap-xs">
                        <label style={{ fontSize: '0.8rem', color: 'var(--primary-400)', fontWeight: 700, letterSpacing: '0.5px' }}>EMAIL ADDRESS</label>
                        <input type="email" className="input-field" placeholder="name@university.edu" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ padding: '0.9rem 1.25rem' }} />
                    </div>

                    <div className="flex-col gap-xs" style={{ position: 'relative' }}>
                        <label style={{ fontSize: '0.8rem', color: 'var(--primary-400)', fontWeight: 700, letterSpacing: '0.5px' }}>PASSWORD</label>
                        <input type={showPassword ? "text" : "password"} className="input-field" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ padding: '0.9rem 1.25rem' }} maxLength={72} />
                        <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', right: '15px', bottom: '14px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>{showPassword ? 'HIDE' : 'SHOW'}</button>
                    </div>

                    {!isLogin && (
                        <div className="flex-col gap-xs">
                            <label style={{ fontSize: '0.8rem', color: 'var(--primary-400)', fontWeight: 700, letterSpacing: '0.5px' }}>CONFIRM PASSWORD</label>
                            <input type={showPassword ? "text" : "password"} className="input-field" placeholder="••••••••" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required={!isLogin} style={{ padding: '0.9rem 1.25rem' }} maxLength={72} />
                        </div>
                    )}

                    {error && (
                        <div className="fade-in" style={{ padding: '1rem', background: 'rgba(255, 77, 77, 0.08)', borderLeft: '4px solid #ff4d4d', borderRadius: '4px', fontSize: '0.9rem', color: '#ff4d4d', fontWeight: 500 }}>
                            ⚠️ {error}
                        </div>
                    )}

                    <button type="submit" disabled={isLoading} className="btn btn-primary mt-md" style={{ width: '100%', justifyContent: 'center', height: '56px', cursor: isLoading ? 'default' : 'pointer', fontSize: '1.1rem', fontWeight: 700, boxShadow: 'var(--shadow-lg)' }}>
                        {isLoading ? (
                            <div className="flex items-center gap-md">
                                <div className="spinner" style={{ width: '20px', height: '20px', border: '3px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }}></div>
                                Authenticating...
                            </div>
                        ) : (isLogin ? `Sign In as ${role}` : `Create ${role} Account`)}
                    </button>

                    <p style={{ textAlign: 'center', fontSize: '0.95rem', color: 'var(--text-secondary)', marginTop: '1rem' }}>
                        {isLogin ? "Don't have an account?" : "Already part of Edunovas?"}{' '}
                        <span onClick={() => { setIsLogin(!isLogin); setError(''); }} style={{ color: 'var(--primary-400)', cursor: 'pointer', fontWeight: 800, textDecoration: 'underline', padding: '4px 8px' }}>
                            {isLogin ? 'Sign Up' : 'Login'}
                        </span>
                    </p>
                </form>
            </div>

            <style>{`
                @keyframes slideDown { from { transform: translate(-50%, -100%); opacity: 0; } to { transform: translate(-50%, 0); opacity: 1; } }
                @keyframes spin { to { transform: rotate(360deg); } }
                .bg-dark { background: radial-gradient(circle at top right, #e8f5e9, #f1f8e9, #ffffff); }
            `}</style>
        </div>
    );
};
