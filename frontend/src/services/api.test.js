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

  it("downloadResume opens PDF in new tab", async () => {
    const open = vi.fn();
    window.open = open;

    await downloadResume();

    expect(open).toHaveBeenCalledWith("/api/resume/download", "_blank");
  });
});
