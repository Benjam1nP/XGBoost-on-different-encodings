<script lang="ts">
	// G1 / G3: mean AUC, grouped by encoding, one row per model. Grey noise band = median of the
	// nine means ± 0.025. Index group markers at 60 % opacity (text stays black); the lowest point is called out as an
	// outlier only if it falls below the band.
	import { C, ENC_NAME, ENC_ROWS, F, FONT, MODEL_ROWS, MODEL_STYLE, f2 } from './hsg';
	import Marker from './Marker.svelte';

	type Run = { model: string; encoding: string; mean_auc: number };
	let {
		id,
		W,
		H,
		wIn,
		hIn,
		runs,
		xMin,
		xMax,
		bandNote,
		halfBand = 0.025
	}: { id: string; W: number; H: number; wIn: number; hIn: number; runs: Run[]; xMin: number; xMax: number; bandNote: string; halfBand?: number } =
		$props();

	const pad = { top: 30, right: 34, bottom: 50, left: 152 };
	const innerW = $derived(W - pad.left - pad.right);
	const innerH = $derived(H - pad.top - pad.bottom);
	const x = (v: number) => pad.left + ((v - xMin) / (xMax - xMin)) * innerW;
	const ticks = $derived(
		Array.from({ length: Math.round((xMax - xMin) / 0.05) + 1 }, (_, i) => +(xMin + i * 0.05).toFixed(2))
	);

	// layout: per group one header line + one line per model
	const lines = ENC_ROWS.length * (MODEL_ROWS.length + 1);
	const lineH = $derived(innerH / lines);
	const headY = (g: number) => pad.top + (g * (MODEL_ROWS.length + 1) + 0.5) * lineH;
	const rowY = (g: number, m: number) => pad.top + (g * (MODEL_ROWS.length + 1) + m + 1.5) * lineH;

	const get = (m: string, e: string) => runs.find((r) => r.model === m && r.encoding === e)!.mean_auc;
	const median = $derived.by(() => {
		const v = runs.map((r) => r.mean_auc).sort((a, b) => a - b);
		return v.length % 2 ? v[(v.length - 1) / 2] : (v[v.length / 2 - 1] + v[v.length / 2]) / 2;
	});
	const lowest = $derived(runs.reduce((a, b) => (b.mean_auc < a.mean_auc ? b : a)));
	const isOutlier = (r: Run) => r === lowest && r.mean_auc < median - halfBand;

	const bandL = $derived(x(Math.max(xMin, median - halfBand)));
	const bandR = $derived(x(Math.min(xMax, median + halfBand)));
	// band note: centred on the band unless that would run past the right edge
	const noteRightAligned = $derived((bandL + bandR) / 2 + bandNote.length * F.note * 0.27 > W - 4);
</script>

<svg {id} xmlns="http://www.w3.org/2000/svg" width="{wIn}in" height="{hIn}in" viewBox="0 0 {W} {H}" font-family={FONT} style="display:block;width:{wIn * 96}px;height:{hIn * 96}px">
	<rect width={W} height={H} fill={C.white} />

	<!-- noise band -->
	<rect x={bandL} y={pad.top - 6} width={bandR - bandL} height={innerH + 6} fill={C.light} />
	<text
		x={noteRightAligned ? W - 4 : (bandL + bandR) / 2}
		y={pad.top - 12}
		text-anchor={noteRightAligned ? 'end' : 'middle'}
		font-size={F.note}
		fill={C.dark}>{bandNote}</text
	>

	<!-- light horizontal gridlines, one per row -->
	{#each ENC_ROWS as e, g (e)}
		{#each MODEL_ROWS as m, i (m)}
			<line x1={pad.left} x2={pad.left + innerW} y1={rowY(g, i)} y2={rowY(g, i)} stroke={C.grid} stroke-width="0.75" />
		{/each}
	{/each}

	<!-- x axis -->
	<line x1={pad.left} x2={pad.left + innerW} y1={pad.top + innerH} y2={pad.top + innerH} stroke={C.grey} stroke-width="0.75" />
	{#each ticks as t (t)}
		<line x1={x(t)} x2={x(t)} y1={pad.top + innerH} y2={pad.top + innerH + 4} stroke={C.grey} stroke-width="0.75" />
		<text x={x(t)} y={pad.top + innerH + 6 + F.tick} text-anchor="middle" font-size={F.tick} fill={C.text}>{f2(t)}</text>
	{/each}
	<text x={pad.left + innerW / 2} y={H - 6} text-anchor="middle" font-size={F.axis} fill={C.text}>AUC</text>

	{#each ENC_ROWS as e, g (e)}
		{@const op = e === 'index' ? 0.6 : 1}
		<text x={6} y={headY(g)} dy="0.35em" font-size={F.direct} font-weight="bold" fill={C.dark}>{ENC_NAME[e]}</text>
		{#each MODEL_ROWS as m, i (m)}
			{@const run = runs.find((r) => r.model === m && r.encoding === e)!}
			{@const v = get(m, e)}
			{@const out = isOutlier(run)}
			{@const o = out ? 1 : op}
			{@const s = MODEL_STYLE[m]}
			<text x={18} y={rowY(g, i)} dy="0.35em" font-size={F.tick} fill={C.text}>{s.name}</text>
			<Marker kind={s.marker} cx={x(v)} cy={rowY(g, i)} color={s.color} r={6} opacity={o} />
			<text x={x(v) + 10} y={rowY(g, i)} dy="0.35em" font-size={F.direct} fill={C.text} font-weight={out ? 'bold' : 'normal'}>
				{f2(v)}{#if out}<tspan dx="8" fill={C.dark} font-weight="normal" font-size={F.note}>outlier (below noise band)</tspan>{/if}
			</text>
		{/each}
	{/each}
</svg>
