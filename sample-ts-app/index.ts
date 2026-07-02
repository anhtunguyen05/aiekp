/**
 * Handles authentication for the application.
 */
export class AuthController {
    /**
     * Authenticates a user.
     * @param username The username
     * @param password The password
     */
    public async login(username: string, password: string): Promise<boolean> {
        if (username === "admin" && password === "secret") {
            return true;
        }
        return false;
    }
}

/**
 * Validates a user token.
 */
export function validateToken(token: string): boolean {
    return token.length > 10;
}
