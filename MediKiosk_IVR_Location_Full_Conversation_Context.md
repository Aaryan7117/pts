# MediKiosk — Full Conversation Context

> Purpose: Share this file with another agent so it has the full context of the current MediKiosk discussion, especially the IVR/location problem and the decisions reached.

---

## Conversation Context

### User
We are trying to implement the IVR but how do we get their location so we can determine the nearest clinic. I don't want to make the ai ask and ascertain the location as there can be inconsistencies

### Assistant
Yes — and you should not make the AI infer the location from what the patient says. That would be exactly the kind of inconsistency your architecture is designed to avoid.

The important catch is: a normal IVR call does not give Twilio the caller's GPS location. Twilio can identify the incoming phone number, but a regular PSTN/2G call does not expose the phone's precise latitude/longitude to your application.

For MediKiosk, location should be a deterministic routing attribute, separate from the conversational AI.

Suggested architecture:

```text
                 PATIENT CALLS IVR
                       │
                       ▼
              Caller phone number
                       │
          ┌────────────┴────────────┐
          │                         │
   Known/registered number     Unknown number
          │                         │
          ▼                         ▼
   Patient profile has        Deterministic
   home/registered area       location selection
          │                         │
          └────────────┬────────────┘
                       ▼
              LOCATION RESOLVER
                       │
                       ▼
              Lat/Lon / Pincode
                       │
                       ▼
           NEAREST CLINIC ENGINE
                       │
                       ▼
             Clinic A — 2.3 km
             Clinic B — 4.7 km
             Clinic C — 7.1 km
                       │
                       ▼
              IVR / SMS response
```

The existing architecture treats IVR as another ingestion channel feeding the same clinical engine, so location should be handled before the clinical conversation, not by the LLM.

### User
We are targeting old people who have not much knowledge about technology or location. I am using exotel so how can I make their technology talk and not them talk about location.

### Assistant
The ideal experience is:

> Call number → "Namaste, please tell me your problem." → patient talks → MediKiosk figures out the appropriate clinic automatically.

With Exotel, a normal incoming call does not give the application the caller's GPS coordinates. The phone network may know information about the cell connection, but the normal Exotel voice integration should not be assumed to provide precise latitude/longitude.

Therefore, use information that can be obtained without asking the patient.

#### Best approach: phone number → location

When the patient calls:

```text
Patient
  │
  │ calls
  ▼
Exotel
  │
  │ caller number
  ▼
MediKiosk backend
  │
  ├── Look up registered patient
  ├── Retrieve patient's registered locality/pincode
  │
  ▼
Location Resolver
  │
  ▼
Nearest MediKiosk clinic
```

The patient never needs to say their city, locality, or pincode.

If previously registered:

```text
phone number
    ↓
pincode / registered location
    ↓
coordinates
    ↓
nearest supported clinic
```

No AI is involved in location resolution.

#### Existing-patient case

If the person is already registered:

```text
Phone number
      ↓
Patient registry
      ↓
Address / pincode
      ↓
Nearest clinic
```

This is suitable because healthcare registration often already contains address/contact information.

#### First-time caller

A normal Exotel/PSTN call cannot reliably expose the caller's GPS location.

Do not architect the solution around a claim that Exotel automatically provides GPS or cell-tower location.

Potential fallback mechanisms:

1. Prior registration by a health worker/hospital.
2. A one-time deterministic IVR mechanism such as DTMF pincode entry.
3. A different location-capable channel such as a smartphone app with explicit GPS permission.
4. In a multi-region deployment, separate service numbers could represent service regions, if operationally appropriate.

#### Recommended separation

```text
                    INCOMING CALL
                         │
                         ▼
                  ┌──────────────┐
                  │    Exotel    │
                  └──────┬───────┘
                         │
                 caller phone number
                         │
                         ▼
              ┌─────────────────────┐
              │ PATIENT RESOLVER    │
              │                     │
              │ Phone → Patient     │
              │ Patient → Location  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ CLINIC ROUTER       │
              │                     │
              │ Location → Clinic   │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ CLINICAL IVR        │
              │                     │
              │ ASR → Facts →       │
              │ Questions → Triage  │
              └──────────┬──────────┘
                         │
                         ▼
                  DOCTOR QUEUE
```

The clinical AI should deal only with the medical conversation. Location resolution should happen before clinical intake.

For the judges, the accurate claim is:

> "We resolve the patient's service location deterministically from their registered phone-linked profile, and the routing engine selects the nearest supported clinic. The conversational AI is never responsible for determining location."

Do not claim that Exotel automatically supplies the patient's GPS.

### User
Won't the storing of the data become a scaling problem

