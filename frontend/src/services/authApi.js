import {
  clearAuthentication,
  getAccessToken,
  storeAccessToken,
  storeUser,
} from "./authStorage";


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const AUTH_API_URL =
  `${API_BASE_URL}/api/v1/auth`;


async function parseResponse(response) {
  try {
    return await response.json();
  } catch {
    throw new Error(
      "The server returned an invalid response.",
    );
  }
}


function extractErrorMessage(
  responseData,
  fallbackMessage,
) {
  if (
    typeof responseData?.error?.message ===
    "string"
  ) {
    return responseData.error.message;
  }

  if (
    typeof responseData?.detail === "string"
  ) {
    return responseData.detail;
  }

  return fallbackMessage;
}


function createApiError(
  message,
  status,
  code = null,
) {
  const error = new Error(message);

  error.status = status;
  error.code = code;

  return error;
}


async function request(
  path,
  options = {},
) {
  let response;

  try {
    response = await fetch(
      `${AUTH_API_URL}${path}`,
      options,
    );
  } catch {
    throw new Error(
      "Unable to connect to the authentication server.",
    );
  }

  const data = await parseResponse(response);

  if (!response.ok) {
    throw createApiError(
      extractErrorMessage(
        data,
        "The authentication request failed.",
      ),
      response.status,
      data?.error?.code ?? null,
    );
  }

  return data;
}


export async function registerUser({
  email,
  username,
  fullName,
  password,
}) {
  return request(
    "/register",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        email,
        username,
        full_name: fullName || null,
        password,
      }),
    },
  );
}


export async function loginUser({
  identifier,
  password,
}) {
  const data = await request(
    "/login",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        identifier,
        password,
      }),
    },
  );

  storeAccessToken(
    data.access_token,
  );

  storeUser(
    data.user,
  );

  return data;
}


export async function getCurrentUser() {
  const token = getAccessToken();

  if (!token) {
    return null;
  }

  try {
    const user = await request(
      "/me",
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      },
    );

    storeUser(user);

    return user;
  } catch (error) {
    if (error.status === 401) {
      clearAuthentication();
    }

    throw error;
  }
}


export function logoutUser() {
  clearAuthentication();
}