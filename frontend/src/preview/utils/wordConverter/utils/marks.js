import { normalizeColor } from './color.js';
import { parseFontSize, parseFontFamily } from './style.js';
import { FONT_SIZE_MAP } from '../config.js';

const STYLE_HANDLERS = {
  'font-weight': (value, marks) => {
    if (value === 'bold' || parseInt(value) >= 700) {
      marks.bold = true;
    }
  },
  'font-style': (value, marks) => {
    if (value === 'italic') {
      marks.italic = true;
    }
  },
  'text-decoration': (value, marks) => {
    if (value.includes('underline')) {
      marks.underline = true;
    }
    if (value.includes('line-through')) {
      marks.strikethrough = true;
    }
  },
  color: (value, marks) => {
    const normalized = normalizeColor(value);
    if (normalized) {
      marks.color = normalized;
    }
  },
  'font-size': (value, marks) => {
    const sizeInfo = parseFontSize(value);
    if (sizeInfo) {
      marks.sz = sizeInfo.sz;
      marks.szUnit = sizeInfo.szUnit;
    }
  },
  'background-color': (value, marks) => {
    const normalized = normalizeColor(value);
    if (normalized) {
      marks.backgroundColor = normalized;
    }
  },
  background: (value, marks) => {
    const normalized = normalizeColor(value);
    if (normalized) {
      marks.backgroundColor = normalized;
    }
  },
  'font-family': (value, marks) => {
    const fonts = parseFontFamily(value);
    if (fonts) {
      marks.fonts = fonts;
    }
  },
  'text-align': (value, marks) => {
    marks.align = value.toLowerCase();
  },
};

const TAG_MARKS = {
  STRONG: { bold: true },
  B: { bold: true },
  EM: { italic: true },
  I: { italic: true },
  U: { underline: true },
  S: { strikethrough: true },
  STRIKE: { strikethrough: true },
  DEL: { strikethrough: true },
  SUP: { sup: true },
  SUB: { sub: true },
  MARK: { highlight: true },
};

export const getTagMarks = (tagName) => {
  return TAG_MARKS[tagName] || {};
};

export const getStyleMarks = (style) => {
  const marks = {};
  if (!style) return marks;

  const stylePairs = style.split(';').filter((s) => s.trim());

  for (const pair of stylePairs) {
    const [key, value] = pair.split(':').map((s) => s.trim());
    if (!key || !value) continue;

    const handler = STYLE_HANDLERS[key.toLowerCase()];
    if (handler) {
      handler(value, marks);
    }
  }

  return marks;
};

export const getFontMarks = (node) => {
  const marks = {};

  const color = node.getAttribute('color');
  if (color) {
    const normalized = normalizeColor(color);
    if (normalized) {
      marks.color = normalized;
    }
  }

  const size = node.getAttribute('size');
  if (size) {
    if (FONT_SIZE_MAP[size]) {
      marks.sz = FONT_SIZE_MAP[size];
      marks.szUnit = 'pt';
    } else {
      const numSize = parseInt(size);
      if (!isNaN(numSize)) {
        marks.sz = numSize * 2;
        marks.szUnit = 'pt';
      }
    }
  }

  const face = node.getAttribute('face');
  if (face) {
    const fonts = parseFontFamily(face);
    if (fonts) {
      marks.fonts = fonts;
    }
  }

  return marks;
};

export const getInlineMarks = (node) => {
  const marks = { ...getTagMarks(node.tagName) };

  const style = node.getAttribute('style') || '';
  const styleMarks = getStyleMarks(style);
  Object.assign(marks, styleMarks);

  if (node.tagName === 'FONT') {
    const fontMarks = getFontMarks(node);
    Object.assign(marks, fontMarks);
  }

  return marks;
};
