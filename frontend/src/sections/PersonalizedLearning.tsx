import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  Paper,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import MailRoundedIcon from "@mui/icons-material/MailRounded";

import SectionCard from "../components/SectionCard";
import MetricCard from "../components/MetricCard";
import { postFormData } from "../api/client";
import type { EmailProcessingResult } from "../types";

interface PersonalizedLearningProps {}

export const PersonalizedLearning = ({}: PersonalizedLearningProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EmailProcessingResult | null>(null);

  const handleUpload = async () => {
    if (!file) {
      setError("Please choose a CSV or Excel file with assessment data.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await postFormData<EmailProcessingResult>(
        "/process/assessment_and_email",
        formData
      );
      setResult(response);
    } catch (apiError) {
      setError(
        apiError instanceof Error
          ? apiError.message
          : "Failed to process assessment data."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SectionCard
      title="Personalized Learning Engine"
      subtitle="Analyse assessment data, notify facilitators, and auto-email tailored study packs."
      icon={<MailRoundedIcon color="primary" fontSize="large" />}
    >
      <Stack spacing={4}>
        <Alert severity="info">
          Upload a CSV or Excel file with assessment scores. The system will
          generate personalised PDFs and email them to learners scoring below
          70%.
        </Alert>

        <Paper
          variant="outlined"
          sx={{
            p: 3,
            borderStyle: "dashed",
            borderWidth: 2,
            borderColor: "rgba(0, 176, 255, 0.24)",
            background: "rgba(0, 176, 255, 0.04)",
          }}
        >
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, md: 8 }}>
              <Stack spacing={1}>
                <Typography variant="subtitle1">
                  Upload assessment spreadsheet
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Accepted formats: .csv, .xlsx, .xls · Include student name,
                  email, score, and question level details where possible.
                </Typography>
                {file ? (
                  <Typography variant="body2" color="primary">
                    Selected file: {file.name}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Stack direction="row" justifyContent="flex-end" spacing={1}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUploadRoundedIcon />}
                >
                  Choose file
                  <input
                    hidden
                    type="file"
                    accept=".csv, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    onChange={(event) => {
                      const selected = event.target.files?.[0];
                      if (selected) {
                        setFile(selected);
                        setResult(null);
                      }
                    }}
                  />
                </Button>
                <Button
                  variant="contained"
                  onClick={handleUpload}
                  disabled={loading}
                  startIcon={
                    loading ? (
                      <CircularProgress size={18} color="inherit" />
                    ) : undefined
                  }
                >
                  {loading ? "Processing…" : "Process & email"}
                </Button>
              </Stack>
            </Grid>
          </Grid>
        </Paper>

        {error ? <Alert severity="error">{error}</Alert> : null}

        {result ? (
          <Stack spacing={3}>
            <Alert severity="success">
              Assessment processed. {result.emails_sent} personalised study packs
              sent to learners.
            </Alert>

            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 4 }}>
                <MetricCard
                  label="Total Learners"
                  value={result.total_students}
                  caption="Rows processed from the uploaded sheet"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <MetricCard
                  label="Average Score"
                  value={`${result.average_score.toFixed(1)}%`}
                  caption="Class-wide average"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <MetricCard
                  label="Emails Sent"
                  value={result.emails_sent}
                  caption="Study guides delivered automatically"
                />
              </Grid>
            </Grid>

            <Divider />

            <Box>
              <Typography variant="h6" gutterBottom>
                Email delivery report
              </Typography>
              {result.email_results?.length ? (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {Object.keys(result.email_results[0]).map((key) => (
                        <TableCell key={key}>
                          {key.replace(/_/g, " ")}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {result.email_results.map((row, index) => (
                      <TableRow key={`email-row-${index}`}>
                        {Object.values(row).map((value, cellIndex) => (
                          <TableCell
                            key={`cell-${cellIndex}`}
                            sx={
                              typeof value === "string" && value.includes("✅")
                                ? { color: "success.main", fontWeight: 600 }
                                : typeof value === "string" && value.includes("❌")
                                ? { color: "error.main", fontWeight: 600 }
                                : undefined
                            }
                          >
                            {String(value)}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No emails were sent. Everyone scored above the threshold—great work!
                </Typography>
              )}
            </Box>

            <Divider />

            <Box>
              <Typography variant="h6" gutterBottom>
                Most challenging questions
              </Typography>
              {result.weak_questions?.length ? (
                <Stack spacing={2}>
                  {result.weak_questions.map((question, index) => (
                    <Paper
                      key={`weak-question-${index}`}
                      variant="outlined"
                      sx={{ p: 2, borderRadius: 2 }}
                    >
                      <Typography variant="subtitle2" color="primary">
                        Success rate: {question.success_rate.toFixed(1)}%
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ whiteSpace: "pre-wrap", mt: 1 }}
                      >
                        {question.question}
                      </Typography>
                    </Paper>
                  ))}
                </Stack>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No weak questions detected for this cohort.
                </Typography>
              )}
            </Box>
          </Stack>
        ) : null}
      </Stack>
    </SectionCard>
  );
};

export default PersonalizedLearning;
