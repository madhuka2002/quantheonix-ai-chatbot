import {
  useEffect,
  useState,
} from "react";

import {
  addDomain,
  deleteDomain,
  listDomains,
} from "../../services/domainApi";


export default function DomainsPage({
  assistant,
}) {
  const [
    domains,
    setDomains,
  ] = useState([]);

  const [
    domainInput,
    setDomainInput,
  ] = useState("");

  const [
    isLoading,
    setIsLoading,
  ] = useState(
    () => Boolean(assistant?.id),
  );

  const [
    isSaving,
    setIsSaving,
  ] = useState(false);

  const [
    deletingId,
    setDeletingId,
  ] = useState(null);

  const [
    error,
    setError,
  ] = useState("");

  const [
    successMessage,
    setSuccessMessage,
  ] = useState("");


  useEffect(() => {
    if (!assistant?.id) {
      return undefined;
    }

    let cancelled = false;

    async function loadDomains() {
      try {
        const data =
          await listDomains(
            assistant.id,
          );

        if (cancelled) {
          return;
        }

        setDomains(
          Array.isArray(data)
            ? data
            : [],
        );

        setError("");
        setIsLoading(false);
      } catch (requestError) {
        if (cancelled) {
          return;
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Allowed domains could not be loaded.",
        );

        setIsLoading(false);
      }
    }

    void loadDomains();

    return () => {
      cancelled = true;
    };
  }, [assistant?.id]);


  async function handleAddDomain(
    event,
  ) {
    event.preventDefault();

    const value =
      domainInput.trim();

    if (!value) {
      return;
    }

    setIsSaving(true);
    setError("");
    setSuccessMessage("");

    try {
      const created =
        await addDomain(
          assistant.id,
          value,
        );

      setDomains(
        (current) => [
          ...current,
          created,
        ],
      );

      setDomainInput("");

      setSuccessMessage(
        "Domain added successfully.",
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The domain could not be added.",
      );
    } finally {
      setIsSaving(false);
    }
  }


  async function handleDeleteDomain(
    domain,
  ) {
    const confirmed =
      window.confirm(
        `Remove "${domain.domain}" from this assistant?`,
      );

    if (!confirmed) {
      return;
    }

    setDeletingId(
      domain.id,
    );

    setError("");
    setSuccessMessage("");

    try {
      await deleteDomain(
        assistant.id,
        domain.id,
      );

      setDomains(
        (current) =>
          current.filter(
            (item) =>
              item.id !== domain.id,
          ),
      );

      setSuccessMessage(
        "Domain removed successfully.",
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The domain could not be removed.",
      );
    } finally {
      setDeletingId(null);
    }
  }


  if (!assistant) {
    return (
      <div className="dashboard-page">
        <section className="dashboard-empty-state">
          <strong>
            Select an assistant
          </strong>

          <p>
            Choose an assistant before
            managing its allowed
            domains.
          </p>
        </section>
      </div>
    );
  }


  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="widget-studio-loading">
          Loading allowed domains...
        </div>
      </div>
    );
  }


  return (
    <div className="dashboard-page">
      <section className="dashboard-toolbar">
        <div>
          <span className="dashboard-eyebrow">
            Deployment Security
          </span>

          <h2>
            Allowed domains
          </h2>

          <p>
            Control which websites can
            embed{" "}
            <strong>
              {assistant.display_name}
            </strong>
            .
          </p>
        </div>
      </section>


      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="dashboard-success">
          {successMessage}
        </div>
      )}


      <div className="domains-layout">
        <section className="domains-panel">
          <div className="domains-panel__header">
            <div>
              <h3>
                Add a website
              </h3>

              <p>
                Enter only the hostname
                or domain. Quantheonix
                will normalize common
                URL formats for you.
              </p>
            </div>
          </div>


          <form
            className="domain-form"
            onSubmit={
              handleAddDomain
            }
          >
            <div className="domain-input-wrapper">
              <span>
                https://
              </span>

              <input
                type="text"
                value={
                  domainInput
                }
                onChange={
                  (event) =>
                    setDomainInput(
                      event.target.value,
                    )
                }
                placeholder="example.com"
                maxLength={255}
                required
              />
            </div>

            <button
              type="submit"
              className="dashboard-primary-button"
              disabled={
                isSaving ||
                !domainInput.trim()
              }
            >
              {isSaving
                ? "Adding..."
                : "Add domain"}
            </button>
          </form>


          <div className="domain-help">
            <strong>
              Examples
            </strong>

            <div>
              <code>
                example.com
              </code>

              <code>
                app.example.com
              </code>

              <code>
                https://example.com/
              </code>
            </div>

            <p>
              URLs containing paths such
              as{" "}
              <code>
                example.com/chat
              </code>{" "}
              are intentionally rejected.
            </p>
          </div>
        </section>


        <section className="domains-panel">
          <div className="domains-panel__header domains-panel__header--list">
            <div>
              <h3>
                Approved websites
              </h3>

              <p>
                {domains.length}{" "}
                {domains.length === 1
                  ? "domain"
                  : "domains"}{" "}
                currently allowed.
              </p>
            </div>

            <span className="domains-count">
              {domains.length}
            </span>
          </div>


          {domains.length ? (
            <div className="domain-list">
              {domains.map(
                (domain) => (
                  <article
                    key={domain.id}
                    className="domain-row"
                  >
                    <div className="domain-row__icon">
                      ◎
                    </div>

                    <div className="domain-row__content">
                      <strong>
                        {domain.domain}
                      </strong>

                      <span>
                        {domain.is_active
                          ? "Active"
                          : "Inactive"}
                      </span>
                    </div>

                    <button
                      type="button"
                      className="dashboard-danger-button"
                      disabled={
                        deletingId ===
                        domain.id
                      }
                      onClick={() =>
                        handleDeleteDomain(
                          domain,
                        )
                      }
                    >
                      {deletingId ===
                      domain.id
                        ? "Removing..."
                        : "Remove"}
                    </button>
                  </article>
                ),
              )}
            </div>
          ) : (
            <div className="domain-empty">
              <div>
                ◎
              </div>

              <strong>
                No domains added
              </strong>

              <p>
                Add the first website
                where this assistant
                will be embedded.
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}