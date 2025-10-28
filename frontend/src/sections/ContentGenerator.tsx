import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  Chip,
  Divider,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import CreateRoundedIcon from "@mui/icons-material/CreateRounded";
import DownloadRoundedIcon from "@mui/icons-material/DownloadRounded";

import SectionCard from "../components/SectionCard";
import DocumentSelector from "../components/DocumentSelector";
import MarkdownRenderer from "../components/MarkdownRenderer";
import { postJson } from "../api/client";
import { downloadFromApi } from "../utils/download";
import {
  LANGUAGES,
  CONTENT_TYPES,
  TONES,
  CONTENT_LENGTH_OPTIONS,
} from "../constants";
import type { ContentResult } from "../types";

type FormatOption = "json" | "docx" | "pdf";

interface ContentGeneratorProps {
  documents: string[];
  suggestedLanguage?: string;
}

export const ContentGenerator = ({
  documents,
  suggestedLanguage = "English",
}: ContentGeneratorProps) => {
  const [topic, setTopic] = useState(
    "Create a learner handout on effective body language for front desk associates."
  );
  const [contentType, setContentType] = useState(CONTENT_TYPES[0]);
  const [tone, setTone] = useState(TONES[0]);
  const [audience, setAudience] = useState("Front Desk Associate trainees");
  const [length, setLength] = useState(CONTENT_LENGTH_OPTIONS[1]);
  const [includePractice, setIncludePractice] = useState(true);
  const [language, setLanguage] = useState(suggestedLanguage);
  const [format, setFormat] = useState<FormatOption>("json");
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [result, setResult] = useState<ContentResult | null>(null);
  const [lastDownload, setLastDownload] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"preview" | "json">("preview");

  useEffect(() => {
    setLanguage(suggestedLanguage);
  }, [suggestedLanguage]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLastDownload(null);
    setViewMode("preview");

    if (!topic.trim()) {
      setError("Please describe the content you need.");
      return;
    }

    if (selectedDocs.length === 0) {
      setError("Select at least one knowledge base document to ground the content.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        query: topic.trim(),
        content_type: contentType,
        audience: audience.trim() || "Front Desk Associate trainees",
        tone,
        length,
        include_practice: includePractice,
        language,
        output_format: format,
        selected_documents: selectedDocs,
      };

      const response = await postJson<ContentResult>(
        "/create/content",
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
        apiError instanceof Error
          ? apiError.message
          : "Failed to generate learning content."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SectionCard
      title="Content Generator"
      subtitle="Produce facilitator guides, learner handouts, or quick reference sheets within minutes."
      icon={<CreateRoundedIcon color="primary" fontSize="large" />}
    >
      <Stack spacing={4}>
        <DocumentSelector
          title="Select Source Documents"
          description="Ensure factual accuracy by anchoring the content in Tata Strive knowledge assets."
          documents={documents}
          value={selectedDocs}
          onChange={setSelectedDocs}
        />

        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 8 }}>
              <TextField
                label="Primary topic or brief"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                multiline
                minRows={3}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField
                select
                SelectProps={{ native: true }}
                label="Content type"
                value={contentType}
                onChange={(event) => setContentType(event.target.value)}
                fullWidth
              >
                {CONTENT_TYPES.map((option) => (
                  <option value={option} key={option}>
                    {option}
                  </option>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField
                select
                SelectProps={{ native: true }}
                label="Preferred tone"
                value={tone}
                onChange={(event) => setTone(event.target.value)}
                fullWidth
              >
                {TONES.map((option) => (
                  <option value={option} key={option}>
                    {option}
                  </option>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField
                label="Target audience"
                value={audience}
                onChange={(event) => setAudience(event.target.value)}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField
                select
                SelectProps={{ native: true }}
                label="Depth"
                value={length}
                onChange={(event) => setLength(event.target.value)}
                fullWidth
              >
                {CONTENT_LENGTH_OPTIONS.map((option) => (
                  <option value={option} key={option}>
                    {option}
                  </option>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
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
            <Grid size={{ xs: 12, md: 4 }} display="flex" alignItems="center">
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includePractice}
                    onChange={(event) => setIncludePractice(event.target.checked)}
                  />
                }
                label="Include a practical activity or checklist"
              />
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
                    ) : undefined
                  }
                  disabled={loading}
                >
                  {loading ? "Building content…" : "Generate content"}
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
              Content draft generated. Review and customise before sharing.
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
                {result.metadata ? (
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Generation settings
                    </Typography>
                    <Stack direction="row" flexWrap="wrap" gap={1}>
                      {Object.entries(result.metadata).map(([key, value]) => (
                        <Chip
                          key={key}
                          label={`${key.replace(/_/g, " ")}: ${String(value)}`}
                          variant="outlined"
                          color="primary"
                        />
                      ))}
                    </Stack>
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

export default ContentGenerator;
