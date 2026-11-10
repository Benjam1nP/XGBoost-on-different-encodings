// Runs `python experiment.py --json -m <model>` in the Demo folder and returns its JSON.
import { error, json } from '@sveltejs/kit';
import { spawn } from 'node:child_process';
import path from 'node:path';
import type { RequestHandler } from './$types';
import type { ModelKey } from '#lib/experiment.js';

const MODELS: ModelKey[] = ['xgboost', 'random_forest', 'logistic_regression', 'svm'];
const TIMEOUT_MS = 10 * 60 * 1000;

// The Python project is the parent folder of the frontend unless DEMO_DIR says otherwise.
const demoDir = () => process.env.DEMO_DIR ?? path.resolve(process.cwd(), '..');
const python = () => process.env.PYTHON ?? (process.platform === 'win32' ? 'python' : 'python3');

function runPython(args: string[]): Promise<string> {
	return new Promise((resolve, reject) => {
		const proc = spawn(python(), args, { cwd: demoDir(), windowsHide: true });
		let out = '';
		let err = '';
		const timer = setTimeout(() => {
			proc.kill();
			reject(new Error('The run took longer than 10 minutes and was stopped.'));
		}, TIMEOUT_MS);
		proc.stdout.on('data', (d: Buffer) => (out += d));
		proc.stderr.on('data', (d: Buffer) => (err += d));
		proc.on('error', (e) => {
			clearTimeout(timer);
			reject(new Error(`Could not start Python (${python()}): ${e.message}`));
		});
		proc.on('close', (code) => {
			clearTimeout(timer);
			if (code === 0) resolve(out);
			else reject(new Error(err.trim().split('\n').slice(-3).join('\n') || `Python exited with code ${code}`));
		});
	});
}

export const POST: RequestHandler = async ({ request }) => {
	const body = await request.json().catch(() => ({}));
	const model = body.model as ModelKey;
	if (!MODELS.includes(model)) error(400, `Unknown model "${body.model}"`);

	const args = ['experiment.py', '--json', '-m', model];
	if (body.caseAttributes === false) args.push('--no-case-attributes');

	try {
		const stdout = await runPython(args);
		const line = stdout.trim().split('\n').pop() ?? '';
		return json({ ...JSON.parse(line), finished_at: new Date().toISOString() });
	} catch (e) {
		error(500, (e as Error).message);
	}
};
