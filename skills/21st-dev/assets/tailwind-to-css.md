# Tailwind → CSS Variable Conversion

When taking 21st.dev components (Tailwind) into our pure-CSS projects (lab, portfolio, news).

## Color Mappings

| Tailwind class | Our CSS variable | Dark value | Light value |
|---|---|---|---|
| `bg-background` | `var(--bg)` | `#0c1222` | `#f8fafc` |
| `bg-card` | `var(--card-bg)` | `#151d2e` | `#ffffff` |
| `border-border` | `var(--border)` | `#1e293b` | `#e2e8f0` |
| `text-foreground` | `var(--text-primary)` | `#e5e7eb` | `#0f172a` |
| `text-muted-foreground` | `var(--text-secondary)` | `#94a3b8` | `#475569` |
| `text-muted` | `var(--text-muted)` | `#64748b` | `#94a3b8` |
| `text-primary` / accent | `var(--accent)` | `#c9a962` | `#b8892a` |
| `bg-primary` | `background: var(--accent)` | — | — |
| `bg-muted` | `rgba(30,41,59,0.5)` | — | — |
| `ring-ring` | `var(--border)` | — | — |

## Spacing (Tailwind → px)

| Tailwind | px |
|---|---|
| `p-2` | `8px` |
| `p-4` | `16px` |
| `p-6` | `24px` |
| `p-8` | `32px` |
| `gap-4` | `gap: 16px` |
| `gap-6` | `gap: 24px` |
| `rounded-lg` | `border-radius: 8px` |
| `rounded-xl` | `border-radius: 12px` |
| `rounded-full` | `border-radius: 9999px` |

## Typography

| Tailwind | CSS |
|---|---|
| `text-sm` | `font-size: 0.875rem` |
| `text-base` | `font-size: 1rem` |
| `text-lg` | `font-size: 1.125rem` |
| `text-xl` | `font-size: 1.25rem` |
| `text-2xl` | `font-size: 1.5rem` |
| `font-medium` | `font-weight: 500` |
| `font-semibold` | `font-weight: 600` |
| `font-bold` | `font-weight: 700` |

## Common Patterns

### Glassmorphism card (Tailwind → CSS)
```css
/* Tailwind: bg-card/50 backdrop-blur-sm border border-border rounded-xl */
background: rgba(21, 29, 46, 0.5);
backdrop-filter: blur(8px);
border: 1px solid var(--border);
border-radius: 12px;
```

### Button primary
```css
/* Tailwind: bg-primary text-primary-foreground hover:bg-primary/90 */
background: var(--accent);
color: #0c1222;
transition: opacity 0.2s;
/* hover: opacity: 0.9 */
```

### Button outline
```css
/* Tailwind: border border-border hover:bg-accent hover:text-accent-foreground */
border: 1px solid var(--border);
background: transparent;
color: var(--text-secondary);
transition: border-color 0.2s, color 0.2s;
/* hover: border-color: var(--accent); color: var(--accent) */
```
