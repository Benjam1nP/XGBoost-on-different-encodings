<svelte:options namespace="svg" />

<script lang="ts">
	import { C, type MarkerKind } from './hsg';
	let {
		kind,
		cx,
		cy,
		color,
		r = 5,
		opacity = 1
	}: { kind: MarkerKind; cx: number; cy: number; color: string; r?: number; opacity?: number } = $props();
</script>

{#if kind === 'square'}
	<rect x={cx - r * 0.9} y={cy - r * 0.9} width={r * 1.8} height={r * 1.8} fill={color} stroke={C.white} stroke-width="1.2" {opacity} />
{:else if kind === 'triangle'}
	<path d="M{cx} {cy - r * 1.15} L{cx + r * 1.1} {cy + r * 0.85} L{cx - r * 1.1} {cy + r * 0.85} Z" fill={color} stroke={C.white} stroke-width="1.2" {opacity} />
{:else if kind === 'diamond'}
	<path d="M{cx} {cy - r * 1.25} L{cx + r * 1.25} {cy} L{cx} {cy + r * 1.25} L{cx - r * 1.25} {cy} Z" fill={color} stroke={C.white} stroke-width="1.2" {opacity} />
{:else}
	<circle {cx} {cy} {r} fill={color} stroke={C.white} stroke-width="1.2" {opacity} />
{/if}
