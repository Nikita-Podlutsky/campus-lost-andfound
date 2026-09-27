import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import SearchIcon from '@mui/icons-material/Search';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
}

export function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <TextField
      fullWidth
      placeholder="Например, чёрный рюкзак"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      slotProps={{
        input: {
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon color="action" />
            </InputAdornment>
          ),
        },
      }}
    />
  );
}


export function filterListings<T extends { description: string }>(
  listings: T[],
  query: string,
): T[] {
  const q = query.trim().toLowerCase();
  if (!q) return listings;
  return listings.filter((l) => l.description.toLowerCase().includes(q));
}
