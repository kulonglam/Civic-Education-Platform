import { describe, expect, it } from "vitest";
import { decodeJwtPayload, getOrgSlugFromToken } from "./jwt";
describe("jwt helpers", () => {
  const token = "header." + btoa(JSON.stringify({ org_slug: "acme-civic", org: "uuid-123", email: "a@test.com" })) + ".sig";
  it("decodes JWT payload", () => {
    const payload = decodeJwtPayload(token);
    expect(payload?.org_slug).toBe("acme-civic");
    expect(payload?.email).toBe("a@test.com");
  });
  it("extracts org slug from token", () => {
    expect(getOrgSlugFromToken(token)).toBe("acme-civic");
  });
  it("returns null for invalid token", () => {
    expect(decodeJwtPayload("not-a-jwt")).toBeNull();
    expect(getOrgSlugFromToken("bad")).toBeNull();
  });
});
