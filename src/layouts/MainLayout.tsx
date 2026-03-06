import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/Navbar';

export const MainLayout = () => {
    return (
        <div className="flex-col min-h-screen">
            <Navbar />
            <main className="container" style={{ flex: 1 }}>
                <Outlet />
            </main>
            <footer style={{
                marginTop: 'auto',
                padding: '4rem 0',
                borderTop: '1px solid var(--glass-border)',
                background: 'rgba(52, 160, 90, 0.05)'
            }} className="text-center">
                <p style={{ color: 'var(--text-muted)' }}>
                    © 2026 Edunovas AI Ecosystem. All rights reserved.
                </p>
            </footer>
        </div>
    );
};
