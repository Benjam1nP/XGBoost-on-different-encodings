<script lang="ts">
	import './layout.css';
	import { Toaster } from '#lib/components/ui/sonner/index.js';
	import * as Tooltip from '#lib/components/ui/tooltip/index.js';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<title>Encoding comparison</title>
</svelte:head>

<Toaster position="bottom-right" />
<Tooltip.Provider delayDuration={150}>
	{@render children()}
</Tooltip.Provider>
