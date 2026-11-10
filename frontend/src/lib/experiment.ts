// Shared types, metadata and the plain-language description of a run.

export type ModelKey = 'xgboost' | 'random_forest' | 'logistic_regression' | 'svm';
export type EncodingKey = 'last_state' | 'aggregation' | 'index';

export interface EncodingRun {
	encoding: EncodingKey;
	encoding_name: string;
	bucketing: 'single' | 'prefix';
	model: ModelKey;
	model_name: string;
	auc: Record<string, number>; // prefix length -> AUC
	mean_auc: number;
	seconds: number;
}

export interface RunResult {
	use_case_attributes: boolean;
	runs: EncodingRun[];
	test_cases: Record<string, number>;
	test_positives: Record<string, number>;
	finished_at: string; // added by the server
}

export const MODELS: { key: ModelKey; name: string; summary: string; details: string }[] = [
	{
		key: 'xgboost',
		name: 'XGBoost',
		summary: 'Gradient-boosted trees',
		details:
			'200 shallow trees (depth 3) built one after another, each one correcting the errors of the previous ones. Missing lab values are handled natively.'
	},
	{
		key: 'random_forest',
		name: 'Random forest',
		summary: 'Bagged decision trees',
		details:
			'300 independent trees, each grown on a bootstrap sample and a random subset of features, then averaged. Missing lab values are filled with the training median.'
	},
	{
		key: 'logistic_regression',
		name: 'Logistic regression',
		summary: 'Linear baseline',
		details:
			'A regularised linear model (C = 0.1) on standardised features. Easy to interpret, but it can only add up effects, not combine them.'
	},
	{
		key: 'svm',
		name: 'SVM',
		summary: 'Kernel method',
		details:
			'Support vector machine with an RBF kernel on standardised features; probabilities come from Platt scaling. Sensitive to many sparse one-hot columns.'
	}
];

export const ENCODINGS: Record<EncodingKey, { name: string; details: string; color: string }> = {
	last_state: {
		name: 'Last state',
		details: 'Only the latest event: its activity, resource and the last observed lab values.',
		color: 'var(--chart-1)'
	},
	aggregation: {
		name: 'Aggregation',
		details: 'Counts of every activity and resource plus mean and max lab values. Order is lost.',
		color: 'var(--chart-5)'
	},
	index: {
		name: 'Index',
		details: 'Activity and resource at every position 1…k. Lossless, so one model per prefix length.',
		color: 'var(--chart-2)'
	}
};

export const ENCODING_ORDER: EncodingKey[] = ['last_state', 'aggregation', 'index'];

const NOISE = 0.05;

const fmt = (v: number) => v.toFixed(3);
const mean = (xs: number[]) => xs.reduce((a, b) => a + b, 0) / xs.length;

/** Number of prefix lengths at which each encoding has the highest AUC. */
export function wins(result: RunResult): Record<string, number> {
	const out: Record<string, number> = Object.fromEntries(result.runs.map((r) => [r.encoding, 0]));
	for (const k of Object.keys(result.test_cases)) {
		const best = result.runs.reduce((a, b) => ((b.auc[k] ?? 0) > (a.auc[k] ?? 0) ? b : a));
		out[best.encoding]++;
	}
	return out;
}

/** A short, calm interpretation of one model run across the three encodings. */
export function describe(result: RunResult): string[] {
	const ranked = [...result.runs].sort((a, b) => b.mean_auc - a.mean_auc);
	const [best, second, worst] = [ranked[0], ranked[1], ranked[ranked.length - 1]];
	const name = (r: EncodingRun) => ENCODINGS[r.encoding].name.toLowerCase();
	const model = MODELS.find((m) => m.key === best.model)?.name ?? best.model_name;
	const ks = Object.keys(best.auc).map(Number).sort((a, b) => a - b);
	const pos = Object.values(result.test_positives);
	const minPos = Math.min(...pos);
	const maxPos = Math.max(...pos);
	const w = wins(result);
	const out: string[] = [];

	out.push(
		`With ${model}, ${name(best)} encoding scores highest with a mean AUC of ${fmt(best.mean_auc)}, ` +
			`followed by ${name(second)} (${fmt(second.mean_auc)})` +
			(ranked.length > 2 ? ` and ${name(worst)} (${fmt(worst.mean_auc)}).` : '.')
	);

	const gap = best.mean_auc - worst.mean_auc;
	const n = minPos === maxPos ? `${minPos}` : `${minPos}–${maxPos}`;
	if (gap < 0.03) {
		out.push(
			`The spread between the encodings is only ${fmt(gap)}. With ${n} ICU patients per prefix length in the test set, that is well inside the noise, so the encodings are effectively tied for this model.`
		);
	} else if (gap < NOISE + 0.01) {
		out.push(
			`The gap between best and worst is ${fmt(gap)}, close to the ~${NOISE} noise band that ${n} ICU patients per prefix length allow. Treat the ranking as a tendency, not a result.`
		);
	} else {
		out.push(
			`The gap between ${name(best)} and ${name(worst)} is ${fmt(gap)}, larger than the ~${NOISE} noise band, so ${name(worst)} encoding is genuinely weaker with ${model}.`
		);
	}

	// Trend over the prefix for the best encoding
	const early = mean(ks.filter((k) => k <= 3).map((k) => best.auc[k]));
	const late = mean(ks.filter((k) => k >= ks[ks.length - 1] - 2).map((k) => best.auc[k]));
	const d = late - early;
	const trend =
		Math.abs(d) < 0.02
			? `stays roughly flat between short prefixes (1–3 events, ${fmt(early)}) and long ones (${fmt(late)})`
			: d > 0
				? `improves from ${fmt(early)} on short prefixes (1–3 events) to ${fmt(late)} on long ones, so more observed events help`
				: `drops from ${fmt(early)} on short prefixes (1–3 events) to ${fmt(late)} on long ones; fewer cases reach those lengths, and the remaining ones are harder`;
	out.push(`For ${name(best)} encoding the AUC ${trend}.`);

	const winText = ranked.map((r) => `${name(r)} ${w[r.encoding]}`).join(', ');
	out.push(`Best encoding per prefix length (out of ${ks.length}): ${winText}.`);

	const idx = result.runs.find((r) => r.encoding === 'index');
	if (idx && idx === worst && gap >= 0.03) {
		out.push(
			`Index encoding trains a separate model for every prefix length, so each model only sees the prefixes of that one length and many sparse position-specific columns. ${model} pays for that with lower AUC.`
		);
	} else if (idx && idx === best) {
		out.push(
			`Index encoding keeps the exact order of events, and ${model} can use that even though each per-length model sees fewer training prefixes.`
		);
	}

	if (!result.use_case_attributes) {
		out.push(
			'This run excludes the static case attributes (age, diagnostics, SIRS criteria), so only the control flow, resources, lab values and elapsed time are used.'
		);
	}
	return out;
}
