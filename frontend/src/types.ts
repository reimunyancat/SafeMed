export type Severity = "high" | "medium" | "low";
export type Band = "green" | "yellow" | "red";

export interface Drug {
  item_seq: string;
  item_name: string;
  entp_name?: string;
  efcy?: string;
  use_method?: string;
  caution?: string;
  interaction?: string;
}

export interface Profile {
  age: number;
  is_pregnant: boolean;
  conditions: string[];
}

export interface Finding {
  kind: string;
  severity: Severity;
  drug_a_name: string;
  drug_b_name: string | null;
  message: string;
  evidence: string;
}

export interface RiskOut {
  score: number;
  band: Band;
  rule_component: number;
  prr_component: number;
  ae_component: number;
  gcn_component: number;
}

export interface AnalyzeResponse {
  risk: RiskOut;
  findings: Finding[];
  easy_summary: string;
  detail_summary: string;
  cautions: string[];
  safe_alternatives: string[];
}

export interface MfdsItem {
  itemSeq: string;
  itemName: string;
  entpName?: string;
  efcyQesitm?: string;
  useMethodQesitm?: string;
  atpnQesitm?: string;
  intrcQesitm?: string;
}
