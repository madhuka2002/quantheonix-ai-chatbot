export default function FieldHelp({
  text,
}) {
  return (
    <span
      className="field-help"
      tabIndex={0}
      aria-label={text}
    >
      ?
      <span
        className="field-help__tooltip"
        role="tooltip"
      >
        {text}
      </span>
    </span>
  );
}