export const parseStyleSize = (size) => {
  if (!size) return null;
  const match = size.match(/(\d+)/);
  return match ? parseInt(match[1]) : null;
};

export const parseIndent = (indent) => {
  if (!indent) return null;
  const match = indent.match(/(\d+(?:\.\d+)?)(px|pt|em|%)?/);
  if (match) {
    const val = parseFloat(match[1]);
    const unit = match[2] || 'px';
    if (!isNaN(val)) {
      if (unit === 'pt') {
        return Math.round(val);
      }
      if (unit === 'em') {
        return Math.round(val * 12);
      }
      return Math.round(val / 10);
    }
  }
  return null;
};

export const parseFontSize = (value) => {
  const match = value.match(/(\d+(?:\.\d+)?)(px|pt|em|rem)?/);
  if (!match) return null;

  const size = parseFloat(match[1]);
  const unit = match[2] || 'px';

  if (unit === 'pt') {
    return { sz: size, szUnit: 'pt' };
  }
  if (unit === 'em' || unit === 'rem') {
    return { sz: Math.round(size * 12), szUnit: 'pt' };
  }
  return { sz: Math.round(size * 0.75), szUnit: 'pt' };
};

export const parseFontFamily = (value) => {
  if (!value) return null;
  const fonts = value.replace(/['"]/g, '').split(',').map(s => s.trim()).filter(Boolean);
  if (fonts.length === 0) return null;
  
  const result = {};
  const firstFont = fonts[0];
  
  if (/[\u4e00-\u9fa5]/.test(firstFont)) {
    result.eastAsia = firstFont;
  } else {
    result.ascii = firstFont;
    result.hAnsi = firstFont;
  }
  
  for (const font of fonts) {
    if (/[\u4e00-\u9fa5]/.test(font) && !result.eastAsia) {
      result.eastAsia = font;
    } else if (!result.ascii) {
      result.ascii = font;
      result.hAnsi = font;
    }
  }
  
  return Object.keys(result).length > 0 ? result : null;
};

export const getParagraphAttrs = (node) => {
  const attrs = {};

  const align = node.getAttribute('align') || node.style?.textAlign || node.getAttribute('data-align');
  if (align) {
    attrs.jc = align.toLowerCase();
  }

  const indent = node.style?.textIndent || node.getAttribute('text-indent') || node.getAttribute('data-indent');
  if (indent) {
    const indentValue = parseIndent(indent);
    if (indentValue !== null) {
      attrs.ind = { firstLine: indentValue, firstLineChars: Math.round(indentValue * 7) };
    }
  }

  const leftMargin = node.style?.marginLeft || node.style?.paddingLeft;
  if (leftMargin) {
    const marginIndent = parseIndent(leftMargin);
    if (marginIndent !== null) {
      attrs.ind = attrs.ind || {};
      attrs.ind.left = marginIndent;
    }
  }

  const lineHeight = node.style?.lineHeight;
  if (lineHeight && lineHeight !== 'normal') {
    const lh = parseFloat(lineHeight);
    if (!isNaN(lh)) {
      attrs.spacing = { line: lh, lineRule: 'auto' };
    }
  }

  const fontSize = node.style?.fontSize;
  const fontFamily = node.style?.fontFamily;
  
  if (fontSize || fontFamily) {
    attrs.rPr = {};
    
    if (fontSize) {
      const sizeInfo = parseFontSize(fontSize);
      if (sizeInfo) {
        attrs.rPr.sz = sizeInfo.sz;
        attrs.rPr.szUnit = sizeInfo.szUnit;
      }
    }
    
    if (fontFamily) {
      const fonts = parseFontFamily(fontFamily);
      if (fonts) {
        attrs.rPr.fonts = fonts;
      }
    }
  }

  return Object.keys(attrs).length > 0 ? attrs : {};
};
