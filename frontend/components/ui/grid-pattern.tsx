"use client";
import React, { useState, useId, useEffect } from "react";
import { GridPatternProps } from "@/types/hackathon";

// Grid Pattern Component
export const GridPattern = ({ width, height, x, y, squares, className, ...props }: GridPatternProps) => {
    const patternId = useId();

    return (
        <svg aria-hidden="true" className={className} {...props}>
            <defs>
                <pattern id={patternId} width={width} height={height} patternUnits="userSpaceOnUse" x={x} y={y}>
                    <path d={`M.5 ${height}V.5H${width}`} fill="none" />
                </pattern>
            </defs>
            <rect width="100%" height="100%" strokeWidth={0} fill={`url(#${patternId})`} />
            {squares && (
                <svg x={x} y={y} className="overflow-visible">
                    {squares.map(([x, y]: number[], i: number) => (
                        <rect
                            strokeWidth="0"
                            key={`${x}-${y}-${i}`}
                            width={width + 1}
                            height={height + 1}
                            x={x * width}
                            y={y * height}
                        />
                    ))}
                </svg>
            )}
        </svg>
    );
};

// Grid Component
export const Grid = ({ pattern, size }: { pattern?: number[][]; size?: number }) => {
    const [clientPattern, setClientPattern] = useState<number[][] | null>(null);

    useEffect(() => {
        if (!pattern) {
            const randomPattern = [
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
            ];
            setClientPattern(randomPattern);
        }
    }, [pattern]);

    const p = pattern ?? clientPattern ?? [];

    return (
        <div className="pointer-events-none absolute left-1/2 top-0 -ml-20 -mt-2 h-full w-full [mask-image:linear-gradient(white,transparent)]">
            <div className="absolute inset-0 bg-gradient-to-r [mask-image:radial-gradient(farthest-side_at_top,white,transparent)] dark:from-zinc-900/30 from-zinc-100/30 to-zinc-300/30 dark:to-zinc-900/30 opacity-100">
                <GridPattern
                    width={size ?? 20}
                    height={size ?? 20}
                    x="-12"
                    y="4"
                    squares={p}
                    className="absolute inset-0 h-full w-full mix-blend-overlay dark:fill-white/10 dark:stroke-white/10 stroke-black/10 fill-black/10"
                />
            </div>
        </div>
    );
};
