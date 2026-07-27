import { useEffect, useState } from "react";


function CopyButton({
  text,
  defaultLabel = "Copy",
  copiedLabel = "Copied",
  className = "",
}) {
  const [isCopied, setIsCopied] = useState(false);


  useEffect(() => {
    if (!isCopied) {
      return undefined;
    }

    const timerId = window.setTimeout(() => {
      setIsCopied(false);
    }, 2000);

    return () => {
      window.clearTimeout(timerId);
    };
  }, [isCopied]);


  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
    } catch (copyError) {
      console.error(
        "Unable to copy content.",
        copyError,
      );
    }
  }


  return (
    <button
      className={`copy-button ${className}`.trim()}
      type="button"
      onClick={handleCopy}
      aria-label={
        isCopied ? copiedLabel : defaultLabel
      }
    >
      {isCopied ? copiedLabel : defaultLabel}
    </button>
  );
}


export default CopyButton;