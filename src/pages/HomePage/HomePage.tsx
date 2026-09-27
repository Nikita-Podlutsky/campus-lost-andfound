import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Fab from '@mui/material/Fab';
import AddIcon from '@mui/icons-material/Add';
import type { Listing } from '../../entities/listing';
import { MapView } from '../../shared/ui/MapView';
import { ListingCard } from '../../shared/ui/ListingCard';
import { SearchBar, filterListings } from '../../features/search-listings/SearchBar';

interface HomePageProps {
  listings: Listing[];
}

export function HomePage({ listings }: HomePageProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered = useMemo(() => filterListings(listings, query), [listings, query]);

  function handleSelect(id: string) {
    setExpandedId((current) => (current === id ? null : id));
  }

  return (
    <Box sx={{ pb: 10 }}>
      <Container maxWidth="sm" sx={{ pt: 2 }}>
        <Typography variant="h5" component="h1" sx={{ mb: 2, fontWeight: 600 }}>
          Campus Lost &amp; Found
        </Typography>

        <MapView listings={filtered} selectedId={expandedId} onSelect={handleSelect} />

        <Box sx={{ mt: 2, mb: 1 }}>
          <SearchBar value={query} onChange={setQuery} />
        </Box>

        {filtered.length === 0 ? (
          <Typography color="text.secondary" sx={{ mt: 3, textAlign: 'center' }}>
            Ничего не найдено. Попробуйте другой запрос.
          </Typography>
        ) : (
          <Box sx={{ mt: 1 }}>
            {filtered.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                expanded={expandedId === listing.id}
                onToggle={handleSelect}
              />
            ))}
          </Box>
        )}
      </Container>

      <Fab
        color="primary"
        aria-label="Отметить находку"
        onClick={() => navigate('/report')}
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
}
