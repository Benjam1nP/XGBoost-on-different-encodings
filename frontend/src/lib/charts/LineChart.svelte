<script lang="ts" module>
	import type { MarkerKind } from './hsg';
	const pt2 = (2 * 96) / 72; // 2 pt default line width
	export interface Line {
		key: string;
		label: string;
		color: string;
		marker: MarkerKind;
		dash?: string;
		width?: number;
		values: Record<string, number>;
	}
	export interface Scales {
		x: (k: number) => number;
		y: (v: number) => number;
		pad: { top: number; right: number; bottom: number; left: number };
		innerW: number;
		innerH: number;
	}
</script>

<script lang="ts">
	// G2 / G4: AUC per prefix length. Direct labels at the line ends (spread apart), dotted
	// guessing line at 0.5 labelled in the same column, optional grey shading below 0.5.
	import type { Snippet } from 'svelte';
	import { C, F, FONT, f2, spread } from './hsg';
	import Marker from './Marker.svelte';

	let {
		id,
		W,
		H,
		wIn,
		hIn,
		lines,
		yMin,
		yMax,
		labelWidth = 190,
		shadeBelowGuess = false,
		extra
	}: {
		id: string;
		W: number;
		H: number;
		wIn: number;
		hIn: number;
		lines: Line[];
		yMin: number;
		yMax: number;
		labelWidth?: number;
		shadeBelowGuess?: boolean;
		extra?: Snippet<[Scales]>;
	} = $props();

	const pad = $derived({ top: 14, right: labelWidth, bottom: 50, left: 66 });
	const ks = $derived([...new Set(lines.flatMap((l) => Object.keys(l.values).map(Number)))].sort((a, b) => a - b));
	const innerW = $derived(W - pad.left - pad.right);
	const innerH = $derived(H - pad.top - pad.bottom);
	const x = (k: number) => pad.left + ((k - ks[0]) / (ks[ks.length - 1] - ks[0])) * innerW;
	const y = (v: number) => pad.top + (1 - (v - yMin) / (yMax - yMin)) * innerH;
	const yTicks = $derived.by(() => {
		const out: number[] = [];
		for (let t = Math.ceil(yMin * 10 - 1e-9) / 10; t <= yMax + 1e-9; t = +(t + 0.1).toFixed(2)) out.push(t);
		return out;
	});
	const path = (l: Line) => ks.map((k, i) => `${i ? 'L' : 'M'}${x(k)},${y(l.values[k])}`).join('');
	const last = $derived(ks[ks.length - 1]);

	const labels = $derived(
		spread(
			[
				...lines.map((l) => ({ key: l.key, text: l.label, value: l.values[last] as number | null, want: y(l.values[last]) })),
				{ key: '__guess', text: 'guessing (0.5)', value: null, want: y(0.5) }
			],
			F.direct + 3,
			pad.top + 6,
			pad.top + innerH
		)
	);
</script>

<svg {id} xmlns="http://www.w3.org/2000/svg" width="{wIn}in" height="{hIn}in" viewBox="0 0 {W} {H}" font-family={FONT} style="display:block;width:{W}px;height:{H}px">
	<rect width={W} height={H} fill={C.white} />

	{#if shadeBelowGuess}
		<rect x={pad.left} y={y(0.5)} width={innerW} height={y(yMin) - y(0.5)} fill={C.light} />
	{/if}

	{#each yTicks as t (t)}
		<line x1={pad.left} x2={pad.left + innerW} y1={y(t)} y2={y(t)} stroke={C.grid} stroke-width="0.75" />
		<text x={pad.left - 8} y={y(t)} dy="0.35em" text-anchor="end" font-size={F.tick} fill={C.text}>{f2(t)}</text>
	{/each}
	<line x1={pad.left} x2={pad.left} y1={pad.top} y2={pad.top + innerH} stroke={C.grey} stroke-width="0.75" />
	<line x1={pad.left} x2={pad.left + innerW} y1={pad.top + innerH} y2={pad.top + innerH} stroke={C.grey} stroke-width="0.75" />
	{#each ks as k (k)}
		<line x1={x(k)} x2={x(k)} y1={pad.top + innerH} y2={pad.top + innerH + 4} stroke={C.grey} stroke-width="0.75" />
		<text x={x(k)} y={pad.top + innerH + 6 + F.tick} text-anchor="middle" font-size={F.tick} fill={C.text}>{k}</text>
	{/each}
	<text x={pad.left + innerW / 2} y={H - 6} text-anchor="middle" font-size={F.axis} fill={C.text}>Prefix length k (events observed)</text>
	<text transform="translate({F.axis * 0.9} {pad.top + innerH / 2}) rotate(-90)" text-anchor="middle" font-size={F.axis} fill={C.text}>AUC</text>

	<!-- guessing -->
	<line x1={pad.left} x2={pad.left + innerW} y1={y(0.5)} y2={y(0.5)} stroke={C.grey} stroke-width="1.2" stroke-dasharray="1.5 3.5" stroke-linecap="round" />

	{@render extra?.({ x, y, pad, innerW, innerH })}

	<!-- draw the main (widest) line last so it sits on top -->
	{#each [...lines].sort((a, b) => (a.width ?? 2) - (b.width ?? 2)) as l (l.key)}
		<path d={path(l)} fill="none" stroke={l.color} stroke-width={l.width ?? pt2} stroke-dasharray={l.dash} stroke-linejoin="round" stroke-linecap="round" />
		{#each ks as k (k)}
			<Marker kind={l.marker} cx={x(k)} cy={y(l.values[k])} color={l.color} r={(l.width ?? pt2) > pt2 ? 5 : 4.2} />
		{/each}
	{/each}

	{#each labels as lb (lb.key)}
		{@const lx = pad.left + innerW}
		{#if lb.key !== '__guess'}
			<line x1={lx + 8} x2={lx + 16} y1={lb.want} y2={lb.at} stroke={C.grey} stroke-width="0.6" />
		{/if}
		<text x={lx + 20} y={lb.at} dy="0.35em" font-size={lb.key === '__guess' ? F.note : F.direct} fill={lb.key === '__guess' ? C.grey : C.text}>
			{lb.text}
		</text>
	{/each}
</svg>
