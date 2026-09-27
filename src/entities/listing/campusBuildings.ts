
interface CampusAnchor {
  lat: number;
  lng: number;
  x: number;
  y: number;
}

const campusAnchors: CampusAnchor[] = [
  { lat: 55.7223, lng: 37.548, x: 30, y: 40 },
  { lat: 55.7219, lng: 37.5492, x: 55, y: 65 },
  { lat: 55.7229, lng: 37.5486, x: 70, y: 25 },
  { lat: 55.7217, lng: 37.5478, x: 45, y: 80 },
  { lat: 55.7233, lng: 37.547, x: 15, y: 15 },
  { lat: 55.7212, lng: 37.5495, x: 85, y: 70 },
];

function haversineDistance(a: CampusAnchor, lat: number, lng: number): number {
  const R = 6371e3;
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const dLat = toRad(lat - a.lat);
  const dLng = toRad(lng - a.lng);
  const sinLat = Math.sin(dLat / 2);
  const sinLng = Math.sin(dLng / 2);
  const h =
    sinLat * sinLat + Math.cos(toRad(a.lat)) * Math.cos(toRad(lat)) * sinLng * sinLng;
  return 2 * R * Math.asin(Math.sqrt(h));
}


export function coordsToMapPosition(lat: number, lng: number): { x: number; y: number } {
  const nearest = campusAnchors.reduce((closest, anchor) =>
    haversineDistance(anchor, lat, lng) < haversineDistance(closest, lat, lng) ? anchor : closest,
  );
  return { x: nearest.x, y: nearest.y };
}
