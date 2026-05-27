export const createLeaf = (text, marks = {}) => {
  return ['span', { 'data-type': 'leaf', ...marks }, text];
};

export const createTextSpan = (children) => {
  return ['span', { 'data-type': 'text' }, ...children];
};

export const createParagraph = (attrs = {}, children = []) => {
  const content = children.length ? children : [createLeaf('')];
  return ['p', attrs, createTextSpan(content)];
};

export const createHeading = (level, attrs = {}, children = []) => {
  const content = children.length ? children : [createLeaf('')];
  return ['heading', { level, ...attrs }, createTextSpan(content)];
};

export const createList = (type, attrs = {}, items = []) => {
  return ['list', { type, ...attrs }, ...items];
};

export const createListItem = (children = []) => {
  const content = children.length ? children : [createLeaf('')];
  return ['list-item', {}, createTextSpan(content)];
};

export const createQuote = (attrs = {}, children = []) => {
  const content = children.length ? children : [createLeaf('')];
  return ['quote', attrs, createTextSpan(content)];
};

export const createCodeBlock = (text, marks = {}) => {
  return ['code-block', {}, createTextSpan([createLeaf(text, { code: true, ...marks })])];
};

export const createImage = (src, alt = '', width = null, height = null) => {
  return ['image', { src, alt, width, height }];
};

export const createDivider = () => {
  return ['divider', {}];
};

export const createLink = (href, children = []) => {
  return ['link', { href }, createTextSpan(children)];
};

export const createTable = (rows = [], colsWidth = []) => {
  return ['table', { colsWidth }, ...rows];
};

export const createTableRow = (cells = []) => {
  return ['tr', {}, ...cells];
};

export const createTableCell = (children = [], rowSpan = 1, colSpan = 1) => {
  const content = children.length ? children : [createLeaf('')];
  return ['tc', { rowSpan, colSpan }, ...content];
};

export const createEmptyDocument = () => {
  return ['root', {}, createParagraph()];
};

export const createSimpleDocument = (text) => {
  if (!text || !text.trim()) {
    return createEmptyDocument();
  }

  const paragraphs = text.split('\n').filter((p) => p.trim());

  if (paragraphs.length === 0) {
    return createEmptyDocument();
  }

  return [
    'root',
    {},
    ...paragraphs.map((p) => createParagraph({}, [createLeaf(p)])),
  ];
};

export const createRoot = (children = []) => {
  if (children.length === 0) {
    return createEmptyDocument();
  }
  return ['root', {}, ...children];
};
