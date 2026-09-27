import { useState } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AppRoutes } from './app/routes';
import { mockListings } from './entities/listing';
import type { Listing } from './entities/listing';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#2e7d5b' },
    secondary: { main: '#d97706' },
    background: { default: '#fafaf9' },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: [
      'Inter',
      'system-ui',
      '-apple-system',
      'Segoe UI',
      'Roboto',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  const [listings, setListings] = useState<Listing[]>(mockListings);

  function handlePublish(newListing: Listing) {
    setListings((prev) => [newListing, ...prev]);
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AppRoutes listings={listings} onPublish={handlePublish} />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
