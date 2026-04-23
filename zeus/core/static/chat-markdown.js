// zeus/core/static/chat-markdown.js — Safe assistant markdown (marked + DOMPurify)
import { marked } from 'marked';
import DOMPurify from 'dompurify';

marked.setOptions({ gfm: true, breaks: true });

const ALLOWED_TAGS = [
  'p', 'br', 'strong', 'em', 'b', 'i', 'code', 'pre', 'h1', 'h2', 'h3', 'h4',
  'ul', 'ol', 'li', 'blockquote', 'a', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
];

const ALLOWED_ATTR = ['href', 'title', 'colspan', 'rowspan'];

/**
 * @param {string} text
 * @returns {string}
 */
export function renderAssistantMarkdown(text) {
  const raw = marked.parse(text || '', { async: false });
  const clean = DOMPurify.sanitize(raw, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    ALLOW_DATA_ATTR: false,
    ALLOWED_URI_REGEXP:
      /^(?:(?:https?|mailto):|[^a-z]|[a-z+.-]+(?:[^a-z+.\-:]|$))/i,
  });
  const tpl = document.createElement('template');
  tpl.innerHTML = clean;
  tpl.content.querySelectorAll('a[href]').forEach((a) => {
    try {
      const u = new URL(a.getAttribute('href') || '', location.origin);
      if (u.origin !== location.origin) {
        a.setAttribute('target', '_blank');
        a.setAttribute('rel', 'noopener noreferrer');
      }
    } catch {
      /* ignore bad href */
    }
  });
  return tpl.innerHTML;
}
