import {
  useMemo,
  useState,
} from "react";

import {
  API_BASE_URL,
} from "../../services/apiClient";


function CodeBlock({
  code,
  label,
}) {
  const [
    copied,
    setCopied,
  ] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(
        code,
      );

      setCopied(true);

      window.setTimeout(
        () => {
          setCopied(false);
        },
        1600,
      );
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="installation-code">
      <div className="installation-code__header">
        <span>
          {label}
        </span>

        <button
          type="button"
          onClick={handleCopy}
        >
          {copied
            ? "Copied"
            : "Copy"}
        </button>
      </div>

      <pre>
        <code>
          {code}
        </code>
      </pre>
    </div>
  );
}


export default function InstallationPage({
  assistant,
}) {
  const assistantId =
    assistant?.id ?? "";

  const apiBaseUrl =
    API_BASE_URL;

  const npmInstall =
    "npm install @quantheonix/chatbot";

  const reactExample =
    useMemo(
      () =>
`import {
  QuantheonixChatbot,
} from "@quantheonix/chatbot";

export default function App() {
  return (
    <QuantheonixChatbot
      assistantId="${assistantId}"
      apiBaseUrl="${apiBaseUrl}"
    />
  );
}`,
      [
        assistantId,
        apiBaseUrl,
      ],
    );

  const scriptExample =
    useMemo(
      () =>
`<script
  src="https://unpkg.com/@quantheonix/chatbot/dist/quantheonix-chatbot.js"
  data-assistant-id="${assistantId}"
  data-api-base-url="${apiBaseUrl}">
</script>`,
      [
        assistantId,
        apiBaseUrl,
      ],
    );

  const configExample =
    useMemo(
      () =>
`{
  "assistantId": "${assistantId}",
  "apiBaseUrl": "${apiBaseUrl}"
}`,
      [
        assistantId,
        apiBaseUrl,
      ],
    );


  if (!assistant) {
    return (
      <div className="dashboard-page">
        <section className="dashboard-empty-state">
          <strong>
            Select an assistant
          </strong>

          <p>
            Choose an assistant before
            generating installation
            instructions.
          </p>
        </section>
      </div>
    );
  }


  return (
    <div className="dashboard-page">
      <section className="installation-header">
        <div>
          <span className="dashboard-eyebrow">
            Deployment
          </span>

          <h2>
            Install {
              assistant.display_name
            }
          </h2>

          <p>
            Use the assistant ID and
            your Quantheonix API URL to
            embed this chatbot into a
            website.
          </p>
        </div>
      </section>


      <div className="installation-grid">
        <section className="installation-card installation-card--identity">
          <span className="dashboard-eyebrow">
            Assistant Identity
          </span>

          <h3>
            Deployment details
          </h3>

          <div className="installation-detail">
            <span>
              Assistant
            </span>

            <strong>
              {
                assistant.display_name
              }
            </strong>
          </div>

          <div className="installation-detail">
            <span>
              Assistant ID
            </span>

            <code>
              {assistant.id}
            </code>
          </div>

          <div className="installation-detail">
            <span>
              API URL
            </span>

            <code>
              {apiBaseUrl}
            </code>
          </div>

          <div className="installation-detail">
            <span>
              Status
            </span>

            <strong
              className={
                assistant.is_active
                  ? "installation-status installation-status--active"
                  : "installation-status"
              }
            >
              {assistant.is_active
                ? "Active"
                : "Inactive"}
            </strong>
          </div>
        </section>


        <section className="installation-card">
          <span className="dashboard-eyebrow">
            NPM
          </span>

          <h3>
            Install the package
          </h3>

          <p>
            Add the Quantheonix widget
            package to your frontend
            project.
          </p>

          <CodeBlock
            label="Terminal"
            code={npmInstall}
          />
        </section>


        <section className="installation-card installation-card--wide">
          <span className="dashboard-eyebrow">
            React
          </span>

          <h3>
            React integration
          </h3>

          <p>
            Use the package directly
            inside your React
            application.
          </p>

          <CodeBlock
            label="React"
            code={reactExample}
          />
        </section>


        <section className="installation-card installation-card--wide">
          <span className="dashboard-eyebrow">
            Plain HTML
          </span>

          <h3>
            Script integration
          </h3>

          <p>
            For websites that do not
            use React, load the widget
            through a script tag.
          </p>

          <CodeBlock
            label="HTML"
            code={scriptExample}
          />
        </section>


        <section className="installation-card">
          <span className="dashboard-eyebrow">
            Configuration
          </span>

          <h3>
            Runtime config
          </h3>

          <CodeBlock
            label="JSON"
            code={configExample}
          />
        </section>


        <section className="installation-card">
          <span className="dashboard-eyebrow">
            Security
          </span>

          <h3>
            Before deployment
          </h3>

          <div className="installation-checklist">
            <div>
              <span>
                01
              </span>

              <p>
                Add the website to
                Allowed Domains.
              </p>
            </div>

            <div>
              <span>
                02
              </span>

              <p>
                Make sure the assistant
                is active.
              </p>
            </div>

            <div>
              <span>
                03
              </span>

              <p>
                Confirm the backend API
                is reachable from the
                website.
              </p>
            </div>

            <div>
              <span>
                04
              </span>

              <p>
                Test the chatbot before
                production deployment.
              </p>
            </div>
          </div>
        </section>


        <section className="installation-card installation-card--wide">
          <span className="dashboard-eyebrow">
            Self-hosted
          </span>

          <h3>
            Local or private deployment
          </h3>

          <p>
            If Quantheonix is hosted on
            your own machine or server,
            replace the API URL with the
            address reachable by the
            client website.
          </p>

          <div className="installation-note">
            <strong>
              Example
            </strong>

            <code>
              http://192.168.1.50:8000
            </code>

            <p>
              A browser running on
              another device cannot use
              127.0.0.1 to reach your
              Quantheonix backend.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}