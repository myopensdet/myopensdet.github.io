<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->

# Login and permissions test plan: <app name>

## 1. How login works

- Login: <path, e.g. POST /api/login; JSON body or form?>
- What comes back: <token in the answer / cookie / redirect>
- How the token is sent: <Authorization: Bearer ... / cookie>
- Token lifetime: <e.g. 15 minutes; is there a refresh token?>
- Logout: <path; does it end the token on the server?>

## 2. Test users (test-only accounts)

| Name in the tests | Role | Owns |
| --- | --- | --- |
| `USER_A` | <customer> | <order 101> |
| `USER_B` | <customer> | <order 102> |
| `ADMIN` | <admin> | |

## 3. Who may do what

| Page or action | Not logged in | Owner | Another user | Admin |
| --- | --- | --- | --- | --- |
| <GET /api/orders/{id}> | 401 | 200 | 403 or 404 | <200?> |
| <GET /api/admin/users> | 401 | 403 | 403 | 200 |

## 4. Checks

| Kind | Check | Automated? |
| --- | --- | --- |
| Login | Right user gets a token; wrong password refused; unknown user gets the same answer; bad requests give 400, not 500; no password in the answer | [ ] |
| Tokens | No token, made-up token, changed token: 401. Token stops working after logout <and after it expires> | [ ] |
| Permissions | Owner reads own data; nobody else does; only admins open admin pages | [ ] |

## 5. Questions for the team

1. <e.g. Should another user's record give 403 or 404?>

## 6. Not in this plan

- <Password reset and sign-up flows>
- <Login rate limits and lockout: agree first, they can lock real accounts>
