import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

import "highlight.js/styles/github-dark.css";


function MarkdownMessage({
  content,
}) {
  return (
    <div className="qx-markdown">
      <ReactMarkdown
        remarkPlugins={[
          remarkGfm,
        ]}
        rehypePlugins={[
          rehypeHighlight,
        ]}
        components={{
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


export default MarkdownMessage;