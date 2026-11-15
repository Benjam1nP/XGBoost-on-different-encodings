<script lang="ts">
	// Legend row: swatch (line + marker) and a label in text ink.
	let {
		items,
		title
	}: { items: { label: string; color: string; dash?: string; marker?: string }[]; title?: string } = $props();
</script>

<div class="legend">
	{#if title}<span class="title">{title}</span>{/if}
	{#each items as it (it.label)}
		<span class="item">
			<svg width="44" height="24" aria-hidden="true">
				<line x1="2" x2="42" y1="12" y2="12" stroke={it.color} stroke-width="4" stroke-dasharray={it.dash} />
				{#if it.marker === 'square'}
					<rect x="15" y="5" width="14" height="14" fill={it.color} stroke="#fff" stroke-width="2" />
				{:else if it.marker === 'diamond'}
					<path d="M22 3 L31 12 L22 21 L13 12 Z" fill={it.color} stroke="#fff" stroke-width="2" />
				{:else if it.marker === 'triangle'}
					<path d="M22 3 L31 20 L13 20 Z" fill={it.color} stroke="#fff" stroke-width="2" />
				{:else}
					<circle cx="22" cy="12" r="8" fill={it.color} stroke="#fff" stroke-width="2" />
				{/if}
			</svg>
			{it.label}
		</span>
	{/each}
</div>

<style>
	.legend {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 10px 36px;
		font-size: 26px;
		color: #0b0b0b;
	}
	.title {
		color: #52514e;
	}
	.item {
		display: inline-flex;
		align-items: center;
		gap: 10px;
	}
</style>
