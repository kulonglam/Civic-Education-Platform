import { describe, expect, it } from "vitest";
import axios from "axios";
import { extractError } from "./api";
describe("extractError", () => {
  it("reads detail from axios error response", () => {
    const err = new axios.AxiosError(
      "Request failed",
      "402",
      void 0,
      void 0,
      {
        status: 402,
        statusText: "Payment Required",
        headers: {},
        config: { headers: new axios.AxiosHeaders() },
        data: { detail: "Plan quota exceeded." }
      }
    );
    expect(extractError(err)).toBe("Plan quota exceeded.");
  });
  it("falls back for unknown errors", () => {
    expect(extractError(new Error("boom"))).toBe("An unexpected error occurred.");
  });
});
