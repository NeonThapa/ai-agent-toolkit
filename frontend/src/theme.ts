import { createTheme } from "@mui/material/styles";

const tataBlue = "#00b0ff";
const steelGray = "#1f2933";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: tataBlue,
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#13c4a3",
    },
    background: {
      default: "#f4f7fb",
      paper: "#ffffff",
    },
    text: {
      primary: steelGray,
      secondary: "#4b5563",
    },
  },
  typography: {
    fontFamily: ["'Inter'", "Roboto", "'Segoe UI'", "sans-serif"].join(","),
    h3: {
      fontWeight: 700,
      letterSpacing: "-0.03em",
    },
    h5: {
      fontWeight: 600,
    },
    subtitle2: {
      textTransform: "uppercase",
      letterSpacing: "0.08em",
    },
    button: {
      textTransform: "none",
      fontWeight: 600,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 18,
          boxShadow: "0 24px 48px rgba(15, 23, 42, 0.08)",
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          fontSize: "0.95rem",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

export default theme;
