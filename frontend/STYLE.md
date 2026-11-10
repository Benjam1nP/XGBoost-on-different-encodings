# Style guide (exported from Firn)

A calm, dense, dark-first UI. Cool blue-grey neutrals, a single glacier-blue accent, a mono font for numbers, and a serif used only for display text. Layers are separated by surface colour and 1px borders, not shadows.

**Stack:** SvelteKit + Svelte 5 (runes), Tailwind v4, shadcn-svelte (style `vega`), bits-ui, mode-watcher, Phosphor icons via `unplugin-icons`, svelte-sonner, LayerChart for charts.

**Source of truth for tokens:** `src/routes/layout.css` (included in this kit).

---

## 0. Setup in a fresh SvelteKit project

```bash
# Tailwind v4 (skip if already set up)
pnpm add -D tailwindcss @tailwindcss/vite tw-animate-css

# shadcn-svelte: answer the prompts, then replace components.json with the one in this kit
pnpm dlx shadcn-svelte@latest init
pnpm dlx shadcn-svelte@latest add button card input textarea badge tooltip skeleton separator tabs dialog sheet popover select table sonner

# Fonts, icons, theme
pnpm add -D @fontsource-variable/geist @fontsource/geist-mono @fontsource/instrument-serif \
  unplugin-icons @iconify-json/ph mode-watcher svelte-sonner cn tailwind-variants
```

1. Copy `src/routes/layout.css` over yours. If your CSS file lives elsewhere, update `tailwind.css` in `components.json`.
2. Copy `components.json`. It sets `style: "vega"` and `iconLibrary: "phosphor"`, so future `shadcn-svelte add` calls match. Then run the `add` command above. Do this after copying the CSS so the components pick up the tokens.
3. `vite.config.ts`: add the icons plugin.

   ```ts
   import Icons from 'unplugin-icons/vite';
   // plugins: [tailwindcss(), sveltekit(), Icons({ compiler: 'svelte' })]
   ```

   For TS types, add `"types": ["unplugin-icons/types/svelte"]` to `tsconfig.json` `compilerOptions`.
4. `src/app.html`: dark by default, with no light flash on load.

   ```html
   <html lang="en" class="dark">
   <head>
     <meta name="theme-color" content="#0A0E13" />
     <script>
       try {
         const mode = localStorage.getItem('mode-watcher-mode') ?? 'dark';
         if (mode === 'light' || (mode === 'system' && matchMedia('(prefers-color-scheme: light)').matches)) {
           document.documentElement.classList.remove('dark');
           document.documentElement.style.colorScheme = 'light';
           document.querySelector('meta[name="theme-color"]').content = '#F7F9FB';
         }
       } catch {}
     </script>
     %sveltekit.head%
   ```

   This script is only needed when SSR is off. With SSR on, mode-watcher handles it.
5. Root `src/routes/+layout.svelte`:

   ```svelte
   <script lang="ts">
     import './layout.css';
     import { ModeWatcher } from 'mode-watcher';
     import { Toaster } from '$lib/components/ui/sonner';
     import * as Tooltip from '$lib/components/ui/tooltip';
     let { children } = $props();
   </script>

   <ModeWatcher defaultMode="dark" themeColors={{ dark: '#0A0E13', light: '#F7F9FB' }} />
   <Toaster position="bottom-right" />
   <Tooltip.Provider delayDuration={150}>
     {@render children()}
   </Tooltip.Provider>
   ```
6. `src/lib/components/ThemeToggle.svelte` is included in this kit (a ghost icon button with a sun/moon icon).

---

## 1. Colour

Use semantic tokens (`bg-card`, `text-muted-foreground`), never raw hex. **Dark is the default**; light is fully supported.

### Brand palette

| Name | Hex | Role |
|---|---|---|
| polar-night | `#0A0E13` | Dark background, light-mode text |
| slate-900 | `#111821` | Dark cards |
| slate-800 | `#18212C` | Dark hover / secondary |
| slate-700 | `#1E2733` | Dark borders |
| firn | `#EEF3F7` | Dark-mode text |
| paper | `#F7F9FB` | Light background |
| mist | `#8B98A6` | Dark muted text |
| stone | `#5B6773` | Light muted text |
| glacier-300 | `#8CC8F2` | Accent (dark) |
| glacier-500 | `#3B8BD4` | Chart tint |
| glacier-600 | `#2A70B5` | Accent (light) |
| glacier-700 | `#1E5E9A` | Links (light) |

### Semantic tokens

