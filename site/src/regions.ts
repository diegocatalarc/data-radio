export type RegionKey = 'cl' | 'au' | 'nz' | 'eu';

export interface Region {
  key: RegionKey;
  name: string;
  short: string;
  lat: number;
  lon: number;
  blurb: string;
}

export const regions: Region[] = [
  { key: 'cl', name: 'Chile', short: 'Chile', lat: -33.45, lon: -70.67,
    blurb: 'Analítica, datos y regulación en el mercado chileno.' },
  { key: 'au', name: 'Australia', short: 'Australia', lat: -33.87, lon: 151.21,
    blurb: 'Del sector financiero a la minería: cómo se usa y se regula el dato.' },
  { key: 'nz', name: 'Nueva Zelanda', short: 'N. Zelanda', lat: -41.29, lon: 174.78,
    blurb: 'Un mercado pequeño y ágil: gobierno de datos, IA y talento en Aotearoa.' },
  { key: 'eu', name: 'Países Bajos & Europa', short: 'Europa', lat: 52.37, lon: 4.9,
    blurb: 'De Ámsterdam a Bruselas: regulación, infraestructura y talento de datos.' },
];

export const regionByKey = Object.fromEntries(regions.map((r) => [r.key, r])) as Record<RegionKey, Region>;
