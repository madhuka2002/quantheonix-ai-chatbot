const navigation = [
  {
    id: "overview",
    label: "Overview",
    icon: "◈",
  },
  {
    id: "assistants",
    label: "Assistants",
    icon: "◇",
  },
  {
    id: "customize",
    label: "Customize",
    icon: "✦",
  },
  {
    id: "domains",
    label: "Domains",
    icon: "◎",
  },
  {
    id: "ai-settings",
    label: "AI Settings",
    icon: "⌘",
  },
  {
    id: "installation",
    label: "Installation",
    icon: "</>",
  },
  {
    id: "test-chat",
    label: "Test Chat",
    icon: "◌",
  },
];


export default function DashboardSidebar({
  activePage,
  onNavigate,
}) {
  return (
    <aside className="dashboard-sidebar">
      <div className="dashboard-brand">
        <div className="dashboard-brand__logo">
          QX
        </div>

        <div>
          <strong>
            Quantheonix
          </strong>

          <span>
            AI Assistant
          </span>
        </div>
      </div>

      <nav className="dashboard-nav">
        <span className="dashboard-nav__label">
          Workspace
        </span>

        {navigation.map((item) => (
          <button
            key={item.id}
            type="button"
            className={
              activePage === item.id
                ? "dashboard-nav__item dashboard-nav__item--active"
                : "dashboard-nav__item"
            }
            onClick={() =>
              onNavigate(item.id)
            }
          >
            <span className="dashboard-nav__icon">
              {item.icon}
            </span>

            <span>
              {item.label}
            </span>
          </button>
        ))}
      </nav>

      <div className="dashboard-sidebar__footer">
        <span>
          Quantheonix
        </span>

        <small>
          Community Edition
        </small>
      </div>
    </aside>
  );
}