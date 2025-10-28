import type { ReactElement, SyntheticEvent } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Container,
  LinearProgress,
  Paper,
  Stack,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import EmojiObjectsRoundedIcon from "@mui/icons-material/EmojiObjectsRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";

import DataConfigurationPanel from "./components/DataConfigurationPanel";
import AssessmentCreator from "./sections/AssessmentCreator";
import LessonPlanner from "./sections/LessonPlanner";
import ContentGenerator from "./sections/ContentGenerator";
import PersonalizedLearning from "./sections/PersonalizedLearning";
import MetricCard from "./components/MetricCard";
import StatusPill from "./components/StatusPill";
import { get, postJson } from "./api/client";
import type { HealthStatus, LocationData } from "./types";

import tataStriveLogo from "./assets/tata-strive-logo.png";

type TabValue = "assessment" | "lesson" | "content" | "personalized";

const TAB_CONFIG: Array<{
  label: string;
  value: TabValue;
  icon: ReactElement;
}> = [
  {
    label: "Assessment Creator",
    value: "assessment",
    icon: <InsightsRoundedIcon />,
  },
  {
    label: "Lesson Planner",
    value: "lesson",
    icon: <EmojiObjectsRoundedIcon />,
  },
  {
    label: "Content Generator",
    value: "content",
    icon: <AutoAwesomeRoundedIcon />,
  },
  {
    label: "Personalized Learning",
    value: "personalized",
    icon: <GroupsRoundedIcon />,
  },
];

interface DocumentsResponse {
  documents: string[];
  total_count?: number;
}

const gradientBackground =
  "linear-gradient(130deg, #02203b 0%, #0b5cab 40%, #13c4a3 100%)";

