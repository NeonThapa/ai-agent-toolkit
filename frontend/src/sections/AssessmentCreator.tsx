import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  Chip,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import DescriptionRoundedIcon from "@mui/icons-material/DescriptionRounded";
import TranslateRoundedIcon from "@mui/icons-material/TranslateRounded";
import ArticleRoundedIcon from "@mui/icons-material/ArticleRounded";
import DownloadRoundedIcon from "@mui/icons-material/DownloadRounded";

import SectionCard from "../components/SectionCard";
import DocumentSelector from "../components/DocumentSelector";
import MarkdownRenderer from "../components/MarkdownRenderer";
import { postJson } from "../api/client";
import { downloadFromApi } from "../utils/download";
import type { AssessmentResult } from "../types";
import { LANGUAGES } from "../constants";

type FormatOption = "json" | "docx" | "pdf";

interface AssessmentCreatorProps {
  documents: string[];
  suggestedLanguage?: string;
}

export const AssessmentCreator = ({
  documents,
  suggestedLanguage = "English",
}: AssessmentCreatorProps) => {
  const [topic, setTopic] = useState(
    "Create a quiz about greeting guests at a hotel."
  );
  const [language, setLanguage] = useState(suggestedLanguage);
  const [format, setFormat] = useState<FormatOption>("json");
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [result, setResult] = useState<AssessmentResult | null>(null);
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

    if (selectedDocs.length === 0) {
      setError("Please choose at least one knowledge base document.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        query: topic.trim(),
        language,
        output_format: format,
        selected_documents: selectedDocs,
      };

      const response = await postJson<AssessmentResult>(
        "/create/assessment",
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
        apiError instanceof Error ? apiError.message : "Failed to generate assessment."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SectionCard
      title="Assessment Creator"
      subtitle="Design rich formative or summative assessments grounded in Tata Strive knowledge."
      icon={<DescriptionRoundedIcon color="primary" fontSize="large" />}
    >
      <Stack spacing={4}>
        <DocumentSelector
          title="Select Source Documents"
          description="Ground the quiz in relevant facilitator guides, handbooks, or internal documentation."
          documents={documents}
          value={selectedDocs}
          onChange={setSelectedDocs}
        />

        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid size={12}>
              <TextField
                label="Topic for the assessment"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                multiline
                minRows={3}
                fullWidth
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
                onChange={(_, value: FormatOption | null) => {
                  if (value) {
                    setFormat(value);
                  }
                }}
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
                  disabled={loading}
                  startIcon={
                    loading ? (
                      <CircularProgress size={18} color="inherit" />
                    ) : (
                      <ArticleRoundedIcon />
                    )
                  }
                >
                  {loading ? "Generating…" : "Generate assessment"}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {error ? <Alert severity="error">{error}</Alert> : null}
        {lastDownload ? (
          <Alert
            icon={<DownloadRoundedIcon fontSize="inherit" />}
            severity="success"
          >
            Download ready: {lastDownload}
          </Alert>
        ) : null}

        {result ? (
          <Stack spacing={3}>
            <Alert severity="success">Assessment generated successfully.</Alert>
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
                  <Typography variant="subtitle1" gutterBottom display="flex" gap={1} alignItems="center">
                    <DescriptionRoundedIcon fontSize="small" />
                    English Version
                  </Typography>
                  <Box
                    sx={{
                      backgroundColor: "rgba(15,23,42,0.02)",
                      p: 2,
                      borderRadius: 2,
                    }}
                  >
                    <MarkdownRenderer content={result.english_answer} />
                  </Box>
                </Box>
                {result.language && result.language !== "English" ? (
                  <Box>
                    <Typography variant="subtitle1" gutterBottom display="flex" gap={1} alignItems="center">
                      <TranslateRoundedIcon fontSize="small" />
                      {result.language} Translation
                    </Typography>
                    <Box
                      sx={{
                        backgroundColor: "rgba(19,196,163,0.06)",
                        p: 2,
                        borderRadius: 2,
                      }}
                    >
                      <MarkdownRenderer content={result.translated_answer || ""} />
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
                          <Chip
                            key={source}
                            label={source}
                            color="primary"
                            variant="outlined"
                          />
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

export default AssessmentCreator;
