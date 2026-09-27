import Box from '@mui/material/Box';
import Tooltip from '@mui/material/Tooltip';
import PlaceIcon from '@mui/icons-material/Place';
import type { Listing } from '../../entities/listing';

interface MapViewProps {
  listings: Listing[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function MapView({ listings, selectedId, onSelect }: MapViewProps) {
  return (
    <Box
      sx={{
        position: 'relative',
        width: '100%',
        height: { xs: 220, sm: 320 },
        borderRadius: 2,
        overflow: 'hidden',
        background:
          'repeating-linear-gradient(0deg, #e8ede9 0px, #e8ede9 1px, #f4f7f5 1px, #f4f7f5 40px), repeating-linear-gradient(90deg, #e8ede9 0px, #e8ede9 1px, #f4f7f5 1px, #f4f7f5 40px)',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      {listings.map((listing) => {
        const isSelected = listing.id === selectedId;
        return (
          <Tooltip key={listing.id} title={listing.title} arrow>
            <Box
              component="button"
              onClick={() => onSelect(listing.id)}
              aria-label={`Показать находку: ${listing.title}`}
              sx={{
                position: 'absolute',
                left: `${listing.x}%`,
                top: `${listing.y}%`,
                transform: 'translate(-50%, -100%)',
                background: 'none',
                border: 'none',
                padding: 0,
                cursor: 'pointer',
                color: isSelected ? 'secondary.main' : 'primary.main',
                transition: 'transform 0.15s ease',
                '&:hover': {
                  transform: 'translate(-50%, -100%) scale(1.15)',
                },
              }}
            >
              <PlaceIcon fontSize={isSelected ? 'large' : 'medium'} />
            </Box>
          </Tooltip>
        );
      })}
    </Box>
  );
}
