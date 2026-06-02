// src/lib/markdown.ts — lightweight markdown render + DOMPurify sanitize +
// highlight.js for fenced code blocks. Languages registered selectively to
// keep the bundle reasonable.
import DOMPurify from 'dompurify';
import hljs from 'highlight.js/lib/core';
import bash from 'highlight.js/lib/languages/bash';
import css from 'highlight.js/lib/languages/css';
import diff from 'highlight.js/lib/languages/diff';
import dockerfile from 'highlight.js/lib/languages/dockerfile';
import go from 'highlight.js/lib/languages/go';
import ini from 'highlight.js/lib/languages/ini';
import javascript from 'highlight.js/lib/languages/javascript';
import json from 'highlight.js/lib/languages/json';
import markdown from 'highlight.js/lib/languages/markdown';
import python from 'highlight.js/lib/languages/python';
import rust from 'highlight.js/lib/languages/rust';
import shell from 'highlight.js/lib/languages/shell';
import sql from 'highlight.js/lib/languages/sql';
import typescript from 'highlight.js/lib/languages/typescript';
import xml from 'highlight.js/lib/languages/xml';
import yaml from 'highlight.js/lib/languages/yaml';

import 'highlight.js/styles/github-dark-dimmed.css';
import { Marked } from 'marked';

hljs.registerLanguage('bash', bash);
hljs.registerLanguage('css', css);
hljs.registerLanguage('diff', diff);
hljs.registerLanguage('dockerfile', dockerfile);
hljs.registerLanguage('go', go);
hljs.registerLanguage('ini', ini);
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('js', javascript);
hljs.registerLanguage('json', json);
hljs.registerLanguage('markdown', markdown);
hljs.registerLanguage('md', markdown);
hljs.registerLanguage('python', python);
hljs.registerLanguage('py', python);
hljs.registerLanguage('rust', rust);
hljs.registerLanguage('rs', rust);
hljs.registerLanguage('shell', shell);
hljs.registerLanguage('sh', shell);
hljs.registerLanguage('sql', sql);
hljs.registerLanguage('typescript', typescript);
hljs.registerLanguage('ts', typescript);
hljs.registerLanguage('xml', xml);
hljs.registerLanguage('html', xml);
hljs.registerLanguage('yaml', yaml);
hljs.registerLanguage('yml', yaml);

// `breaks: true` was breaking marked 18's block-level lexer: single-newline
// separators were converting to <br>, which stopped lists and headings from
// being recognised as block elements. Default GFM behaviour handles
// paragraphs correctly without it.
const marked = new Marked({
  gfm: true
});

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escapeAttr(s: string): string {
  return s.replace(/"/g, '&quot;').replace(/</g, '&lt;');
}

// Encode the raw code text into a data attribute so the chat container's
// click delegate can copy it without re-extracting from the highlighted spans.
function encodeRawForAttr(text: string): string {
  // Base64 keeps newlines, quotes, and unicode safe in an HTML attribute.
  return btoa(unescape(encodeURIComponent(text)));
}

marked.use({
  renderer: {
    code(this: unknown, { text, lang }: { text: string; lang?: string }) {
      const language = (lang || '').toLowerCase();
      const known = language && hljs.getLanguage(language);
      let body: string;
      try {
        body = known
          ? hljs.highlight(text, { language, ignoreIllegals: true }).value
          : hljs.highlightAuto(text).value;
      } catch {
        body = escapeHtml(text);
      }
      const label = known ? language : 'text';
      const clip = encodeRawForAttr(text);
      // Wrap so the copy button can sit absolute-top-right over the <pre>.
      return (
        `<div class="code-block-wrap">` +
        `<button class="code-copy-btn" type="button" data-clip-b64="${clip}" aria-label="Copy code">Copy</button>` +
        `<span class="code-lang">${escapeAttr(label)}</span>` +
        `<pre class="hljs"><code class="hljs language-${escapeAttr(label)}">${body}</code></pre>` +
        `</div>`
      );
    }
  }
});

export function renderMarkdown(src: string): string {
  const html = marked.parse(src, { async: false }) as string;
  return DOMPurify.sanitize(html, {
    ADD_ATTR: ['target', 'rel', 'data-clip-b64'],
    USE_PROFILES: { html: true }
  });
}

// Helper for callers that mount rendered markdown into the DOM. Returns the
// raw text that the clicked button represents (after base64-decode), or null.
export function readCodeClip(btn: HTMLElement): string | null {
  const b64 = btn.getAttribute('data-clip-b64');
  if (!b64) return null;
  try {
    return decodeURIComponent(escape(atob(b64)));
  } catch {
    return null;
  }
}