const App = () => {
  const [activeTab, setActiveTab] = useState<TabValue>("assessment");
  const [documents, setDocuments] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [location, setLocation] = useState<LocationData | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [dataStatus, setDataStatus] = useState({
    courses: false,
    holidays: false,
    guidelines: false,
    documentCount: 0,
  });
  const [locationSource, setLocationSource] = useState<
    "unknown" | "ip" | "browser"
  >("unknown");
  const [geolocationDenied, setGeolocationDenied] = useState(false);

  const fetchLocation = useCallback(
    async (coords?: { lat: number; lon: number }) => {
      try {
        const payload = coords
          ? { lat: coords.lat, lon: coords.lon }
          : {};
        const response = await postJson<LocationData>(
          "/detect_location",
          payload
        );
        if (response.kind === "json") {
          setLocation(response.data);
          setLocationSource(coords ? "browser" : "ip");
          if (coords) {
            setGeolocationDenied(false);
          }
        }
      } catch (locationError) {
        if (coords) {
          setGeolocationDenied(true);
        } else {
          setLocationSource("unknown");
        }
        console.warn("Location lookup failed", locationError);
      }
    },
    []
  );

  useEffect(() => {
    const initialise = async () => {
      try {
        setLoading(true);
        setError(null);

        const [docs, healthRes] = await Promise.all([
          get<DocumentsResponse>("/get_documents"),
          get<HealthStatus>("/health").catch(() => null),
        ]);

        setDocuments(docs?.documents || []);
        setDataStatus((prev) => ({
          ...prev,
          documentCount: docs?.documents?.length || 0,
        }));

        if (healthRes) {
          setHealth(healthRes);
          setDataStatus((prev) => ({
            ...prev,
            courses: (healthRes.courses_loaded || 0) > 0,
            holidays: (healthRes.states_with_holidays || 0) > 0,
            guidelines: Boolean(healthRes.guidelines_loaded),
          }));
        }

        await fetchLocation();
      } catch (initialisationError) {
        setError(
          initialisationError instanceof Error
            ? initialisationError.message
            : "Unable to load initial data."
        );
      } finally {
        setLoading(false);
      }
    };

    initialise();
  }, [fetchLocation]);

  useEffect(() => {
    if (!("geolocation" in navigator)) {
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        fetchLocation({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
      },
      (geoError) => {
        if (geoError.code === geoError.PERMISSION_DENIED) {
          setGeolocationDenied(true);
        }
      },
      { enableHighAccuracy: false, timeout: 10000 }
    );
  }, [fetchLocation]);

  const handleTabChange = (_: SyntheticEvent, value: TabValue) => {
    setActiveTab(value);
  };

  const handleStatusChange = (update: Partial<typeof dataStatus>) => {
    setDataStatus((prev) => ({ ...prev, ...update }));
  };

  const suggestedLanguage = useMemo(
    () => location?.suggested_language || "English",
    [location]
  );
  const suggestedState = useMemo(
    () => location?.location?.state || "Corporate",
    [location]
  );

  const locationSourceSuffix =
    locationSource === "browser"
      ? " (browser)"
      : locationSource === "ip"
      ? " (IP lookup)"
      : "";
  const locationDescription = location?.location?.detected
    ? `Detected: ${location.location.city || "Your city"}, ${
        location.location.state || "India"
      }${locationSourceSuffix}`
    : "Location not detected. Defaults applied.";

  const renderActiveTab = () => {
    switch (activeTab) {
      case "assessment":
        return (
          <AssessmentCreator
            documents={documents}
            suggestedLanguage={suggestedLanguage}
          />
        );
      case "lesson":
        return (
          <LessonPlanner
            documents={documents}
            suggestedLanguage={suggestedLanguage}
            suggestedState={suggestedState}
            coursesLoaded={dataStatus.courses}
            holidaysLoaded={dataStatus.holidays}
          />
        );
      case "content":
        return (
          <ContentGenerator
            documents={documents}
            suggestedLanguage={suggestedLanguage}
          />
        );
      case "personalized":
        return <PersonalizedLearning />;
      default:
        return null;
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "radial-gradient(circle at 10% 20%, #f0f7ff 0%, #ffffff 80%)",
        pb: 8,
      }}
    >
      <Container maxWidth="xl" sx={{ pt: { xs: 6, md: 8 } }}>
        {loading ? (
          <LinearProgress
            sx={{
              mb: 4,
              "& .MuiLinearProgress-bar": { backgroundColor: "primary.main" },
            }}
          />
        ) : null}

        <Stack spacing={5}>
          <Paper
            elevation={0}
            sx={{
              position: "relative",
              borderRadius: 5,
              overflow: "hidden",
              background: gradientBackground,
              color: "#ffffff",
              px: { xs: 4, md: 6 },
              py: { xs: 5, md: 7 },
            }}
          >
            <Box
              sx={{
                position: "absolute",
                inset: 0,
                background:
                  "radial-gradient(circle at 65% 18%, rgba(255,255,255,0.45), transparent 58%)",
                opacity: 0.8,
                mixBlendMode: "screen",
              }}
            />
            <Box
              sx={{
                position: "relative",
                zIndex: 1,
                display: "flex",
                flexDirection: { xs: "column", md: "row" },
                alignItems: "center",
                gap: { xs: 4, md: 5 },
              }}
            >
              <Box
                sx={{
                  flexShrink: 0,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  p: { xs: 1.5, md: 2.25 },
                  borderRadius: 4,
                  backgroundColor: "rgba(255,255,255,0.24)",
                  backdropFilter: "blur(8px)",
                  boxShadow: "0 22px 44px rgba(6, 32, 59, 0.3)",
                  border: "1px solid rgba(255,255,255,0.35)",
                }}
              >
                <Box
                  component="img"
                  src={tataStriveLogo}
                  alt="Tata Strive logo"
                  sx={{
                    width: { xs: 140, md: 165 },
                    height: "auto",
                    maxWidth: "100%",
                  }}
                />
              </Box>
              <Box
                sx={{
                  backgroundColor: "rgba(255,255,255,0.18)",
                  backdropFilter: "blur(16px)",
                  borderRadius: 4,
                  px: { xs: 3, md: 4 },
                  py: { xs: 3, md: 3.5 },
                  boxShadow: "0 20px 48px rgba(4, 29, 56, 0.28)",
                  maxWidth: { xs: "100%", md: 580 },
                }}
              >
                <Stack spacing={1.5}>
                  <Typography
                    variant="overline"
                    sx={{
                      color: "rgba(8,29,56,0.75)",
                      letterSpacing: "0.24em",
                      fontWeight: 600,
                    }}
                  >
                    Tata Strive
                  </Typography>
                  <Typography
                    variant="h4"
                    sx={{ fontWeight: 700, color: "#082848" }}
                  >
                    AI Agent Toolkit
                  </Typography>
                  <Typography
                    variant="subtitle1"
                    sx={{
                      color: "rgba(16, 24, 40, 0.82)",
                      lineHeight: 1.5,
                    }}
                  >
                    Craft assessments, lesson plans, facilitator notes, and personalised
                    learning journeys within minutes—grounded in Tata Strive’s
                    learning ecosystem.
                  </Typography>
                </Stack>
              </Box>
            </Box>
            <Box
              sx={{
                mt: { xs: 4, md: 6 },
                display: "grid",
                gap: 3,
                gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
              }}
            >
              <Box>
                <MetricCard
                  label="Knowledge base docs"
                  value={dataStatus.documentCount}
                  caption="Pinecone indexed records"
                />
              </Box>
              <Box>
                <MetricCard
                  label="Courses configured"
                  value={dataStatus.courses ? "Ready" : "Pending"}
                  caption={
                    health?.courses_loaded
                      ? `${health.courses_loaded} uploaded`
                      : "Upload course CSV"
                  }
                />
              </Box>
              <Box>
                <Stack spacing={1.5}>
                  <Typography variant="subtitle2" sx={{ opacity: 0.7 }}>
                    Experience defaults
                  </Typography>
                  <StatusPill
                    label={locationDescription}
                    active={Boolean(location?.location?.detected)}
                    color="primary"
                  />
                  <StatusPill
                    label={`Suggested language: ${suggestedLanguage}`}
                    active
                    color="primary"
                  />
                  {geolocationDenied ? (
                    <StatusPill
                      label="Browser location blocked (using IP estimate)"
                      active
                      color="warning"
                    />
                  ) : null}
                </Stack>
              </Box>
            </Box>
          </Paper>

          {error ? <Alert severity="error">{error}</Alert> : null}

          <Box sx={{ display: "grid", gap: 4, gridTemplateColumns: { xs: "1fr", lg: "minmax(0, 420px) 1fr" } }}>
            <Box>
              <DataConfigurationPanel
                statuses={dataStatus}
                onStatusChange={handleStatusChange}
              />
            </Box>
            <Box>
              <Paper
                elevation={0}
                sx={{
                  p: { xs: 2, md: 3 },
                  borderRadius: 4,
                  background:
                    "linear-gradient(180deg, rgba(242,246,255,0.9) 0%, #ffffff 100%)",
                }}
              >
                <Tabs
                  value={activeTab}
                  onChange={handleTabChange}
                  variant="scrollable"
                  scrollButtons="auto"
                  sx={{
                    "& .MuiTabs-indicator": { height: 4, borderRadius: 2 },
                    mb: 3,
                  }}
                >
                  {TAB_CONFIG.map((tab) => (
                    <Tab
                      key={tab.value}
                      value={tab.value}
                      label={tab.label}
                      icon={tab.icon}
                      iconPosition="start"
                      sx={{ alignItems: "center", gap: 1.5 }}
                    />
                  ))}
                </Tabs>
                {renderActiveTab()}
              </Paper>
            </Box>
          </Box>
        </Stack>
      </Container>
    </Box>
  );
};

export default App;
