import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Box } from "@mui/material";

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer = ({ content }: MarkdownRendererProps) => {
  return (
    <Box
      sx={{
        typography: "body1",
        "& h1": { typography: "h4", mt: 2, mb: 1 },
        "& h2": { typography: "h5", mt: 2, mb: 1 },
        "& h3": { typography: "subtitle1", mt: 2, mb: 1 },
        "& h4, & h5, & h6": { typography: "subtitle2", mt: 2, mb: 1 },
        "& p": { mb: 1.5, lineHeight: 1.7 },
        "& ul, & ol": { pl: 3, mb: 2 },
        "& li": { mb: 0.75 },
        "& table": {
          borderCollapse: "collapse",
          width: "100%",
          mb: 2,
        },
        "& th, & td": {
          border: "1px solid rgba(148, 163, 184, 0.4)",
          p: 1,
          textAlign: "left",
        },
        "& blockquote": {
          borderLeft: "4px solid rgba(0, 176, 255, 0.35)",
          pl: 2,
          color: "text.secondary",
          fontStyle: "italic",
          mb: 2,
        },
        "& code": {
          fontFamily: "Menlo, Consolas, 'Courier New', monospace",
          backgroundColor: "rgba(15, 23, 42, 0.06)",
          px: 0.75,
          py: 0.25,
          borderRadius: 1,
        },
      }}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </Box>
  );
};

export default MarkdownRenderer;
