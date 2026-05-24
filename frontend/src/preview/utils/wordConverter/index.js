import mammoth from 'mammoth-plus-plus-2';
import { MAMMOTH_OPTIONS } from './config.js';
import { createHtmlParser } from './parsers/index.js';
import { createEmptyDocument, createSimpleDocument } from './factory.js';

class WordConverter {
  constructor() {
    this.htmlParser = createHtmlParser();
  }

  async convert(arrayBuffer) {
    const result = await mammoth.convertToHtml({ arrayBuffer }, MAMMOTH_OPTIONS);

    const html = result.value;

    if (result.messages.length > 0) {
      console.warn('Mammoth warnings:', result.messages);
    }

    console.log('Mammoth HTML output:', html.substring(0, 1000));

    return this.htmlParser.parse(html);
  }

  registerElementParser(tagName, parser) {
    this.htmlParser.registerElementParser(tagName, parser);
  }

  registerInlineParser(tagName, parser) {
    this.htmlParser.registerInlineParser(tagName, parser);
  }
}

let defaultConverter = null;

const getConverter = () => {
  if (!defaultConverter) {
    defaultConverter = new WordConverter();
  }
  return defaultConverter;
};

export const convertWordToCangjieFormat = async (arrayBuffer) => {
  return getConverter().convert(arrayBuffer);
};

export { createEmptyDocument, createSimpleDocument, WordConverter };
