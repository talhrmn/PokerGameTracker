export const EMPTY_USER = {
  username: "",
  email: "",
  _id: "",
};

export const COOKIE_EXPERATION_IN_DAYS = 1;

export const DASHBOARD_ROUTE = "/dashboard";

export const AuthTab = {
  login: {
    tabName: "login",
    tabTitle: "-- Login --",
    submitRoute: "/auth/login",
  },
  signup: {
    tabName: "signup",
    tabTitle: "-- Signup --",
    submitRoute: "/auth/signup",
  },
};

export const TabItems = [
  {
    key: AuthTab.login.tabName,
    label: AuthTab.login.tabTitle,
  },
  {
    key: AuthTab.signup.tabName,
    label: AuthTab.signup.tabTitle,
  },
];

export type AuthTabType = "login" | "signup";

export const DEFAULT_AUTH_TAB = AuthTab.login;

export const UNEXPECTED_ERROR = "An unexpected error occurred. Please try again.";

export const INVALID_PASSWORD_MSG = "Password must be at least 8 characters long, contain at least one number, one uppercase letter, one lowercase letter, and one special character.";

export const VALID_PASSWORD_PATTERN = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_])[A-Za-z\d\W_]{8,}$/;

export const VALID_EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

