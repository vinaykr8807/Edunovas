import { useRef, useEffect } from 'react';

interface KnowledgeNode {
    id: string;
    label: string;
    level: number; // 0 to 1
    status: 'done' | 'learning' | 'struggling' | 'idle';
}

export const KnowledgeGraph = ({ data }: { data: KnowledgeNode[] }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (!canvasRef.current || !data) return;
        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;

        // Simple Radar/Orbital Layout
        const width = canvasRef.current.width;
        const height = canvasRef.current.height;
        const centerX = width / 2;
        const centerY = height / 2;

        ctx.clearRect(0, 0, width, height);

        // Draw Rings
        ctx.strokeStyle = 'rgba(0,0,0,0.05)';
        for (let i = 1; i <= 4; i++) {
            ctx.beginPath();
            ctx.arc(centerX, centerY, (i * (width / 2)) / 4, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Draw Nodes
        const angleStep = (Math.PI * 2) / data.length;
        data.forEach((node, i) => {
            const angle = i * angleStep;
            const radius = (node.level * (width / 2 - 40)) + 20;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;

            // Gradient for node
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, 10);
            const color = node.status === 'done' ? '#34d399' : 
                          node.status === 'learning' ? '#3b82f6' : 
                          node.status === 'struggling' ? '#ef4444' : '#6b7280';
            
            gradient.addColorStop(0, color);
            gradient.addColorStop(1, 'transparent');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, 15, 0, Math.PI * 2);
            ctx.fill();

            // Label
            ctx.fillStyle = '#111';
            ctx.font = '700 10px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(node.label, x, y + 25);
        });

        // Connect nodes to center
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.1)';
        data.forEach((node, i) => {
            const angle = i * angleStep;
            const radius = (node.level * (width / 2 - 40)) + 20;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.stroke();
        });

    }, [data]);

    return (
        <div className="flex-col items-center">
            <canvas 
                ref={canvasRef} 
                width={400} 
                height={400} 
                style={{ maxWidth: '100%', height: 'auto' }}
            />
            <div className="flex gap-md mt-md">
                <div className="flex items-center gap-xs"><span style={{width:8,height:8,background:'#34d399',borderRadius:'50%'}}></span> <span style={{fontSize:'0.7rem'}}>Mastered</span></div>
                <div className="flex items-center gap-xs"><span style={{width:8,height:8,background:'#3b82f6',borderRadius:'50%'}}></span> <span style={{fontSize:'0.7rem'}}>Learning</span></div>
                <div className="flex items-center gap-xs"><span style={{width:8,height:8,background:'#ef4444',borderRadius:'50%'}}></span> <span style={{fontSize:'0.7rem'}}>Weak</span></div>
            </div>
        </div>
    );
};
