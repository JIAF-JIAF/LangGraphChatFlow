import { NAMED_COLORS } from '../config.js';

export const normalizeColor = (color) => {
  if (!color) return null;

  color = color.trim().toLowerCase();

  if (color === 'auto' || color === 'inherit' || color === 'initial' || color === 'none') {
    return null;
  }

  if (color.startsWith('#')) {
    if (color.length === 4) {
      return '#' + color[1] + color[1] + color[2] + color[2] + color[3] + color[3];
    }
    return color;
  }

  if (/^[0-9a-f]{6}$/.test(color)) {
    return '#' + color;
  }

  if (/^[0-9a-f]{8}$/.test(color)) {
    return '#' + color.substring(0, 6);
  }

  if (NAMED_COLORS[color]) {
    return NAMED_COLORS[color];
  }

  const rgbMatch = color.match(/rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/i);
  if (rgbMatch) {
    const r = parseInt(rgbMatch[1]).toString(16).padStart(2, '0');
    const g = parseInt(rgbMatch[2]).toString(16).padStart(2, '0');
    const b = parseInt(rgbMatch[3]).toString(16).padStart(2, '0');
    return `#${r}${g}${b}`;
  }

  return null;
};
