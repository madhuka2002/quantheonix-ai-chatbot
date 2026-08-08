import { useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

import "highlight.js/styles/github-dark.css";


function CodeBlock({
  inline,
  className,
  children,
  ...props
}) {
  const [isCopied, setIsCopied] =
    useState(false);

  const codeText = String(children).replace(
    /\n$/,
    "",
  );

  if (inline) {
    return (
      <code
        className="markdown-inline-code"
        {...props}
      >
        {children}
      </code>
    );
  }

  const language =
    className?.replace(
      "language-",
      "",
    ) || "text";


  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(
        codeText,
      );

      setIsCopied(true);

      window.setTimeout(() => {
        setIsCopied(false);
      }, 1500);
    } catch (error) {
      console.error(
        "Code copy failed:",
        error,
      );
    }
  }


  return (
    <div className="markdown-code-block">
      <div className="markdown-code-header">
        <span>{language}</span>

        <button
          type="button"
          onClick={handleCopy}
        >
          {isCopied ? "Copied" : "Copy"}
        </button>
      </div>

      <pre>
        <code
          className={className}
          {...props}
        >
          {codeText}
        </code>
      </pre>
    </div>
  );
}


export default function MarkdownMessage({
  content,
}) {
  return (
    <div className="markdown-message">
      <ReactMarkdown
        remarkPlugins={[
          remarkGfm,
        ]}
        rehypePlugins={[
          rehypeHighlight,
        ]}
        components={{
          code: CodeBlock,

          a({
            children,
            href,
            ...props
          }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                {...props}
              >
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}