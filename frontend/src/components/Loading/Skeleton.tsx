import React from 'react';

interface SkeletonProps {
    className?: string;
    variant?: 'text' | 'rect' | 'circle';
}

const Skeleton: React.FC<SkeletonProps> = ({ className = '', variant = 'text' }) => {
    const baseClasses = "bg-gray-700 animate-pulse";
    const variantClasses: Record<string, string> = {
        text: "h-4 w-full rounded",
        rect: "h-32 w-full rounded-lg",
        circle: "h-12 w-12 rounded-full"
    };

    return (
        <div
            className={`${baseClasses} ${variantClasses[variant] || ''} ${className}`}
            aria-hidden="true"
        />
    );
};

export default Skeleton;
