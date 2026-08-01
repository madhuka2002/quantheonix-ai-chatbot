const ACCESS_TOKEN_KEY =
  "quantheonix_access_token";

const CURRENT_USER_KEY =
  "quantheonix_current_user";


export function getAccessToken() {
  return localStorage.getItem(
    ACCESS_TOKEN_KEY,
  );
}


export function storeAccessToken(token) {
  if (
    typeof token !== "string" ||
    !token.trim()
  ) {
    throw new Error(
      "A valid access token is required.",
    );
  }

  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    token,
  );
}


export function removeAccessToken() {
  localStorage.removeItem(
    ACCESS_TOKEN_KEY,
  );
}


export function getStoredUser() {
  const storedValue = localStorage.getItem(
    CURRENT_USER_KEY,
  );

  if (!storedValue) {
    return null;
  }

  try {
    return JSON.parse(storedValue);
  } catch {
    localStorage.removeItem(
      CURRENT_USER_KEY,
    );

    return null;
  }
}


export function storeUser(user) {
  localStorage.setItem(
    CURRENT_USER_KEY,
    JSON.stringify(user),
  );
}


export function removeStoredUser() {
  localStorage.removeItem(
    CURRENT_USER_KEY,
  );
}


export function clearAuthentication() {
  removeAccessToken();
  removeStoredUser();
}