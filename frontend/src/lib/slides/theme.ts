// Shared look for the slide figures: one colour per model in every chart (validated palette,
// see the dataviz skill), one colour per initial-data variant, and large type for projection.

export const MODEL_ORDER = ['logistic_regression', 'random_forest', 'xgboost'] as const;
export type SlideModel = (typeof MODEL_ORDER)[number];

export const MODEL: Record<SlideModel, { name: string; color: string }> = {
	logistic_regression: { name: 'Logistic regression', color: '#2a78d6' },
	random_forest: { name: 'Random forest', color: '#eb6834' },
	xgboost: { name: 'XGBoost', color: '#1baf7a' }
};

export const ENCODING_ORDER = ['last_state', 'aggregation', 'index'] as const;
export const ENCODING_NAME: Record<string, string> = {
	last_state: 'Last state',
	aggregation: 'Aggregation',
	index: 'Index'
};

// Initial-data variants. "none" is the grey dashed baseline.
export const VARIANT: Record<string, { name: string; color: string; dash?: string; marker: 'circle' | 'square' | 'diamond' | 'triangle' }> = {
	all: { name: 'All initial data', color: '#6250d6', marker: 'circle' },
	no_symptoms: { name: 'Without disfuncorg, hypotensie, hypoxie, oligurie', color: '#e87ba4', marker: 'square' },
	age_diagnostic: { name: 'Only age + diagnostic* (no symptoms)', color: '#eda100', marker: 'diamond' },
	age: { name: 'Only Age', color: '#e87ba4', marker: 'square' },
	none: { name: 'No initial data', color: '#6b6b68', dash: '10 8', marker: 'triangle' }
};

export const INK = { primary: '#0b0b0b', secondary: '#52514e', muted: '#8a8984', grid: '#e4e3df', surface: '#ffffff' };
