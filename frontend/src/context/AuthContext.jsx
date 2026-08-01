import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from "../services/authApi";

import {
  getAccessToken,
  getStoredUser,
} from "../services/authStorage";


export const AuthContext = createContext(null);


export function AuthProvider({ children }) {
  const [user, setUser] = useState(
    () => getStoredUser(),
  );

  const [isLoading, setIsLoading] =
    useState(Boolean(getAccessToken()));

  const [authError, setAuthError] =
    useState("");

  const restoreAuthentication =
    useCallback(async () => {
      const token = getAccessToken();

      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      try {
        const currentUser =
          await getCurrentUser();

        setUser(currentUser);
      } catch (error) {
        setUser(null);

        setAuthError(
          error instanceof Error
            ? error.message
            : "Your login session could not be restored.",
        );
      } finally {
        setIsLoading(false);
      }
    }, []);


  useEffect(() => {
    restoreAuthentication();
  }, [restoreAuthentication]);


  const login = useCallback(
    async ({
      identifier,
      password,
    }) => {
      setAuthError("");

      try {
        const result = await loginUser({
          identifier,
          password,
        });

        setUser(result.user);

        return result.user;
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Login failed.";

        setAuthError(message);
        throw error;
      }
    },
    [],
  );


  const register = useCallback(
    async ({
      email,
      username,
      fullName,
      password,
    }) => {
      setAuthError("");

      try {
        return await registerUser({
          email,
          username,
          fullName,
          password,
        });
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Registration failed.";

        setAuthError(message);
        throw error;
      }
    },
    [],
  );


  const logout = useCallback(() => {
    logoutUser();
    setUser(null);
    setAuthError("");
  }, []);


  const clearAuthError = useCallback(() => {
    setAuthError("");
  }, []);


  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      authError,
      login,
      register,
      logout,
      clearAuthError,
    }),
    [
      user,
      isLoading,
      authError,
      login,
      register,
      logout,
      clearAuthError,
    ],
  );


  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}