### Assistant
Not really — if location data is separated from clinical data properly.

Do not store a new GPS coordinate for every call and every conversation turn. Store a compact location reference.

Example:

```text
Patient
────────────────────────────
patient_id
phone_number_hash
location_id
```

Separate location table:

```text
Location
────────────────────────────
location_id
pincode
latitude
longitude
```

Clinic table:

```text
Clinic
────────────────────────────
clinic_id
name
latitude
longitude
```

So even with 100,000 patients, many patients can share the same `location_id`.

Example:

```text
100,000 patients
       │
       ├── many share the same location_id
       │
       ▼
perhaps a few thousand locations
       │
       ▼
hundreds of clinics
```

This is a small relational-data problem, not a fundamental scaling problem.

Do not store location repeatedly per conversation. An encounter can simply reference the patient and/or resolved clinic:

```text
Call
├── call_id
├── patient_id
├── encounter_id
├── timestamp
├── clinical facts
└── selected clinic_id
```

No repeated latitude/longitude is necessary.

The more important issue is location correctness, not storage size.

For example, a patient's home location may not equal their current location. Someone living in Ambattur could be visiting relatives in Madurai. Therefore, avoid treating a home location as universally equivalent to current location.

A better hierarchy is:

```text
Incoming IVR
      │
      ▼
Is caller registered?
   /          \
 YES           NO
  │             │
  ▼             ▼
Known patient   New caller
  │             │
  ▼             ▼
Registered area Other mechanism
  │
  ▼
Candidate clinics
  │
  ▼
Current facility?
Existing encounter?
Selected service centre?
  │
  ▼
Clinic routing
```

For the hackathon, an even simpler approach can be used if the system is deployed as region-specific MediKiosk services:

```text
Chennai MediKiosk IVR
        ↓
Chennai clinic network

Madurai MediKiosk IVR
        ↓
Madurai clinic network
```

Then patient location does not have to be stored for routing at all.

If using one national number, phone-linked registration can be the fallback.

The scalable design is:

> Phone number → patient ID → service location ID → nearest clinic

rather than storing GPS coordinates/history for every call.

The core challenge is not database size. It is obtaining a trustworthy location signal for a first-time caller without asking the elderly patient.

---

## Key Requirements Inferred From This Conversation

1. MediKiosk targets elderly users who may have limited technical literacy.
2. The elderly user should not be required to verbally provide their location.
3. The conversational AI should NOT infer location from natural-language speech.
4. Location resolution should be deterministic.
5. Exotel is being used for the IVR.
6. A normal Exotel/PSTN incoming call should not be assumed to provide precise GPS coordinates to the backend.
7. Caller phone number can be used to identify a registered patient.
8. A registered patient's service location can be stored as a compact reference, such as `location_id`.
9. A location record can contain pincode and coordinates.
10. Clinics can have their own coordinates.
11. The backend can calculate/select the nearest supported clinic.
12. Location should be resolved before the clinical AI conversation begins.
13. The AI should focus on clinical intake, facts, questions, and triage rather than location resolution.
14. For first-time callers with no registered location, a reliable zero-interaction GPS solution is not available through ordinary Exotel/PSTN alone.
15. Possible fallback mechanisms include prior registration, deterministic DTMF input, a GPS-capable smartphone channel, or region-specific service numbers.
16. Storage is not expected to be a major scaling bottleneck if normalized references are used.
17. A patient's registered/home location should not automatically be assumed to be their current physical location in every scenario.

---

## Important Architecture Principle

**Separate deterministic routing from conversational intelligence.**

Recommended pipeline:

```text
Exotel
   ↓
Caller identification
   ↓
Patient/location resolver
   ↓
Clinic routing
   ↓
Clinical IVR / ASR
   ↓
Clinical fact extraction
   ↓
Questioning / triage
   ↓
Doctor queue
```

Location should be an infrastructure/backend concern, not an LLM inference task.

---

## Open Design Decision

The unresolved product question is:

> How should MediKiosk handle a first-time caller who has no registered location, while still requiring the elderly user to say nothing about location?

Ordinary Exotel/PSTN does not provide a reliable precise GPS signal for this. This requires a product/technical decision around registration, regional numbers, or another location-capable mechanism.

---

## Uploaded Project Context

The conversation also has uploaded MediKiosk project documents that were referenced while discussing architecture:

- `MediKiosk_Tech_Stack_Finalized.md`
- `MediKiosk_Architecture_Review_v2.md`
- `MediKiosk_Full_Context_Handoff.md`
- `README.md`
- `MediKiosk_Android_Two_Developer_Execution_Plan.md`

These should be considered alongside this conversation when the receiving agent continues the work.

