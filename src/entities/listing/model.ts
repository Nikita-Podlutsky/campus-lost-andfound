export type ListingType = 'lost' | 'found';

export interface Listing {
  id: string;
  type: ListingType;
  title: string;
  description: string;
  photoUrl: string;
  location: string;
  createdAt: string;
  
  x: number;
  y: number;
}
