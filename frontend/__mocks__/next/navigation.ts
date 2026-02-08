import { vi } from "vitest";

const push = vi.fn();
const replace = vi.fn();
const back = vi.fn();
const refresh = vi.fn();

export const useRouter = vi.fn(() => ({
  push,
  replace,
  back,
  refresh,
}));

export const usePathname = vi.fn(() => "/");
export const redirect = vi.fn();
