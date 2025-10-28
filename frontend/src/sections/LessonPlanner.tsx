import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  Chip,
  Divider,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import CalendarMonthRoundedIcon from "@mui/icons-material/CalendarMonthRounded";
import SchoolRoundedIcon from "@mui/icons-material/SchoolRounded";
import DownloadRoundedIcon from "@mui/icons-material/DownloadRounded";

import SectionCard from "../components/SectionCard";
import DocumentSelector from "../components/DocumentSelector";
import MarkdownRenderer from "../components/MarkdownRenderer";
import StatusPill from "../components/StatusPill";
import { LANGUAGES, STATES } from "../constants";
import type { LessonPlanResult } from "../types";
import { postJson } from "../api/client";
import { downloadFromApi } from "../utils/download";

type FormatOption = "json" | "docx" | "pdf";

interface LessonPlannerProps {
  documents: string[];
  suggestedLanguage?: string;
  suggestedState?: string;
  coursesLoaded: boolean;
  holidaysLoaded: boolean;
}

export const LessonPlanner = ({
  documents,
  suggestedLanguage = "English",
  suggestedState = "Corporate",
  coursesLoaded,
  holidaysLoaded,
}: LessonPlannerProps) => {
  const [topic, setTopic] = useState(
    "A detailed lesson plan for Front Desk Associate trainees focusing on guest engagement."
  );
  const [courseName, setCourseName] = useState("");
  const [state, setState] = useState(suggestedState);
  const [startDate, setStartDate] = useState("");
  const [language, setLanguage] = useState(suggestedLanguage);
  const [format, setFormat] = useState<FormatOption>("json");
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [result, setResult] = useState<LessonPlanResult | null>(null);
  const [lastDownload, setLastDownload] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"preview" | "json">("preview");

  useEffect(() => {
    if (suggestedState) {
      setState(suggestedState);
    }
  }, [suggestedState]);

  useEffect(() => {
    setLanguage(suggestedLanguage);
  }, [suggestedLanguage]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLastDownload(null);
    setViewMode("preview");

    if (!topic.trim()) {
      setError("Please describe the lesson plan focus area.");
      return;
    }

    if (selectedDocs.length === 0) {
      setError("Select at least one document to ground the lesson plan.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        query: topic.trim(),
        course_name: courseName.trim(),
        state,
        start_date: startDate,
        language,
        output_format: format,
        selected_documents: selectedDocs,
      };

      const response = await postJson<LessonPlanResult>(
        "/create/lesson_plan",
        payload
      );

      if (response.kind === "json") {
        setResult(response.data);
      } else {
        await downloadFromApi(response);
        setLastDownload(response.fileName);
        setResult(null);
      }
    } catch (apiError) {
      setError(
        apiError instanceof Error ? apiError.message : "Failed to generate lesson plan."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SectionCard
      title="Lesson Planner"
      subtitle="Generate trainer-ready lesson plans that respect calendars, holidays, and course durations."
      icon={<CalendarMonthRoundedIcon color="primary" fontSize="large" />}
    >
      <Stack spacing={4}>
        <Box display="flex" gap={1} flexWrap="wrap">
          <StatusPill
            label={coursesLoaded ? "Courses loaded" : "Courses pending"}
            active={coursesLoaded}
            color="success"
          />
          <StatusPill
            label={holidaysLoaded ? "Holiday calendar ready" : "Holidays pending"}
            active={holidaysLoaded}
            color="success"
          />
        </Box>

        <DocumentSelector
          title="Select Source Documents"
          description="Pick facilitator guides or competency frameworks that the lesson should draw from."
          documents={documents}
          value={selectedDocs}
          onChange={setSelectedDocs}
        />

        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid size={12}>
              <TextField
                label="Topic for the lesson plan"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                multiline
                minRows={3}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                label="Course name (optional)"
                placeholder="Hospitality - Front Desk Associate"
                value={courseName}
                onChange={(event) => setCourseName(event.target.value)}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                select
                SelectProps={{ native: true }}
                label="State / Region"
                value={state}
                onChange={(event) => setState(event.target.value)}
                fullWidth
              >
                {STATES.map((option) => (
                  <option value={option} key={option}>
                    {option}
                  </option>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                type="date"
                label="Cohort start date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                select
                SelectProps={{ native: true }}
                label="Delivery language"
                value={language}
                onChange={(event) => setLanguage(event.target.value)}
                fullWidth
              >
                {LANGUAGES.map((option) => (
                  <option value={option} key={option}>
                    {option}
                  </option>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <ToggleButtonGroup
                value={format}
                exclusive
                onChange={(_, value: FormatOption | null) => value && setFormat(value)}
                fullWidth
                color="primary"
              >
                <ToggleButton value="json">Interactive view</ToggleButton>
                <ToggleButton value="docx">Word (docx)</ToggleButton>
                <ToggleButton value="pdf">PDF</ToggleButton>
              </ToggleButtonGroup>
            </Grid>
            <Grid size={12}>
              <Box display="flex" justifyContent="flex-end">
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  startIcon={
                    loading ? (
                      <CircularProgress size={18} color="inherit" />
                    ) : (
                      <SchoolRoundedIcon />
                    )
                  }
                  disabled={loading}
                >
                  {loading ? "Crafting plan…" : "Generate lesson plan"}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {lastDownload ? (
          <Alert
            severity="success"
            icon={<DownloadRoundedIcon fontSize="inherit" />}
          >
            Download ready: {lastDownload}
          </Alert>
        ) : null}

        {result ? (
          <Stack spacing={3}>
            <Alert severity="success">
              Lesson plan generated successfully with calendar considerations.
            </Alert>
            <Box display="flex" justifyContent="flex-end">
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                size="small"
                onChange={(_, value: "preview" | "json" | null) => {
                  if (value) {
                    setViewMode(value);
                  }
                }}
              >
                <ToggleButton value="preview">Preview</ToggleButton>
                <ToggleButton value="json">JSON</ToggleButton>
              </ToggleButtonGroup>
            </Box>
            {viewMode === "json" ? (
              <Box
                sx={{
                  bgcolor: "rgba(15,23,42,0.07)",
                  p: 2,
                  borderRadius: 2,
                  overflowX: "auto",
                }}
              >
                <Typography
                  component="pre"
                  sx={{
                    m: 0,
                    fontFamily: "Menlo, Consolas, 'Courier New', monospace",
                    fontSize: "0.85rem",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {JSON.stringify(result, null, 2)}
                </Typography>
              </Box>
            ) : (
              <>
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    English Version
                  </Typography>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: "rgba(0, 176, 255, 0.05)",
                    }}
                  >
                    <MarkdownRenderer content={result.english_answer} />
                  </Box>
                </Box>
                {result.language && result.language !== "English" ? (
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      {result.language} Translation
                    </Typography>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        background: "rgba(19,196,163,0.08)",
                      }}
                    >
                      <MarkdownRenderer content={result.translated_answer || ""} />
                    </Box>
                  </Box>
                ) : null}
                {result.holidays_considered ? (
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Holidays taken into account
                    </Typography>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        background: "rgba(148, 163, 184, 0.12)",
                      }}
                    >
                      <MarkdownRenderer content={result.holidays_considered} />
                    </Box>
                  </Box>
                ) : null}
                <Divider />
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Sources referenced
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={1}>
                    {result.sources?.length
                      ? result.sources.map((source) => (
                          <Chip key={source} label={source} color="primary" variant="outlined" />
                        ))
                      : (
                        <Typography variant="body2">No sources returned.</Typography>
                      )}
                  </Stack>
                </Box>
              </>
            )}
          </Stack>
        ) : null}
      </Stack>
    </SectionCard>
  );
};

export default LessonPlanner;
