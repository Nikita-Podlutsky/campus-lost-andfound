import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PlaceIcon from '@mui/icons-material/Place';
import type { Listing } from '../../entities/listing';

interface ListingCardProps {
  listing: Listing;
  expanded: boolean;
  onToggle: (id: string) => void;
}

export function ListingCard({ listing, expanded, onToggle }: ListingCardProps) {
  const formattedDate = new Date(listing.createdAt).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
  });

  return (
    <Accordion
      expanded={expanded}
      onChange={() => onToggle(listing.id)}
      disableGutters
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
          <Box
            component="img"
            src={listing.photoUrl}
            alt={listing.title}
            sx={{ width: 48, height: 48, borderRadius: 1, objectFit: 'cover', flexShrink: 0 }}
          />
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="subtitle1" noWrap>
              {listing.title}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap component="div">
              {listing.location}
            </Typography>
          </Box>
          <Chip
            label={listing.type === 'found' ? 'Найдено' : 'Потеряно'}
            color={listing.type === 'found' ? 'success' : 'warning'}
            size="small"
          />
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Box
          component="img"
          src={listing.photoUrl}
          alt={listing.title}
          sx={{ width: '100%', maxHeight: 240, objectFit: 'cover', borderRadius: 1, mb: 1.5 }}
        />
        <Typography variant="body2" sx={{ mb: 1 }}>
          {listing.description}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
          <PlaceIcon fontSize="small" />
          <Typography variant="body2">{listing.location}</Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">
          Опубликовано {formattedDate}
        </Typography>
      </AccordionDetails>
    </Accordion>
  );
}
