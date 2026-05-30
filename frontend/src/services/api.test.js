import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchResume, downloadResume } from "./api";

const mockAxios = vi.hoisted(() => ({
  create: vi.fn(() => mockAxios),
  get: vi.fn(),
  post: vi.fn(),
}));

vi.mock("axios", () => ({
  default: mockAxios,
}));

describe("API Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetchResume calls the correct endpoint", async () => {
    const mockData = { name: "Test" };
    mockAxios.get.mockResolvedValue({ data: mockData });

    const result = await fetchResume();
    expect(mockAxios.get).toHaveBeenCalledWith("/resume");
    expect(result).toEqual(mockData);
  });

  it("fetchResume throws on network error", async () => {
    mockAxios.get.mockRejectedValue(new Error("Network error"));

    await expect(fetchResume()).rejects.toThrow("Network error");
  });

  it("downloadResume creates a download link", async () => {
    const blob = new Blob(["test"], { type: "application/json" });
    mockAxios.get.mockResolvedValue({ data: blob });

    const createObjectURL = vi.fn(() => "blob:test");
    const revokeObjectURL = vi.fn();

    window.URL.createObjectURL = createObjectURL;
    window.URL.revokeObjectURL = revokeObjectURL;

    const appendChild = vi.fn();
    const remove = vi.fn();
    const click = vi.fn();

    document.body.appendChild = appendChild;
    document.createElement = vi.fn().mockReturnValue({
      href: "",
      setAttribute: vi.fn(),
      click,
      remove,
    });

    await downloadResume();

    expect(mockAxios.get).toHaveBeenCalledWith("/resume/download", {
      responseType: "blob",
    });
    expect(createObjectURL).toHaveBeenCalled();
    expect(click).toHaveBeenCalled();
  });
});
