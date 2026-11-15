<script lang="ts">
	// Seminar figures. Every <Figure id="..."> is captured by screenshots.py as screenshots/<id>.png.
	// Numbers come from src/lib/slides.json (python slides.py).
	import data from '#lib/slides.json';
	import Figure from '#lib/slides/Figure.svelte';
	import Legend from '#lib/slides/Legend.svelte';
	import LineChart, { type LineSeries } from '#lib/slides/LineChart.svelte';
	import DotPlot from '#lib/slides/DotPlot.svelte';
	import { ENCODING_NAME, MODEL, MODEL_ORDER, VARIANT } from '#lib/slides/theme.js';

	const sep = data.sepsis;
	const bpic = data.bpic2011;
	const caseA = sep.case;
	const icu = caseA.label === 1 ? 'yes' : 'no';
	const prefix4 = caseA.events.slice(0, 4);

	const modelLegend = MODEL_ORDER.map((m) => ({ label: MODEL[m].name, color: MODEL[m].color, marker: 'circle' }));

	const SHORT: Record<string, string> = {
		all: 'All',
		no_symptoms: 'No symptoms',
		age_diagnostic: 'Age + diagnostic*',
		age: 'Only Age',
		none: 'None'
	};
	const lineSeries = (rows: { variant: string; auc: Record<string, number | null> }[]): LineSeries[] =>
		rows.map((r) => ({
			key: r.variant,
			short: SHORT[r.variant],
			color: VARIANT[r.variant].color,
			dash: VARIANT[r.variant].dash,
			marker: VARIANT[r.variant].marker,
			values: r.auc as Record<string, number>
		}));
	const variantLegend = (rows: { variant: string }[]) =>
		rows.map((r) => ({ label: VARIANT[r.variant].name, ...VARIANT[r.variant] }));

	const fmt = (v: number | null | undefined, d = 1) => (v === null || v === undefined ? '–' : (+v.toFixed(d)).toString());
	const fmtVal = (v: number | null) => (v === null ? '–' : Number.isInteger(v) ? String(v) : (+v.toFixed(2)).toString());

	const ENC_TEXT: Record<string, string> = {
		last_state: 'Only the latest event: its activity and resource (one-hot) and the last observed lab values.',
		aggregation: 'Counts of every activity and resource plus mean and max of each lab value. Order is lost.',
		index: 'Activity and resource at every position 1…4 (one-hot). Lossless, so one model per prefix length.'
	};
	const encFigs = (['last_state', 'aggregation', 'index'] as const).map((e) => ({ e, ...sep.encoded[e] }));
	const COMMON = new Set(['elapsed_h', 'prefix_len']);

	const imp = sep.importance;
	const impMax = Math.max(...imp.map((d) => d.importance));
</script>

<svelte:head><title>Slide figures</title></svelte:head>

