<script lang="ts">
	// AUC per prefix length, one line per series, dashed 0.5 "guessing" reference,
	// short direct labels at the line ends (spread so they never overlap).
	import { INK } from './theme';

	export interface LineSeries {
		key: string;
		short: string;
		color: string;
		dash?: string;
		marker: string;
		values: Record<string, number>;
	}

	let {
		series,
		yMin,
		yMax,
		width = 1472,
		height = 600,
		xLabel = 'Prefix length (events observed so far)',
		yLabel = 'AUC on test cases'
	}: { series: LineSeries[]; yMin: number; yMax: number; width?: number; height?: number; xLabel?: string; yLabel?: string } =
		$props();

	const pad = { top: 36, right: 300, bottom: 92, left: 128 };
	const ks = $derived([...new Set(series.flatMap((s) => Object.keys(s.values).map(Number)))].sort((a, b) => a - b));
	const innerW = $derived(width - pad.left - pad.right);
	const innerH = $derived(height - pad.top - pad.bottom);
	const x = (k: number) => pad.left + ((k - ks[0]) / (ks[ks.length - 1] - ks[0])) * innerW;
	const y = (v: number) => pad.top + (1 - (v - yMin) / (yMax - yMin)) * innerH;
	const yTicks = $derived(
		Array.from({ length: Math.round((yMax - yMin) / 0.1) + 1 }, (_, i) => +(yMin + i * 0.1).toFixed(1))
	);
	const path = (s: LineSeries) => ks.map((k, i) => `${i ? 'L' : 'M'}${x(k)},${y(s.values[k])}`).join('');

	// direct labels at the right end, pushed apart to at least `gap` px
	const labels = $derived.by(() => {
		const gap = 34;
		const last = ks[ks.length - 1];
		const ls = series.map((s) => ({ s, want: y(s.values[last]), at: y(s.values[last]) })).sort((a, b) => a.want - b.want);
		for (let i = 1; i < ls.length; i++) ls[i].at = Math.max(ls[i].at, ls[i - 1].at + gap);
		const overflow = ls.length ? ls[ls.length - 1].at - (pad.top + innerH) : 0;
		if (overflow > 0) for (const l of ls) l.at -= overflow;
		for (let i = ls.length - 2; i >= 0; i--) ls[i].at = Math.min(ls[i].at, ls[i + 1].at - gap);
		return ls;
	});
</script>

{#snippet marker(kind: string, cx: number, cy: number, color: string)}
	{#if kind === 'square'}
		<rect x={cx - 8} y={cy - 8} width="16" height="16" fill={color} stroke={INK.surface} stroke-width="2.5" />
	{:else if kind === 'diamond'}
		<path d="M{cx} {cy - 11} L{cx + 11} {cy} L{cx} {cy + 11} L{cx - 11} {cy} Z" fill={color} stroke={INK.surface} stroke-width="2.5" />
	{:else if kind === 'triangle'}
		<path d="M{cx} {cy - 10} L{cx + 10} {cy + 8} L{cx - 10} {cy + 8} Z" fill={color} stroke={INK.surface} stroke-width="2.5" />
	{:else}
		<circle {cx} {cy} r="8.5" fill={color} stroke={INK.surface} stroke-width="2.5" />
	{/if}
{/snippet}

<svg {width} {height} role="img" aria-label="AUC per prefix length" font-family="'Geist Variable', sans-serif">
	{#each yTicks as t (t)}
		<line x1={pad.left} x2={pad.left + innerW} y1={y(t)} y2={y(t)} stroke={INK.grid} stroke-width="1.5" />
		<text x={pad.left - 16} y={y(t)} dy="0.35em" text-anchor="end" font-size="24" fill={INK.secondary} font-family="'Geist Mono', monospace">
			{t.toFixed(1)}
		</text>
	{/each}
	{#each ks as k (k)}
		<text x={x(k)} y={pad.top + innerH + 40} text-anchor="middle" font-size="24" fill={INK.secondary} font-family="'Geist Mono', monospace">{k}</text>
	{/each}
	<line x1={pad.left} x2={pad.left + innerW} y1={pad.top + innerH} y2={pad.top + innerH} stroke={INK.secondary} stroke-width="1.5" />

	<text x={pad.left + innerW / 2} y={height - 10} text-anchor="middle" font-size="26" fill={INK.primary}>{xLabel}</text>
	<text transform="translate(34 {pad.top + innerH / 2}) rotate(-90)" text-anchor="middle" font-size="26" fill={INK.primary}>{yLabel}</text>

	<!-- 0.5 = guessing -->
	<line x1={pad.left} x2={pad.left + innerW} y1={y(0.5)} y2={y(0.5)} stroke={INK.primary} stroke-width="2" stroke-dasharray="12 8" />
	<text x={pad.left + innerW + 36} y={y(0.5)} dy="0.35em" font-size="24" fill={INK.primary}>0.5 = guessing</text>

	{#each series as s (s.key)}
		<path d={path(s)} fill="none" stroke={s.color} stroke-width="4" stroke-dasharray={s.dash} stroke-linejoin="round" stroke-linecap="round" />
		{#each ks as k (k)}
			{@render marker(s.marker, x(k), y(s.values[k]), s.color)}
		{/each}
	{/each}

	{#each labels as l (l.s.key)}
		{@const lx = pad.left + innerW}
		<line x1={lx + 14} x2={lx + 30} y1={l.want} y2={l.at} stroke={INK.muted} stroke-width="1.5" />
		<text x={lx + 36} y={l.at} dy="0.35em" font-size="24" fill={INK.primary}>
			{l.s.short}
			<tspan fill={INK.secondary} font-family="'Geist Mono', monospace">{l.s.values[ks[ks.length - 1]].toFixed(2)}</tspan>
		</text>
	{/each}
</svg>
