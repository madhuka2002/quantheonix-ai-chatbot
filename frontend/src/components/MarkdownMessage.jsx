import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  Prism as SyntaxHighlighter,
} from "react-syntax-highlighter";

import {
  oneDark,
} from "react-syntax-highlighter/dist/esm/styles/prism";

import CopyButton from "./CopyButton";


function extractText(children) {
  if (typeof children === "string") {
    return children;
  }

  if (Array.isArray(children)) {
    return children
      .map((child) => extractText(child))
      .join("");
  }

  if (
    children &&
    typeof children === "object" &&
    "props" in children
  ) {
    return extractText(children.props.children);
  }

  return "";
}


function CodeBlock({
  className,
  children,
  ...properties
}) {
  const languageMatch =
    /language-(\w+)/.exec(className || "");

  const codeText = extractText(children).replace(
    /\n$/,
    "",
  );

  const isInline =
    !languageMatch &&
    !codeText.includes("\n");

  if (isInline) {
    return (
      <code
        className="markdown-inline-code"
        {...properties}
      >
        {children}
      </code>
    );
  }

  const language =
    languageMatch?.[1] || "text";

  return (
    <div className="code-block">
      <div className="code-block__header">
        <span>{language}</span>

        <CopyButton
          text={codeText}
          defaultLabel="Copy code"
          copiedLabel="Copied"
          className="code-block__copy"
        />
      </div>

      <SyntaxHighlighter
        language={language}
        style={oneDark}
        PreTag="div"
        customStyle={{
          margin: 0,
          padding: "1rem",
          background: "transparent",
          borderRadius: 0,
        }}
        codeTagProps={{
          style: {
            fontFamily:
              '"SFMono-Regular", Consolas, "Liberation Mono", monospace',
          },
        }}
        wrapLongLines
      >
        {codeText}
      </SyntaxHighlighter>
    </div>
  );
}


function MarkdownMessage({ content }) {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        skipHtml
        components={{
          code: CodeBlock,

          a({
            href,
            children,
            ...properties
          }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                {...properties}
              >
                {children}
              </a>
            );
          },

          table({ children }) {
            return (
              <div className="markdown-table-wrapper">
                <table>{children}</table>
              </div>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}


export default MarkdownMessage;