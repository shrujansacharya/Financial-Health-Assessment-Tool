export interface FinancialData {
    score: number;
    metrics: {
        rev_growth_pct: number;
        expense_ratio: number;
        net_cash_flow: number;
        working_capital: number;
        debt_burden_ratio: number;
        cash_flow_volatility: number;
    };
    flags: Array<{ type: string; severity: string }>;
    charts_data: Array<any>;
    ai_insights: string;
    // New Advanced Fields
    credit_score?: number;
    tax_status?: string;
    forecast_next_month?: number;
}

export type Language = 'en' | 'hi';
