# API Documentation — Appointment Service

> **Base URL:** `/api/appointments/`  
> **Auth:** OAuth2 Bearer Token — `Authorization: Bearer <access_token>`

---

## Table of Contents

- [1. Domain Model](#1-domain-model)
- [2. Status Enums](#2-status-enums)
- [3. Patient APIs](#3-patient-apis)
- [4. Doctor APIs](#4-doctor-apis)
- [5. Receptionist APIs](#5-receptionist-apis)
- [6. Admin APIs](#6-admin-apis)
- [7. Error Handling](#7-error-handling)
- [8. Architecture Notes](#8-architecture-notes)

---

## 1. Domain Model

### Appointment Object

```json
{
  "id": 1,
  "patient": 1,
  "patient_name": "Nguyen Van A",
  "doctor": 2,
  "doctor_name": "Dr. Tran B",
  "time_slot": 10,
  "appointment_date": "2026-05-10",
  "start_time": "09:00:00",
  "symptoms": "Fever, headache",
  "status": "BOOKED",
  "notes": "",
  "created_at": "2026-05-01T10:00:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique appointment ID |
| `patient` | integer | Patient user ID |
| `patient_name` | string | Patient display name |
| `doctor` | integer | Doctor user ID |
| `doctor_name` | string | Doctor display name |
| `time_slot` | integer | TimeSlot ID |
| `appointment_date` | date | Date of appointment (`YYYY-MM-DD`) |
| `start_time` | time | Start time of the slot (`HH:MM:SS`) |
| `symptoms` | string | Reported symptoms |
| `status` | enum | `BOOKED` / `COMPLETED` / `CANCELED` |
| `notes` | string | Additional notes |
| `created_at` | datetime | Record creation timestamp (ISO 8601) |

---

## 2. Status Enums

### AppointmentStatus

| Value | Description |
|-------|-------------|
| `BOOKED` | Appointment is confirmed and upcoming |
| `COMPLETED` | Appointment has been completed by doctor |
| `CANCELED` | Appointment was canceled |

### SlotStatus

| Value | Description |
|-------|-------------|
| `AVAILABLE` | Time slot is open for booking |
| `BOOKED` | Time slot is already taken |

---

## 3. Patient APIs

> **Permission:** Patient role required for all endpoints in this section.

---

### 3.1 Create Appointment

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/api/appointments/` |
| **Permission** | Patient only |

#### Request Body

```json
{
  "time_slot": 10,
  "symptoms": "Fever and cough"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `time_slot` | integer | v | ID of the time slot to book |
| `symptoms` | string | v | Patient's reported symptoms |

#### Business Logic

**Validation:**
- Slot status must be `AVAILABLE`
- Slot must not be in the past
- No double booking allowed

**Transaction (atomic):**
1. Lock slot via `select_for_update()`
2. Set slot status → `BOOKED`
3. Create appointment record

#### Response `201 Created`

```json
{
  "id": 1,
  "status": "BOOKED"
}
```

---

### 3.2 List My Appointments

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/appointments/` |
| **Permission** | Patient only |

#### Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter by `BOOKED` / `COMPLETED` / `CANCELED` |
| `from` | date | Filter start date (`YYYY-MM-DD`) |
| `to` | date | Filter end date (`YYYY-MM-DD`) |

#### Response `200 OK`

```json
{
  "count": 10,
  "results": [...]
}
```

---

### 3.3 Retrieve Appointment Detail

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/appointments/{id}/` |
| **Permission** | Patient only |

#### Path Parameters

| Param | Type | Description |
|-------|------|-------------|
| `id` | integer | Appointment ID |

#### Response `200 OK`

Returns a full [Appointment Object](#appointment-object).

---

### 3.4 Cancel Appointment

| | |
|---|---|
| **Method** | `PATCH` |
| **Endpoint** | `/api/appointments/{id}/cancel/` |
| **Permission** | Patient only |

#### Path Parameters

| Param | Type | Description |
|-------|------|-------------|
| `id` | integer | Appointment ID |

#### Business Rules

-  Cannot cancel if status is `COMPLETED`
-  Cannot cancel if status is already `CANCELED`

#### Side Effects

- Time slot status → `AVAILABLE`

#### Response `200 OK`

```json
{
  "detail": "Appointment canceled successfully.",
  "status": "CANCELED"
}
```

---

## 4. Doctor APIs

> **Permission:** Doctor role required for all endpoints in this section.

---

### 4.1 List Doctor Appointments

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/appointments/` |
| **Permission** | Doctor only |

> Results are automatically filtered to the currently authenticated doctor's appointments.

#### Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter by `BOOKED` / `COMPLETED` / `CANCELED` |
| `from` | date | Filter start date (`YYYY-MM-DD`) |
| `to` | date | Filter end date (`YYYY-MM-DD`) |

#### Response `200 OK`

```json
{
  "count": 10,
  "results": [...]
}
```

---

### 4.2 Complete Appointment

| | |
|---|---|
| **Method** | `PATCH` |
| **Endpoint** | `/api/appointments/{id}/complete/` |
| **Permission** | Doctor only (owner of the appointment) |

#### Path Parameters

| Param | Type | Description |
|-------|------|-------------|
| `id` | integer | Appointment ID |

#### Business Rules

-  Only the doctor assigned to the appointment may mark it complete
-  Cannot complete if status is `CANCELED`
-  Cannot complete if status is already `COMPLETED`
-  Cannot complete a future appointment

#### Response `200 OK`

```json
{
  "detail": "Appointment marked as completed successfully.",
  "status": "COMPLETED"
}
```

---

## 5. Receptionist APIs

> **Permission:** Receptionist role required for all endpoints in this section.

---

### 5.1 Book Appointment for Patient

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/api/appointments/book-for-patient/` |
| **Permission** | Receptionist only |

> **Composite Use Case** — Nhiều bước được thực hiện trong 1 API call duy nhất.

#### Request Body

```json
{
  "phone_number": "0901234567",
  "fullname": "Nguyen Van A",
  "email": "a@gmail.com",
  "time_slot": 10,
  "symptoms": "Headache",
  "notes": "First visit"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phone_number` | string | v | Patient's phone number (10–11 digits) |
| `fullname` | string | v | Patient's full name |
| `email` | string | x | Patient's email (optional, can be empty) |
| `time_slot` | integer | v | ID of the time slot to book |
| `symptoms` | string | v | Patient's reported symptoms |
| `notes` | string | x | Additional notes |

#### Business Logic — Composite Flow

```
1. Receptionist inputs phone number
2. System checks if user exists:
   ├── Exists     → reuse existing user
   └── Not found  → create new user
3. Create PatientProfile if not already present
4. Lock TimeSlot via select_for_update()
5. Check slot status = AVAILABLE
6. Create Appointment record
7. Update slot status → BOOKED
```

#### Side Effects

- New `User` may be created if `phone_number` is not found
- New `PatientProfile` may be created if not already present
- `TimeSlot` status → `BOOKED`

#### Response `201 Created`

```json
{
  "message": "Booked successfully",
  "data": {
    "id": 1,
    "appointment_date": "2026-05-10",
    "start_time": "09:00:00",
    "doctor_name": "Dr. B",
    "status": "BOOKED"
  }
}
```

---

### 5.2 Today's Dashboard

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/appointments/dashboard/` |
| **Permission** | Receptionist only |

#### Response `200 OK`

```json
{
  "total": 20,
  "completed": 5,
  "waiting": 10,
  "canceled": 5,
  "results": [...]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total appointments today |
| `completed` | integer | Completed appointments count |
| `waiting` | integer | Pending / booked appointments count |
| `canceled` | integer | Canceled appointments count |
| `results` | array | List of today's appointment objects |

---

## 6. Admin APIs

> **Permission:** Admin role required for all endpoints in this section.

---

### 6.1 List All Appointments

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/appointments/` |
| **Permission** | Admin only |

> Returns all appointments across all users — not filtered by patient or doctor.

#### Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter by `BOOKED` / `COMPLETED` / `CANCELED` |
| `from` | date | Filter start date (`YYYY-MM-DD`) |
| `to` | date | Filter end date (`YYYY-MM-DD`) |

#### Response `200 OK`

```json
{
  "count": 100,
  "results": [...]
}
```

---

## 7. Error Handling

### Standard Error Responses

| HTTP Status | Meaning | Example Response |
|-------------|---------|-----------------|
| `400` | Validation Error | `{ "time_slot": "This time slot is already booked." }` |
| `403` | Permission Denied | `{ "detail": "You do not have permission." }` |
| `404` | Not Found | `{ "detail": "Not found." }` |
| `401` | Unauthorized | `{ "detail": "Authentication credentials were not provided." }` |

### 400 — Validation Error

```json
{
  "time_slot": "This time slot is already booked."
}
```

### 403 — Permission Denied

```json
{
  "detail": "You do not have permission."
}
```

---

## 8. Architecture Notes

> Relevant for Software Architecture course documentation.

### 8.1 Layered Architecture Pattern

The system applies a **Layered Architecture**:

| Layer | Implementation |
|-------|---------------|
| Controller | `ViewSet` (DRF) |
| Service | `query_service` |
| Repository | Django ORM |

→ Clear separation of concerns across layers.

### 8.2 Concurrency Control

```python
TimeSlot.objects.select_for_update()
```

- Pattern: **Pessimistic Locking**
- Purpose: Resolves race conditions when multiple users attempt to book the same time slot simultaneously

### 8.3 Transaction Boundary

```python
with transaction.atomic():
    ...
```

- Ensures Appointment creation and Slot status update are **atomic**
- Prevents data inconsistency on partial failures

### 8.4 Async Processing

```python
send_appointment_confirmation.delay()
```

- Pattern: **Event-driven / Async Task** (e.g., Celery)
- Benefit: Improves system scalability in a distributed architecture

---

*Last updated: May 2026*
