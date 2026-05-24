import { getParagraphAttrs, getInlineMarks, parseStyleSize } from '../utils/index.js';
import { createLeaf, createParagraph, createHeading, createQuote, createCodeBlock, createImage, createDivider, createLink, createTextSpan } from '../factory.js';
import { parseInlineNodes, mergeSpanChildren } from './inlineParser.js';
import { parseList, parseListItems } from './listParser.js';
import { parseTable } from './tableParser.js';

class ElementParserRegistry {
  constructor() {
    this.parsers = new Map();
    this.inlineParsers = new Map();
    this._registerDefaultParsers();
  }

  _registerDefaultParsers() {
    this.register('p', this._parseParagraph.bind(this));
    this.register('h1', this._parseHeading.bind(this, 1));
    this.register('h2', this._parseHeading.bind(this, 2));
    this.register('h3', this._parseHeading.bind(this, 3));
    this.register('h4', this._parseHeading.bind(this, 4));
    this.register('h5', this._parseHeading.bind(this, 5));
    this.register('h6', this._parseHeading.bind(this, 6));
    this.register('ul', this._parseList.bind(this, 'bullet'));
    this.register('ol', this._parseList.bind(this, 'number'));
    this.register('blockquote', this._parseQuote.bind(this));
    this.register('pre', this._parseCodeBlock.bind(this));
    this.register('table', this._parseTable.bind(this));
    this.register('img', this._parseImage.bind(this));
    this.register('hr', this._parseDivider.bind(this));
    this.register('div', this._parseDiv.bind(this));
    this.register('center', this._parseCenter.bind(this));

    this.registerInline('strong', this._parseBold.bind(this));
    this.registerInline('b', this._parseBold.bind(this));
    this.registerInline('em', this._parseItalic.bind(this));
    this.registerInline('i', this._parseItalic.bind(this));
    this.registerInline('u', this._parseUnderline.bind(this));
    this.registerInline('s', this._parseStrikethrough.bind(this));
    this.registerInline('strike', this._parseStrikethrough.bind(this));
    this.registerInline('del', this._parseStrikethrough.bind(this));
    this.registerInline('sup', this._parseSuperscript.bind(this));
    this.registerInline('sub', this._parseSubscript.bind(this));
    this.registerInline('mark', this._parseHighlight.bind(this));
    this.registerInline('a', this._parseLink.bind(this));
    this.registerInline('code', this._parseCode.bind(this));
    this.registerInline('br', this._parseBreak.bind(this));
    this.registerInline('font', this._parseFont.bind(this));
    this.registerInline('span', this._parseSpan.bind(this));
    this.registerInline('ul', this._parseInlineList.bind(this, 'bullet'));
    this.registerInline('ol', this._parseInlineList.bind(this, 'number'));
    this.registerInline('div', this._parseInlineDiv.bind(this));
    this.registerInline('p', this._parseInlineParagraph.bind(this));
  }

  register(tagName, parser) {
    this.parsers.set(tagName.toLowerCase(), parser);
  }

  registerInline(tagName, parser) {
    this.inlineParsers.set(tagName.toLowerCase(), parser);
  }

  getParser(tagName) {
    return this.parsers.get(tagName.toLowerCase());
  }

  getInlineParser(tagName) {
    return this.inlineParsers.get(tagName.toLowerCase());
  }

  parse(node, context = {}) {
    const tagName = node.tagName.toLowerCase();
    const parser = this.getParser(tagName);

    if (parser) {
      return parser(node, context);
    }

    return null;
  }

  parseInline(node, inheritedMarks = {}, context = {}) {
    const tagName = node.tagName.toLowerCase();
    const parser = this.getInlineParser(tagName);

    if (parser) {
      return parser(node, inheritedMarks, context);
    }

    return this._parseDefaultInline(node, inheritedMarks, context);
  }

  register(tagName, parser) {
    this.parsers.set(tagName.toLowerCase(), parser);
  }

  registerInline(tagName, parser) {
    this.inlineParsers.set(tagName.toLowerCase(), parser);
  }

  _parseParagraph(node, context) {
    const children = parseInlineNodes(node.childNodes, {}, { ...context, parseInlineElement: this.parseInline.bind(this) });
    const attrs = getParagraphAttrs(node);
    return createParagraph(attrs, children);
  }

  _parseHeading(level, node, context) {
    const children = parseInlineNodes(node.childNodes, {}, { ...context, parseInlineElement: this.parseInline.bind(this) });
    const attrs = getParagraphAttrs(node);
    return createHeading(level, attrs, children);
  }

