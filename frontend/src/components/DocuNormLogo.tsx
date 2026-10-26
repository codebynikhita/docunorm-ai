"use client";

import React from "react";

interface DocuNormLogoProps {
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  showText?: boolean;
  showBadge?: boolean;
  showSubtitle?: boolean;
  className?: string;
  isHoverable?: boolean;
}

export function DocuNormLogo({
  size = "sm",
  showText = true,
  showBadge = true,
  showSubtitle = true,
  className = "",
  isHoverable = true,
}: DocuNormLogoProps) {
  // Dimensions map
  const dimensions = {
    xs: { icon: 24, text: "text-xs", badge: "text-[8px]" },
    sm: { icon: 34, text: "text-sm", badge: "text-[9px]" },
    md: { icon: 44, text: "text-base", badge: "text-[9.5px]" },
    lg: { icon: 56, text: "text-xl", badge: "text-[10px]" },
    xl: { icon: 72, text: "text-2xl", badge: "text-[11px]" },
  }[size];

  return (
    <div className={`flex items-center gap-2.5 select-none ${className}`}>
      {/* 1. Sovereign Emblem (Shield + DIN A4 Document + Paragraph Sign + AI Sparkle) */}
      <div
        className={`relative flex items-center justify-center shrink-0 transition-all duration-300 ${
          isHoverable ? "group-hover:scale-105" : ""
        }`}
        style={{ width: dimensions.icon, height: dimensions.icon }}
      >
        <svg
          viewBox="0 0 44 44"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full drop-shadow-md"
        >
          <defs>
            {/* Primary German Institutional Shield Gradient */}
            <linearGradient id="shieldGrad" x1="6" y1="4" x2="38" y2="40" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="var(--accent-tangerine)" stopOpacity="0.22" />
              <stop offset="60%" stopColor="var(--surface-dark)" stopOpacity="0.95" />
              <stop offset="100%" stopColor="var(--surface-card)" stopOpacity="0.9" />
            </linearGradient>

            {/* Glowing Contour Gradient */}
            <linearGradient id="shieldBorder" x1="4" y1="4" x2="40" y2="40" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="var(--accent-tangerine)" stopOpacity="0.9" />
              <stop offset="45%" stopColor="var(--accent-tangerine)" stopOpacity="0.5" />
              <stop offset="100%" stopColor="var(--accent-cyan)" stopOpacity="0.8" />
            </linearGradient>

            {/* Fold Corner Gradient */}
            <linearGradient id="foldGrad" x1="24" y1="11" x2="29" y2="16" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="var(--accent-tangerine)" stopOpacity="0.8" />
              <stop offset="100%" stopColor="var(--accent-tangerine)" stopOpacity="0.3" />
            </linearGradient>

            {/* Paragraph Glow */}
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="0" stdDeviation="1.5" floodColor="var(--accent-tangerine)" floodOpacity="0.45" />
            </filter>
          </defs>

          {/* Outer Sovereign Hexagonal Shield */}
          <path
            d="M22 3.5L37 8.5V21C37 30.5 30 37.5 22 40.5C14 37.5 7 30.5 7 21V8.5L22 3.5Z"
            fill="url(#shieldGrad)"
            stroke="url(#shieldBorder)"
            strokeWidth="1.8"
            strokeLinejoin="round"
          />

          {/* Inner Precision Grid Guidelines */}
          <path
            d="M13 14H31M13 22H31M13 30H27"
            stroke="var(--foreground)"
            strokeOpacity="0.07"
            strokeWidth="1"
            strokeDasharray="2 2"
          />

          {/* DIN A4 Contract Sheet with Precision Folded Corner */}
          <path
            d="M14 11H25L30 16V31H14V11Z"
            fill="var(--surface-dark)"
            stroke="var(--foreground)"
            strokeOpacity="0.25"
            strokeWidth="1.2"
            strokeLinejoin="round"
          />
          {/* Folded Corner Dog-Ear */}
          <path
            d="M25 11V16H30"
            fill="url(#foldGrad)"
            stroke="var(--accent-tangerine)"
            strokeWidth="1.2"
            strokeLinejoin="round"
          />

          {/* Modern Geometric Paragraph Sign (§) in Center */}
          <g filter="url(#glow)">
            {/* Top Loop */}
            <path
              d="M20.5 16C20.5 14.8 21.4 14 22.5 14C23.6 14 24.5 14.8 24.5 16C24.5 17.5 22.5 18.5 20.5 19.5C18.5 20.5 16.5 21.7 16.5 24C16.5 26.2 18.3 28 20.5 28C22.7 28 24.5 26.5 24.5 25"
              fill="none"
              stroke="var(--accent-tangerine)"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Bottom Loop */}
            <path
              d="M23.5 26C23.5 27.2 22.6 28 21.5 28C20.4 28 19.5 27.2 19.5 26C19.5 24.5 21.5 23.5 23.5 22.5C25.5 21.5 27.5 20.3 27.5 18C27.5 15.8 25.7 14 23.5 14C21.3 14 19.5 15.5 19.5 17"
              fill="none"
              stroke="var(--accent-tangerine)"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Connecting Center Pillar */}
            <circle cx="22" cy="21" r="1.4" fill="var(--accent-cyan)" />
          </g>

          {/* AI Neural Verification Sparkle Node at Vertex */}
          <g transform="translate(32, 6)">
            <circle cx="0" cy="0" r="2.2" fill="var(--accent-lime)" />
            <circle cx="0" cy="0" r="4" fill="var(--accent-lime)" opacity="0.3" className="animate-ping" />
          </g>
        </svg>
      </div>

      {/* 2. Typographic Wordmark & Institutional Metadata */}
      {showText && (
        <div className="flex flex-col justify-center leading-tight">
          <div className="flex items-center gap-2">
            <span
              className={`font-black tracking-tight font-mono text-[var(--foreground)] uppercase ${dimensions.text}`}
            >
              DOCUNORM
              <span className="text-[var(--accent-tangerine)] font-extrabold tracking-normal">.DE</span>
            </span>

            {showBadge && (
              <span
                className={`font-mono font-bold tracking-widest uppercase px-1.5 py-0.5 rounded border ${dimensions.badge} bg-[var(--accent-tangerine)]/10 text-[var(--accent-tangerine)] border-[var(--accent-tangerine)]/30 shrink-0 hidden sm:inline-block`}
              >
                BAFIN-READY
              </span>
            )}
          </div>

          {showSubtitle && (
            <p className="text-[9.5px] font-mono tracking-wider text-[var(--foreground)] opacity-55 uppercase hidden md:block">
              Regulatory AI • DORA & BDSG § 26
            </p>
          )}
        </div>
      )}
    </div>
  );
}