| Token | Tailwind | Light | Dark | Use |
|---|---|---|---|---|
| background | `bg-background` | `#F7F9FB` | `#0A0E13` | Page |
| card / popover | `bg-card` | `#FFFFFF` | `#111821` | Cards, dialogs, menus |
| secondary / accent | `bg-secondary` | `#E8EEF3` | `#18212C` | Hover fills, active nav, secondary buttons |
| muted | `bg-muted` | `#EEF2F6` | `#151D27` | Skeletons, table header |
| border | `border-border` | `#DCE3EA` | `#1E2733` | Dividers, card borders, gridlines |
| input | `border-input` | `#CFD8E1` | `#263140` | Input borders |
| foreground | `text-foreground` | `#0A0E13` | `#EEF3F7` | Primary text |
| muted-foreground | `text-muted-foreground` | `#5B6773` | `#8B98A6` | Secondary text, labels |
| primary / ring | `bg-primary` | `#2A70B5` | `#8CC8F2` | One primary action per view, focus ring |
| link | `text-link` | `#1E5E9A` | `#8CC8F2` | Inline links |
| destructive | `text-destructive` | `#C23B40` | `#F2777A` | Destructive actions, errors |
| agent-rule | `border-agent-rule` | `#2A70B5` | `#8CC8F2` | 2px left accent rule (highlighted / selected / assistant items) |
| chart-1..5 | `fill-chart-1` | glacier-600, stone, mist, glacier-700, glacier-300 | glacier-300, mist, stone, glacier-500, firn | Chart series, in this order |
| sidebar-* | `bg-sidebar` | white | slate-900 | Sidebar surface |

**Optional, domain-specific:** `gain` (`#16804F` / `#3DD68C`), `loss` (`#C23B40` / `#F2777A`), `benchmark` (stone / mist). These are for positive and negative numbers and reference series. Drop or rename them if you don't need them.

### Rules

- **Monochrome first.** The blue accent goes on the single primary action, focus rings, links and the selected state. Nothing else.
- Green and red are for data only, always paired with a sign (`+` / `−`, true minus). No green "success" or amber "warning" banners. Status uses neutral badges plus an icon.
- Text selection is `color-mix(primary 35%, transparent)`.
- All text pairs pass WCAG AA.

---

## 2. Typography

Fonts: **Geist** (`font-sans`, all UI), **Geist Mono** (`font-mono`, or the `text-figure` utility, for every number that changes), **Instrument Serif** (`font-heading`, display only, weight 400).

The scale is custom, with a **15px body** (overrides Tailwind defaults in `@theme`):

| Step | Classes | Size / line height | Use |
|---|---|---|---|
| Display | `font-heading text-5xl` | 72 / 1.05 | Landing headline |
| Display S | `font-heading text-4xl` | 48 / 1.1 | Empty-state titles, hero summary |
| H1 | `text-2xl font-bold tracking-tight` | 28 / 34 | Page title |
| H2 | `text-xl font-bold tracking-tight` | 20 / 28 | Card / section title |
| Dialog title | `font-sans text-lg font-semibold tracking-tight` | 18 / 26 | Dialog headers |
| H3 | `text-lg font-medium` | 18 / 26 | Subsection |
| Body | `text-base` | 15 / 24 | Paragraphs, chat |
| Small | `text-sm` | 13 / 20 | Tables, captions, buttons, nav |
| Caption | `text-xs` | 12 / 16 | Timestamps, bottom tab labels |
| Label | `text-label` | 12 / 16, uppercase, +0.06em, 500, muted colour | Overlines, table headers, sidebar group titles |
| KPI | `text-figure text-3xl font-medium` | 36 / 40 | Hero numbers |
| Figure | `text-figure text-sm` | 13 / 20 | Prices, IDs, percentages |

- `text-label` and `text-figure` are custom `@utility` classes defined in `layout.css`. `text-figure` = mono + `tabular-nums`.
- Headings use `tracking-tight`. **Sentence case everywhere** ("New plan", not "New Plan").
- Numbers are right-aligned in tables. Percentages use one decimal.

---

## 3. Spacing, layout, radius, elevation

- **4px base** (Tailwind default scale). Prefer `1 2 3 4 6 8 12 16`.
- **Padding:** cards `p-5`, buttons and inputs `px-2.5`–`px-3`, dense table cells `px-3 py-2`.
- **Gaps:** related items `gap-2`, groups `gap-4`, sections `gap-8`, page sections `gap-12`.
- **Radius:** `--radius: 0.5rem`. Cards and dialogs use `rounded-lg` (8px). Buttons, inputs, badges and nav items use `rounded-md`. `rounded-full` is only for avatars and status dots.
- **No shadows for elevation**, especially in dark mode. Layer with surface colour (`background` → `card` → `secondary`) plus a 1px `border`. `shadow-lg` is allowed on popovers and dialogs in light mode only.
- **Breakpoints:** Tailwind defaults. Mobile `<md`, desktop `md+`.

### App shell (desktop `md+`)

```
┌──────────────┬──────────────────────────────────────┐
│ Logo (h-6)   │                                      │
│              │   main: max-w-7xl mx-auto            │
│ ▢ Overview   │         px-8 py-8                    │
│ ▢ Chat       │                                      │
│              │                                      │
│ LABEL        │                                      │
│ │ Item  +2.1%│  ← selected: bg-secondary +          │
│   Item  −0.4%│    2px left border-agent-rule        │
│              │                                      │
│ status  ☾ ⇥  │                                      │
└──────────────┴──────────────────────────────────────┘
 aside: w-60, sticky h-dvh, border-r, bg-sidebar, px-4 py-6, gap-8
```

