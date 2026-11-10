<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { Button } from '#lib/components/ui/button/index.js';
	import { Switch } from '#lib/components/ui/switch/index.js';
	import { Skeleton } from '#lib/components/ui/skeleton/index.js';
	import * as Table from '#lib/components/ui/table/index.js';
	import * as Tooltip from '#lib/components/ui/tooltip/index.js';
	import AucChart, { type Series } from './AucChart.svelte';
	import { ENCODINGS, ENCODING_ORDER, MODELS, describe, wins, type ModelKey } from '#lib/experiment.js';
	import { store, runModel } from '#lib/results.svelte.js';
	import Play from '~icons/ph/play-light';
	import ArrowClockwise from '~icons/ph/arrow-clockwise-light';
	import CircleNotch from '~icons/ph/circle-notch-light';
	import ChartLine from '~icons/ph/chart-line-light';
	import Info from '~icons/ph/info';

	let { model }: { model: ModelKey } = $props();

	const meta = $derived(MODELS.find((m) => m.key === model)!);
	const result = $derived(store.results[model]);
	const running = $derived(!!store.running[model]);
	const error = $derived(store.errors[model]);

	let caseAttributes = $derived(store.caseAttributes[model] ?? true);

	const runs = $derived(
		result
			? ENCODING_ORDER.map((e) => result.runs.find((r) => r.encoding === e)!).filter(Boolean)
			: []
	);
	const best = $derived(runs.length ? runs.reduce((a, b) => (b.mean_auc > a.mean_auc ? b : a)) : null);
	const winCount = $derived(result ? wins(result) : {});
	const description = $derived(result ? describe(result) : []);
	const series: Series[] = $derived(
		runs.map((r) => ({
			key: r.encoding,
			label: ENCODINGS[r.encoding].name,
			color: ENCODINGS[r.encoding].color,
			values: r.auc,
			main: r === best
		}))
	);
	const ks = $derived(result ? Object.keys(result.test_cases).sort((a, b) => +a - +b) : []);
	const totalSeconds = $derived(runs.reduce((a, r) => a + r.seconds, 0));
	const stale = $derived(!!result && result.use_case_attributes !== caseAttributes);

	async function run() {
		try {
			await runModel(model);
			toast(`${meta.name} finished`, { description: 'All three encodings were evaluated.' });
		} catch (e) {
			toast(`${meta.name} run failed`, { description: (e as Error).message });
		}
	}
</script>

