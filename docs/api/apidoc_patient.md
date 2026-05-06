# API Documentation — Patient Service

> **Base URL:** `/api/patients/`  
> **Auth:** OAuth2 Bearer Token — `Authorization: Bearer <access_token>`

---

## Table of Contents

- [1. Domain Model](#1-domain-model)
- [2. Actors](#2-actors)
- [3. Patient APIs](#3-patient-apis)
- [4. Shared APIs (Doctor / Admin / Receptionist)](#4-shared-apis-doctor--admin--receptionist)
- [5. Validation Rules](#5-validation-rules)
- [6. Error Handling](#6-error-handling)

---

## 1. Domain Model

### PatientProfile Object

```json
{
  "id": 1,
  "user": {
    "id": 10,
    "fullname": "Nguyen Van A",
    "phone_number": "0901234567",
    "email": "a@gmail.com"
  },
  "address": "Ho Chi Minh",
  "dob": "2000-01-01"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique PatientProfile ID |
| `user` | object | Nested User object (read-only) |
| `user.id` | integer | Linked User ID |
| `user.fullname` | string | Patient's display name |
| `user.phone_number` | string | Patient's phone number |
| `user.email` | string | Patient's email address |
| `address` | string | Patient's home address |
| `dob` | date | Date of birth (`YYYY-MM-DD`) |

---

## 2. Actors

| Actor | Access |
|-------|--------|
| Patient | View & update own profile |
| Admin / Staff | Search and retrieve patients |
| Doctor | View patient appointment history |
| Receptionist | Search and retrieve patients |

---

## 3. Patient APIs

> **Permission:** Authenticated + Patient role required for all endpoints in this section.

---

### 3.1 Get My Profile

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/patients/me/` |
| **Permission** | Authenticated + Patient |

#### Response `200 OK`

```json
{
  "id": 1,
  "user": {
    "fullname": "Nguyen Van A",
    "phone_number": "0901234567"
  },
  "address": "HCM",
  "dob": "2000-01-01"
}
```

---

### 3.2 Update My Profile

| | |
|---|---|
| **Method** | `PATCH` |
| **Endpoint** | `/api/patients/me/` |
| **Permission** | Authenticated + Patient (owner only) |

#### Request Body

```json
{
  "address": "Ha Noi",
  "dob": "1999-05-10",
  "user": {
    "fullname": "Nguyen Van Updated"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `address` | string | x | Updated home address (cannot be empty) |
| `dob` | date | x | Updated date of birth (cannot be in the future) |
| `user.fullname` | string | x | Updated display name (partial update supported) |

#### Business Rules

- `dob` must not be in the future
- `address` cannot be empty
- `user` supports **partial update** only

#### Response `200 OK`

```json
{
  "id": 1,
  "address": "Ha Noi",
  "dob": "1999-05-10"
}
```

---

## 4. Shared APIs (Doctor / Admin / Receptionist)

> **Permission:** Doctor, Admin, or Receptionist role required for all endpoints in this section.

---

### 4.1 List Patients

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/patients/` |
| **Permission** | Doctor / Admin / Receptionist |

#### Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search by name / phone number / address |
| `dob` | date | Filter by date of birth (`YYYY-MM-DD`) |

#### Example Request

```
GET /api/patients/?q=Nguyen&dob=2000-01-01
```

#### Response `200 OK`

```json
{
  "count": 10,
  "results": [...]
}
```

---

### 4.2 Retrieve Patient Detail

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/patients/{id}/` |
| **Permission** | Doctor / Admin / Receptionist |

#### Path Parameters

| Param | Type | Description |
|-------|------|-------------|
| `id` | integer | PatientProfile ID |

#### Response `200 OK`

Returns a full [PatientProfile Object](#patientprofile-object).

---

### 4.3 Get Patient Appointments

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/patients/{id}/appointments/` |
| **Permission** | Doctor / Admin / Receptionist |

#### Path Parameters

| Param | Type | Description |
|-------|------|-------------|
| `id` | integer | PatientProfile ID |

#### Response `200 OK`

```json
{
  "patient": {
    "id": 1,
    "fullname": "Nguyen Van A"
  },
  "appointments": [
    {
      "id": 10,
      "doctor_name": "Dr. B",
      "appointment_date": "2026-05-10",
      "start_time": "09:00:00",
      "status": "BOOKED"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `patient.id` | integer | PatientProfile ID |
| `patient.fullname` | string | Patient display name |
| `appointments` | array | List of appointment records for this patient |
| `appointments[].id` | integer | Appointment ID |
| `appointments[].doctor_name` | string | Assigned doctor's display name |
| `appointments[].appointment_date` | date | Date of appointment (`YYYY-MM-DD`) |
| `appointments[].start_time` | time | Start time of slot (`HH:MM:SS`) |
| `appointments[].status` | enum | `BOOKED` / `COMPLETED` / `CANCELED` |

---

## 5. Validation Rules

| Field | Rule | Error |
|-------|------|-------|
| `dob` | Must not be in the future | `{ "dob": "Date of birth cannot be in the future." }` |
| `address` | Cannot be empty | `{ "address": "Address cannot be empty." }` |
| `user` | Partial update only | Only provided sub-fields will be updated |

---

## 6. Error Handling

### Standard Error Responses

| HTTP Status | Scenario | Example Response |
|-------------|---------|-----------------|
| `400` | Invalid DOB | `{ "dob": "Date of birth cannot be in the future." }` |
| `400` | Empty Address | `{ "address": "Address cannot be empty." }` |
| `404` | Patient not found | `{ "detail": "Patient not found." }` |
| `401` | Unauthorized | `{ "detail": "Authentication credentials were not provided." }` |
| `403` | Permission Denied | `{ "detail": "You do not have permission." }` |

### 400 — Invalid DOB

```json
{
  "dob": "Date of birth cannot be in the future."
}
```

### 400 — Empty Address

```json
{
  "address": "Address cannot be empty."
}
```

### 404 — Not Found

```json
{
  "detail": "Patient not found."
}
```

---

*Last updated: May 2026*
