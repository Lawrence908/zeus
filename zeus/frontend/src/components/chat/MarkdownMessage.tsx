// zeus/frontend/src/components/chat/MarkdownMessage.tsx
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import type { Components } from 'react-markdown'
import type { ClassAttributes, HTMLAttributes } from 'react'

interface MarkdownMessageProps {
  content: string
}

type CodeProps = ClassAttributes<HTMLElement> &
  HTMLAttributes<HTMLElement> & {
    inline?: boolean
    node?: unknown
  }

const components: Components = {
  code({ inline, className, children, ...props }: CodeProps) {
    if (inline) {
      return (
        <code
          className="bg-surface-container-high px-1 rounded text-primary-fixed-dim font-mono text-xs"
          {...props}
        >
          {children}
        </code>
      )
    }
    return (
      <code
        className={`${className ?? ''} font-mono text-xs`}
        {...props}
      >
        {children}
      </code>
    )
  },

  pre({ children, ...props }) {
    return (
      <pre
        className="bg-surface-container-lowest border-l-2 border-primary-container font-mono text-xs p-4 overflow-x-auto my-2 rounded"
        {...props}
      >
        {children}
      </pre>
    )
  },

  a({ children, href, ...props }) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-primary underline underline-offset-2 hover:text-primary-container transition-colors"
        {...props}
      >
        {children}
      </a>
    )
  },

  p({ children, ...props }) {
    return (
      <p className="mb-2 last:mb-0 leading-relaxed" {...props}>
        {children}
      </p>
    )
  },

  ul({ children, ...props }) {
    return (
      <ul className="list-disc list-inside mb-2 space-y-1" {...props}>
        {children}
      </ul>
    )
  },

  ol({ children, ...props }) {
    return (
      <ol className="list-decimal list-inside mb-2 space-y-1" {...props}>
        {children}
      </ol>
    )
  },

  blockquote({ children, ...props }) {
    return (
      <blockquote
        className="border-l-2 border-outline-variant pl-3 italic text-on-surface-variant my-2"
        {...props}
      >
        {children}
      </blockquote>
    )
  },

  h1({ children, ...props }) {
    return <h1 className="font-headline font-bold text-lg mb-2 text-on-surface" {...props}>{children}</h1>
  },
  h2({ children, ...props }) {
    return <h2 className="font-headline font-semibold text-base mb-2 text-on-surface" {...props}>{children}</h2>
  },
  h3({ children, ...props }) {
    return <h3 className="font-headline font-semibold text-sm mb-1 text-on-surface" {...props}>{children}</h3>
  },

  table({ children, ...props }) {
    return (
      <div className="overflow-x-auto my-2">
        <table className="text-xs border-collapse w-full" {...props}>
          {children}
        </table>
      </div>
    )
  },
  th({ children, ...props }) {
    return (
      <th className="border border-outline-variant/30 px-2 py-1 text-left font-label font-semibold text-on-surface-variant uppercase text-[10px] tracking-wider" {...props}>
        {children}
      </th>
    )
  },
  td({ children, ...props }) {
    return (
      <td className="border border-outline-variant/20 px-2 py-1 text-on-surface" {...props}>
        {children}
      </td>
    )
  },
}

export function MarkdownMessage({ content }: MarkdownMessageProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={components}
    >
      {content}
    </ReactMarkdown>
  )
}
