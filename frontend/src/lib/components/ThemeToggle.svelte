<script lang="ts">
	import { toggleMode, mode } from 'mode-watcher';
	import { Button } from '#lib/components/ui/button/index.js';
	import Sun from '~icons/ph/sun-light';
	import Moon from '~icons/ph/moon-light';
</script>

<Button
	variant="ghost"
	size="icon-sm"
	class="size-11 md:size-8"
	onclick={toggleMode}
	aria-label={mode.current === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
>
	{#if mode.current === 'dark'}
		<Sun class="size-5" />
	{:else}
		<Moon class="size-5" />
	{/if}
</Button>
