export const colors = {
  // Brand
  primary: '#4A90D9',
  primaryLight: '#7AB3F0',

  // Surfaces
  background: '#F8F9FA',
  card: '#FFFFFF',
  overlay: 'rgba(0, 0, 0, 0.5)',

  // Text
  text: '#1A1A2E',
  textSecondary: '#6B7280',
  placeholder: '#9CA3AF',
  onBrand: '#FFFFFF',

  // Borders & dividers
  border: '#E5E7EB',

  // Shadow
  shadow: '#000000',

  // Scrim
  scrim: 'rgba(0, 0, 0, 0.3)',

  // Semantic states
  success: '#22C55E',
  successBg: 'rgba(34,197,94,0.15)',
  warning: '#F59E0B',
  warningBg: 'rgba(245,158,11,0.15)',
  error: '#EF4444',
  errorBg: 'rgba(239,68,68,0.1)',
  info: '#3B82F6',
} as const;

export type AppColors = typeof colors;
