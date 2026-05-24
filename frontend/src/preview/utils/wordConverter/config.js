export const MAMMOTH_STYLE_MAP = [
  'p[style-name="Heading 1"] => h1:fresh',
  'p[style-name="Heading 2"] => h2:fresh',
  'p[style-name="Heading 3"] => h3:fresh',
  'p[style-name="Heading 4"] => h4:fresh',
  'p[style-name="Heading 5"] => h5:fresh',
  'p[style-name="Heading 6"] => h6:fresh',
  'p[style-name="List Paragraph"] => p:fresh',
  'p[style-name="Quote"] => blockquote:fresh',
  'p[style-name="Title"] => h1.title:fresh',
  'p[style-name="Subtitle"] => h2.subtitle:fresh',
  'b => strong',
  'i => em',
  'u => u',
  'strike => s',
];

export const NAMED_COLORS = {
  red: '#ff0000',
  green: '#008000',
  blue: '#0000ff',
  yellow: '#ffff00',
  black: '#000000',
  white: '#ffffff',
  orange: '#ffa500',
  purple: '#800080',
  pink: '#ffc0cb',
  gray: '#808080',
  grey: '#808080',
  cyan: '#00ffff',
  magenta: '#ff00ff',
};

export const FONT_SIZE_MAP = {
  1: 10,
  2: 12,
  3: 14,
  4: 16,
  5: 18,
  6: 20,
  7: 22,
};

export const MAMMOTH_OPTIONS = {
  styleMap: MAMMOTH_STYLE_MAP,
  includeDefaultStyleMap: true,
  ignoreEmptyParagraphs: false,
};
