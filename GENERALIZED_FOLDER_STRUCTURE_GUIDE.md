# 🏛️ Production-Ready Frontend Architecture & Universal Folder Structure Guide

A standardized, scalable, and enterprise-grade blueprint for modern **React + TypeScript + Vite + Tailwind CSS / shadcn/ui** applications.

> **Purpose of this Document:**  
> This guide defines the canonical folder structure, component placement rules, architectural patterns, and code standards for frontend codebases. It is designed so that **engineering teams and AI coding assistants** can generate, scaffold, and maintain clean, modular, and consistent code without ambiguity.

---

## 📑 Table of Contents

1. [Architectural Philosophy](#-architectural-philosophy)
2. [Root Project Structure](#-root-project-structure)
3. [Source Code Organization (`src/`)](#-source-code-organization-src)
4. [Pages & Feature Structure (`src/pages/`)](#-pages--feature-structure-srcpages)
5. [Components Folder Structure (`src/components/`)](#-components-folder-structure-srccomponents)
6. [Hooks — When & Where to Create (`src/hooks/`)](#-hooks--when--where-to-create-srchooks)
7. [Helpers Folder Structure (`src/helpers/`)](#-helpers-folder-structure-srchelpers)
8. [Utils Folder Structure (`src/utils/`)](#-utils-folder-structure-srcutils)
9. [Providers Folder Structure (`src/providers/`)](#-providers-folder-structure-srcproviders)
10. [Shared Components Guidelines (`src/pages/shared-components/`)](#-shared-components-guidelines-srcpagesshared-components)
11. [File Naming & Code Conventions](#-file-naming--code-conventions)
12. [When to Create New Folders & Files](#-when-to-create-new-folders--files)
13. [Quick Reference Decision Tree](#-quick-reference-decision-tree)
14. [AI Agent Scaffolding Directives](#-ai-agent-scaffolding-directives)
15. [Real-World Walkthrough: Adding a New Feature](#-real-world-walkthrough-adding-a-new-feature)
16. [Best Practices & Anti-Patterns Checklist](#-best-practices--anti-patterns-checklist)
17. [Folder Summary Cheat Sheet](#-folder-summary-cheat-sheet)

---

## 💡 Architectural Philosophy

Our architecture is founded on four core principles:

1. **Separation of Concerns:** Pure UI primitives, app-level layout, feature-specific logic, API communications, and pure utilities are decoupled into designated, predictable layers.
2. **Feature-Driven Colocation:** Code that changes together stays together. Components, types, and logic specific to a single feature are colocated within that feature's directory rather than scattered globally.
3. **Unidirectional Dependency Flow:**
   - `pages` import from `components`, `hooks`, `helpers`, `utils`, `providers`.
   - `components` import from `components/ui`, `hooks`, `utils`.
   - `helpers/api` never imports UI components.
   - `utils` are pure functions with **zero external state or side effects**.
4. **AI-First Clarity:** Explicit directory rules and naming conventions eliminate guessing. Any developer or AI model given this guide can generate files in the exact expected destination.

---

## 📁 Root Project Structure

A clean, predictable root structure separating build tools, static assets, and source code:

```
project-root/
├── public/                    # Raw static assets served directly (never processed by Vite)
│   ├── favicon.ico            # Browser tab icon
│   ├── robots.txt             # Search crawler instructions
│   ├── site.webmanifest       # PWA manifest
│   └── fonts/                 # Custom local webfonts (.woff2, .ttf)
│
├── src/                       # All application source code
├── .env.example               # Template for environment variables (committed to git)
├── .env                       # Local environment variables (IGNORED in .gitignore)
├── .gitignore                 # Git ignore rules
├── eslint.config.js           # ESLint linting configuration
├── index.html                 # Single Page Application HTML entry point
├── package.json               # Dependencies, scripts, and package metadata
├── postcss.config.js          # PostCSS configuration (for Tailwind CSS)
├── tailwind.config.ts         # Tailwind CSS styling configuration
├── tsconfig.json              # TypeScript root configuration
├── tsconfig.app.json          # TypeScript frontend configuration
└── vite.config.ts             # Vite build & plugin configuration
```

### What goes in `public/` vs `src/assets/`?

| Criteria | `public/` | `src/assets/` |
|:---|:---|:---|
| **Build Processing** | Copied as-is to dist root without hashing | Processed, optimized, and hashed by Vite |
| **Import Method** | Referenced by absolute path: `/favicon.ico` | Imported in JS/TS: `import logo from '@/assets/logo.svg'` |
| **Use Cases** | `robots.txt`, `favicon.ico`, static download templates, unbundled scripts | SVGs, branded logos, JSON mock files, background images |

---

## 🗂️ Source Code Organization (`src/`)

```
src/
├── app/                       # Application-wide routing and route guards
│   ├── router.tsx             # React Router configuration
│   └── ProtectedRoute.tsx     # Route authentication guard
│
├── assets/                    # Bundled static assets (logos, illustrations, icons)
│   ├── images/
│   └── icons/
│
├── components/                # Application-wide UI components
│   ├── ui/                    # Primitive design-system elements (shadcn/ui - DO NOT MODIFY directly)
│   ├── app-sidebar.tsx        # Global application sidebar navigation
│   ├── site-header.tsx        # Global top navigation bar
│   ├── nav-main.tsx           # Sidebar primary navigation group
│   ├── nav-user.tsx           # Authenticated user dropdown in sidebar/header
│   ├── data-table.tsx         # Reusable data table with sort, filter, and pagination
│   ├── page-header.tsx        # Standard page header with breadcrumbs and actions
│   └── theme-toggle.tsx       # Light / Dark mode switcher
│
├── helpers/                   # Business logic, API communication, and integration
│   ├── api/                   # Axios client and entity-specific API service files
│   ├── common/                # Shared helpers (table helpers, pagination, route helpers)
│   └── auth/                  # Token management, session validation, and permissions
│
├── hooks/                     # Custom React hooks (reusable stateful logic)
│   ├── use-debounce.ts        # Debounce hook for inputs and queries
│   ├── use-mobile.tsx         # Viewport / responsive breakpoint detection
│   └── use-toast.ts           # Toast notification trigger hook
│
├── lib/                       # Third-party library wrapper and utility configurations
│   └── utils.ts               # Class merge utility (clsx + tailwind-merge for shadcn)
│
├── pages/                     # Feature pages and route views
│   ├── Authentication/        # Login, Register, Forgot Password, Reset Password
│   ├── Dashboard/             # Main metrics, analytics, and overview
│   ├── Users/                 # User management feature
│   ├── <FeatureName>/         # Major feature modules (e.g. Products, Orders, Projects)
│   └── shared-components/     # Complex domain components shared across 2+ features
│
├── providers/                 # React Context providers for global cross-cutting state
│   ├── AuthProvider.tsx       # User session and authorization state
│   └── ThemeProvider.tsx      # Dark / light / system theme state
│
├── types/                     # Shared global TypeScript definitions
│   ├── common.ts              # Global primitives (ID, Status, ApiResponse, etc.)
│   └── user.ts                # Global user entity interfaces
│
├── utils/                     # Pure mathematical, formatting, and validation utilities
│   ├── formatters.ts          # Currency, date, string formatting
│   ├── validators.ts          # Email, password, input validation
│   └── constants.ts           # Application constants and static config
│
├── App.tsx                    # Top-level application component
├── AppWrapper.tsx             # Context provider wrapping hierarchy
├── main.tsx                   # React root mount entry point
├── index.css                  # Global Tailwind CSS directives and theme variables
└── App.css                    # App-specific overrides (if any)
```

---

## 🧭 Pages & Feature Structure (`src/pages/`)

Each subfolder in `src/pages/` represents a **major feature or route domain** of the application.

### Canonical Feature Folder Layout:

```
src/pages/
├── Authentication/            # Authentication & Onboarding
│   ├── LoginPage.tsx          # Login route component
│   ├── RegisterPage.tsx       # User registration
│   ├── ForgotPassword.tsx     # Password recovery
│   └── authHelper.ts          # Auth-specific local helpers (if not global)
│
├── Dashboard/                 # Dashboard & Analytics
│   ├── DashboardPage.tsx      # Dashboard layout view
│   ├── components/            # Dashboard-specific widgets (colocated)
│   │   ├── MetricCard.tsx
│   │   ├── RevenueChart.tsx
│   │   └── RecentActivityList.tsx
│   └── dashboardOptions.json  # Static configuration or filter options
│
├── <FeatureName>/             # E.g., 'Projects', 'Orders', 'Inventory', 'Users'
│   ├── <FeatureName>ListPage.tsx   # Primary list view with filters & data table
│   ├── <FeatureName>DetailPage.tsx # Single entity view with tabs/details
│   ├── <FeatureName>Modal.tsx      # Create / Edit modal or drawer
│   ├── components/                 # Sub-components ONLY used inside this feature
│   │   ├── <FeatureName>Card.tsx
│   │   ├── <FeatureName>FilterBar.tsx
│   │   └── <FeatureName>Stats.tsx
│   └── types.ts                    # Feature-specific TypeScript interfaces (optional)
│
├── NotFoundPage.tsx           # Standalone 404 page (placed directly in pages/)
├── UnauthorizedPage.tsx       # Standalone 403 page
│
└── shared-components/         # Domain components shared across MULTIPLE features
    ├── StatusBadge.tsx        # Shared entity status badge
    ├── EmptyState.tsx         # Shared empty placeholder state
    ├── ConfirmDialog.tsx      # Shared action confirmation dialog
    ├── PageContainer.tsx      # Uniform page padding and layout wrapper
    └── ActionButton.tsx       # Standard action button with icon & permission check
```

### 🎯 Rules for Adding Pages:

1. **Major Feature (3+ files or sub-views):** Always create a dedicated folder under `src/pages/<FeatureName>/`.
2. **Subcomponents:** When a page grows beyond ~250 lines or has child components (like cards, tabs, filters), create a `components/` subfolder inside that feature folder.
3. **Single-File Route:** Only place `.tsx` files directly at `src/pages/` root if they are self-contained, single-purpose pages with no dedicated subcomponents (e.g., `NotFoundPage.tsx`, `TermsOfService.tsx`).

---

## 🧩 Components Folder Structure (`src/components/`)

We enforce a strict **3-Tier Component Hierarchy** to prevent component pollution:

```
src/components/
├── ui/                        # TIER 1: Design System Primitives (shadcn/ui)
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── dropdown-menu.tsx
│   ├── input.tsx
│   ├── select.tsx
│   ├── table.tsx
│   └── toast.tsx
│
├── app-sidebar.tsx            # TIER 2: App Shell / Layout Components
├── site-header.tsx
├── nav-main.tsx
├── nav-user.tsx
├── data-table.tsx             # Generic reusable data table
├── page-header.tsx
└── theme-toggle.tsx
```

### The 3 Component Tiers Explained:

#### Tier 1: UI Primitives (`src/components/ui/`)
- **What belongs here:** Raw, headless or styled primitive design tokens (buttons, badges, inputs, dialogs, tooltips).
- **Installed via:** `npx shadcn@latest add <component-name>`
- **Strict Rule:** **NEVER write business logic, entity models, or API calls inside `components/ui/`**. Keep them 100% reusable and presentation-only.

#### Tier 2: App Shell & Global Layout (`src/components/`)
- **What belongs here:** Structural elements that frame the application (Sidebars, Topbars, User Profile Navigators, Global Breadcrumb Bars, App Data Tables).
- **Rule:** Used across multiple pages or as part of the primary app layout frame.

#### Tier 3: Feature-Scoped Components (`src/pages/<FeatureName>/components/`)
- **What belongs here:** Components that only make sense within that specific feature (e.g., `ProjectTimeline.tsx` only in `Projects/`).
- **Rule:** If a component is NOT used outside `<FeatureName>`, keep it strictly inside `<FeatureName>/components/`.

---

## 🪝 Hooks — When & Where to Create (`src/hooks/`)

**Location:** `src/hooks/`  
**Purpose:** Encapsulate reusable stateful logic, side effects, subscriptions, or complex component behavior.

### 🎯 When to Create a Custom Hook?

Create a hook if and only if:
1. You are reusing **stateful logic (`useState`, `useEffect`, `useContext`)** across 2+ components.
2. You need to extract complex, cluttered logic out of a component to improve readability and testability.
3. You are handling browser APIs (window size, localStorage, media queries, event listeners).
4. You are managing async lifecycle queries with loading, data, and error states.

---

### Production Hook Examples:

#### ✅ Example 1: Generic Data Fetching Hook with State & Refresh
```typescript
// src/hooks/useEntityQuery.ts
import { useState, useEffect, useCallback } from 'react';

interface UseEntityQueryResult<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
    refetch: () => Promise<void>;
}

export const useEntityQuery = <T>(
    fetcher: () => Promise<T>,
    deps: unknown[] = []
): UseEntityQueryResult<T> => {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const executeFetch = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await fetcher();
            setData(result);
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'An unexpected error occurred';
            setError(message);
        } finally {
            setLoading(false);
        }
    }, deps); // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => {
        executeFetch();
    }, [executeFetch]);

    return { data, loading, error, refetch: executeFetch };
};
```

---

#### ✅ Example 2: Debounced Value Hook (Search & Input optimization)
```typescript
// src/hooks/use-debounce.ts
import { useState, useEffect } from 'react';

export const useDebounce = <T>(value: T, delayMs: number = 300): T => {
    const [debouncedValue, setDebouncedValue] = useState<T>(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delayMs);

        return () => {
            clearTimeout(handler);
        };
    }, [value, delayMs]);

    return debouncedValue;
};
```

---

#### ✅ Example 3: Synchronized LocalStorage Hook
```typescript
// src/hooks/useLocalStorage.ts
import { useState, useEffect, useCallback } from 'react';

export const useLocalStorage = <T>(key: string, initialValue: T) => {
    const readValue = useCallback((): T => {
        if (typeof window === 'undefined') return initialValue;
        try {
            const item = window.localStorage.getItem(key);
            return item ? (JSON.parse(item) as T) : initialValue;
        } catch (error) {
            console.warn(`[useLocalStorage] Error reading key "${key}":`, error);
            return initialValue;
        }
    }, [key, initialValue]);

    const [storedValue, setStoredValue] = useState<T>(readValue);

    const setValue = (value: T | ((val: T) => T)) => {
        try {
            const newValue = value instanceof Function ? value(storedValue) : value;
            setStoredValue(newValue);
            if (typeof window !== 'undefined') {
                window.localStorage.setItem(key, JSON.stringify(newValue));
                window.dispatchEvent(new Event('local-storage-sync'));
            }
        } catch (error) {
            console.warn(`[useLocalStorage] Error setting key "${key}":`, error);
        }
    };

    useEffect(() => {
        setStoredValue(readValue());
        const handleSync = () => setStoredValue(readValue());
        window.addEventListener('local-storage-sync', handleSync);
        return () => window.removeEventListener('local-storage-sync', handleSync);
    }, [readValue]);

    return [storedValue, setValue] as const;
};
```

---

#### ✅ Example 4: Role & Permission Verification Hook
```typescript
// src/hooks/usePermissions.ts
import { useAuthentication } from '@/providers/AuthProvider';

export const usePermissions = () => {
    const { user, isAuthenticated } = useAuthentication();

    const hasRole = (requiredRole: string): boolean => {
        if (!isAuthenticated || !user) return false;
        return user.role === requiredRole;
    };

    const hasPermission = (permission: string): boolean => {
        if (!isAuthenticated || !user) return false;
        return user.permissions?.includes(permission) ?? false;
    };

    return {
        isAdmin: hasRole('admin'),
        isManager: hasRole('manager'),
        hasRole,
        hasPermission,
    };
};
```

---

### ❌ When NOT to Create a Hook:
- **Pure calculations or transformations:** If there is no `useState`, `useEffect`, or other hook inside, put it in `src/utils/`.
- **Direct API functions without state:** Put them in `src/helpers/api/`.
- **One-off simple component state:** Use standard `useState` directly in the component.

```typescript
// ❌ WRONG: Not a hook! No React state or lifecycle.
export const useCalculateDiscount = (price: number, discount: number) => {
    return price * (1 - discount / 100);
};

// ✅ RIGHT: Pure utility function in src/utils/formatters.ts
export const calculateDiscount = (price: number, discount: number): number => {
    return price * (1 - discount / 100);
};
```

---

## 🛠️ Helpers Folder Structure (`src/helpers/`)

**Location:** `src/helpers/`  
**Purpose:** Business logic integration, API communication, parameter normalization, and identity/auth services.

```
src/helpers/
├── api/                       # HTTP API client and entity services
│   ├── apiClient.ts           # Axios instance with request/response interceptors
│   ├── authApiHelper.ts       # Authentication endpoints (login, refresh, logout)
│   ├── userApiHelper.ts       # User CRUD API operations
│   └── <entity>ApiHelper.ts   # Entity-specific API services (e.g. projects, orders)
│
├── common/                    # Shared helper functions with business awareness
│   ├── apiParamsHelper.ts     # Query parameter serializer & builder
│   ├── tableHelper.ts         # Generic table pagination types & calculators
│   └── routesHelper.ts        # Dynamic route building & permission mapping
│
└── auth/                      # Authentication & Identity utilities
    └── authHelper.ts          # JWT token decoding, expiration check, cookie/token storage
```

---

### Standard Production API Client Pattern:

```typescript
// src/helpers/api/apiClient.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getAuthToken, removeAuthToken } from '../auth/authHelper';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Inject JWT Bearer Token
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = getAuthToken();
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error: AxiosError) => Promise.reject(error)
);

// Response Interceptor: Global Error Handler & Token Expiry Catch
apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        if (error.response?.status === 401) {
            removeAuthToken();
            window.location.href = '/login?expired=true';
        }
        return Promise.reject(error);
    }
);

export default apiClient;
```

---

### Standard Entity API Helper Template:

```typescript
// src/helpers/api/<entity>ApiHelper.ts
import apiClient from './apiClient';
import { PaginatedResponse, PaginationParams } from '../common/tableHelper';

export interface EntityModel {
    id: string;
    title: string;
    status: 'active' | 'pending' | 'inactive' | 'archived';
    createdAt: string;
    updatedAt: string;
}

export type CreateEntityDto = Omit<EntityModel, 'id' | 'createdAt' | 'updatedAt'>;
export type UpdateEntityDto = Partial<CreateEntityDto>;

export const getEntities = async (
    params?: PaginationParams
): Promise<PaginatedResponse<EntityModel>> => {
    const response = await apiClient.get<PaginatedResponse<EntityModel>>(`/entities`, { params });
    return response.data;
};

export const getEntityById = async (id: string): Promise<EntityModel> => {
    const response = await apiClient.get<EntityModel>(`/entities/${id}`);
    return response.data;
};

export const createEntity = async (payload: CreateEntityDto): Promise<EntityModel> => {
    const response = await apiClient.post<EntityModel>(`/entities`, payload);
    return response.data;
};

export const updateEntity = async (id: string, payload: UpdateEntityDto): Promise<EntityModel> => {
    const response = await apiClient.put<EntityModel>(`/entities/${id}`, payload);
    return response.data;
};

export const deleteEntity = async (id: string): Promise<void> => {
    await apiClient.delete(`/entities/${id}`);
};
```

---

## 🔧 Utils Folder Structure (`src/utils/`)

**Location:** `src/utils/`  
**Purpose:** Pure utility functions with **deterministic outputs**, zero side effects, and no dependency on React or component state.

### 🎯 The Difference Matrix:

| Aspect | `src/utils/` | `src/helpers/` | `src/hooks/` |
|:---|:---|:---|:---|
| **Purity** | **100% Pure Functions** | May have side effects / I/O | Stateful (React Lifecycle) |
| **API Calls** | ❌ Never | ✅ Yes (in `helpers/api/`) | ⚠️ Only via calling helpers |
| **React Hooks** | ❌ Never | ❌ Never | ✅ Always (`useState`, etc.) |
| **Examples** | `formatCurrency`, `isValidEmail` | `apiClient`, `tableHelper` | `useDebounce`, `useLocalStorage` |

---

### Production Utility Examples:

#### 1. Pure Formatters (`src/utils/formatters.ts`)
```typescript
// src/utils/formatters.ts

export const formatCurrency = (amount: number, currency: string = 'USD', locale: string = 'en-US'): string => {
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency,
        minimumFractionDigits: 2,
    }).format(amount);
};

export const formatDate = (dateString: string | Date, options?: Intl.DateTimeFormatOptions): string => {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    if (isNaN(date.getTime())) return 'N/A';
    return new Intl.DateTimeFormat('en-US', options ?? {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    }).format(date);
};

export const truncateString = (text: string, maxLength: number): string => {
    if (!text || text.length <= maxLength) return text;
    return `${text.slice(0, maxLength)}...`;
};

export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};
```

#### 2. Pure Validators (`src/utils/validators.ts`)
```typescript
// src/utils/validators.ts

export const isValidEmail = (email: string): boolean => {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
};

export const isStrongPassword = (password: string): boolean => {
    // Min 8 chars, 1 uppercase, 1 lowercase, 1 number
    return password.length >= 8 &&
        /[A-Z]/.test(password) &&
        /[a-z]/.test(password) &&
        /[0-9]/.test(password);
};

export const isValidUrl = (url: string): boolean => {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
};
```

---

## 🔄 Providers Folder Structure (`src/providers/`)

**Location:** `src/providers/`  
**Purpose:** React Context providers responsible for application-wide, cross-cutting state.

### 🎯 When to Create a Provider?
- Global session authentication & user profile state
- Visual theme mode (`light`, `dark`, `system`)
- Modal/Dialog global manager
- WebSocket or real-time event hub
- **DO NOT** use Context for simple local component state or server-cache that belongs in React Query/SWR.

---

### Production Auth Provider Template:

```typescript
// src/providers/AuthProvider.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getAuthToken, removeAuthToken, setAuthToken } from '@/helpers/auth/authHelper';

export interface UserProfile {
    id: string;
    email: string;
    name: string;
    role: 'admin' | 'manager' | 'user';
    permissions: string[];
}

interface AuthContextType {
    user: UserProfile | null;
    isAuthenticated: boolean;
    loading: boolean;
    login: (token: string, user: UserProfile) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const token = getAuthToken();
        if (token) {
            // Validate or re-hydrate user from session
            try {
                const storedUser = localStorage.getItem('current_user');
                if (storedUser) setUser(JSON.parse(storedUser));
            } catch {
                removeAuthToken();
            }
        }
        setLoading(false);
    }, []);

    const login = (token: string, newUser: UserProfile) => {
        setAuthToken(token);
        setUser(newUser);
        localStorage.setItem('current_user', JSON.stringify(newUser));
    };

    const logout = () => {
        removeAuthToken();
        setUser(null);
        localStorage.removeItem('current_user');
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated: !!user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuthentication = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuthentication must be used within an AuthProvider');
    }
    return context;
};
```

---

### Production Theme Provider Template:

```typescript
// src/providers/ThemeProvider.tsx
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

type Theme = 'dark' | 'light' | 'system';

interface ThemeProviderProps {
    children: ReactNode;
    defaultTheme?: Theme;
    storageKey?: string;
}

interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({
    children,
    defaultTheme = 'system',
    storageKey = 'app-ui-theme',
}: ThemeProviderProps) => {
    const [theme, setTheme] = useState<Theme>(
        () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
    );

    useEffect(() => {
        const root = window.document.documentElement;
        root.classList.remove('light', 'dark');

        if (theme === 'system') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
                ? 'dark'
                : 'light';
            root.classList.add(systemTheme);
            return;
        }

        root.classList.add(theme);
    }, [theme]);

    const value = {
        theme,
        setTheme: (newTheme: Theme) => {
            localStorage.setItem(storageKey, newTheme);
            setTheme(newTheme);
        },
    };

    return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = (): ThemeContextType => {
    const context = useContext(ThemeContext);
    if (!context) throw new Error('useTheme must be used within a ThemeProvider');
    return context;
};
```

---

### App Provider Hierarchy (`src/AppWrapper.tsx`):

```typescript
// src/AppWrapper.tsx
import { ReactNode } from 'react';
import { AuthProvider } from '@/providers/AuthProvider';
import { ThemeProvider } from '@/providers/ThemeProvider';

export const AppWrapper = ({ children }: { children: ReactNode }) => {
    return (
        <ThemeProvider defaultTheme="system">
            <AuthProvider>
                {children}
            </AuthProvider>
        </ThemeProvider>
    );
};
```

---

## 🌐 Shared Components Guidelines (`src/pages/shared-components/`)

**Location:** `src/pages/shared-components/`  
**Purpose:** Reusable, domain-aware UI components used across **multiple pages or features**.

### 🎯 Where Does a Component Go?

```
Is it a primitive element (button, simple dialog, raw input)?
├── YES → src/components/ui/ (shadcn)
└── NO → Is it used ONLY in one feature (e.g. Orders)?
         ├── YES → src/pages/Orders/components/
         └── NO → Is it an app-wide frame (sidebar, header)?
                  ├── YES → src/components/
                  └── NO → src/pages/shared-components/
```

---

### Production Shared Component Examples:

#### 1. Universal Status Badge (`src/pages/shared-components/StatusBadge.tsx`)
```typescript
// src/pages/shared-components/StatusBadge.tsx
import { Badge } from '@/components/ui/badge';

export type StatusType = 'active' | 'pending' | 'inactive' | 'failed' | 'completed';

interface StatusBadgeProps {
    status: StatusType;
    label?: string;
}

const statusConfig: Record<StatusType, { bg: string; text: string; defaultLabel: string }> = {
    active: { bg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20', text: 'Active', defaultLabel: 'Active' },
    pending: { bg: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20', text: 'Pending', defaultLabel: 'Pending' },
    inactive: { bg: 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20', text: 'Inactive', defaultLabel: 'Inactive' },
    failed: { bg: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20', text: 'Failed', defaultLabel: 'Failed' },
    completed: { bg: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20', text: 'Completed', defaultLabel: 'Completed' },
};

export const StatusBadge = ({ status, label }: StatusBadgeProps) => {
    const config = statusConfig[status] || statusConfig.inactive;

    return (
        <Badge variant="outline" className={`font-medium capitalize ${config.bg}`}>
            {label || config.defaultLabel}
        </Badge>
    );
};
```

---

#### 2. Universal Empty State (`src/pages/shared-components/EmptyState.tsx`)
```typescript
// src/pages/shared-components/EmptyState.tsx
import { ReactNode } from 'react';
import { LucideIcon, Inbox } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EmptyStateProps {
    title: string;
    description: string;
    icon?: LucideIcon;
    actionLabel?: string;
    onAction?: () => void;
    children?: ReactNode;
}

export const EmptyState = ({
    title,
    description,
    icon: Icon = Inbox,
    actionLabel,
    onAction,
    children,
}: EmptyStateProps) => {
    return (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border p-12 text-center animate-in fade-in-50">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted/60 text-muted-foreground mb-4">
                <Icon className="h-8 w-8 stroke-[1.5]" />
            </div>
            <h3 className="text-lg font-semibold text-foreground">{title}</h3>
            <p className="mt-1 text-sm text-muted-foreground max-w-sm mb-6">
                {description}
            </p>
            {actionLabel && onAction && (
                <Button onClick={onAction} className="gap-2">
                    {actionLabel}
                </Button>
            )}
            {children}
        </div>
    );
};
```

---

#### 3. Universal Confirmation Dialog (`src/pages/shared-components/ConfirmDialog.tsx`)
```typescript
// src/pages/shared-components/ConfirmDialog.tsx
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface ConfirmDialogProps {
    isOpen: boolean;
    title: string;
    description: string;
    confirmLabel?: string;
    cancelLabel?: string;
    variant?: 'default' | 'destructive';
    onConfirm: () => void;
    onCancel: () => void;
}

export const ConfirmDialog = ({
    isOpen,
    title,
    description,
    confirmLabel = 'Continue',
    cancelLabel = 'Cancel',
    variant = 'default',
    onConfirm,
    onCancel,
}: ConfirmDialogProps) => {
    return (
        <AlertDialog open={isOpen} onOpenChange={(open) => !open && onCancel()}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>{title}</AlertDialogTitle>
                    <AlertDialogDescription>{description}</AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel onClick={onCancel}>{cancelLabel}</AlertDialogCancel>
                    <AlertDialogAction
                        onClick={onConfirm}
                        className={variant === 'destructive' ? 'bg-destructive hover:bg-destructive/90 text-destructive-foreground' : ''}
                    >
                        {confirmLabel}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
};
```

---

## 📝 File Naming & Code Conventions

Consistently naming files ensures predictable imports and automatic sorting across all IDEs and AI tools.

| Category | Convention | Examples |
|:---|:---|:---|
| **Page Components** | `PascalCase.tsx` | `UsersListPage.tsx`, `LoginPage.tsx`, `DashboardPage.tsx` |
| **Feature Components** | `PascalCase.tsx` | `UserCard.tsx`, `ProjectFilterBar.tsx` |
| **UI Primitives (shadcn)** | `kebab-case.tsx` | `button.tsx`, `dropdown-menu.tsx`, `dialog.tsx` |
| **App Layout Components** | `kebab-case.tsx` | `app-sidebar.tsx`, `site-header.tsx`, `data-table.tsx` |
| **Custom Hooks** | `use<CamelCase>.ts(x)` | `useLocalStorage.ts`, `useEntityQuery.ts`, `use-debounce.ts` |
| **API Helpers** | `<entity>ApiHelper.ts` | `usersApiHelper.ts`, `projectsApiHelper.ts` |
| **Utility Files** | `camelCase.ts` | `formatters.ts`, `validators.ts`, `constants.ts` |
| **TypeScript Types** | `camelCase.ts` or `types.ts` | `common.ts`, `user.ts`, `types.ts` |
| **Context Providers** | `PascalCase.tsx` | `AuthProvider.tsx`, `ThemeProvider.tsx` |

---

## 📦 When to Create New Folders & Files

To maintain a clean codebase as features expand, follow these explicit quantitative rules:

| Trigger / Condition | Action Required | Destination |
|:---|:---|:---|
| A new route / domain is added (e.g. Billing) | Create new feature folder | `src/pages/Billing/` |
| A page file exceeds **250 lines** | Split sub-views into components | `src/pages/<Feature>/components/` |
| 3+ related components exist for one feature | Group in feature component folder | `src/pages/<Feature>/components/` |
| A component is used in **2 or more independent features** | Move component to shared | `src/pages/shared-components/` |
| Stateful logic is repeated in 2+ components | Extract into a custom hook | `src/hooks/use<Name>.ts` |
| A new backend entity needs CRUD endpoints | Create new API helper file | `src/helpers/api/<entity>ApiHelper.ts` |
| A function has NO state, NO side-effects, and NO React imports | Place in utility file | `src/utils/formatters.ts` (or relevant util) |
| App-wide state needed across disconnected routes | Create Context provider | `src/providers/<Name>Provider.tsx` |

---

## 🌳 Quick Reference Decision Tree

Follow this step-by-step logic tree whenever deciding where a new file belongs:

```
START: "Where should this file go?"
│
├── Is it a Page or Route endpoint?
│   ├── YES → Does it have multiple components/tabs/views?
│   │         ├── YES → Create: src/pages/<FeatureName>/<FeatureName>Page.tsx
│   │         └── NO (Single simple page) → Place: src/pages/<PageName>.tsx
│   │
│   └── NO → Is it a UI Component?
│             ├── Is it a primitive design token (button, badge, input, modal dialog)?
│             │   └── YES → src/components/ui/<component>.tsx (shadcn/ui)
│             │
│             ├── Is it an App Shell / Global Frame layout component (header, sidebar)?
│             │   └── YES → src/components/<component-name>.tsx
│             │
│             ├── Is it used across 2 or more independent features?
│             │   └── YES → src/pages/shared-components/<ComponentName>.tsx
│             │
│             └── Is it used ONLY within one specific feature?
│                 └── YES → src/pages/<FeatureName>/components/<ComponentName>.tsx
│
├── Is it Stateful React Logic (uses useState, useEffect, useContext)?
│   ├── Is it App-Wide Global State wrapping the component tree?
│   │   └── YES → src/providers/<Name>Provider.tsx
│   │
│   └── Is it reusable reactive logic or event listeners?
│       └── YES → src/hooks/use<Name>.ts
│
├── Is it an HTTP Request / Backend Communication?
│   ├── Is it the Axios instance / interceptor setup?
│   │   └── YES → src/helpers/api/apiClient.ts
│   │
│   └── Is it CRUD operations for a specific backend entity?
│       └── YES → src/helpers/api/<entity>ApiHelper.ts
│
└── Is it a Helper or Utility function?
    ├── Does it perform pure math, string formatting, date formatting, or regex validation?
    │   └── YES (Pure, no I/O) → src/utils/<category>.ts
    │
    └── Does it involve route permissions, table pagination logic, or browser storage?
        └── YES → src/helpers/common/<helperName>.ts
```

---

## 🤖 AI Agent Scaffolding Directives

> **Instructions for AI Coding Assistants (Copilot, Cursor, Claude, Antigravity, etc.):**  
> When the user asks you to implement a new feature, page, API, or component, **you must strictly conform to the rules in this document**.

### AI Execution Protocol:

1. **Feature Scaffolding:**
   - When asked to "Create the `<Feature>` feature", generate:
     1. `src/helpers/api/<feature>ApiHelper.ts` (Typed API calls & DTOs)
     2. `src/pages/<Feature>/<Feature>ListPage.tsx` (Primary view)
     3. `src/pages/<Feature>/components/` (Colocated sub-components)
     4. Route registration in `src/app/router.tsx` or `App.tsx`
2. **Never inline API calls:**
   - Do **NOT** write `axios.get()` or `fetch()` inside component files or `useEffect`.
   - Always route requests through `src/helpers/api/`.
3. **Never place domain logic in `components/ui/`:**
   - `src/components/ui/` is reserved exclusively for uncoupled design primitives.
4. **Colocation First:**
   - Do not pollute `src/components/` with components used by only one feature page.
5. **Types Placement:**
   - Global entity types go in `src/types/`.
   - Feature-specific DTOs/interfaces go in `src/helpers/api/<feature>ApiHelper.ts` or `src/pages/<Feature>/types.ts`.

---

## 🚀 Real-World Walkthrough: Adding a New Feature

Here is the exact step-by-step workflow for adding a new domain feature (e.g., **`Orders`**):

### Step 1: Create the API Helper & Types
Create `src/helpers/api/ordersApiHelper.ts` with all types, endpoints, and pagination:
```typescript
// src/helpers/api/ordersApiHelper.ts
import apiClient from './apiClient';
import { PaginatedResponse, PaginationParams } from '../common/tableHelper';

export interface Order {
    id: string;
    orderNumber: string;
    customerName: string;
    totalAmount: number;
    status: 'active' | 'pending' | 'completed' | 'failed';
    createdAt: string;
}

export const getOrders = async (params?: PaginationParams): Promise<PaginatedResponse<Order>> => {
    const res = await apiClient.get<PaginatedResponse<Order>>(`/orders`, { params });
    return res.data;
};

export const cancelOrder = async (orderId: string): Promise<void> => {
    await apiClient.post(`/orders/${orderId}/cancel`);
};
```

### Step 2: Create the Feature Directory & Components
Create `src/pages/Orders/` and its subcomponents:
```
src/pages/Orders/
├── OrdersListPage.tsx              # Main list with table & search
├── OrderDetailPage.tsx             # Detail view of single order
└── components/
    ├── OrderStatsCards.tsx         # Summary stats on top
    └── OrderFilterBar.tsx          # Filter & date range controls
```

### Step 3: Implement Feature List Page using Standard Architecture
```typescript
// src/pages/Orders/OrdersListPage.tsx
import { useState, useEffect } from 'react';
import { Order, getOrders } from '@/helpers/api/ordersApiHelper';
import { StatusBadge } from '@/pages/shared-components/StatusBadge';
import { EmptyState } from '@/pages/shared-components/EmptyState';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { Button } from '@/components/ui/button';
import { OrderStatsCards } from './components/OrderStatsCards';

export const OrdersListPage = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getOrders()
            .then((data) => setOrders(data.items))
            .finally(() => setLoading(false));
    }, []);

    if (!loading && orders.length === 0) {
        return (
            <EmptyState
                title="No orders found"
                description="Create your first customer order to get started."
                actionLabel="New Order"
                onAction={() => console.log('New Order Clicked')}
            />
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Orders</h1>
                    <p className="text-muted-foreground">Manage and fulfill customer orders.</p>
                </div>
                <Button>Create Order</Button>
            </div>

            <OrderStatsCards />

            {/* Reusable Data Table */}
            <div className="rounded-lg border bg-card">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b text-muted-foreground">
                            <th className="p-4 text-left">Order #</th>
                            <th className="p-4 text-left">Customer</th>
                            <th className="p-4 text-left">Date</th>
                            <th className="p-4 text-left">Total</th>
                            <th className="p-4 text-left">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {orders.map((order) => (
                            <tr key={order.id} className="border-b hover:bg-muted/50">
                                <td className="p-4 font-medium">{order.orderNumber}</td>
                                <td className="p-4">{order.customerName}</td>
                                <td className="p-4">{formatDate(order.createdAt)}</td>
                                <td className="p-4">{formatCurrency(order.totalAmount)}</td>
                                <td className="p-4">
                                    <StatusBadge status={order.status} />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
```

### Step 4: Register Route in App Router
```typescript
// In src/app/router.tsx or App.tsx:
<Route path="/orders" element={<OrdersListPage />} />
<Route path="/orders/:id" element={<OrderDetailPage />} />
```

---

## 🛡️ Best Practices & Anti-Patterns Checklist

### ✅ Architectural Best Practices Checklist
- [ ] Components are placed in the correct tier based on reusability (`ui/` vs `components/` vs `shared-components/` vs feature `components/`).
- [ ] All API requests pass through `src/helpers/api/` (never direct `axios` calls in components).
- [ ] Utilities in `src/utils/` are 100% pure functions (no React hooks, no state, no API calls).
- [ ] Custom hooks are prefixed with `use` and contain active React state/lifecycle hooks.
- [ ] Shared components in `src/pages/shared-components/` are used by at least 2 distinct features.
- [ ] File names strictly adhere to naming conventions (`PascalCase.tsx`, `camelCase.ts`, etc.).
- [ ] Page components exceeding ~250 lines have their sub-views extracted into colocated `components/`.
- [ ] Global Context Providers are mounted cleanly in `AppWrapper.tsx`.

---

### ❌ Anti-Patterns to Avoid at All Costs

#### Anti-Pattern 1: Inlining API calls in components
```typescript
// ❌ WRONG: Inlining API calls inside components
const UserList = () => {
    useEffect(() => {
        axios.get('/api/v1/users').then(res => setUsers(res.data)); // ❌
    }, []);
};

// ✅ RIGHT: Calling dedicated API service helper
const UserList = () => {
    useEffect(() => {
        getUsers().then(res => setUsers(res.items)); // ✅
    }, []);
};
```

#### Anti-Pattern 2: Domain logic inside `components/ui/`
```typescript
// ❌ WRONG: Putting domain logic or API types in shadcn UI primitives
// src/components/ui/button.tsx
interface ButtonProps {
    orderStatus?: 'pending' | 'completed'; // ❌ Domain logic pollution!
}

// ✅ RIGHT: Keep UI primitives 100% generic
// src/components/ui/button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'default' | 'destructive' | 'outline';
}
```

#### Anti-Pattern 3: Fake hooks without React state
```typescript
// ❌ WRONG: Hook without state or effects
export const useFormatDate = (date: string) => {
    return new Date(date).toLocaleDateString(); // ❌ No state or lifecycle!
};

// ✅ RIGHT: Pure utility in src/utils/formatters.ts
export const formatDate = (date: string): string => {
    return new Date(date).toLocaleDateString(); // ✅ Pure utility
};
```

#### Anti-Pattern 4: Dumping single-feature components into global shared
```typescript
// ❌ WRONG: Placing a component used only by Orders into shared-components
// src/pages/shared-components/OrderInvoiceCalculator.tsx (Only used in Orders!)

// ✅ RIGHT: Colocate inside the feature
// src/pages/Orders/components/OrderInvoiceCalculator.tsx
```

---

## 📊 Folder Summary Cheat Sheet

| Folder Path | Primary Responsibility | Strict Placement Rules | Examples |
|:---|:---|:---|:---|
| `public/` | Unprocessed static assets | Direct URL access, never hashed | `favicon.ico`, `robots.txt`, fonts |
| `src/assets/` | Bundled assets | Processed and hashed by Vite | `logo.svg`, illustrations, mock JSON |
| `src/components/ui/` | Design system primitives | Headless/generic, NO domain logic | `button.tsx`, `dialog.tsx`, `input.tsx` |
| `src/components/` | App shell layout & frames | Global layout used across routes | `app-sidebar.tsx`, `site-header.tsx` |
| `src/pages/<Feature>/` | Major feature pages | Route view endpoints | `OrdersListPage.tsx`, `LoginPage.tsx` |
| `src/pages/<Feature>/components/`| Colocated subcomponents | Used ONLY by this feature | `OrderCard.tsx`, `UserFilterBar.tsx` |
| `src/pages/shared-components/` | Shared domain components | Reused in **2+ independent features** | `StatusBadge.tsx`, `EmptyState.tsx` |
| `src/hooks/` | Custom React hooks | Must use `useState`/`useEffect` | `useLocalStorage.ts`, `useDebounce.ts` |
| `src/helpers/api/` | HTTP API integration | Axios client & entity CRUD methods | `apiClient.ts`, `usersApiHelper.ts` |
| `src/helpers/common/` | Shared business helpers | Table pagination, query serializers | `tableHelper.ts`, `apiParamsHelper.ts` |
| `src/helpers/auth/` | Auth & token services | Token decode, session validation | `authHelper.ts` |
| `src/utils/` | Pure deterministic utils | 100% pure functions, zero side effects | `formatters.ts`, `validators.ts` |
| `src/providers/` | Context providers | Global cross-cutting state | `AuthProvider.tsx`, `ThemeProvider.tsx` |
| `src/types/` | Global TypeScript definitions | Shared across the entire codebase | `common.ts`, `user.ts` |

---

## 📚 Standard Tooling & References

- **React Documentation:** [https://react.dev](https://react.dev)
- **Vite Guide:** [https://vitejs.dev](https://vitejs.dev)
- **shadcn/ui Component Registry:** [https://ui.shadcn.com](https://ui.shadcn.com)
- **Tailwind CSS Documentation:** [https://tailwindcss.com](https://tailwindcss.com)
- **TypeScript Handbook:** [https://www.typescriptlang.org/docs](https://www.typescriptlang.org/docs)

---

**Architecture Standard:** Enterprise Frontend Template (React + Vite + TypeScript)  
**Maintained For:** Cross-Functional Engineering Teams & AI Coding Agents  
**Revision:** Generalized Production Standard v2.0
