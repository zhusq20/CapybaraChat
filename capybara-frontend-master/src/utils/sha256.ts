import { createHash } from "crypto";

export default function sha256(input: string): string {
  const hash = createHash("sha256");
  input = "capybara" + input;
  hash.update(input);
  return hash.digest("hex");
}