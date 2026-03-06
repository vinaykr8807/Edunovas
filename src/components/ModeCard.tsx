import React from 'react';
import type { Mode } from '../types';

interface ModeCardProps {
    id: Mode;
    name: string;
    tagline: string;
    icon: string;
    color: string;
    isActive: boolean;
    onClick: () => void;
}

export const ModeCard: React.FC<ModeCardProps> = ({ name, tagline, icon, color, isActive, onClick }) => {
    return (
        <div
            className={`glass-card ${isActive ? 'active' : ''}`}
            onClick={onClick}
            style={{
                cursor: 'pointer',
                padding: '2rem',
                border: isActive ? `1px solid ${color}` : '1px solid var(--glass-border)',
                background: isActive ? `rgba(${color.slice(4, -1)}, 0.08)` : 'var(--glass-bg)',
                display: 'flex',
                flexDirection: 'column',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                minHeight: '180px',
                justifyContent: 'center'
            }}
        >
            <div style={{
                fontSize: '2rem',
                marginBottom: '1.25rem',
                opacity: isActive ? 1 : 0.8
            }}>{icon}</div>
            <h3 style={{
                marginBottom: '0.5rem',
                fontSize: '1.15rem',
                color: isActive ? color : 'var(--text-primary)',
                transition: 'color 0.3s'
            }}>{name}</h3>
            <p style={{
                color: 'var(--text-secondary)',
                fontSize: '0.85rem',
                lineHeight: '1.4',
                maxWidth: '90%'
            }}>{tagline}</p>

            {isActive && (
                <div style={{
                    position: 'absolute',
                    top: '1.25rem',
                    right: '1.25rem',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: color,
                    boxShadow: `0 0 12px ${color}`
                }} />
            )}
        </div>
    );
};
