import type { ReactNode } from "react";
import { Box, Paper, Typography, Divider, Stack } from "@mui/material";

interface SectionCardProps {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  gutterBottom?: boolean;
}

export const SectionCard = ({
  title,
  subtitle,
  icon,
  actions,
  children,
  gutterBottom = true,
}: SectionCardProps) => {
  return (
    <Paper
      sx={{
        p: 4,
        background: "linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%)",
        border: "1px solid rgba(0, 176, 255, 0.12)",
        ...(gutterBottom ? { mb: 4 } : {}),
      }}
    >
      <Stack spacing={3}>
        <Box
          display="flex"
          alignItems={{ xs: "flex-start", md: "center" }}
          flexDirection={{ xs: "column", md: "row" }}
          gap={2}
          justifyContent="space-between"
        >
          <Box display="flex" alignItems="center" gap={2}>
            {icon}
            <Box>
              <Typography variant="h5">{title}</Typography>
              {subtitle ? (
                <Typography variant="body2" color="text.secondary" mt={0.5}>
                  {subtitle}
                </Typography>
              ) : null}
            </Box>
          </Box>
          {actions ? <Box>{actions}</Box> : null}
        </Box>
        <Divider sx={{ borderStyle: "dashed", opacity: 0.4 }} />
        <Box>{children}</Box>
      </Stack>
    </Paper>
  );
};

export default SectionCard;
