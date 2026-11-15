// HSG template look for the slide charts. Charts are drawn at their placeholder size:
// 1 SVG user unit = 1 CSS px = 1/96 in, so pt sizes convert with pt(…).

export const C = {
	green: '#00802F', // accent1: main series, random forest, "all data"
	dark: '#0A5F2D', // dk2: annotation text
	teal: '#73A5AF', // accent4: second series, XGBoost
	sand: '#A8956E', // darkened sand: third series
	grey: '#555555', // fourth series / baseline, logistic regression, axis labels
	light: '#EEEEEE', // noise band, shaded areas
	grid: '#E0E0E0',
	lightGreen: '#CCE6D5', // registration-feature highlight
	text: '#1A1A1A',
	white: '#FFFFFF'
};

export const FONT = "'Gill Sans Nova', Arial, sans-serif";

export const pt = (p: number) => (p * 96) / 72;
export const F = { axis: pt(14), tick: pt(12), direct: pt(13), note: pt(12) };

export const inch = (w: number, h: number) => ({ W: w * 96, H: h * 96, wIn: w, hIn: h });

export type MarkerKind = 'circle' | 'square' | 'triangle' | 'diamond';

export const MODEL_STYLE: Record<string, { name: string; color: string; marker: MarkerKind }> = {
	random_forest: { name: 'Random forest', color: C.green, marker: 'circle' },
	xgboost: { name: 'XGBoost', color: C.teal, marker: 'square' },
	logistic_regression: { name: 'Logistic regression', color: C.grey, marker: 'triangle' }
};
export const MODEL_ROWS = ['random_forest', 'xgboost', 'logistic_regression'];
export const ENC_ROWS = ['last_state', 'aggregation', 'index'];
export const ENC_NAME: Record<string, string> = { last_state: 'Last state', aggregation: 'Aggregation', index: 'Index' };

export const f2 = (v: number) => v.toFixed(2);

/** Push label y-positions apart to at least `gap`, keeping them inside [lo, hi]. */
export function spread<T extends { want: number }>(items: T[], gap: number, lo: number, hi: number) {
	const ls = items.map((it) => ({ ...it, at: it.want })).sort((a, b) => a.want - b.want);
	for (let i = 1; i < ls.length; i++) ls[i].at = Math.max(ls[i].at, ls[i - 1].at + gap);
	const over = ls.length ? ls[ls.length - 1].at - hi : 0;
	if (over > 0) for (const l of ls) l.at -= over;
	for (let i = ls.length - 2; i >= 0; i--) ls[i].at = Math.min(ls[i].at, ls[i + 1].at - gap);
	const under = ls.length ? lo - ls[0].at : 0;
	if (under > 0) for (const l of ls) l.at += under;
	return ls;
}
