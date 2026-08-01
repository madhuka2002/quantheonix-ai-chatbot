import {
  useState,
} from "react";

import {
  useAuth,
} from "../hooks/useAuth";


export default function LoginPage({
  onShowRegister,
}) {
  const {
    login,
    authError,
    clearAuthError,
  } = useAuth();

  const [identifier, setIdentifier] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [isSubmitting, setIsSubmitting] =
    useState(false);


  async function handleSubmit(event) {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    clearAuthError();

    try {
      await login({
        identifier,
        password,
      });
    } catch {
      // AuthContext already stores the error.
    } finally {
      setIsSubmitting(false);
    }
  }


  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo">
            QX
          </div>

          <h1>Quantheonix AI</h1>

          <p>
            Log in to continue your conversations.
          </p>
        </div>

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >
          <label htmlFor="identifier">
            Email or username
          </label>

          <input
            id="identifier"
            type="text"
            value={identifier}
            onChange={(event) =>
              setIdentifier(event.target.value)
            }
            autoComplete="username"
            maxLength={320}
            required
            disabled={isSubmitting}
          />

          <label htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            autoComplete="current-password"
            maxLength={128}
            required
            disabled={isSubmitting}
          />

          {authError && (
            <div
              className="auth-error"
              role="alert"
            >
              {authError}
            </div>
          )}

          <button
            className="auth-submit"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Logging in..."
              : "Log in"}
          </button>
        </form>

        <p className="auth-switch">
          Do not have an account?{" "}

          <button
            type="button"
            onClick={onShowRegister}
            disabled={isSubmitting}
          >
            Create one
          </button>
        </p>
      </section>
    </main>
  );
}