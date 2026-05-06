# API Documentation — Doctor Service

> **Base URL:** `/api/doctors/`  
> **Auth:** OAuth2 Bearer Token — `Authorization: Bearer <access_token>`

---

## Table of Contents

- [1. Domain Model](#1-domain-model)
- [2. Actors](#2-actors)
- [3. Public APIs (Patient / Guest)](#3-public-apis-patient--guest)
- [4. Doctor APIs](#4-doctor-apis)
- [5. Admin APIs](#5-admin-apis)
- [6. Validation Rules](#6-validation-rules)
- [7. Pagination](#7-pagination)
- [8. Error Handling](#8-error-handling)
- [9. Architecture Notes](#9-architecture-notes)

---

## 1. Domain Model

### DoctorProfile Object

```json
{
  "id": 1,
  "user": 10,
  "fullname": "Dr. Nguyen Van A",
  "specialty": 3,
  "bio": "10 years experience in cardiology",
  "experience_years": 10
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique DoctorProfile ID |
| `user` | integer | Linked User ID (read-only) |
| `fullname` | string | Doctor's display name |
| `specialty` | integer | Specialty ID |
| `bio` | string | Doctor's biography / description |
| `experience_years` | integer | Years of professional experience |

---

## 2. Actors

| Actor | Access |
|-------|--------|
| Patient / Guest | View doctor list |
| Doctor | Manage own profile + view dashboard |
| Admin | Update any doctor profile |

---

## 3. Public APIs (Patient / Guest)

> **Permission:** Authenticated users (Patient or Guest).

---

### 3.1 List Doctors

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/doctors/` |
| **Permission** | Public / Authenticated |
| **Pagination** | Cursor Pagination (`DoctorProfileCursorPagination`) |

#### Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `speciality_id` | integer | Filter by specialty |
| `date` | date | Filter doctors who have a working schedule on that date (`YYYY-MM-DD`) |

#### Example Request

```
GET /api/doctors/?speciality_id=1&date=2026-05-10
```

#### Response `200 OK`

```json
{
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": 1,
      "fullname": "Dr. A",
      "specialty": 1,
      "experience_years": 5
    }
  ]
}
```

---

## 4. Doctor APIs

> **Permission:** Doctor role required for all endpoints in this section.

---

### 4.1 Get My Profile

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/doctors/me/` |
| **Permission** | Authenticated + Doctor |

#### Response `200 OK`

```json
{
  "id": 1,
  "fullname": "Dr. A",
  "specialty": 1,
  "bio": "Cardiologist",
  "experience_years": 10
}
```

---

### 4.2 Update My Profile

| | |
|---|---|
| **Method** | `PATCH` |
| **Endpoint** | `/api/doctors/me/` |
| **Permission** | Authenticated + Doctor (owner only) |

#### Request Body

```json
{
  "bio": "Updated bio",
  "experience_years": 12
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bio` | string | x | Updated biography |
| `experience_years` | integer | x | Updated years of experience |

#### Business Rules

- `experience_years` must be `>= 0`
- Doctor can only update their **own** profile

#### Response `200 OK`

```json
{
  "id": 1,
  "bio": "Updated bio",
  "experience_years": 12
}
```

---

### 4.3 Doctor Dashboard

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/doctors/dashboard/` |
| **Permission** | Doctor only |
| **Pagination** | PageNumber Pagination (`AppointmentsPagination`) |

#### Business Logic

- Returns data for **today** only
- Computes:
  - Total appointment count for today
  - Count of appointments still waiting (status `BOOKED`)

#### Response `200 OK`

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "patient_name": "Nguyen Van B",
      "start_time": "09:00:00",
      "status": "BOOKED"
    }
  ],
  "today_count": 10,
  "scheduled_count": 5
}
```

| Field | Type | Description |
|-------|------|-------------|
| `count` | integer | Number of records in current page |
| `results` | array | List of today's appointment objects |
| `today_count` | integer | Total appointments today |
| `scheduled_count` | integer | Appointments currently waiting |

---

### 4.4 List All Examinations

> **Internal API** — Not yet exposed via `@action`. Needs to be added if public access is required.

| | |
|---|---|
| **Method** | `GET` |
| **Suggested Endpoint** | `/api/doctors/examinations/` |
| **Permission** | Doctor only |

#### Description

- Returns all examination schedules for the authenticated doctor
- Default ordering: `-work_date`, `-start_time`

---

## 5. Admin APIs

> **Permission:** Admin OR Owner (Doctor) required for all endpoints in this section.

---

### 5.1 Update Doctor Profile

| | |
|---|---|
| **Method** | `PATCH` |
| **Endpoint** | `/api/doctors/{id}/` |
| **Permission** | Admin OR Owner |

#### Path Parameters

| Param | Type | Description |
|-------|------|-------------|
| `id` | integer | DoctorProfile ID |

---

## 6. Validation Rules

| Field | Rule |
|-------|------|
| `experience_years` | Must be `>= 0` |
| `user` | Read-only; cannot be modified |
| Doctor profile update | Only the owner (doctor) can update their own profile |

---

## 7. Pagination

| Context | Pagination Type | Class |
|---------|----------------|-------|
| Doctor List | Cursor Pagination | `DoctorProfileCursorPagination` |
| Dashboard Appointments | Page Number Pagination | `AppointmentsPagination` |

---

## 8. Error Handling

### Standard Error Responses

| HTTP Status | Meaning | Example Response |
|-------------|---------|-----------------|
| `400` | Validation Error | `{ "experience_years": "Experience years cannot be negative." }` |
| `403` | Forbidden | `{ "detail": "You can only update your own doctor profile." }` |
| `404` | Not Found | `{ "detail": "Not found." }` |
| `401` | Unauthorized | `{ "detail": "Authentication credentials were not provided." }` |

### 400 — Validation Error

```json
{
  "experience_years": "Experience years cannot be negative."
}
```

### 403 — Forbidden

```json
{
  "detail": "You can only update your own doctor profile."
}
```

---

## 9. Architecture Notes

---

### 9.1 Query Optimization

```python
select_related('user', 'specialty')
prefetch_related('schedules')
```

| Technique | Purpose |
|-----------|---------|
| **Eager Loading** | Pre-fetches related objects in a single query |
| **Avoid N+1 Query** | Prevents repeated DB calls per record |

→ Critical for performance in production healthcare systems.

---

### 9.2 Separation of Concerns

| Layer | Responsibility |
|-------|---------------|
| ViewSet | API routing + permission check |
| Serializer | Input/output validation |
| Service (`get_base_queryset`) | Query logic |

→ Follows **Clean Architecture-lite** principle for maintainability.

---

### 9.3 Reuse Query Service

```python
get_base_queryset()
```

- Pattern: **Query Object Pattern**
- Benefits: reusable, easy to maintain, testable in isolation

---

### 9.4 Role-Based Access Control

```python
if user.role == RoleEnum.DOCTOR:
    ...
```

- Pattern: **RBAC (Role-Based Access Control)**
- Suitable for multi-role healthcare systems (Patient / Doctor / Receptionist / Admin)

---

*Last updated: May 2026*
