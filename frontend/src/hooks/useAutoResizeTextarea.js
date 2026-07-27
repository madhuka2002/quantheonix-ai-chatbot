import { useEffect } from "react";


export function useAutoResizeTextarea(
  textareaRef,
  value,
  maximumHeight = 160,
) {
  useEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    textarea.style.height = `${Math.min(
      textarea.scrollHeight,
      maximumHeight,
    )}px`;
  }, [textareaRef, value, maximumHeight]);
}