import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Alert from '@mui/material/Alert';
import Stack from '@mui/material/Stack';
import CircularProgress from '@mui/material/CircularProgress';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { PhotoCapture } from '../../features/report-listing/PhotoCapture';
import { DescriptionForm, type DescriptionFormValues } from '../../features/report-listing/DescriptionForm';
import { useGeoPin } from '../../features/report-listing/useGeoPin';
import type { Listing } from '../../entities/listing';

const PLACEHOLDER_PHOTO =
  'https://images.unsplash.com/photo-1587574293340-e0011c4e8ecf?w=400';

interface ReportPageProps {
  onPublish: (listing: Listing) => void;
}

export function ReportPage({ onPublish }: ReportPageProps) {
  const navigate = useNavigate();
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [values, setValues] = useState<DescriptionFormValues>({
    title: '',
    description: '',
    location: '',
  });
  const [error, setError] = useState<string | null>(null);


  const { status: geoStatus, pin, error: geoError, requestPin } = useGeoPin();

  useEffect(() => {
    requestPin();
  }, []);

  function handlePublish() {
    if (!values.title.trim() || !values.description.trim() || !values.location.trim()) {
      setError('Заполните название, описание и место находки.');
      return;
    }
    setError(null);

    const mapPosition = pin ?? { x: 20 + Math.random() * 60, y: 20 + Math.random() * 60 };

    const newListing: Listing = {
      id: crypto.randomUUID(),
      type: 'found',
      title: values.title.trim(),
      description: values.description.trim(),
      photoUrl: photoUrl ?? PLACEHOLDER_PHOTO,
      location: values.location.trim(),
      createdAt: new Date().toISOString(),
      x: mapPosition.x,
      y: mapPosition.y,
    };

    onPublish(newListing);
    navigate('/');
  }

  return (
    <Container maxWidth="sm" sx={{ pt: 2, pb: 6 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <IconButton aria-label="Назад" onClick={() => navigate('/')}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h5" component="h1" sx={{ fontWeight: 600 }}>
          Отметить находку
        </Typography>
      </Box>

      <Stack spacing={3}>
        <PhotoCapture photoUrl={photoUrl} onPhotoSelected={setPhotoUrl} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {geoStatus === 'loading' && (
            <>
              <CircularProgress size={16} />
              <Typography variant="caption" color="text.secondary">
                Определяем метку на карте по геолокации…
              </Typography>
            </>
          )}
          {geoStatus === 'success' && (
            <>
              <LocationOnIcon fontSize="small" color="primary" />
              <Typography variant="caption" color="text.secondary">
                Метка на карте определена по вашей геолокации
              </Typography>
            </>
          )}
          {geoStatus === 'error' && (
            <Alert severity="warning" sx={{ width: '100%' }}>
              {geoError} Название места находки укажите ниже вручную - оно не
              зависит от геолокации.
            </Alert>
          )}
        </Box>

        <DescriptionForm values={values} onChange={setValues} />

        {error && <Alert severity="error">{error}</Alert>}

        <Button variant="contained" size="large" onClick={handlePublish}>
          Опубликовать
        </Button>
      </Stack>
    </Container>
  );
}
