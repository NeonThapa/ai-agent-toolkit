import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Divider,
  Stack,
  Typography,
  Paper,
} from "@mui/material";
import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import CloudDoneRoundedIcon from "@mui/icons-material/CloudDoneRounded";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

import SectionCard from "./SectionCard";
import StatusPill from "./StatusPill";
import { postFormData } from "../api/client";

type UploadType = "courses" | "holidays" | "guidelines";

interface DataConfigurationPanelProps {
  statuses: {
    courses: boolean;
    holidays: boolean;
    guidelines: boolean;
    documentCount: number;
  };
  onStatusChange: (update: Partial<DataConfigurationPanelProps["statuses"]>) => void;
}

const uploadConfig: Record<
  UploadType,
  {
    label: string;
    description: string;
    accept: string;
    endpoint: string;
    successMessage: (payload: Record<string, unknown>) => string;
  }
> = {
  courses: {
    label: "Course duration data",
    description:
      "Upload the CSV that lists course durations, theory hours, and eligibility criteria.",
    accept: ".csv",
    endpoint: "/upload/course_data",
    successMessage: (payload) =>
      `Loaded ${payload.courses_loaded || payload.records_loaded || "the uploaded"} courses.`,
  },
  holidays: {
    label: "Holiday calendar",
    description:
      "Upload the CSV containing state-wise holidays to avoid scheduling sessions on those dates.",
    accept: ".csv",
    endpoint: "/upload/holidays",
    successMessage: (payload) =>
      `Loaded holiday data for ${payload.states_loaded || payload.regions_loaded || "the uploaded"} regions.`,
  },
  guidelines: {
    label: "Assessment guidelines",
    description:
      "Upload the textual guidelines (TXT format) that should shape question difficulty and structure.",
    accept: ".txt",
    endpoint: "/upload/guidelines",
    successMessage: (payload) =>
      `Guidelines imported (${payload.guidelines_length || "unknown"} characters).`,
  },
};

export const DataConfigurationPanel = ({
  statuses,
  onStatusChange,
}: DataConfigurationPanelProps) => {
  const [uploading, setUploading] = useState<Record<UploadType, boolean>>({
    courses: false,
    holidays: false,
    guidelines: false,
  });
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (type: UploadType, file: File) => {
    const config = uploadConfig[type];
    setUploading((prev) => ({ ...prev, [type]: true }));
    setMessage(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await postFormData<Record<string, unknown>>(
        config.endpoint,
        formData
      );
      onStatusChange({ [type]: true });
      setMessage(config.successMessage(response));
    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "Upload failed. Please try again."
      );
    } finally {
      setUploading((prev) => ({ ...prev, [type]: false }));
    }
  };

  return (
    <SectionCard
      title="System Configuration"
      subtitle="Upload once, reuse forever. The data stays active until the server restarts."
      gutterBottom={false}
      icon={<InfoOutlinedIcon color="primary" fontSize="large" />}
    >
      <Stack spacing={3}>
        <Box display="flex" flexWrap="wrap" gap={1}>
          <StatusPill
            label={`${statuses.documentCount} knowledge base docs`}
            active={statuses.documentCount > 0}
            color="primary"
          />
          <StatusPill
            label={statuses.courses ? "Courses ready" : "Courses pending"}
            active={statuses.courses}
            color="success"
          />
          <StatusPill
            label={statuses.holidays ? "Holidays ready" : "Holidays pending"}
            active={statuses.holidays}
            color="success"
          />
          <StatusPill
            label={
              statuses.guidelines ? "Assessment guidelines set" : "Guidelines pending"
            }
            active={statuses.guidelines}
            color="success"
          />
        </Box>

        <Divider />

        <Stack spacing={3}>
          {(Object.keys(uploadConfig) as UploadType[]).map((type) => {
            const config = uploadConfig[type];
            return (
              <Paper
                key={type}
                variant="outlined"
                sx={{
                  p: 3,
                  background: "rgba(0,176,255,0.04)",
                  borderStyle: "dashed",
                  borderColor: "rgba(0,176,255,0.3)",
                  borderWidth: 2,
                }}
              >
                <Stack spacing={1.5}>
                  <Typography variant="subtitle1">{config.label}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {config.description}
                  </Typography>
                  <Box>
                    <Button
                      variant={statuses[type] ? "outlined" : "contained"}
                      startIcon={
                        statuses[type] ? <CloudDoneRoundedIcon /> : <CloudUploadRoundedIcon />
                      }
                      component="label"
                      disabled={uploading[type]}
                    >
                      {statuses[type] ? "Replace file" : "Upload file"}
                      <input
                        type="file"
                        hidden
                        accept={config.accept}
                        onChange={(event) => {
                          const file = event.target.files?.[0];
                          if (file) {
                            handleUpload(type, file);
                            event.target.value = "";
                          }
                        }}
                      />
                    </Button>
                  </Box>
                </Stack>
              </Paper>
            );
          })}
        </Stack>

        {message ? <Alert severity="success">{message}</Alert> : null}
        {error ? <Alert severity="error">{error}</Alert> : null}
      </Stack>
    </SectionCard>
  );
};

export default DataConfigurationPanel;
