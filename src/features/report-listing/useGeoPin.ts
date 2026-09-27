import { useState } from 'react';

type GeoStatus = 'idle' | 'loading' | 'success' | 'error';

interface GeoResult {
  x: number;
  y: number;
}


export function useGeoPin() {
  const [status, setStatus] = useState<GeoStatus>('idle');
  const [pin, setPin] = useState<GeoResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  function requestPin() {
    if (!navigator.geolocation) {
      setStatus('error');
      setError('Геолокация не поддерживается браузером.');
      return;
    }

    setStatus('loading');
    setError(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { coordsToMapPosition } = await import('../../entities/listing/campusBuildings');
        const { latitude, longitude } = position.coords;
        setPin(coordsToMapPosition(latitude, longitude));
        setStatus('success');
      },
      () => {
        setStatus('error');
        setError('Не удалось определить местоположение. Точка будет выбрана случайно.');
      },
      { enableHighAccuracy: true, timeout: 8000 },
    );
  }

  return { status, pin, error, requestPin };
}
