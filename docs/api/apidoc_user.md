# API Documentation — User Service

> **Version:** 1.0  
> **Base URL:** `/api/users/`  
> **Auth:** JWT Bearer Token — `Authorization: Bearer <access_token>`

---

## Table of Contents

- [1. Domain Model](#1-domain-model)
- [2. Actors](#2-actors)
- [3. Public APIs (Guest)](#3-public-apis-guest)
- [4. Authenticated APIs](#4-authenticated-apis)
- [5. Authentication Flow (UI)](#5-authentication-flow-ui)
- [6. Validation Rules](#6-validation-rules)
- [7. Error Handling](#7-error-handling)

---

## 1. Domain Model

### User Object

```json
{
  "id": 1,
  "username": "user123",
  "fullname": "Nguyen Van A",
  "email": "a@gmail.com",
  "phone_number": "0901234567",
  "gender": "male",
  "role": "PATIENT",
  "avatar": "/media/avatar.jpg"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique user ID |
| `username` | string | Login username |
| `fullname` | string | Display name |
| `email` | string | Email address |
| `phone_number` | string | Phone number (10–11 digits) |
| `gender` | enum | `male` / `female` |
| `role` | enum | `PATIENT` / `DOCTOR` / `ADMIN` |
| `avatar` | string | URL path to avatar image |

---

## 2. Actors

| Actor | Access |
|-------|--------|
| Guest | Register a new account |
| User (Authenticated) | View & update own profile, change password |
| Admin | Manage users |

---

## 3. Public APIs (Guest)

> **Permission:** No authentication required.

---

### 3.1 Register User

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/api/users/` |
| **Permission** | Public |

#### Request Body

```json
{
  "username": "user123",
  "password": "123456",
  "fullname": "Nguyen Van A",
  "email": "a@gmail.com",
  "phone_number": "0901234567",
  "gender": "male"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | v | Login username (3–50 chars, `[a-zA-Z0-9_]`) |
| `password` | string | v | Account password (min 6 chars) |
| `fullname` | string | v | User's display name |
| `email` | string | v | Valid email address |
| `phone_number` | string | v | Phone number (10–11 digits) |
| `gender` | string | v | `male` / `female` |

#### Side Effects

- New `User` record is created
- Password is hashed before storage
- Confirmation email is sent asynchronously

```python
send_email_confirmation.delay()
```

#### Response `201 Created`

```json
{
  "id": 1,
  "username": "user123",
  "fullname": "Nguyen Van A",
  "email": "a@gmail.com",
  "phone_number": "0901234567",
  "gender": "male",
  "role": "PATIENT"
}
```

---

## 4. Authenticated APIs

> **Permission:** Authenticated (any role) required for all endpoints in this section.

---

### 4.1 Get Current User

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/users/current-user/` |
| **Permission** | Authenticated |

#### Response `200 OK`

```json
{
  "id": 1,
  "fullname": "Nguyen Van A",
  "email": "a@gmail.com",
  "phone_number": "0901234567"
}
```

---

### 4.2 Update Current User

| | |
|---|---|
| **Method** | `PATCH` |
| **Endpoint** | `/api/users/current-user/` |
| **Permission** | Authenticated (owner only) |

> Supports two independent use cases in the same endpoint: **update profile info** and **change password**.

#### Request Body — Update Info

```json
{
  "fullname": "Updated Name",
  "email": "new@gmail.com"
}
```

#### Request Body — Change Password

```json
{
  "old_password": "123456",
  "password": "newpassword"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fullname` | string | x | Updated display name |
| `email` | string | x | Updated email address |
| `old_password` | string | x | Current password (required when changing password) |
| `password` | string | x | New password (min 6 chars) |

#### Business Rules

- `old_password` must match the currently stored password
- Some fields cannot be updated — attempting to update them returns an error
- Partial update: only provided fields are changed

#### Response `200 OK`

```json
{
  "id": 1,
  "fullname": "Updated Name"
}
```

---

## 5. Authentication Flow (UI)

>  This section describes UI-level login/logout flows — not REST API endpoints.

---

### 5.1 Login

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/login/` |

#### Flow

```
1. User enters username + password
2. authenticate()
3. login()
4. redirect based on role → redirect_user_by_role()
```

#### Redirect Logic

```python
redirect_user_by_role()
```

| Role | Redirect URL |
|------|-------------|
| `DOCTOR` | `/doctor/dashboard/` |
| `PATIENT` | `/booking/` |
| `ADMIN` | `/admin/` |

---

### 5.2 Logout

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/logout/` |

---

## 6. Validation Rules

### Username

| Rule | Value |
|------|-------|
| Min length | 3 |
| Max length | 50 |
| Pattern | `[a-zA-Z0-9_]` |

### Password

| Rule | Value |
|------|-------|
| Min length | 6 |
| Required | Yes |

### Phone Number

| Rule | Value |
|------|-------|
| Format | 10–11 digits |

### Email

| Rule | Value |
|------|-------|
| Format | Must match standard email format |

### Gender

| Rule | Value |
|------|-------|
| Allowed values | `male` / `female` |

---

## 7. Error Handling

### Standard Error Responses

| HTTP Status | Scenario | Example Response |
|-------------|---------|-----------------|
| `400` | Invalid username | `{ "username": "Tên đăng nhập phải ít nhất 3 ký tự!" }` |
| `400` | Invalid password | `{ "password": "Mật khẩu phải ít nhất 6 ký tự!" }` |
| `400` | Wrong old password | `{ "old_password": "YOUR OLD PASSWORD IS INCORRECT!" }` |
| `400` | Unauthorized field update | `{ "error": "THIS FIELD CANNOT BE UPDATED" }` |
| `401` | Unauthorized | `{ "detail": "Authentication credentials were not provided." }` |

### 400 — Invalid Username

```json
{
  "username": "Tên đăng nhập phải ít nhất 3 ký tự!"
}
```

### 400 — Invalid Password

```json
{
  "password": "Mật khẩu phải ít nhất 6 ký tự!"
}
```

### 400 — Wrong Old Password

```json
{
  "old_password": "YOUR OLD PASSWORD IS INCORRECT!"
}
```

### 400 — Unauthorized Field Update

```json
{
  "error": "THIS FIELD CANNOT BE UPDATED"
}
```

---

*Last updated: May 2026*
