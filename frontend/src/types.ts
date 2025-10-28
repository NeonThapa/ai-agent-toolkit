export interface LocationData {
  location: {
    city?: string;
    state?: string;
    country?: string;
    detected?: boolean;
  };
  suggested_language: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  courses_loaded: number;
  states_with_holidays: number;
  guidelines_loaded: boolean;
}

export interface AssessmentResult {
  english_answer: string;
  translated_answer?: string;
  language: string;
  sources: string[];
}

export interface LessonPlanResult extends AssessmentResult {
  holidays_considered?: string;
}

export interface ContentResult extends AssessmentResult {
  metadata?: Record<string, unknown>;
}

export interface EmailProcessingResult {
  total_students: number;
  average_score: number;
  emails_sent: number;
  email_results: Array<Record<string, string>>;
  weak_questions: Array<{
    question: string;
    success_rate: number;
  }>;
}
