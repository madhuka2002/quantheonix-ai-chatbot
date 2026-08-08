import {
  useCallback,
  useState,
} from "react";


function readStoredValue(
  key,
  initialValue,
) {
  try {
    const storedValue =
      window.localStorage.getItem(key);

    if (storedValue === null) {
      return typeof initialValue === "function"
        ? initialValue()
        : initialValue;
    }

    return JSON.parse(storedValue);
  } catch {
    return typeof initialValue === "function"
      ? initialValue()
      : initialValue;
  }
}


export function useLocalStorage(
  key,
  initialValue,
) {
  const [storedValue, setStoredValue] =
    useState(() =>
      readStoredValue(
        key,
        initialValue,
      ),
    );


  const setValue = useCallback(
    (value) => {
      setStoredValue(
        (currentValue) => {
          const nextValue =
            typeof value === "function"
              ? value(currentValue)
              : value;

          try {
            window.localStorage.setItem(
              key,
              JSON.stringify(nextValue),
            );
          } catch (error) {
            console.error(
              `Could not store "${key}" in localStorage:`,
              error,
            );
          }

          return nextValue;
        },
      );
    },
    [key],
  );


  const removeValue = useCallback(
    () => {
      try {
        window.localStorage.removeItem(
          key,
        );
      } catch (error) {
        console.error(
          `Could not remove "${key}" from localStorage:`,
          error,
        );
      }

      setStoredValue(
        typeof initialValue === "function"
          ? initialValue()
          : initialValue,
      );
    },
    [
      key,
      initialValue,
    ],
  );


  return [
    storedValue,
    setValue,
    removeValue,
  ];
}