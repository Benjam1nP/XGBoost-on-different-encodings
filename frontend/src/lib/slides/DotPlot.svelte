<script lang="ts">
	// Mean AUC for 3 models x 3 encodings: one row per model inside each encoding group,
	// a thin stem from 0.5 to the dot and the value printed next to it.
	import { ENCODING_NAME, ENCODING_ORDER, INK, MODEL, MODEL_ORDER } from './theme';

	let {
		runs,
		xMin = 0.5,
		xMax,
		width = 1472,
		height = 610
	}: {
		runs: { model: string; encoding: string; mean_auc: number }[];
		xMin?: number;
		xMax: number;
		width?: number;
		height?: number;
	} = $props();

	const pad = { top: 64, right: 40, bottom: 92, left: 230 };
	const innerW = $derived(width - pad.left - pad.right);
	const innerH = $derived(height - pad.top - pad.bottom);
	const x = (v: number) => pad.left + ((v - xMin) / (xMax - xMin)) * innerW;
	const ticks = $derived(
		Array.from({ length: Math.round((xMax - xMin) / 0.05) + 1 }, (_, i) => +(xMin + i * 0.05).toFixed(2))
	);
	const groupGap = 28;
	const rowH = $derived((innerH - groupGap * (ENCODING_ORDER.length - 1)) / (ENCODING_ORDER.length * MODEL_ORDER.length));
	const rowY = (g: number, m: number) => pad.top + g * (MODEL_ORDER.length * rowH + groupGap) + (m + 0.5) * rowH;
	const get = (m: string, e: string) => runs.find((r) => r.model === m && r.encoding === e)!.mean_auc;
</script>

<svg {width} {height} role="img" aria-label="Mean AUC per model and encoding" font-family="'Geist Variable', sans-serif">
	{#each ticks as t (t)}
		<line x1={x(t)} x2={x(t)} y1={pad.top - 8} y2={pad.top + innerH} stroke={INK.grid} stroke-width="1.5" />
		<text x={x(t)} y={pad.top + innerH + 38} text-anchor="middle" font-size="24" fill={INK.secondary} font-family="'Geist Mono', monospace">
			{t.toFixed(2)}
		</text>
	{/each}
	<text x={pad.left + innerW / 2} y={height - 10} text-anchor="middle" font-size="26" fill={INK.primary}>
		Mean AUC over prefix lengths (test cases)
	</text>

	<!-- 0.5 = guessing -->
	<line x1={x(0.5)} x2={x(0.5)} y1={pad.top - 8} y2={pad.top + innerH} stroke={INK.primary} stroke-width="2.5" stroke-dasharray="12 8" />
	<text x={x(0.5) + 10} y={pad.top - 20} font-size="24" fill={INK.primary}>0.5 = guessing</text>

	{#each ENCODING_ORDER as e, g (e)}
		{@const top = rowY(g, 0) - rowH / 2}
		{#if g > 0}
			<line x1={0} x2={width - pad.right} y1={top - groupGap / 2} y2={top - groupGap / 2} stroke={INK.grid} stroke-width="1.5" />
		{/if}
		<text x={0} y={rowY(g, 1)} dy="0.35em" font-size="28" font-weight="600" fill={INK.primary}>{ENCODING_NAME[e]}</text>
		{#each MODEL_ORDER as m, i (m)}
			{@const v = get(m, e)}
			{@const cy = rowY(g, i)}
			<line x1={x(xMin)} x2={x(v)} y1={cy} y2={cy} stroke={MODEL[m].color} stroke-width="4" stroke-linecap="round" />
			<circle cx={x(v)} {cy} r="12" fill={MODEL[m].color} stroke={INK.surface} stroke-width="3" />
			<text x={x(v) + 22} y={cy} dy="0.35em" font-size="24" fill={INK.primary} font-family="'Geist Mono', monospace">{v.toFixed(3)}</text>
		{/each}
	{/each}
</svg>
