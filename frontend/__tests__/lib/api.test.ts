import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// Mock auth-client module
vi.mock("@/lib/auth-client", () => ({
  authClient: {
    token: vi.fn(),
  },
}));

import { authClient } from "@/lib/auth-client";
import { api } from "@/lib/api";

describe("API Client", () => {
  const originalLocation = window.location;

  beforeEach(() => {
    vi.restoreAllMocks();
    // Mock window.location
    Object.defineProperty(window, "location", {
      writable: true,
      value: { ...originalLocation, href: "" },
    });
  });

  afterEach(() => {
    Object.defineProperty(window, "location", {
      writable: true,
      value: originalLocation,
    });
  });

  it("attaches Bearer token to outgoing requests (FR-062)", async () => {
    const mockToken = "test-jwt-token-123";
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: mockToken },
    } as any);

    const mockResponse = {
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue([]),
      headers: new Headers(),
    };
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(mockResponse as any);

    await api.getTasks("user-1");

    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining("/api/user-1/tasks"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: `Bearer ${mockToken}`,
        }),
      })
    );
  });

  it("redirects to login on 401 response (FR-063)", async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: "some-token" },
    } as any);

    const mockResponse = {
      ok: false,
      status: 401,
      json: vi.fn().mockResolvedValue({}),
      headers: new Headers(),
    };
    vi.spyOn(globalThis, "fetch").mockResolvedValue(mockResponse as any);

    await expect(api.getTasks("user-1")).rejects.toThrow();
    expect(window.location.href).toBe("/login");
  });

  it("throws when no token is available", async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: null },
    } as any);

    await expect(api.getTasks("user-1")).rejects.toThrow("Not authenticated");
  });

  it("handles 204 response for deleteTask", async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: "test-token" },
    } as any);

    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 204,
      headers: new Headers(),
    } as any);

    const result = await api.deleteTask("user-1", 1);
    expect(result).toBeNull();
  });

  it("throws on non-ok response with error detail", async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: "test-token" },
    } as any);

    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      status: 422,
      json: vi.fn().mockResolvedValue({ detail: "Validation error" }),
      headers: new Headers(),
    } as any);

    await expect(api.createTask("user-1", { title: "" })).rejects.toThrow(
      "Validation error"
    );
  });

  it("createTask sends POST with body", async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: "test-token" },
    } as any);

    const mockTask = { id: 1, title: "New", completed: false };
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 201,
      json: vi.fn().mockResolvedValue(mockTask),
      headers: new Headers(),
    } as any);

    await api.createTask("user-1", { title: "New" });

    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining("/api/user-1/tasks"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ title: "New" }),
      })
    );
  });

  it("toggleComplete sends PATCH request", async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: "test-token" },
    } as any);

    const mockTask = { id: 1, title: "Task", completed: true };
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue(mockTask),
      headers: new Headers(),
    } as any);

    await api.toggleComplete("user-1", 1);

    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining("/api/user-1/tasks/1/complete"),
      expect.objectContaining({ method: "PATCH" })
    );
  });
});
