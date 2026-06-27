import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { UsageBar } from "./UsageBar";
describe("UsageBar", () => {
  it("renders usage counts", () => {
    render(<UsageBar label="Articles" used={3} limit={10} />);
    expect(screen.getByText("Articles")).toBeInTheDocument();
    expect(screen.getByText("3 / 10")).toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "3");
  });
  it("shows unlimited when limit is null", () => {
    render(<UsageBar label="Members" used={50} limit={null} />);
    expect(screen.getByText("50 / \u221E")).toBeInTheDocument();
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });
});