<main class="slides">
	<h1>Slide figures</h1>
	<p class="intro">
		Each panel is 1600 × 900 and is saved by <code>python screenshots.py</code> under the file name shown above it.
	</p>

	<!-- 1 ------------------------------------------------------------------------------------- -->
	<Figure id="sepsis_case_A" title="Sepsis case A: the running case" subtitle="First 8 events after cutting before “Admission IC”">
		<div class="case-head">
			<span>Case <b>{caseA.case_id}</b> · {caseA.n_events_after_cut} events after cutting</span>
			<span class="label-pill" class:pos={caseA.label === 1}>Label: ICU = <b>{icu}</b></span>
		</div>
		<table class="tbl">
			<thead>
				<tr>
					<th class="num">#</th><th>Activity</th><th>Resource</th><th>Timestamp</th>
					<th class="num">CRP</th><th class="num">Leucocytes</th><th class="num">Lactic acid</th>
				</tr>
			</thead>
			<tbody>
				{#each caseA.events as ev (ev.pos)}
					<tr>
						<td class="num muted">{ev.pos}</td>
						<td>{ev.activity}</td>
						<td>{ev.resource}</td>
						<td class="mono">{ev.timestamp}</td>
						<td class="num">{fmt(ev.crp)}</td>
						<td class="num">{fmt(ev.leucocytes)}</td>
						<td class="num">{fmt(ev.lacticacid)}</td>
					</tr>
				{/each}
			</tbody>
		</table>
		<p class="note">– = not measured in this event</p>
	</Figure>

	<!-- 2 ------------------------------------------------------------------------------------- -->
	<Figure id="sepsis_prefixes_A" title="One case, many prefixes" subtitle="Case A cut after 1, 2, 3 and 4 events. Every prefix gets the label of the full case">
		<div class="stairs">
			<div class="stairs-row head">
				<span class="pk">Prefix</span>
				<span>Activities observed so far</span>
				<span class="pl">Label</span>
			</div>
			{#each [1, 2, 3, 4] as k (k)}
				<div class="stairs-row">
					<span class="pk mono">k = {k}</span>
					<div class="chips">
						{#each caseA.events.slice(0, k) as ev, i (i)}
							<span class="chip" class:new={i === k - 1}>{ev.activity}</span>
						{/each}
					</div>
					<span class="pl"><span class="label-pill" class:pos={caseA.label === 1}>ICU = <b>{icu}</b></span></span>
				</div>
			{/each}
		</div>
		<p class="note">Outlined = event added in this prefix. One training example per prefix length.</p>
	</Figure>

	<!-- 3 ------------------------------------------------------------------------------------- -->
	{#each encFigs as f (f.e)}
		<Figure
			id="encoding_{f.e}"
			title="{ENCODING_NAME[f.e]} encoding"
			subtitle="Case A after 4 events (ER Registration, Leucocytes, CRP, LacticAcid). Non-zero features only"
		>
			<div class="enc">
				<div class="enc-main">
					<p class="enc-text">{ENC_TEXT[f.e]}</p>
					<table class="tbl compact">
						<thead><tr><th>Feature</th><th class="num">Value</th></tr></thead>
						<tbody>
							{#each f.features.filter((x) => !COMMON.has(x.feature)) as x (x.feature)}
								<tr><td class="mono">{x.feature}</td><td class="num">{fmtVal(x.value)}</td></tr>
							{/each}
						</tbody>
					</table>
				</div>
				<aside class="enc-side">
					<p class="side-title">Added to every vector</p>
					<table class="tbl compact">
						<tbody>
							{#each f.features.filter((x) => COMMON.has(x.feature)) as x (x.feature)}
								<tr><td class="mono">{x.feature}</td><td class="num">{fmtVal(x.value)}</td></tr>
							{/each}
						</tbody>
					</table>
					<p class="side-title">Initial data ({f.initial.length} non-zero)</p>
					<p class="init-list mono">
						{f.initial.map((x) => (x.value === 1 ? x.feature : `${x.feature} = ${fmtVal(x.value)}`)).join(' · ')}
					</p>
					<p class="note">Vector length in total: {f.n_columns} columns (zeros omitted)</p>
				</aside>
			</div>
		</Figure>
	{/each}

	<!-- 4 ------------------------------------------------------------------------------------- -->
	<Figure id="sepsis_models_encodings" title="Sepsis: models × encodings" subtitle="Mean AUC over prefix lengths 1–8, all initial data, temporal 80/20 split">
		<Legend items={modelLegend} />
		<DotPlot runs={sep.models} xMax={0.85} />
	</Figure>

	<!-- 5 ------------------------------------------------------------------------------------- -->
	<Figure id="sepsis_initial_data" title="Sepsis: how much do the initial data carry?" subtitle="Random forest, last-state encoding, AUC per prefix length">
		<Legend items={variantLegend(sep.initial)} />
		<LineChart series={lineSeries(sep.initial)} yMin={0.4} yMax={0.9} height={640} />
	</Figure>

	<!-- 6 ------------------------------------------------------------------------------------- -->
	<Figure id="bpic2011_models_encodings" title="BPIC 2011: models × encodings" subtitle="Mean AUC over prefix lengths 1–10, all initial data, temporal 80/20 split">
		<Legend items={modelLegend} />
		<DotPlot runs={bpic.models} xMax={0.95} />
	</Figure>

	<!-- 7 ------------------------------------------------------------------------------------- -->
	<Figure id="bpic2011_initial_data" title="BPIC 2011: how much do the initial data carry?" subtitle="Random forest, last-state encoding, AUC per prefix length">
		<Legend items={variantLegend(bpic.initial)} />
		<LineChart series={lineSeries(bpic.initial)} yMin={0.4} yMax={1.0} height={680} />
	</Figure>

	<!-- 8 (backup) ---------------------------------------------------------------------------- -->
	<Figure id="sepsis_test_counts" title="Sepsis: size of the test set" subtitle="Test cases (last 20 % by start time) that reach each prefix length">
		<table class="tbl counts">
			<thead>
				<tr><th class="num">Prefix length</th><th class="num">Test cases</th><th class="num">ICU cases</th><th class="num">ICU share</th></tr>
			</thead>
			<tbody>
				{#each sep.test_counts as r (r.k)}
					<tr>
						<td class="num">{r.k}</td>
						<td class="num">{r.cases}</td>
						<td class="num">{r.positives}</td>
						<td class="num muted">{((100 * r.positives) / r.cases).toFixed(1)} %</td>
					</tr>
				{/each}
			</tbody>
		</table>
		<p class="note">About 20 ICU cases per prefix length: AUC differences below ~0.05 are within noise.</p>
	</Figure>

	<!-- 9 (backup) ---------------------------------------------------------------------------- -->
	<Figure id="sepsis_feature_importance" title="Sepsis: what XGBoost relies on" subtitle="Top 10 features by gain, aggregation encoding, all initial data, mean over 3 seeds">
		<Legend items={[{ label: 'XGBoost', color: MODEL.xgboost.color, marker: 'square' }]} />
		<div class="bars">
			{#each imp as d (d.feature)}
				<span class="bar-name mono">{d.feature}</span>
				<span class="bar-track">
					<span class="bar" style:width="{(d.importance / impMax) * 100}%"></span>
					<span class="bar-val mono">{(100 * d.importance).toFixed(1)} %</span>
				</span>
			{/each}
			<span></span>
			<span class="bar-axis">Share of total gain (all features = 100 %)</span>
		</div>
	</Figure>
</main>

<style>
	.slides {
		background: #f2f2ef;
		min-height: 100dvh;
		padding: 32px;
		display: flex;
		flex-direction: column;
		gap: 40px;
		width: max-content;
	}
	.slides > h1 {
		font-size: 28px;
		font-weight: 700;
	}
	.intro {
		margin-top: -32px;
		color: #52514e;
	}
	.mono {
		font-family: 'Geist Mono', monospace;
	}
	.muted {
		color: #52514e;
	}
	.note {
		margin-top: auto;
		font-size: 24px;
		color: #52514e;
	}

	/* tables */
	.tbl {
		border-collapse: collapse;
		font-size: 28px;
		width: 100%;
	}
	.tbl th {
		text-align: left;
		font-size: 22px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #52514e;
		padding: 10px 18px;
		border-bottom: 2px solid #0b0b0b;
	}
	.tbl td {
		padding: 11px 18px;
		border-bottom: 1px solid #e4e3df;
	}
	.tbl .num {
		text-align: right;
		font-family: 'Geist Mono', monospace;
		font-variant-numeric: tabular-nums;
	}
	.tbl th.num {
		font-family: inherit;
	}
	.tbl.compact {
		font-size: 25px;
	}
	.tbl.compact td {
		padding: 7px 16px;
	}
	.counts {
		width: 900px;
		font-size: 30px;
	}
	.counts td {
		padding: 10px 24px;
	}

	.case-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 28px;
		margin-bottom: 12px;
	}
	.label-pill {
		display: inline-block;
		font-size: 26px;
		padding: 6px 16px;
		border-radius: 8px;
		border: 2px solid #0b0b0b;
		background: #ffffff;
		white-space: nowrap;
	}
	.label-pill.pos {
		background: #0b0b0b;
		color: #ffffff;
	}

	/* staircase */
	.stairs {
		display: flex;
		flex-direction: column;
		gap: 22px;
		margin-top: 16px;
	}
	.stairs-row {
		display: grid;
		grid-template-columns: 130px 1fr 200px;
		align-items: center;
		gap: 24px;
		font-size: 26px;
	}
	.stairs-row.head {
		font-size: 22px;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #52514e;
		border-bottom: 2px solid #0b0b0b;
		padding-bottom: 8px;
	}
	.pl {
		text-align: right;
	}
	.chips {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 12px;
	}
	.chip {
		font-size: 26px;
		padding: 18px 12px;
		text-align: center;
		border-radius: 8px;
		background: #e8eef3;
		border: 3px solid transparent;
		white-space: nowrap;
	}
	.chip.new {
		background: #ffffff;
		border-color: #2a78d6;
		font-weight: 600;
	}

	/* encodings */
	.enc {
		display: grid;
		grid-template-columns: 1fr 560px;
		gap: 48px;
		min-height: 0;
		flex: 1;
	}
	.enc-main {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}
	.enc-text {
		font-size: 26px;
		line-height: 1.4;
		color: #0b0b0b;
	}
	.enc-side {
		display: flex;
		flex-direction: column;
		gap: 10px;
		background: #f7f7f5;
		border-radius: 8px;
		padding: 20px 24px;
	}
	.side-title {
		font-size: 22px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #52514e;
		margin-top: 8px;
	}
	.init-list {
		font-size: 20px;
		line-height: 1.5;
		color: #0b0b0b;
	}
	.enc-side .note {
		font-size: 20px;
	}

	/* importance bars */
	.bars {
		display: grid;
		grid-template-columns: 420px 1fr;
		gap: 14px 24px;
		align-items: center;
		margin-top: 24px;
	}
	.bar-name {
		font-size: 25px;
		text-align: right;
	}
	.bar-track {
		display: flex;
		align-items: center;
		gap: 14px;
		height: 38px;
	}
	.bar {
		height: 100%;
		background: #1baf7a;
		border-radius: 0 4px 4px 0;
		max-width: calc(100% - 130px);
	}
	.bar-val {
		font-size: 24px;
	}
	.bar-axis {
		font-size: 24px;
		color: #52514e;
		border-top: 2px solid #0b0b0b;
		padding-top: 8px;
	}
</style>
