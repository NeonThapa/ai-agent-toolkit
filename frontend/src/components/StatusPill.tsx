import { Chip } from "@mui/material";

interface StatusPillProps {
  label: string;
  active?: boolean;
  color?: "primary" | "default" | "success" | "warning";
}

export const StatusPill = ({
  label,
  active = false,
  color = "primary",
}: StatusPillProps) => {
  return (
    <Chip
      label={label}
      color={active ? color : "default"}
      variant={active ? "filled" : "outlined"}
      sx={{
        fontWeight: 600,
        borderRadius: 999,
        px: 1.5,
        background: active ? undefined : "rgba(15, 23, 42, 0.06)",
      }}
    />
  );
};

export default StatusPill;
