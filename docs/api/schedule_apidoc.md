# API Documentation — Schedule & TimeSlot Service

> **Base URL:** `/api/schedules/`  
> **Auth:** OAuth2 Bearer Token — `Authorization: Bearer <access_token>`

---

## Table of Contents

- [1. Domain Model](#1-domain-model)
- [2. Actors](#2-actors)
- [3. Doctor APIs](#3-doctor-apis)
- [4. Public APIs (Patient)](#4-public-apis-patient)
- [5. TimeSlot Generation (Internal Logic)](#5-timeslot-generation-internal-logic)
- [6. Error Handling](#6-error-handling)

---

## 1. Domain Model

### DoctorSchedule Object

```json
{
  "id": 1,
  "doctor": 2,
  "work_date": "2026-05-10",
  "start_time": "08:00:00",
  "end_time": "12:00:00"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique schedule ID |
| `doctor` | integer | Doctor user ID |
| `work_date` | date | Working date (`YYYY-MM-DD`) |
| `start_time` | time | Schedule start time (`HH:MM:SS`) |
| `end_time` | time | Schedule end time (`HH:MM:SS`) |

---

### TimeSlot Object

```json
{
  "id": 10,
  "schedule": 1,
  "start_time": "09:00:00",
  "end_time": "09:30:00",
  "status": "AVAILABLE"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique slot ID |
| `schedule` | integer | Parent DoctorSchedule ID |
| `start_time` | time | Slot start time (`HH:MM:SS`) |
| `end_time` | time | Slot end time (`HH:MM:SS`) |
| `status` | enum | `AVAILABLE` / `BOOKED` |

---

## 2. Actors

| Actor | Access |
|-------|--------|
| Doctor | View own schedules |
| Patient / Authenticated | View schedules by doctor; view available time slots |

---

## 3. Doctor APIs

> **Permission:** Authenticated + Doctor role required for all endpoints in this section.

---

### 3.1 Get My Schedules

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/schedules/my-schedules/` |
| **Permission** | Authenticated + Doctor |

#### Query Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | x | Filter by date (`YYYY-MM-DD`) |

#### Example Request

```
GET /api/schedules/my-schedules/?date=2026-05-10
```

#### Response `200 OK`

```json
[
  {
    "id": 1,
    "doctor": 2,
    "work_date": "2026-05-10",
    "start_time": "08:00:00",
    "end_time": "12:00:00"
  }
]
```

---

## 4. Public APIs (Patient)

> **Permission:** Authenticated users (Patient or Guest).

---

### 4.1 Get Schedules by Doctor

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/schedules/by-doctor/` |
| **Permission** | Authenticated |

#### Query Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `doctor_id` | integer | v | Doctor ID |
| `date` | string | x | Filter by date (`YYYY-MM-DD`) |

#### Business Rules

- Only returns schedules from **today onwards**

#### Example Request

```
GET /api/schedules/by-doctor/?doctor_id=1&date=2026-05-10
```

#### Response `200 OK`

```json
[
  {
    "id": 1,
    "doctor": 1,
    "work_date": "2026-05-10",
    "start_time": "08:00:00",
    "end_time": "12:00:00"
  }
]
```

---

### 4.2 Get Available Time Slots

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/api/schedules/available-slots/` |
| **Permission** | Authenticated |

#### Query Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `schedule_id` | integer | v | Schedule ID to fetch slots for |

#### Business Rules

- Only returns slots where:
  - `status = AVAILABLE`
  - If the schedule date is **today** → additionally filter by current time (past slots excluded)

#### Example Request

```
GET /api/schedules/available-slots/?schedule_id=1
```

#### Response `200 OK`

```json
[
  {
    "id": 10,
    "schedule": 1,
    "start_time": "09:00:00",
    "end_time": "09:30:00",
    "status": "AVAILABLE"
  }
]
```

---

## 5. TimeSlot Generation (Internal Logic)

> This section describes internal server-side logic — not a public API endpoint.

---

### 5.1 Generate Slots

#### Logic

```
SLOT_DURATION = 30 minutes
```

#### Example

Given a schedule from `08:00` to `12:00`, the system generates:

| Slot | Start | End |
|------|-------|-----|
| 1 | 08:00 | 08:30 |
| 2 | 08:30 | 09:00 |
| 3 | 09:00 | 09:30 |
| ... | ... | ... |
| 8 | 11:30 | 12:00 |

#### Implementation

```python
generate_timeslots(schedule)
```

#### Notes

- Uses `bulk_create` → optimized for performance
- Prevents overlapping slot creation

---

## 6. Error Handling

### Standard Error Responses

| HTTP Status | Scenario | Example Response |
|-------------|----------|-----------------|
| `400` | Missing required param | `{ "detail": "doctor_id is required." }` |
| `400` | Invalid date format | `{ "date": "Invalid format. Use YYYY-MM-DD" }` |
| `403` | Permission denied | `{ "detail": "Only doctors can access this." }` |

### 400 — Missing Params

```json
{
  "detail": "doctor_id is required."
}
```

```json
{
  "schedule_id": "schedule_id is required."
}
```

### 400 — Invalid Date

```json
{
  "date": "Invalid format. Use YYYY-MM-DD"
}
```

### 403 — Permission Denied

```json
{
  "detail": "Only doctors can access this."
}
```

---

*Last updated: May 2026*
