import { createLeaf, createParagraph, createRoot } from '../factory.js';
import { createParserRegistry } from './elementParser.js';
import { cleanHtml } from '../utils/htmlCleaner.js';

class HtmlParser {
  constructor() {
    this.registry = createParserRegistry();
  }

  parse(html) {
    const cleanedHtml = cleanHtml(html);
    const parser = new DOMParser();
    const doc = parser.parseFromString(cleanedHtml, 'text/html');

    const children = this.parseNodes(doc.body.childNodes);

    return createRoot(children);
  }

  parseNodes(nodes) {
    const result = [];

    for (const node of nodes) {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent;
        if (text && text.trim()) {
          result.push(createParagraph({}, [createLeaf(text)]));
        }
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        const parsed = this.registry.parse(node, {
          parseNodes: this.parseNodes.bind(this),
          parseInlineElement: this.registry.parseInline.bind(this.registry),
        });
        if (parsed) {
          result.push(parsed);
        }
      }
    }

    return result;
  }

  registerElementParser(tagName, parser) {
    this.registry.register(tagName, parser);
  }

  registerInlineParser(tagName, parser) {
    this.registry.registerInline(tagName, parser);
  }
}

export const createHtmlParser = () => {
  return new HtmlParser();
};

export { HtmlParser };