- Nav link: `flex items-center gap-3 rounded-md px-2 py-2 text-sm text-muted-foreground transition-colors duration-100 hover:bg-secondary hover:text-foreground aria-[current=page]:bg-secondary aria-[current=page]:text-foreground`. Use a 20px Phosphor **Light** icon.
- **Mobile:** single column with `px-4 py-6`, a sticky top bar (`border-b bg-background px-4 py-2`, logo h-5), and a fixed bottom tab bar (`h-16`, a 24px icon above a `text-xs` label, `border-t`). Main content gets `pb-16`.

---

## 4. Icons

- **Phosphor only**, via `unplugin-icons`: `import Gear from '~icons/ph/gear-light'`. Icons use `currentColor`.
- Sizes and weights: 16px inline (Regular), 20px default (Light), 24px navigation (Light), 32px empty states (Light).
- Touch targets are at least 44×44px on mobile (`size-11 md:size-8`).
- Primary navigation icons always carry a text label.

---

## 5. Motion

| Duration | Use | Easing |
|---|---|---|
| 100ms | Hover, colour fade | `ease-out` |
| 150ms | Button press, tooltip delay | `ease-out` |
| 200ms | Dropdown, popover, item appearing | `ease-firn` in, `ease-in` out |
| 250ms | Dialog, sheet | `ease-firn` |

- `ease-firn` = `cubic-bezier(0.16, 1, 0.3, 1)` (Tailwind `ease-firn`).
- Max 300ms. Motion only shows causality (something arrived or moved). No bounce, no pulsing, no confetti, no shimmer on skeletons.
- Entrance pattern: `animate-in fade-in duration-200` (tw-animate-css).
- `prefers-reduced-motion` is honoured globally in `layout.css`.

---

## 6. Components

shadcn-svelte `vega` components, with tokens applied:

- **Button:** variants `default` (primary, **one per view**), `secondary`, `outline`, `ghost`, `destructive` (tinted `bg-destructive/10 text-destructive`, not solid red), `link`. Sizes: `sm` 32px, `default` 36px, `lg` 40px, plus `icon`, `icon-sm` and `icon-xs`. Hover is `/80`, press is `translate-y-px`, focus is a 3px `ring-ring/50`, disabled is 50% opacity.
- **Input / Textarea:** `border-input`. Numeric inputs use `text-figure` and are right-aligned. Show the invalid state with `aria-invalid`.
- **Badge:** neutral by default. Use it for status, with an icon carrying the meaning.
- **Table:** header in `text-label`, row hover `bg-secondary/50`, numbers right-aligned in `text-figure`.
- **Tooltip:** 150ms delay. Use it to explain jargon inline.
- **Skeleton:** `bg-muted`, static.
- **Sonner toasts:** neutral style. The icon carries the meaning, never a green or red background.

### Recurring patterns (copy the classes)

**Card / KPI tile**

```svelte
<div class="flex flex-col gap-2 rounded-lg border bg-card p-5">
  <p class="text-label">Total value</p>
  <p class="text-figure text-3xl font-medium">CHF 20,000</p>
  <p class="text-figure text-sm text-muted-foreground">vs last month +0.4%</p>
</div>
```

**Highlighted / assistant message** (card with an accent rule on the left)

```svelte
<article class="flex animate-in fade-in duration-200 flex-col gap-4 rounded-lg border border-l-2 border-l-agent-rule bg-card p-5">
  …
</article>
```

The user message has no background and is right-aligned.

**Empty state**

```svelte
<div class="flex flex-col items-center gap-4 py-16 text-center">
  <Icon class="size-8 text-muted-foreground" />   <!-- Phosphor Light -->
  <h2 class="font-heading text-4xl">Nothing here yet.</h2>
  <p class="max-w-md text-muted-foreground">One sentence on what to do next.</p>
  <Button>One action</Button>
</div>
```

**Page header**

```svelte
<h1 class="text-2xl font-bold tracking-tight">Page title</h1>
```

**Inline error with retry**

```svelte
<p class="text-sm" role="alert">
  <span class="text-muted-foreground">Couldn't load. Your changes are saved.</span>
  <button class="text-link underline-offset-4 hover:underline">Try again</button>
</p>
```

**Charts (LayerChart):** the main series is a 2px solid line in `chart-1`, with an 8% area fill under the main series only. Reference series are dashed 1px lines in a muted colour. Gridlines use `border`. The crosshair tooltip lists every series.

---

## 7. Patterns and voice

- **Loading:** skeletons for data. Never block the UI while secondary data loads.
- **Empty:** an empty state with exactly one next action.
- **Errors:** inline and in plain language, saying what happens next. Use a toast for background failures.
- **Confirmation:** destructive or irreversible actions go through a Dialog.
- **Voice:** calm, short, sentence case. No exclamation marks or hype.
