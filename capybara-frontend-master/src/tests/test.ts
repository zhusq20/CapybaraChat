import sha256 from "../utils/sha256";

describe("sha256 function", () => {
  it("correctly hashes input string", () => {
    const input = "testpassword";
    const expectedHash = "6b328ba0eedf7ed67258adb7c86d93478d4ecd0acc06aecd31f217640933b61e";
    const actualHash = sha256(input);
    expect(actualHash).toBe(expectedHash);
  });
});
