import { createTable, createTableRow, createTableCell } from '../factory.js';
import { parseInlineNodes } from './inlineParser.js';

export const parseTable = (tableNode, context = {}) => {
  const rows = [];
  const colWidths = [];
  const trNodes = tableNode.querySelectorAll('tr');

  for (const tr of trNodes) {
    const cells = [];
    const tdNodes = tr.querySelectorAll('td, th');

    for (const td of tdNodes) {
      const cellChildren = parseInlineNodes(td.childNodes, {}, context);
      const rowSpan = parseInt(td.getAttribute('rowspan')) || 1;
      const colSpan = parseInt(td.getAttribute('colspan')) || 1;
      cells.push(createTableCell(cellChildren, rowSpan, colSpan));
    }

    if (cells.length > 0) {
      rows.push(createTableRow(cells));
      // 计算列宽（取第一行的列数）
      if (colWidths.length === 0) {
        for (let i = 0; i < cells.length; i++) {
          colWidths.push(200); // 默认宽度
        }
      }
    }
  }

  if (rows.length === 0) {
    return null;
  }

  return createTable(rows, colWidths);
};