  _parseList(type, node, context) {
    const attrs = getParagraphAttrs(node);
    const items = parseListItems(node, {
      ...context,
      createLeaf,
      parseInlineElement: this.parseInline.bind(this),
    });
    return ['list', { type, ...attrs }, ...items];
  }

  _parseQuote(node, context) {
    const children = parseInlineNodes(node.childNodes, {}, { ...context, parseInlineElement: this.parseInline.bind(this) });
    const attrs = getParagraphAttrs(node);
    return createQuote(attrs, children);
  }

  _parseCodeBlock(node) {
    return createCodeBlock(node.textContent);
  }

  _parseTable(node, context) {
    return parseTable(node, { ...context, parseInlineElement: this.parseInline.bind(this) });
  }

  _parseImage(node) {
    const src = node.getAttribute('src') || '';
    const alt = node.getAttribute('alt') || '';
    const width = node.getAttribute('width') || parseStyleSize(node.style?.width);
    const height = node.getAttribute('height') || parseStyleSize(node.style?.height);
    return createImage(src, alt, width, height);
  }

  _parseDivider() {
    return createDivider();
  }

  _parseDiv(node, context) {
    const children = context.parseNodes?.(node.childNodes) || [];
    return children.length === 1 ? children[0] : null;
  }

  _parseCenter(node, context) {
    const children = parseInlineNodes(node.childNodes, {}, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return createParagraph({ jc: 'center' }, children);
  }

  _parseBold(node, inheritedMarks, context) {
    const marks = { ...inheritedMarks, bold: true };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseItalic(node, inheritedMarks, context) {
    const marks = { ...inheritedMarks, italic: true };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseUnderline(node, inheritedMarks, context) {
    const marks = { ...inheritedMarks, underline: true };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseStrikethrough(node, inheritedMarks, context) {
    const marks = { ...inheritedMarks, strikethrough: true };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseSuperscript(node, inheritedMarks, context) {
    const marks = { ...inheritedMarks, sup: true };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseSubscript(node, inheritedMarks, context) {
    const marks = { ...inheritedMarks, sub: true };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseHighlight(node, inheritedMarks, context) {
    const marks = { ...inheritedMarks, highlight: true };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseLink(node, inheritedMarks, context) {
    const href = node.getAttribute('href') || '';
    const elementMarks = getInlineMarks(node);
    const marks = { ...inheritedMarks, ...elementMarks };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return createLink(href, children.length ? children : [createLeaf(node.textContent, marks)]);
  }

  _parseCode(node, inheritedMarks, context) {
    const marks = { ...inheritedMarks, code: true };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseBreak() {
    return null;
  }

  _parseFont(node, inheritedMarks, context) {
    const elementMarks = getInlineMarks(node);
    const marks = { ...inheritedMarks, ...elementMarks };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseSpan(node, inheritedMarks, context) {
    const elementMarks = getInlineMarks(node);
    const marks = { ...inheritedMarks, ...elementMarks };
    const children = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return children.length === 1 ? children[0] : children;
  }

  _parseInlineList(type, node, inheritedMarks, context) {
    const items = parseListItems(node, {
      ...context,
      createLeaf,
      parseInlineElement: this.parseInline.bind(this),
    });
    return ['list', { type }, ...items];
  }

  _parseInlineDiv(node, inheritedMarks, context) {
    const elementMarks = getInlineMarks(node);
    const marks = { ...inheritedMarks, ...elementMarks };
    const children = context.parseNodes?.(node.childNodes) || [];
    if (children.length === 1) {
      return children[0];
    }
    const inlineChildren = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return createTextSpan(inlineChildren);
  }

  _parseInlineParagraph(node, inheritedMarks, context) {
    const elementMarks = getInlineMarks(node);
    const marks = { ...inheritedMarks, ...elementMarks };
    const children = context.parseNodes?.(node.childNodes) || [];
    if (children.length === 1) {
      return children[0];
    }
    const inlineChildren = parseInlineNodes(node.childNodes, marks, { ...context, parseInlineElement: this.parseInline.bind(this) });
    return createParagraph({}, inlineChildren);
  }

  _parseDefaultInline(node, inheritedMarks, context) {
    return null;
  }
}

export const createParserRegistry = () => {
  return new ElementParserRegistry();
};

export { ElementParserRegistry };
