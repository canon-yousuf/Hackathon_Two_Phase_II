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
  usePathname: vi.fn(() => "/signup"),
}));

// Mock useAuth hook
const mockSignUp = vi.fn();
vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(() => ({
    session: null,
    isLoading: false,
    isAuthenticated: false,
    signIn: vi.fn(),
    signUp: mockSignUp,
    signOut: vi.fn(),
    getToken: vi.fn(),
  })),
}));

import SignupForm from "@/components/SignupForm";

describe("SignupForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders name, email, and password inputs (FR-059)", () => {
    render(<SignupForm />);

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign up/i })).toBeInTheDocument();
  });

  it("form submission calls signUp (FR-060)", async () => {
    mockSignUp.mockResolvedValue({ data: { user: { id: "1" } } });
    const user = userEvent.setup();

    render(<SignupForm />);

    await user.type(screen.getByLabelText(/name/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign up/i }));

    expect(mockSignUp).toHaveBeenCalledWith(
      "test@example.com",
      "password123",
      "Test User"
    );
  });

  it("duplicate email shows error message (FR-061)", async () => {
    mockSignUp.mockResolvedValue({
      error: { message: "Email already exists" },
    });
    const user = userEvent.setup();

    render(<SignupForm />);

    await user.type(screen.getByLabelText(/name/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "dupe@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign up/i }));

    expect(
      await screen.findByText(/email already exists/i)
    ).toBeInTheDocument();
  });
});