<div class="flex flex-col gap-8">
	<!-- Model header + controls -->
	<section class="flex flex-col gap-4 rounded-lg border bg-card p-5 md:flex-row md:items-start md:justify-between">
		<div class="flex max-w-2xl flex-col gap-2">
			<p class="text-label">{meta.summary}</p>
			<h2 class="text-xl font-bold tracking-tight">{meta.name}</h2>
			<p class="text-muted-foreground">{meta.details}</p>
		</div>
		<div class="flex shrink-0 items-center gap-4">
			<label class="flex items-center gap-2 text-sm text-muted-foreground">
				<Switch
					checked={caseAttributes}
					onCheckedChange={(v) => (store.caseAttributes[model] = v)}
					disabled={running}
				/>
				Case attributes
				<Tooltip.Root>
					<Tooltip.Trigger class="text-muted-foreground hover:text-foreground" aria-label="What are case attributes?">
						<Info class="size-4" />
					</Tooltip.Trigger>
					<Tooltip.Content class="max-w-64">
						Static patient data recorded at registration: age, ordered diagnostics, SIRS criteria. Turn off to see how much the
						event sequence alone carries.
					</Tooltip.Content>
				</Tooltip.Root>
			</label>
			{#if result || running}
				<Button onclick={run} disabled={running}>
					{#if running}
						<CircleNotch class="animate-spin" /> Running
					{:else}
						<ArrowClockwise /> Run again
					{/if}
				</Button>
			{/if}
		</div>
	</section>

	{#if error && !running}
		<p class="text-sm" role="alert">
			<span class="text-muted-foreground">The run didn't finish: {error}</span>
			<button class="ml-1 text-link underline-offset-4 hover:underline" onclick={run}>Try again</button>
		</p>
	{/if}

	{#if running && !result}
		<!-- loading skeletons -->
		<div class="grid gap-4 md:grid-cols-3">
			{#each ENCODING_ORDER as e (e)}
				<Skeleton class="h-28 rounded-lg" />
			{/each}
		</div>
		<Skeleton class="h-80 rounded-lg" />
		<p class="text-sm text-muted-foreground">
			Training {meta.name} on all three encodings. This takes a few seconds up to a minute.
		</p>
	{:else if !result}
		<!-- empty state -->
		<div class="flex flex-col items-center gap-4 py-16 text-center">
			<ChartLine class="size-8 text-muted-foreground" />
			<h2 class="font-heading text-4xl">No run yet.</h2>
			<p class="max-w-md text-muted-foreground">
				Run {meta.name} with the last state, aggregation and index encodings to compare them.
			</p>
			<Button onclick={run}><Play /> Run {meta.name}</Button>
		</div>
	{:else}
		<div class="flex flex-col gap-8 transition-opacity duration-100" class:opacity-50={running}>
			{#if stale}
				<p class="text-sm text-muted-foreground">
					These results were computed {result.use_case_attributes ? 'with' : 'without'} case attributes. Run again to apply the new
					setting.
				</p>
			{/if}

			<!-- KPI tiles: mean AUC per encoding -->
			<div class="grid gap-4 md:grid-cols-3">
				{#each runs as r (r.encoding)}
					<div
						class="flex animate-in flex-col gap-2 rounded-lg border bg-card p-5 duration-200 fade-in"
						class:border-l-2={r === best}
						class:border-l-agent-rule={r === best}
					>
						<div class="flex items-center gap-2">
							<span class="size-2.5 rounded-[2px]" style:background={ENCODINGS[r.encoding].color}></span>
							<p class="text-label">{ENCODINGS[r.encoding].name}</p>
							{#if r === best}<span class="ml-auto text-xs text-muted-foreground">Highest mean</span>{/if}
						</div>
						<p class="text-figure text-3xl font-medium">{r.mean_auc.toFixed(3)}</p>
						<p class="text-sm text-muted-foreground">
							Mean AUC · best at <span class="text-figure">{winCount[r.encoding] ?? 0}</span> of
							<span class="text-figure">{ks.length}</span> lengths
						</p>
						<p class="text-xs text-muted-foreground">{ENCODINGS[r.encoding].details}</p>
					</div>
				{/each}
			</div>

			<!-- Chart -->
			<section class="flex flex-col gap-4 rounded-lg border bg-card p-5">
				<div class="flex flex-col gap-1 md:flex-row md:items-end md:justify-between">
					<div>
						<h2 class="text-xl font-bold tracking-tight">AUC per prefix length</h2>
						<p class="text-sm text-muted-foreground">
							{meta.name} on held-out patients · 0.5 is guessing, 1.0 is perfect
						</p>
					</div>
					<div class="flex flex-wrap gap-4 text-sm">
						{#each series as s (s.key)}
							<span class="flex items-center gap-1.5 text-muted-foreground">
								<span class="size-2.5 rounded-[2px]" style:background={s.color}></span>{s.label}
							</span>
						{/each}
					</div>
				</div>
				<AucChart {series} />
			</section>

			<!-- Description -->
			<article class="flex animate-in flex-col gap-3 rounded-lg border border-l-2 border-l-agent-rule bg-card p-5 duration-200 fade-in">
				<h2 class="text-xl font-bold tracking-tight">What this shows</h2>
				{#each description as p, i (i)}
					<p class="max-w-3xl">{p}</p>
				{/each}
			</article>

			<!-- Table -->
			<section class="flex flex-col gap-4 rounded-lg border bg-card p-5">
				<h2 class="text-xl font-bold tracking-tight">Results</h2>
				<Table.Root>
					<Table.Header>
						<Table.Row>
							<Table.Head class="text-label">Prefix length</Table.Head>
							{#each runs as r (r.encoding)}
								<Table.Head class="text-right text-label">{ENCODINGS[r.encoding].name}</Table.Head>
							{/each}
							<Table.Head class="text-right text-label">Test cases</Table.Head>
							<Table.Head class="text-right text-label">ICU</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each ks as k (k)}
							{@const top = Math.max(...runs.map((r) => r.auc[k]))}
							<Table.Row class="hover:bg-secondary/50">
								<Table.Cell class="text-figure">{k}</Table.Cell>
								{#each runs as r (r.encoding)}
									<Table.Cell class="text-right text-figure {r.auc[k] === top ? 'text-foreground' : 'text-muted-foreground'}">
										{r.auc[k].toFixed(3)}
									</Table.Cell>
								{/each}
								<Table.Cell class="text-right text-figure text-muted-foreground">{result.test_cases[k]}</Table.Cell>
								<Table.Cell class="text-right text-figure text-muted-foreground">{result.test_positives[k]}</Table.Cell>
							</Table.Row>
						{/each}
						<Table.Row class="hover:bg-secondary/50">
							<Table.Cell class="font-medium">Mean</Table.Cell>
							{#each runs as r (r.encoding)}
								<Table.Cell class="text-right text-figure font-medium">{r.mean_auc.toFixed(3)}</Table.Cell>
							{/each}
							<Table.Cell></Table.Cell>
							<Table.Cell></Table.Cell>
						</Table.Row>
					</Table.Body>
				</Table.Root>
				<p class="text-xs text-muted-foreground">
					{result.use_case_attributes ? 'With' : 'Without'} case attributes · training time
					<span class="text-figure">{totalSeconds.toFixed(1)} s</span> · finished
					<span class="text-figure">{new Date(result.finished_at).toLocaleTimeString()}</span>
				</p>
			</section>
		</div>
	{/if}
</div>
