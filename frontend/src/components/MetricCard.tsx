import { Paper, Stack, Typography } from "@mui/material";

interface MetricCardProps {
  label: string;
  value: string | number;
  caption?: string;
}

export const MetricCard = ({ label, value, caption }: MetricCardProps) => {
  return (
    <Paper
      sx={{
        p: 3,
        borderRadius: 16,
        background: "linear-gradient(135deg, rgba(0,176,255,0.12) 0%, #ffffff 100%)",
        border: "1px solid rgba(0, 176, 255, 0.18)",
      }}
      elevation={0}
    >
      <Stack spacing={1}>
        <Typography variant="subtitle2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4">{value}</Typography>
        {caption ? (
          <Typography variant="caption" color="text.secondary">
            {caption}
          </Typography>
        ) : null}
      </Stack>
    </Paper>
  );
};

export default MetricCard;
