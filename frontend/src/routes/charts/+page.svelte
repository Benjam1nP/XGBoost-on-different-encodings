<script lang="ts">
	// Slide charts G1–G7 (HSG template). Every <svg id="G…"> is exported by make_charts.py as
	// SVG + 300 dpi PNG at the placeholder size. All numbers and annotations come from the JSON files.
	import data from '#lib/slides.json';
	import extra from '#lib/charts_extra.json';
	import DotPlot from '#lib/charts/DotPlot.svelte';
	import LineChart, { type Line } from '#lib/charts/LineChart.svelte';
	import { C, F, FONT, f2, inch, spread } from '#lib/charts/hsg.js';

	const sep = data.sepsis;
	const bpic = data.bpic2011;
	const big = inch(7.9, 4.4);
	const small = inch(6.0, 3.6);
	// G3 uses G1's layout (same canvas height, so same row spacing and proportions) scaled into 6 x 3.6 in
	const g3Size = { ...small, W: big.H * (small.wIn / small.hIn), H: big.H };
	const mean = (xs: number[]) => xs.reduce((a, b) => a + b, 0) / xs.length;
	const auc = (rows: { variant: string; auc: Record<string, number | null> }[], v: string) =>
		rows.find((r) => r.variant === v)!.auc as Record<string, number>;

	// ---- noise-band notes: average positives per k in the test set
	const sepPos = Math.round(mean(sep.test_counts.map((r) => r.positives)));
	const bpicPos = Math.round(mean(extra.bpic_test_counts.map((r) => r.positives)));

	// ---- G2
	const g2: Line[] = [
		{ key: 'all', label: 'All registration data', color: C.green, marker: 'circle', width: 4, values: auc(sep.initial, 'all') },
		{ key: 'no_symptoms', label: 'Without symptom flags', color: C.teal, marker: 'square', values: auc(sep.initial, 'no_symptoms') },
		{ key: 'age_diagnostic', label: 'Only age + diagnostics', color: C.sand, marker: 'diamond', values: auc(sep.initial, 'age_diagnostic') },
		{ key: 'none', label: 'No registration data', color: C.grey, marker: 'triangle', dash: '6 4', values: auc(sep.initial, 'none') }
	];
	const sAll = g2[0].values;
	const sNone = g2[3].values;
	const sKs = Object.keys(sNone).map(Number);
	const peakK = sKs.reduce((a, b) => (sNone[b] > sNone[a] ? b : a));
	const peakNeighbours = Math.min(...[peakK - 1, peakK + 1].filter((k) => k in sNone).map((k) => sNone[k]));

	// ---- G4
	const g4: Line[] = [
		{ key: 'all', label: 'All initial data', color: C.green, marker: 'circle', width: 4, values: auc(bpic.initial, 'all') },
		{ key: 'age', label: 'Only age', color: C.sand, marker: 'diamond', values: auc(bpic.initial, 'age') },
		{ key: 'none', label: 'No initial data', color: C.grey, marker: 'triangle', dash: '6 4', values: auc(bpic.initial, 'none') }
	];
	const bNone = g4[2].values;
	const firstBelow = Object.keys(bNone).map(Number).sort((a, b) => a - b).find((k) => bNone[k] < 0.5);

	// ---- shared helpers for the bar charts
	function niceTicks(max: number, n = 5) {
		const raw = max / n;
		const mag = 10 ** Math.floor(Math.log10(raw));
		const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw)!;
		const top = Math.ceil(max / step) * step;
		return Array.from({ length: Math.round(top / step) + 1 }, (_, i) => i * step);
	}
	const thousands = (v: number) => v.toLocaleString('en-US');

	// ---- G5
	const g5 = (() => {
		const { W, H } = big;
		const pad = { top: 18, right: 150, bottom: 50, left: 64 };
		const innerW = W - pad.left - pad.right;
		const innerH = H - pad.top - pad.bottom;
		const rows = sep.test_counts;
		const ref = mean(extra.bpic_test_counts.map((r) => r.positives));
		const ticks = niceTicks(Math.max(...rows.map((r) => r.cases), ref) * 1.05);
		const yMax = ticks[ticks.length - 1];
		const band = innerW / rows.length;
		const bw = band * 0.62;
		const x = (i: number) => pad.left + i * band + (band - bw) / 2;
		const y = (v: number) => pad.top + innerH * (1 - v / yMax);
		return { pad, innerW, innerH, rows, ref, ticks, band, bw, x, y, last: rows[rows.length - 1] };
	})();

	// ---- G6
	const ENC6 = [
		{ key: 'last_state', name: 'last state', color: C.green },
		{ key: 'aggregation', name: 'aggregation', color: C.teal },
		{ key: 'index', name: 'index', color: C.grey }
	] as const;
	const g6 = (() => {
		const { W, H } = big;
		const panelW = W / 2;
		const pad = { top: 34, right: 116, bottom: 50, left: 72 };
		const innerW = panelW - pad.left - pad.right;
		const innerH = H - pad.top - pad.bottom;
		const rows = extra.index_overfit;
		const panels = (['columns', 'train_cases'] as const).map((field, p) => {
			const vals = rows.flatMap((r) => ENC6.map((e) => r[field][e.key]));
			const ticks = niceTicks(Math.max(...vals) * 1.02, 4);
			const yMax = ticks[ticks.length - 1];
			const ox = p * panelW;
			const band = innerW / rows.length;
			const bw = (band * 0.8) / ENC6.length;
			const x = (i: number, j: number) => ox + pad.left + i * band + band * 0.1 + j * bw;
			const y = (v: number) => pad.top + innerH * (1 - v / yMax);
			const lastRow = rows[rows.length - 1];
			const labels = spread(
				ENC6.map((e, j) => ({ ...e, j, value: lastRow[field][e.key], want: y(lastRow[field][e.key]) })),
				F.direct + 2,
				pad.top + 4,
				pad.top + innerH - 4
			);
			return { field, ticks, ox, band, bw, x, y, labels, axis: field === 'columns' ? 'Feature columns per vector' : 'Training cases per model' };
		});
		return { pad, innerW, innerH, rows, panels };
	})();

	// ---- G7
	const reg = new Set(extra.registration_features);
	const g7 = (() => {
		const { W, H } = big;
		const rows = sep.importance.map((d) => ({ ...d, registration: reg.has(d.feature) }));
		const top = 12;
		const rowH = (H - top - 12) / rows.length;
		const tagW = 96;
		const barL = 308;
		const barMaxW = W - barL - 72;
		const max = Math.max(...rows.map((r) => r.importance));
		return { rows, top, rowH, tagW, barL, barMaxW, max };
	})();
