<script lang="ts">
	import './layout.css';
	import { ModeWatcher } from 'mode-watcher';
	import { Toaster } from '#lib/components/ui/sonner/index.js';
	import * as Tooltip from '#lib/components/ui/tooltip/index.js';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<title>Encoding comparison</title>
</svelte:head>

<ModeWatcher defaultMode="dark" themeColors={{ dark: '#0A0E13', light: '#F7F9FB' }} />
<Toaster position="bottom-right" />
<Tooltip.Provider delayDuration={150}>
	{@render children()}
</Tooltip.Provider>
