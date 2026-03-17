---
name: 21st-dev
description: UI component library and design resource from 21st.dev — community-curated React components for SaaS, AI, and modern web apps. Use when building or redesigning any frontend project for Suhail (Prompt Studio, portfolio, lab, news, or any new app) and components, patterns, or inspiration are needed. Triggers on phrases like "redesign", "new UI", "component for", "make it look like", "use 21st.dev", "add a hero section", "AI chat component", "pricing section", "landing page", or any frontend build task where polished components would accelerate the work. NOT for backend or infrastructure tasks.
---

# 21st.dev — UI Component Library

21st.dev is a community-driven React component library focused on modern SaaS, AI, and web app UI. Think shadcn/ui but more AI-native, with richer animations and SaaS-specific patterns.

## What's Available

| Category | Examples |
|---|---|
| **Heroes** | Full-screen, split, minimal, animated |
| **AI Chat** | Chat bubbles, streaming text, thinking indicators |
| **Features** | Grid, bento, icon grids |
| **Pricing** | Toggle monthly/annual, tiers, comparison |
| **CTAs** | Gradient, bordered, split |
| **Buttons** | Animated, glow, loading states |
| **Text Effects** | Typewriter, fade-in, scramble, gradient |
| **Testimonials** | Cards, marquee, avatars |
| **Shaders** | WebGL backgrounds, aurora, particles |

## How to Use

### 1. Browse & find a component
Go to `https://21st.dev/community/components` — filter by category or search by name.

### 2. Copy the code
Each component has a "Copy" button — raw React + Tailwind or CSS. No package install needed for most.

### 3. Adapt to our design system
Our design tokens to apply when adapting:
- **Background:** `#0c1222` (dark) / `#f8fafc` (light)
- **Cards:** `#151d2e` (dark) / `#ffffff` (light)
- **Border:** `#1e293b` (dark) / `#e2e8f0` (light)
- **Accent/Gold:** `#c9a962` (dark) / `#b8892a` (light)
- **Text primary:** `#e5e7eb` / `#0f172a`
- **Text secondary:** `#94a3b8` / `#475569`

Replace any `blue-500`/`purple-500` accent colors with our gold `#c9a962`.

### 4. Integration patterns

**If project uses Tailwind:** paste directly, swap color classes.

**If project uses pure CSS (lab, portfolio, news):** convert Tailwind classes to inline styles or CSS variables using our token map above. Reference `assets/tailwind-to-css.md` for common conversions.

**If project uses shadcn/ui:** components are usually drop-in compatible.

## Prompt Studio Redesign Notes

When redesigning Prompt Studio, prioritize these 21st.dev categories:
- **AI Chat Components** — for the prompt input/output area
- **Text Effects** — for streaming/typewriter output display
- **Buttons** — for Run, Copy, Save actions
- **Features (bento grid)** — for template/saved prompt library

See `references/prompt-studio-plan.md` for the full redesign plan.

## 1Code (AI Component Generator)

21st.dev also has **1Code** at `https://21st.dev/1code` — describe a component in plain English and it generates the React code. Useful for one-off custom components that aren't in the library.

## Component Categories Reference

See `references/components-catalog.md` for a curated list of the most useful components per project type.
