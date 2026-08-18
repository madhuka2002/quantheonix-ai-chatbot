import {
  useAuth,
} from "../../hooks/useAuth";


const pageTitles = {
  overview: {
    title: "Overview",
    description:
      "Manage and monitor your AI assistants.",
  },
  assistants: {
    title: "Assistants",
    description:
      "Create and configure assistants for your websites.",
  },
  customize: {
    title: "Customize",
    description:
      "Control how your chatbot looks and behaves.",
  },
  domains: {
    title: "Allowed Domains",
    description:
      "Control where your assistant can be embedded.",
  },
  "ai-settings": {
    title: "AI Settings",
    description:
      "Configure model behavior and assistant instructions.",
  },
  installation: {
    title: "Installation",
    description:
      "Connect Quantheonix to your website.",
  },
  "test-chat": {
    title: "Test Chat",
    description:
      "Test your assistant before deployment.",
  },
};


export default function DashboardHeader({
  activePage,
}) {
  const {
    user,
    logout,
  } = useAuth();

  const page =
    pageTitles[activePage] ??
    pageTitles.overview;

  const initials =
    user?.full_name
      ?.split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() ||
    user?.username
      ?.slice(0, 2)
      .toUpperCase() ||
    "QX";

  return (
    <header className="dashboard-header">
      <div>
        <h1>
          {page.title}
        </h1>

        <p>
          {page.description}
        </p>
      </div>

      <div className="dashboard-header__actions">
        <div className="dashboard-user">
          <div className="dashboard-user__avatar">
            {initials}
          </div>

          <div className="dashboard-user__details">
            <strong>
              {user?.full_name ||
                user?.username}
            </strong>

            <span>
              {user?.email}
            </span>
          </div>
        </div>

        <button
          type="button"
          className="dashboard-logout"
          onClick={logout}
        >
          Sign out
        </button>
      </div>
    </header>
  );
}