<script lang="ts">
	import * as Tabs from '#lib/components/ui/tabs/index.js';
	import ModelPanel from '#lib/components/ModelPanel.svelte';
	import ThemeToggle from '#lib/components/ThemeToggle.svelte';
	import { MODELS, type ModelKey } from '#lib/experiment.js';
	import { store } from '#lib/results.svelte.js';
	import CircleNotch from '~icons/ph/circle-notch-light';

	let tab = $state<ModelKey>('xgboost');
</script>

<div class="min-h-dvh">
	<header class="sticky top-0 z-20 border-b bg-background">
		<div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-2 md:px-8 md:py-3">
			<div class="flex items-baseline gap-3">
				<span class="font-heading text-2xl leading-none">PPM</span>
				<span class="hidden text-sm text-muted-foreground sm:inline">Sepsis cases · ICU prediction</span>
			</div>
			<ThemeToggle />
		</div>
	</header>

	<main class="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-6 md:px-8 md:py-8">
		<div class="flex flex-col gap-2">
			<h1 class="text-2xl font-bold tracking-tight">Encoding comparison</h1>
			<p class="max-w-3xl text-muted-foreground">
				Will a patient with suspected sepsis end up in intensive care? Each tab trains one classifier on prefixes of the
				<span class="text-foreground">Sepsis Cases</span> log with three encodings and evaluates them on later patients (temporal
				80/20 split).
			</p>
		</div>

		<Tabs.Root bind:value={tab} class="flex flex-col gap-6">
			<div class="-mx-4 overflow-x-auto px-4 md:mx-0 md:px-0">
				<Tabs.List variant="line" class="w-full justify-start gap-1 border-b">
					{#each MODELS as m (m.key)}
						<Tabs.Trigger value={m.key} class="flex-none px-3">
							{m.name}
							{#if store.running[m.key]}
								<CircleNotch class="size-4 animate-spin text-muted-foreground" aria-label="running" />
							{:else if store.results[m.key]}
								<span class="text-figure text-xs text-muted-foreground">
									{Math.max(...store.results[m.key]!.runs.map((r) => r.mean_auc)).toFixed(3)}
								</span>
							{/if}
						</Tabs.Trigger>
					{/each}
				</Tabs.List>
			</div>

			{#each MODELS as m (m.key)}
				<Tabs.Content value={m.key}>
					<ModelPanel model={m.key} />
				</Tabs.Content>
			{/each}
		</Tabs.Root>
	</main>
</div>
