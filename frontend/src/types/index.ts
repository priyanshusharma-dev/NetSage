/**
 * NetSage Strongly Typed Domain Models
 */

export interface InterfaceInfo {
  name: string;
  ip_address: string;
  subnet_mask: string;
  connected_to: string;
  status: string;
  protocol: string;
  speed_duplex?: string;
}

export interface NodeData {
  id: string;
  name: string;
  type: 'router' | 'switch' | 'host' | 'server';
  x: number;
  y: number;
  interfaces: Record<string, InterfaceInfo>;
  default_gateway?: string;
  dns_server?: string;
  routes_count?: number;
  acls_count?: number;
}

export interface LinkData {
  source_node: string;
  source_port: string;
  target_node: string;
  target_port: string;
  subnet: string;
  status?: string;
}

export interface ActiveFault {
  type: string;
  title: string;
  target_node: string;
  target_interface?: string;
  timestamp: string;
  description: string;
  bad_gateway?: string;
  bad_subnet_mask?: string;
  bad_dns_server?: string;
  bad_route?: Record<string, string>;
}

export interface TopologyState {
  nodes: NodeData[];
  links: LinkData[];
  active_faults: ActiveFault[];
  mode: 'SIMULATED' | 'GNS3_LIVE';
  gns3_online?: boolean;
}

export interface EvidenceMetadata {
  source?: string;
  category?: string;
  section?: string;
  chunk_index?: number;
}

export interface EvidenceChunk {
  id: string;
  content: string;
  metadata: EvidenceMetadata;
  distance: number;
  similarity_score: number;
}

export interface DiagnosisResult {
  run_id?: number;
  status: string;
  fallback_triggered: boolean;
  escalation_reason?: string;
  final_root_cause: string;
  confidence_score: number;
  confidence_threshold: number;
  best_retrieval_distance: number;
  distance_threshold: number;
  affected_layer?: string;
  recommended_fix: string;
  reasoning_chain?: string;
  llm_provider?: string;
  retrieved_evidence?: EvidenceChunk[];
  symptom_summary?: string;
  anomalies_detected?: string[];
}

export interface TelemetryState {
  summary: string;
  anomalies: string[];
}

export interface AuditRecord {
  id: number;
  timestamp: string;
  active_fault: string;
  confidence_score: number;
  best_distance: number;
  fallback_triggered: boolean;
  escalation_reason?: string;
  final_root_cause: string;
  recommended_fix: string;
  reasoning_chain?: string;
  llm_provider: string;
  user_label: 'unlabeled' | 'correct' | 'incorrect';
  retrieved_evidence?: EvidenceChunk[];
}

export interface SystemStats {
  total_runs: number;
  autonomous_runs: number;
  escalated_fallbacks: number;
  labeled_count: number;
  verified_correct: number;
  verified_incorrect: number;
  accuracy_percentage: number;
}

export interface ThresholdConfig {
  maxDistance: number;
  minConfidence: number;
}
