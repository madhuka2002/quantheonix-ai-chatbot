export default function PlaceholderPage({
  eyebrow,
  title,
  description,
}) {
  return (
    <div className="dashboard-page">
      <section className="dashboard-placeholder">
        <span className="dashboard-eyebrow">
          {eyebrow}
        </span>

        <h2>
          {title}
        </h2>

        <p>
          {description}
        </p>

        <div className="dashboard-placeholder__panel">
          This section will be built
          in the next dashboard step.
        </div>
      </section>
    </div>
  );
}