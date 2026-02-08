import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    refresh: vi.fn(),
  })),
  usePathname: vi.fn(() => "/login"),
}));

// Mock useAuth hook
const mockSignIn = vi.fn();
vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(() => ({
    session: null,
    isLoading: false,
    isAuthenticated: false,
    signIn: mockSignIn,
    signUp: vi.fn(),
    signOut: vi.fn(),
    getToken: vi.fn(),
  })),
}));

import LoginForm from "@/components/LoginForm";

describe("LoginForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders email and password inputs (FR-056)", () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    expect(emailInput).toBeInTheDocument();
    expect(emailInput).toHaveAttribute("type", "email");

    const passwordInput = screen.getByLabelText(/password/i);
    expect(passwordInput).toBeInTheDocument();
    expect(passwordInput).toHaveAttribute("type", "password");

    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("form submission calls signIn (FR-057)", async () => {
    mockSignIn.mockResolvedValue({ data: { user: { id: "1" } } });
    const user = userEvent.setup();

    render(<LoginForm />);

    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(mockSignIn).toHaveBeenCalledWith("test@example.com", "password123");
  });

  it("failed signin shows error message (FR-058)", async () => {
    mockSignIn.mockResolvedValue({
      error: { message: "Invalid credentials" },
    });
    const user = userEvent.setup();

    render(<LoginForm />);

    await user.type(screen.getByLabelText(/email/i), "bad@example.com");
    await user.type(screen.getByLabelText(/password/i), "wrong");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      await screen.findByText(/invalid credentials/i)
    ).toBeInTheDocument();
  });
});
