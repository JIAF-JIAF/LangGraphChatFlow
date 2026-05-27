export {
  convertWordToCangjieFormat,
  createEmptyDocument,
  createSimpleDocument,
  WordConverter,
} from './wordConverter/index.js';

export { HtmlParser, createHtmlParser } from './wordConverter/parsers/index.js';
export { ElementParserRegistry, createParserRegistry } from './wordConverter/parsers/index.js';

export {
  createLeaf,
  createTextSpan,
  createParagraph,
  createHeading,
  createList,
  createListItem,
  createQuote,
  createCodeBlock,
  createImage,
  createDivider,
  createLink,
  createTable,
  createTableRow,
  createTableCell,
  createRoot,
} from './wordConverter/factory.js';

export {
  MAMMOTH_STYLE_MAP,
  MAMMOTH_OPTIONS,
  NAMED_COLORS,
  FONT_SIZE_MAP,
} from './wordConverter/config.js';
