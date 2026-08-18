export default function OverviewPage({
  assistants,
  isLoading,
  onNavigate,
}) {
  const activeCount =
    assistants.filter(
      (assistant) =>
        assistant.is_active,
    ).length;

  const ragCount =
    assistants.filter(
      (assistant) =>
        assistant.rag_enabled,
    ).length;

  return (
    <div className="dashboard-page">
      <section className="overview-hero">
        <div>
          <span className="dashboard-eyebrow">
            Quantheonix Workspace
          </span>

          <h2>
            Build an AI assistant
            that feels like part of
            your product.
          </h2>

          <p>
            Configure its behavior,
            appearance, deployment
            domains and installation
            from one place.
          </p>
        </div>

        <button
          type="button"
          className="dashboard-primary-button"
          onClick={() =>
            onNavigate("assistants")
          }
        >
          Manage assistants
        </button>
      </section>

      <section className="dashboard-stats">
        <article className="dashboard-stat-card">
          <span>
            Assistants
          </span>

          <strong>
            {isLoading
              ? "—"
              : assistants.length}
          </strong>

          <small>
            Total configured assistants
          </small>
        </article>

        <article className="dashboard-stat-card">
          <span>
            Active
          </span>

          <strong>
            {isLoading
              ? "—"
              : activeCount}
          </strong>

          <small>
            Available for use
          </small>
        </article>

        <article className="dashboard-stat-card">
          <span>
            RAG enabled
          </span>

          <strong>
            {isLoading
              ? "—"
              : ragCount}
          </strong>

          <small>
            Knowledge-enabled assistants
          </small>
        </article>

        <article className="dashboard-stat-card">
          <span>
            Deployment
          </span>

          <strong>
            Self-hosted
          </strong>

          <small>
            Your infrastructure,
            your data
          </small>
        </article>
      </section>

      <section className="dashboard-section">
        <div className="dashboard-section__heading">
          <div>
            <span className="dashboard-eyebrow">
              Quick start
            </span>

            <h3>
              Configure your workspace
            </h3>
          </div>
        </div>

        <div className="quick-action-grid">
          <button
            type="button"
            className="quick-action-card"
            onClick={() =>
              onNavigate("assistants")
            }
          >
            <strong>
              01
            </strong>

            <h4>
              Create an assistant
            </h4>

            <p>
              Give it a purpose,
              personality and AI
              configuration.
            </p>
          </button>

          <button
            type="button"
            className="quick-action-card"
            onClick={() =>
              onNavigate("customize")
            }
          >
            <strong>
              02
            </strong>

            <h4>
              Customize the widget
            </h4>

            <p>
              Match your website with
              colors, typography and
              layout controls.
            </p>
          </button>

          <button
            type="button"
            className="quick-action-card"
            onClick={() =>
              onNavigate("domains")
            }
          >
            <strong>
              03
            </strong>

            <h4>
              Secure deployment
            </h4>

            <p>
              Define exactly which
              websites may use your
              assistant.
            </p>
          </button>

          <button
            type="button"
            className="quick-action-card"
            onClick={() =>
              onNavigate(
                "installation",
              )
            }
          >
            <strong>
              04
            </strong>

            <h4>
              Install it
            </h4>

            <p>
              Copy your integration
              configuration and deploy.
            </p>
          </button>
        </div>
      </section>
    </div>
  );
}