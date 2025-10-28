import { useMemo, useState } from "react";
import {
  Autocomplete,
  Box,
  Chip,
  TextField,
  Typography,
  Stack,
} from "@mui/material";

interface DocumentSelectorProps {
  title: string;
  description?: string;
  documents: string[];
  value: string[];
  onChange: (docs: string[]) => void;
}

export const DocumentSelector = ({
  title,
  description,
  documents,
  value,
  onChange,
}: DocumentSelectorProps) => {
  const [search, setSearch] = useState("");

  const filteredDocs = useMemo(() => {
    if (!search) {
      return documents;
    }
    const term = search.toLowerCase();
    return documents.filter((doc) => doc.toLowerCase().includes(term));
  }, [documents, search]);

  return (
    <Box mb={3}>
      <Stack spacing={1.5}>
        <Typography variant="h6">{title}</Typography>
        {description ? (
          <Typography variant="body2" color="text.secondary">
            {description}
          </Typography>
        ) : null}
        <Autocomplete
          multiple
          options={filteredDocs}
          value={value}
          onChange={(_, newValue) => {
            onChange(newValue);
          }}
          onInputChange={(_, newInputValue) => setSearch(newInputValue)}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Select source documents"
              placeholder="Search and select documents"
            />
          )}
          renderTags={(tagValue, getTagProps) =>
            tagValue.map((option, index) => (
              <Chip
                label={option}
                {...getTagProps({ index })}
                key={option}
                sx={{ maxWidth: 220 }}
              />
            ))
          }
          sx={{
            "& .MuiChip-root": {
              background: "rgba(0,176,255,0.08)",
              color: "primary.main",
            },
          }}
        />
        <Typography variant="caption" color="text.secondary">
          Tip: Start typing to quickly filter through long document lists.
        </Typography>
      </Stack>
    </Box>
  );
};

export default DocumentSelector;
