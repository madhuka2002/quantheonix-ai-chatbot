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
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

export default function App() {
  return (
    <QuantheonixChat
      apiUrl="${apiBaseUrl}"
      assistantId="${assistantId}"
    />
  );
}`,
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
  "apiUrl": "${apiBaseUrl}"
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
            Install the Quantheonix React
            widget using this assistant ID
            and API URL.
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
            Add the Quantheonix chatbot
            package to your React
            application.
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
            Add the chatbot
          </h3>

          <p>
            Import the component and
            stylesheet, then provide your
            API URL and assistant ID.
          </p>

          <CodeBlock
            label="React"
            code={reactExample}
          />
        </section>


        <section className="installation-card">
          <span className="dashboard-eyebrow">
            Configuration
          </span>

          <h3>
            Runtime values
          </h3>

          <p>
            These are the public values
            required by the widget.
          </p>

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
                Add the website hostname
                to Allowed Domains.
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
                Make sure the Quantheonix
                backend API is reachable
                from the website.
              </p>
            </div>

            <div>
              <span>
                04
              </span>

              <p>
                Configure backend CORS for
                the website origin.
              </p>
            </div>

            <div>
              <span>
                05
              </span>

              <p>
                Test configuration loading
                and chat streaming before
                production deployment.
              </p>
            </div>
          </div>
        </section>


        <section className="installation-card installation-card--wide">
          <span className="dashboard-eyebrow">
            Security Notice
          </span>

          <h3>
            Never expose secrets
          </h3>

          <p>
            The browser integration only
            requires the public assistant
            ID and API URL.
          </p>

          <div className="installation-note">
            <strong>
              Do not place these in frontend code
            </strong>

            <p>
              Gemini API keys, JWT secrets,
              database credentials, user
              access tokens or other private
              server credentials must remain
              on the backend.
            </p>
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
            use an API address that the
            client website can actually
            reach.
          </p>

          <div className="installation-note">
            <strong>
              Example
            </strong>

            <code>
              http://192.168.1.50:8000
            </code>

            <p>
              A browser running on another
              device cannot use 127.0.0.1
              to reach your Quantheonix
              backend.
            </p>
          </div>
        </section>


        <section className="installation-card installation-card--wide">
          <span className="dashboard-eyebrow">
            Coming Later
          </span>

          <h3>
            Plain HTML / script integration
          </h3>

          <p>
            Standalone JavaScript embedding
            for non-React websites is not
            available in the current package
            version. Do not use a script-tag
            installation until that runtime
            is implemented.
          </p>
        </section>
      </div>
    </div>
  );
}