<script lang="ts">
	// Line chart of AUC per prefix length, one series per encoding.
	// Follows STYLE.md: main series 2px with an 8% area fill, reference dashed 1px muted,
	// gridlines in `border`, crosshair tooltip that lists every series.
	export interface Series {
		key: string;
		label: string;
		color: string;
		values: Record<string, number>;
		main?: boolean;
	}

	let {
		series,
		reference = 0.5,
		referenceLabel = 'Random guessing'
	}: { series: Series[]; reference?: number; referenceLabel?: string } = $props();

	let width = $state(640);
	const height = 300;
	const pad = { top: 12, right: 16, bottom: 48, left: 44 };

	const ks = $derived(
		[...new Set(series.flatMap((s) => Object.keys(s.values).map(Number)))].sort((a, b) => a - b)
	);
	const allValues = $derived(series.flatMap((s) => Object.values(s.values)));
	const yMin = $derived(Math.min(0.4, Math.floor((Math.min(...allValues) - 0.02) * 10) / 10));
	const yMax = 1;
	const yTicks = $derived(
		Array.from({ length: Math.round((yMax - yMin) * 10) + 1 }, (_, i) => +(yMin + i * 0.1).toFixed(1))
	);

	const innerW = $derived(Math.max(0, width - pad.left - pad.right));
	const innerH = height - pad.top - pad.bottom;
	const x = (k: number) =>
		pad.left + (ks.length < 2 ? innerW / 2 : ((k - ks[0]) / (ks[ks.length - 1] - ks[0])) * innerW);
	const y = (v: number) => pad.top + (1 - (v - yMin) / (yMax - yMin)) * innerH;

	const linePath = (s: Series) =>
		ks.map((k, i) => `${i ? 'L' : 'M'}${x(k).toFixed(1)},${y(s.values[k]).toFixed(1)}`).join('');
	const areaPath = (s: Series) =>
		`${linePath(s)}L${x(ks[ks.length - 1]).toFixed(1)},${y(yMin)}L${x(ks[0]).toFixed(1)},${y(yMin)}Z`;

	// draw the main series last so it sits on top
	const ordered = $derived([...series].sort((a, b) => Number(!!a.main) - Number(!!b.main)));

	let hover = $state<number | null>(null);
	function onMove(e: PointerEvent) {
		const rect = (e.currentTarget as SVGElement).getBoundingClientRect();
		const px = e.clientX - rect.left;
		let best = ks[0];
		for (const k of ks) if (Math.abs(x(k) - px) < Math.abs(x(best) - px)) best = k;
		hover = best;
	}
	const tooltipLeft = $derived(hover === null ? 0 : x(hover));
	const tooltipFlip = $derived(hover !== null && x(hover) > width - 200);
</script>

<div class="relative w-full" bind:clientWidth={width}>
	<svg
		{width}
		{height}
		role="img"
		aria-label="AUC per prefix length for each encoding"
		class="block touch-none overflow-visible select-none"
		onpointermove={onMove}
		onpointerleave={() => (hover = null)}
	>
		<!-- gridlines + y axis labels -->
		{#each yTicks as t (t)}
			<line x1={pad.left} x2={width - pad.right} y1={y(t)} y2={y(t)} class="stroke-border" stroke-width="1" />
			<text x={pad.left - 10} y={y(t)} dy="0.32em" text-anchor="end" class="fill-muted-foreground font-mono text-xs">
				{t.toFixed(1)}
			</text>
		{/each}

		<!-- x axis labels -->
		{#each ks as k (k)}
			<text x={x(k)} y={height - pad.bottom + 20} text-anchor="middle" class="fill-muted-foreground font-mono text-xs">
				{k}
			</text>
		{/each}

		<!-- reference -->
		<line
			x1={pad.left}
			x2={width - pad.right}
			y1={y(reference)}
			y2={y(reference)}
			class="stroke-benchmark"
			stroke-width="1"
			stroke-dasharray="4 4"
		/>
		<text x={width - pad.right} y={y(reference) - 6} text-anchor="end" class="fill-muted-foreground text-xs">
			{referenceLabel}
		</text>

		<!-- area under the main series only -->
		{#each series.filter((s) => s.main) as s (s.key)}
			<path d={areaPath(s)} fill={s.color} fill-opacity="0.08" />
		{/each}

		{#each ordered as s (s.key)}
			<path
				d={linePath(s)}
				fill="none"
				stroke={s.color}
				stroke-width={s.main ? 2 : 1.5}
				stroke-linejoin="round"
				stroke-linecap="round"
			/>
			{#each ks as k (k)}
				<circle cx={x(k)} cy={y(s.values[k])} r={hover === k ? 4 : 2.5} fill={s.color} class="stroke-card" stroke-width="1.5" />
			{/each}
		{/each}

		<!-- crosshair -->
		{#if hover !== null}
			<line x1={x(hover)} x2={x(hover)} y1={pad.top} y2={pad.top + innerH} class="stroke-muted-foreground" stroke-width="1" stroke-opacity="0.5" />
		{/if}

		<text x={pad.left + innerW / 2} y={height - 2} text-anchor="middle" class="fill-muted-foreground text-xs">
			Prefix length (events observed so far)
		</text>
	</svg>

	{#if hover !== null}
		<div
			class="pointer-events-none absolute top-2 z-10 flex min-w-44 animate-in flex-col gap-1.5 rounded-lg border bg-popover px-3 py-2 text-sm duration-200 fade-in"
			style:left="{tooltipFlip ? tooltipLeft - 12 : tooltipLeft + 12}px"
			style:transform={tooltipFlip ? 'translateX(-100%)' : undefined}
		>
			<p class="text-label">Prefix length {hover}</p>
			{#each [...series].sort((a, b) => b.values[hover!] - a.values[hover!]) as s (s.key)}
				<div class="flex items-center gap-2">
					<span class="size-2.5 shrink-0 rounded-[2px]" style:background={s.color}></span>
					<span class="text-muted-foreground">{s.label}</span>
					<span class="ml-auto pl-4 text-figure">{s.values[hover!].toFixed(3)}</span>
				</div>
			{/each}
		</div>
	{/if}
</div>
