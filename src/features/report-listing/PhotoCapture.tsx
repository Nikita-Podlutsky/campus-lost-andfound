import { useRef } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import AddAPhotoIcon from '@mui/icons-material/AddAPhoto';

interface PhotoCaptureProps {
  photoUrl: string | null;
  onPhotoSelected: (url: string) => void;
}

export function PhotoCapture({ photoUrl, onPhotoSelected }: PhotoCaptureProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    onPhotoSelected(url);
  }

  return (
    <Box>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        hidden
        onChange={handleFileChange}
      />
      {photoUrl ? (
        <Box
          onClick={() => inputRef.current?.click()}
          sx={{ cursor: 'pointer', position: 'relative' }}
        >
          <Box
            component="img"
            src={photoUrl}
            alt="Выбранное фото"
            sx={{ width: '100%', maxHeight: 260, objectFit: 'cover', borderRadius: 2 }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            Нажмите, чтобы заменить фото
          </Typography>
        </Box>
      ) : (
        <Button
          variant="outlined"
          startIcon={<AddAPhotoIcon />}
          onClick={() => inputRef.current?.click()}
          sx={{ width: '100%', py: 3, borderStyle: 'dashed' }}
        >
          Добавить фото
        </Button>
      )}
    </Box>
  );
}
