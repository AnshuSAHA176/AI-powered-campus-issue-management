# 🏫 AI-Powered Campus Issue Management

> An intelligent platform for reporting, tracking, and resolving campus issues through a centralized digital system with AI-assisted issue analysis.

---

## Overview

AI-Powered Campus Issue Management is a backend-first platform designed to modernize how students and campus authorities report, manage, prioritize, and resolve campus-related issues.

Instead of relying on informal communication, paper-based complaints, or fragmented reporting channels, the platform provides a structured workflow where:

- Students can report campus issues.
- Evidence such as images can be attached to complaints.
- Officers can manage and process reported issues.
- Complaints can move through a defined lifecycle.
- User profiles can be maintained securely.
- AI can assist with issue classification, prioritization, and intelligent workflows.
- Cloudinary handles image storage.
- JWT authentication protects API access.

The project is being developed with a focus on scalable backend architecture and production-oriented engineering practices.

---

## ✨ Core Features

### 👤 Authentication & Accounts

- User registration
- JWT-based authentication
- Access and refresh tokens
- Custom User model
- Role-based users
- Student accounts
- Officer accounts
- Admin accounts
- Profile management

### 📝 Complaint Management

Users can report campus issues with:

- Title
- Description
- Location
- Landmark
- Latitude
- Longitude
- Evidence images
- Priority
- Status

Example issues:

- Broken infrastructure
- Water leakage
- Electrical problems
- Road damage
- Cleanliness issues
- Security concerns
- Classroom/laboratory problems
- Other campus-related issues

### 📸 Evidence Management

Complaint evidence is uploaded using Cloudinary.

Features include:

- Image upload
- Cloud-based storage
- Secure image URLs
- Multiple complaint images
- Image-based evidence for reported issues

### 🔄 Complaint Lifecycle

Complaints can progress through different states:

```text
Pending
   ↓
Assigned
   ↓
Accepted
   ↓
Inspection
   ↓
In Progress
   ↓
Resolved
   ↓
Closed