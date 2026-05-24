import { createListItem, createList } from '../factory.js';

export const parseListItems = (listNode, context = {}) => {
  const items = [];
  const liNodes = listNode.querySelectorAll(':scope > li');

  for (const li of liNodes) {
    const liChildren = [];

    for (const child of li.childNodes) {
      if (child.nodeType === Node.TEXT_NODE) {
        const text = child.textContent;
        if (text && text.trim()) {
          liChildren.push(context.createLeaf?.(text) || ['span', { 'data-type': 'leaf' }, text]);
        }
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        const tagName = child.tagName.toLowerCase();

        if (tagName === 'ul' || tagName === 'ol') {
          const nestedList = parseList(child, context);
          liChildren.push(nestedList);
        } else {
          const parsed = context.parseInlineElement?.(child);
          if (parsed) {
            liChildren.push(parsed);
          }
        }
      }
    }

    items.push(createListItem(liChildren));
  }

  return items;
};

export const parseList = (node, context = {}) => {
  const tagName = node.tagName.toLowerCase();
  const type = tagName === 'ul' ? 'bullet' : 'number';
  const items = parseListItems(node, context);
  return createList(type, {}, items);
};
