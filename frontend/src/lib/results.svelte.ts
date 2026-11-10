// Run state shared across tabs, so switching tabs keeps finished results and running jobs.
import type { ModelKey, RunResult } from './experiment.js';

export const store = $state({
	results: {} as Partial<Record<ModelKey, RunResult>>,
	running: {} as Partial<Record<ModelKey, boolean>>,
	errors: {} as Partial<Record<ModelKey, string>>,
	caseAttributes: {} as Partial<Record<ModelKey, boolean>>
});

export async function runModel(model: ModelKey) {
	store.running[model] = true;
	store.errors[model] = undefined;
	try {
		const res = await fetch('/api/run', {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ model, caseAttributes: store.caseAttributes[model] ?? true })
		});
		if (!res.ok) {
			const body = await res.json().catch(() => null);
			throw new Error(body?.message ?? `Request failed (${res.status})`);
		}
		store.results[model] = (await res.json()) as RunResult;
	} catch (e) {
		store.errors[model] = (e as Error).message;
		throw e;
	} finally {
		store.running[model] = false;
	}
}
