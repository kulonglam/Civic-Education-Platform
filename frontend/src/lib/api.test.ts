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
  it("does not dump Django HTML 500 pages", () => {
    const err = new axios.AxiosError(
      "Request failed",
      "500",
      void 0,
      void 0,
      {
        status: 500,
        statusText: "Internal Server Error",
        headers: {},
        config: { headers: new axios.AxiosHeaders() },
        data: "<!doctype html> <html lang=\"en\"> <head> <title>Server Error (500)</title> </head> <body> <h1>Server Error (500)</h1></body> </html>",
      },
    );
    expect(extractError(err)).toMatch(/internal error/i);
    expect(extractError(err)).not.toMatch(/<!doctype/i);
  });
  it("falls back for unknown errors", () => {
    expect(extractError(new Error("boom"))).toBe("An unexpected error occurred.");
  });
});
