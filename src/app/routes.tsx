import { Routes, Route } from 'react-router-dom';
import { HomePage } from '../pages/HomePage';
import { ReportPage } from '../pages/ReportPage';
import type { Listing } from '../entities/listing';

interface AppRoutesProps {
  listings: Listing[];
  onPublish: (listing: Listing) => void;
}

export function AppRoutes({ listings, onPublish }: AppRoutesProps) {
  return (
    <Routes>
      <Route path="/" element={<HomePage listings={listings} />} />
      <Route path="/report" element={<ReportPage onPublish={onPublish} />} />
    </Routes>
  );
}
