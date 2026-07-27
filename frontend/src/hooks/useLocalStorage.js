import { useEffect, useState } from "react";


export function useLocalStorage(
  storageKey,
  initialValue,
) {
  const [storedValue, setStoredValue] = useState(
    () => {
      try {
        const savedValue =
          localStorage.getItem(storageKey);

        if (savedValue === null) {
          return typeof initialValue === "function"
            ? initialValue()
            : initialValue;
        }

        return JSON.parse(savedValue);
      } catch {
        return typeof initialValue === "function"
          ? initialValue()
          : initialValue;
      }
    },
  );


  useEffect(() => {
    try {
      localStorage.setItem(
        storageKey,
        JSON.stringify(storedValue),
      );
    } catch (storageError) {
      console.error(
        `Unable to save ${storageKey} to localStorage.`,
        storageError,
      );
    }
  }, [storageKey, storedValue]);


  function removeStoredValue() {
    try {
      localStorage.removeItem(storageKey);

      setStoredValue(
        typeof initialValue === "function"
          ? initialValue()
          : initialValue,
      );
    } catch (storageError) {
      console.error(
        `Unable to remove ${storageKey} from localStorage.`,
        storageError,
      );
    }
  }


  return [
    storedValue,
    setStoredValue,
    removeStoredValue,
  ];
}