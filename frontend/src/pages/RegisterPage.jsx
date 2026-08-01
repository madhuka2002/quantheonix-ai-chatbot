import {
  useState,
} from "react";

import {
  useAuth,
} from "../hooks/useAuth";


export default function RegisterPage({
  onShowLogin,
}) {
  const {
    register,
    login,
    authError,
    clearAuthError,
  } = useAuth();

  const [form, setForm] = useState({
    email: "",
    username: "",
    fullName: "",
    password: "",
    confirmPassword: "",
  });

  const [localError, setLocalError] =
    useState("");

  const [isSubmitting, setIsSubmitting] =
    useState(false);


  function updateField(event) {
    const {
      name,
      value,
    } = event.target;

    setForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }));
  }


  async function handleSubmit(event) {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    setLocalError("");
    clearAuthError();

    if (
      form.password !==
      form.confirmPassword
    ) {
      setLocalError(
        "Passwords do not match.",
      );

      return;
    }

    setIsSubmitting(true);

    try {
      await register({
        email: form.email,
        username: form.username,
        fullName: form.fullName,
        password: form.password,
      });

      await login({
        identifier: form.email,
        password: form.password,
      });
    } catch {
      // Errors are shown through AuthContext.
    } finally {
      setIsSubmitting(false);
    }
  }


  const displayedError =
    localError || authError;


  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo">
            QX
          </div>

          <h1>Create account</h1>

          <p>
            Create your Quantheonix AI account.
          </p>
        </div>

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >
          <label htmlFor="fullName">
            Full name
          </label>

          <input
            id="fullName"
            name="fullName"
            type="text"
            value={form.fullName}
            onChange={updateField}
            maxLength={150}
            disabled={isSubmitting}
          />

          <label htmlFor="email">
            Email
          </label>

          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={updateField}
            autoComplete="email"
            required
            disabled={isSubmitting}
          />

          <label htmlFor="username">
            Username
          </label>

          <input
            id="username"
            name="username"
            type="text"
            value={form.username}
            onChange={updateField}
            autoComplete="username"
            minLength={3}
            maxLength={50}
            pattern="[a-zA-Z0-9_.-]+"
            required
            disabled={isSubmitting}
          />

          <label htmlFor="newPassword">
            Password
          </label>

          <input
            id="newPassword"
            name="password"
            type="password"
            value={form.password}
            onChange={updateField}
            autoComplete="new-password"
            minLength={8}
            maxLength={128}
            required
            disabled={isSubmitting}
          />

          <label htmlFor="confirmPassword">
            Confirm password
          </label>

          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            value={form.confirmPassword}
            onChange={updateField}
            autoComplete="new-password"
            minLength={8}
            maxLength={128}
            required
            disabled={isSubmitting}
          />

          {displayedError && (
            <div
              className="auth-error"
              role="alert"
            >
              {displayedError}
            </div>
          )}

          <button
            className="auth-submit"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Creating account..."
              : "Create account"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account?{" "}

          <button
            type="button"
            onClick={onShowLogin}
            disabled={isSubmitting}
          >
            Log in
          </button>
        </p>
      </section>
    </main>
  );
}