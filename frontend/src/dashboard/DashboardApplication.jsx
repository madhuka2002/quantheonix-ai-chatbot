import {
  useCallback,
  useEffect,
  useState,
} from "react";

import ChatApplication
  from "../components/ChatApplication";

import {
  listAssistants,
} from "../services/assistantApi";

import DashboardHeader
  from "./components/DashboardHeader";

import DashboardSidebar
  from "./components/DashboardSidebar";

import AssistantsPage
  from "./pages/AssistantsPage";

import CustomizePage
  from "./pages/CustomizePage";

import OverviewPage
  from "./pages/OverviewPage";

import "./styles/dashboard.css";

import DomainsPage
  from "./pages/DomainsPage";

import AISettingsPage
  from "./pages/AISettingsPage";

import InstallationPage
  from "./pages/InstallationPage";


export default function DashboardApplication() {
  const [
    activePage,
    setActivePage,
  ] = useState("overview");

  const [
    assistants,
    setAssistants,
  ] = useState([]);

  const [
    isLoadingAssistants,
    setIsLoadingAssistants,
  ] = useState(true);

  const [
    assistantError,
    setAssistantError,
  ] = useState("");

  const [
    selectedAssistantId,
    setSelectedAssistantId,
  ] = useState(null);


  const loadAssistants = useCallback(
    async () => {
      setIsLoadingAssistants(true);
      setAssistantError("");

      try {
        const data =
          await listAssistants();

        const assistantList =
          Array.isArray(data)
            ? data
            : [];

        setAssistants(
          assistantList,
        );

        /*
         * Keep the current selection if
         * that assistant still exists.
         *
         * Otherwise select the default
         * assistant, or the first one.
         */
        setSelectedAssistantId(
          (currentId) => {
            if (
              currentId &&
              assistantList.some(
                (assistant) =>
                  assistant.id ===
                  currentId,
              )
            ) {
              return currentId;
            }

            const defaultAssistant =
              assistantList.find(
                (assistant) =>
                  assistant.is_default,
              );

            return (
              defaultAssistant?.id ??
              assistantList[0]?.id ??
              null
            );
          },
        );
      } catch (error) {
        setAssistantError(
          error instanceof Error
            ? error.message
            : "Assistants could not be loaded.",
        );
      } finally {
        setIsLoadingAssistants(false);
      }
    },
    [],
  );


  useEffect(() => {
    let cancelled = false;

    async function initializeAssistants() {
      try {
        const data =
          await listAssistants();

        if (cancelled) {
          return;
        }

        const assistantList =
          Array.isArray(data)
            ? data
            : [];

        setAssistants(
          assistantList,
        );

        /*
         * Establish an initial selection.
         *
         * Prefer the default assistant.
         */
        const defaultAssistant =
          assistantList.find(
            (assistant) =>
              assistant.is_default,
          );

        setSelectedAssistantId(
          defaultAssistant?.id ??
            assistantList[0]?.id ??
            null,
        );

        setAssistantError("");
      } catch (error) {
        if (cancelled) {
          return;
        }

        setAssistantError(
          error instanceof Error
            ? error.message
            : "Assistants could not be loaded.",
        );
      } finally {
        if (!cancelled) {
          setIsLoadingAssistants(false);
        }
      }
    }

    void initializeAssistants();

    return () => {
      cancelled = true;
    };
  }, []);


  /*
   * Resolve the full assistant object
   * from the selected ID.
   */
  const selectedAssistant =
    assistants.find(
      (assistant) =>
        assistant.id ===
        selectedAssistantId,
    ) ?? null;


  function handleSelectAssistant(
    assistantId,
  ) {
    setSelectedAssistantId(
      assistantId,
    );
  }


  function renderPage() {
    if (activePage === "overview") {
      return (
        <OverviewPage
          assistants={assistants}
          isLoading={
            isLoadingAssistants
          }
          onNavigate={
            setActivePage
          }
        />
      );
    }


    if (
      activePage === "assistants"
    ) {
      return (
        <AssistantsPage
          assistants={assistants}
          isLoading={
            isLoadingAssistants
          }
          error={assistantError}
          onRefresh={
            loadAssistants
          }
          selectedAssistantId={
            selectedAssistantId
          }
          onSelectAssistant={
            handleSelectAssistant
          }
        />
      );
    }


    if (
      activePage === "customize"
    ) {
      return (
        <CustomizePage
          assistant={
            selectedAssistant
          }
        />
      );
    }


    if (
      activePage === "domains"
    ) {
      return (
        <DomainsPage
          assistant={
            selectedAssistant
          }
        />
      );
    }


    if (
      activePage === "ai-settings"
    ) {
      return (
        <AISettingsPage
          key={
            selectedAssistant?.id ??
            "no-assistant"
          }
          assistant={
            selectedAssistant
          }
          onAssistantUpdated={
            loadAssistants
          }
        />
      );
    }


    if (
      activePage === "installation"
    ) {
      return (
        <InstallationPage
          assistant={
            selectedAssistant
          }
        />
      );
    }


    if (
      activePage === "test-chat"
    ) {
      return (
        <div className="dashboard-chat-page">
          <ChatApplication />
        </div>
      );
    }


    return (
      <OverviewPage
        assistants={assistants}
        isLoading={
          isLoadingAssistants
        }
        onNavigate={
          setActivePage
        }
      />
    );
  }


  return (
    <div className="dashboard-shell">
      <DashboardSidebar
        activePage={activePage}
        onNavigate={
          setActivePage
        }
      />

      <div className="dashboard-workspace">
        <DashboardHeader
          activePage={activePage}
        />

        <main className="dashboard-content">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}