<script lang="ts">
	// A fixed 1600 x 900 (16:9) panel; screenshots.py captures each one by its id.
	import type { Snippet } from 'svelte';
	let {
		id,
		title,
		subtitle,
		children
	}: { id: string; title: string; subtitle?: string; children: Snippet } = $props();
</script>

<section class="fig-wrap">
	<p class="fig-file">{id}.png</p>
	<figure {id} class="fig">
		<header>
			<h2>{title}</h2>
			{#if subtitle}<p>{subtitle}</p>{/if}
		</header>
		<div class="body">{@render children()}</div>
	</figure>
</section>

<style>
	.fig-wrap {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	.fig-file {
		font-family: var(--font-mono);
		font-size: 14px;
		color: #52514e;
	}
	.fig {
		width: 1600px;
		height: 900px;
		margin: 0;
		background: #ffffff;
		color: #0b0b0b;
		padding: 48px 64px 40px;
		display: flex;
		flex-direction: column;
		gap: 24px;
		box-sizing: border-box;
		overflow: hidden;
		font-family: 'Geist Variable', ui-sans-serif, system-ui, sans-serif;
		border: 1px solid #e4e3df;
	}
	header h2 {
		font-size: 44px;
		line-height: 1.15;
		font-weight: 700;
		letter-spacing: -0.01em;
	}
	header p {
		margin-top: 6px;
		font-size: 26px;
		color: #52514e;
	}
	.body {
		flex: 1;
		min-height: 0;
		display: flex;
		flex-direction: column;
	}
</style>
