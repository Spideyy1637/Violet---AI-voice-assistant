"use client";

import { cn } from "@/lib/utils";
import React from "react";

interface AuroraTextProps extends React.HTMLAttributes<HTMLSpanElement> {
    className?: string;
    children: React.ReactNode;
    as?: React.ElementType;
}

export function AuroraText({
    className,
    children,
    as: Component = "span",
    ...props
}: AuroraTextProps) {
    return (
        <Component
            className={cn(
                "bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-violet-500 to-pink-500 animate-aurora bg-[length:300%_auto]",
                className
            )}
            {...props}
        >
            {children}
        </Component>
    );
}