</script>

<svelte:head><title>Slide charts</title></svelte:head>

<main class="charts">
	<h1>Slide charts (HSG)</h1>
	<p>Exported by <code>python make_charts.py</code> to <code>Demo/charts/</code> as SVG and 300 dpi PNG.</p>

	<!-- G1 ---------------------------------------------------------------------------------- -->
	<section>
		<p class="name">G1_sepsis_models_encodings · Results: Sepsis I · 7.9 × 4.4 in</p>
		<DotPlot id="G1_sepsis_models_encodings" {...big} runs={sep.models} xMin={0.7} xMax={0.85}
			bandNote="within noise (~{sepPos} ICU test patients per k)" />
	</section>

	<!-- G2 ---------------------------------------------------------------------------------- -->
	<section>
		<p class="name">G2_sepsis_registration_removed · Results: Sepsis II · 7.9 × 4.4 in</p>
		<LineChart id="G2_sepsis_registration_removed" {...big} lines={g2} yMin={0.4} yMax={0.9} labelWidth={200}>
			{#snippet extra({ x, y })}
				{@const ty = y((peakNeighbours + 0.5) / 2)}
				<!-- gap at the first event -->
				<circle cx={x(1)} cy={y(sAll[1])} r="9" fill="none" stroke={C.dark} stroke-width="1.2" />
				<circle cx={x(1)} cy={y(sNone[1])} r="9" fill="none" stroke={C.dark} stroke-width="1.2" />
				<text x={x(1) + 12} y={y(Math.min(sNone[1], 0.5)) + 24} font-size={F.note} fill={C.dark}>
					{f2(sAll[1])} vs {f2(sNone[1])} at the first event
				</text>
				<!-- peak of "none" -->
				<line x1={x(peakK)} x2={x(peakK)} y1={y(sNone[peakK]) + 8} y2={ty - F.note + 2} stroke={C.dark} stroke-width="0.75" />
				<text x={x(peakK)} y={ty} text-anchor="middle" font-size={F.note} fill={C.dark}>peak {f2(sNone[peakK])} at k = {peakK}</text>
			{/snippet}
		</LineChart>
	</section>

	<!-- G3 ---------------------------------------------------------------------------------- -->
	<section>
		<p class="name">G3_bpic2011_models_encodings · Results: BPIC 2011 (left) · 6.0 × 3.6 in</p>
		<DotPlot id="G3_bpic2011_models_encodings" {...g3Size} runs={bpic.models} xMin={0.7} xMax={0.95}
			bandNote="within noise (~{bpicPos} deviant test cases per k)" />
	</section>

	<!-- G4 ---------------------------------------------------------------------------------- -->
	<section>
		<p class="name">G4_bpic2011_initial_removed · Results: BPIC 2011 (right) · 6.0 × 3.6 in</p>
		<LineChart id="G4_bpic2011_initial_removed" {...small} lines={g4} yMin={0.35} yMax={0.95} labelWidth={150} shadeBelowGuess>
			{#snippet extra({ x, y })}
				{#if firstBelow !== undefined}
					<line x1={x(firstBelow)} x2={x(firstBelow)} y1={y(bNone[firstBelow]) + 7} y2={y(0.35) - F.note - 2} stroke={C.dark} stroke-width="0.75" />
					<text x={x(firstBelow) - 4} y={y(0.35) - 6} font-size={F.note} fill={C.dark}>below guessing from k = {firstBelow}</text>
				{/if}
			{/snippet}
		</LineChart>
	</section>

	<!-- G5 ---------------------------------------------------------------------------------- -->
	<section>
		<p class="name">G5_backup_test_counts · Backup: reliability · 7.9 × 4.4 in</p>
		<svg id="G5_backup_test_counts" xmlns="http://www.w3.org/2000/svg" width="{big.wIn}in" height="{big.hIn}in"
			viewBox="0 0 {big.W} {big.H}" font-family={FONT} style="display:block;width:{big.W}px;height:{big.H}px">
			<rect width={big.W} height={big.H} fill={C.white} />
			{#each g5.ticks as t (t)}
				<line x1={g5.pad.left} x2={g5.pad.left + g5.innerW} y1={g5.y(t)} y2={g5.y(t)} stroke={C.grid} stroke-width="0.75" />
				<text x={g5.pad.left - 8} y={g5.y(t)} dy="0.35em" text-anchor="end" font-size={F.tick} fill={C.text}>{t}</text>
			{/each}
			<line x1={g5.pad.left} x2={g5.pad.left} y1={g5.pad.top} y2={g5.pad.top + g5.innerH} stroke={C.grey} stroke-width="0.75" />
			<text transform="translate({F.axis} {g5.pad.top + g5.innerH / 2}) rotate(-90)" text-anchor="middle" font-size={F.axis} fill={C.text}>Sepsis test cases</text>
			<text x={g5.pad.left + g5.innerW / 2} y={big.H - 6} text-anchor="middle" font-size={F.axis} fill={C.text}>Prefix length k (events observed)</text>

			{#each g5.rows as r, i (r.k)}
				<rect x={g5.x(i)} y={g5.y(r.cases)} width={g5.bw} height={g5.y(0) - g5.y(r.cases)} fill={C.light} />
				<rect x={g5.x(i)} y={g5.y(r.positives)} width={g5.bw} height={g5.y(0) - g5.y(r.positives)} fill={C.green} />
				<text x={g5.x(i) + g5.bw / 2} y={g5.y(r.cases) - 6} text-anchor="middle" font-size={F.direct} fill={C.grey}>{r.cases}</text>
				<text x={g5.x(i) + g5.bw / 2} y={g5.y(r.positives) + F.direct} text-anchor="middle" font-size={F.direct} fill={C.white} font-weight="bold">{r.positives}</text>
				<text x={g5.x(i) + g5.bw / 2} y={g5.y(0) + 6 + F.tick} text-anchor="middle" font-size={F.tick} fill={C.text}>{r.k}</text>
			{/each}
			<line x1={g5.pad.left} x2={g5.pad.left + g5.innerW} y1={g5.y(0)} y2={g5.y(0)} stroke={C.grey} stroke-width="0.75" />

			<!-- BPIC 2011 reference -->
			<line x1={g5.pad.left} x2={g5.pad.left + g5.innerW + 8} y1={g5.y(g5.ref)} y2={g5.y(g5.ref)} stroke={C.grey} stroke-width="1.2" stroke-dasharray="6 4" />
			<text x={g5.pad.left + g5.innerW + 12} y={g5.y(g5.ref)} dy="0.35em" font-size={F.note} fill={C.dark}>
				<tspan>BPIC 2011 ≈ {Math.round(g5.ref)}</tspan>
				<tspan x={g5.pad.left + g5.innerW + 12} dy="1.2em">positives per k</tspan>
			</text>

			<!-- direct series labels at the last bar -->
			<text x={g5.pad.left + g5.innerW + 12} y={g5.y(g5.last.cases)} dy="0.35em" font-size={F.direct} fill={C.grey}>all test cases</text>
			<text x={g5.pad.left + g5.innerW + 12} y={g5.y(g5.last.positives / 2)} dy="0.35em" font-size={F.direct} fill={C.green}>ICU (positive)</text>
		</svg>
	</section>

	<!-- G6 ---------------------------------------------------------------------------------- -->
	<section>
		<p class="name">G6_backup_index_encoding · Backup: index encoding · 7.9 × 4.4 in</p>
		<svg id="G6_backup_index_encoding" xmlns="http://www.w3.org/2000/svg" width="{big.wIn}in" height="{big.hIn}in"
			viewBox="0 0 {big.W} {big.H}" font-family={FONT} style="display:block;width:{big.W}px;height:{big.H}px">
			<rect width={big.W} height={big.H} fill={C.white} />
			<text x={big.W / 2} y={F.note + 2} text-anchor="middle" font-size={F.note} font-weight="bold" fill={C.dark}>
				index: most columns, fewest cases per model
			</text>
			{#each g6.panels as P (P.field)}
				{#each P.ticks as t (t)}
					<line x1={P.ox + g6.pad.left} x2={P.ox + g6.pad.left + g6.innerW} y1={P.y(t)} y2={P.y(t)} stroke={C.grid} stroke-width="0.75" />
					<text x={P.ox + g6.pad.left - 6} y={P.y(t)} dy="0.35em" text-anchor="end" font-size={F.tick} fill={C.text}>{thousands(t)}</text>
				{/each}
				<text transform="translate({P.ox + F.axis * 0.85} {g6.pad.top + g6.innerH / 2}) rotate(-90)" text-anchor="middle" font-size={F.axis} fill={C.text}>{P.axis}</text>
				{#each g6.rows as r, i (r.k)}
					{#each ENC6 as e, j (e.key)}
						<rect x={P.x(i, j)} y={P.y(r[P.field][e.key])} width={P.bw - 0.8} height={P.y(0) - P.y(r[P.field][e.key])} fill={e.color} />
					{/each}
					<text x={P.x(i, 0) + (P.bw * ENC6.length) / 2} y={P.y(0) + 6 + F.tick} text-anchor="middle" font-size={F.tick} fill={C.text}>{r.k}</text>
				{/each}
				<line x1={P.ox + g6.pad.left} x2={P.ox + g6.pad.left + g6.innerW} y1={P.y(0)} y2={P.y(0)} stroke={C.grey} stroke-width="0.75" />
				<!-- direct labels at the k = max group -->
				{#each P.labels as l (l.key)}
					{@const lx = P.ox + g6.pad.left + g6.innerW}
					{@const bx = P.x(g6.rows.length - 1, l.j) + P.bw / 2}
					<line x1={bx} x2={lx + 6} y1={l.want} y2={l.at} stroke={C.grey} stroke-width="0.6" />
					<text x={lx + 9} y={l.at} dy="0.35em" font-size={F.direct} fill={C.text}>
						{l.name}
					</text>
				{/each}
			{/each}
			<text x={big.W / 2} y={big.H - 6} text-anchor="middle" font-size={F.axis} fill={C.text}>
				Prefix length k (events observed) · Sepsis, no initial data
			</text>
		</svg>
	</section>

	<!-- G7 ---------------------------------------------------------------------------------- -->
	<section>
		<p class="name">G7_backup_feature_importance · Backup: feature importance · 7.9 × 4.4 in</p>
		<svg id="G7_backup_feature_importance" xmlns="http://www.w3.org/2000/svg" width="{big.wIn}in" height="{big.hIn}in"
			viewBox="0 0 {big.W} {big.H}" font-family={FONT} style="display:block;width:{big.W}px;height:{big.H}px">
			<rect width={big.W} height={big.H} fill={C.white} />
			{#each g7.rows as r, i (r.feature)}
				{@const cy = g7.top + (i + 0.5) * g7.rowH}
				{@const bh = g7.rowH * 0.64}
				{@const tagX = g7.barL - 10 - g7.tagW}
				<text x={tagX - 10} y={cy} dy="0.35em" text-anchor="end" font-size={F.direct} fill={C.text}>{r.feature}</text>
				<rect x={tagX} y={cy - 11} width={g7.tagW} height="22" rx="4" fill={r.registration ? C.lightGreen : C.light} />
				<text x={tagX + g7.tagW / 2} y={cy} dy="0.35em" text-anchor="middle" font-size={F.note} fill={r.registration ? C.dark : C.grey}>
					{r.registration ? 'registration' : 'event'}
				</text>
				<rect x={g7.barL} y={cy - bh / 2} width={(r.importance / g7.max) * g7.barMaxW} height={bh} fill={r.registration ? C.green : C.grey} />
				<text x={g7.barL + (r.importance / g7.max) * g7.barMaxW + 6} y={cy} dy="0.35em" font-size={F.direct} fill={C.text}>
					{(100 * r.importance).toFixed(1)}%
				</text>
			{/each}
			<line x1={g7.barL} x2={g7.barL} y1={g7.top} y2={big.H - 12} stroke={C.grey} stroke-width="0.75" />
		</svg>
	</section>
</main>

<style>
	.charts {
		padding: 24px;
		display: flex;
		flex-direction: column;
		gap: 28px;
		background: #f4f4f2;
		min-height: 100dvh;
		width: max-content;
	}
	h1 {
		font-size: 22px;
		font-weight: 700;
	}
	.charts > p {
		margin-top: -20px;
		color: #555;
	}
	.name {
		font-family: var(--font-mono);
		font-size: 13px;
		color: #555;
		margin-bottom: 6px;
	}
	section :global(svg) {
		outline: 1px solid #ddd;
	}
</style>
