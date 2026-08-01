import {
  useState,
} from "react";

import {
  AuthProvider,
} from "./context/AuthContext";

import {
  useAuth,
} from "./hooks/useAuth";

import ChatApplication
  from "./components/ChatApplication";

import LoginPage
  from "./pages/LoginPage";

import RegisterPage
  from "./pages/RegisterPage";

import "./styles/auth.css";


function ApplicationContent() {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth();

  const [authPage, setAuthPage] =
    useState("login");


  if (isLoading) {
    return (
      <main className="auth-page">
        <section className="auth-card auth-loading">
          <div className="auth-logo">
            QX
          </div>

          <p>
            Checking your session...
          </p>
        </section>
      </main>
    );
  }


  if (!isAuthenticated) {
    if (authPage === "register") {
      return (
        <RegisterPage
          onShowLogin={() =>
            setAuthPage("login")
          }
        />
      );
    }

    return (
      <LoginPage
        onShowRegister={() =>
          setAuthPage("register")
        }
      />
    );
  }


  return <ChatApplication />;
}


export default function App() {
  return (
    <AuthProvider>
      <ApplicationContent />
    </AuthProvider>
  );
}