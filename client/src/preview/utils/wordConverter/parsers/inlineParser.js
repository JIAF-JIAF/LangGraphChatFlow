import { createLeaf, createTextSpan } from '../factory.js';

export const parseInlineNodes = (nodes, inheritedMarks = {}, context = {}) => {
  const result = [];

  for (const node of nodes) {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent;
      if (text) {
        result.push(createLeaf(text, inheritedMarks));
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const parsed = context.parseInlineElement?.(node, inheritedMarks);
      if (parsed) {
        if (Array.isArray(parsed) && Array.isArray(parsed[0])) {
          result.push(...parsed);
        } else {
          result.push(parsed);
        }
      }
    }
  }

  return result;
};

export const mergeSpanChildren = (children, marks = {}) => {
  if (children.length === 0) {
    return [createLeaf('', marks)];
  }

  if (children.length === 1) {
    const child = children[0];
    if (Array.isArray(child) && child[0] === 'span' && child[1]?.['data-type'] === 'leaf') {
      const existingMarks = { ...child[1] };
      delete existingMarks['data-type'];
      return [createLeaf(child[2], { ...existingMarks, ...marks })];
    }
    return children;
  }

  return children;
};
