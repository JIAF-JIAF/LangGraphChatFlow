export const cleanHtml = (html) => {
  let cleaned = html;

  cleaned = cleaned.replace(/<\?xml[^>]*\?>/gi, '');
  cleaned = cleaned.replace(/<!DOCTYPE[^>]*>/gi, '');
  cleaned = cleaned.replace(/<\[if[^>]*>\s*<!\[endif\]>/gi, '');
  cleaned = cleaned.replace(/<!\[if[^>]*>\s*<!\[endif\]>/gi, '');
  cleaned = cleaned.replace(/<\!\[CDATA\[.*?\]\]>/g, '');

  cleaned = cleaned.replace(/&nbsp;/g, ' ');
  cleaned = cleaned.replace(/&amp;/g, '&');
  cleaned = cleaned.replace(/&lt;/g, '<');
  cleaned = cleaned.replace(/&gt;/g, '>');

  return cleaned;
};