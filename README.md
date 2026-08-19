# 🤖 XYZ AI – Human-Like AI School Assistant

XYZ AI is a standalone Applied AI School Assistant designed to interact with
Students, Parents, Teachers, and School Management through Chat and Voice.

The system understands natural-language requests, identifies the user's role,
detects intent, maintains conversation context, applies role-based permissions,
communicates with mock school APIs, performs authorized actions, and provides
role-specific responses.

---

## 🚀 Key Features

- 💬 AI Chat Assistant
- 🎤 Voice Interaction
- 🤖 AI Avatar Support
- 🧠 Conversation Memory
- 👤 Role-Based AI Personas
- 🔐 Role-Based Access Control (RBAC)
- 🛡️ Authorization at Application/API Layer
- 📊 Attendance Management
- 📝 Student Marks
- 📅 Timetable
- 🏫 School Information
- 📈 Principal Attendance Analytics
- 📞 Teacher Escalation
- 🏢 School Management Escalation
- 🌐 Multi-Language Support
- 🔌 Mock School APIs
- 🔒 Session-Based Authentication

---

## 👥 Supported Roles

### 🎓 Student
- View own attendance
- View own marks
- View timetable
- View school information
- Request teacher/school assistance

### 👨‍👩‍👦 Parent
- View child's attendance
- View child's marks
- View timetable
- View school information
- Request teacher/school assistance

### 👨‍🏫 Teacher
- View student attendance
- Mark student present/absent
- View student marks
- View timetable
- View school information

### 👨‍💼 Principal
- View school-wide attendance analytics
- View student information
- View timetable
- View school information

---

## 🧠 AI Personas

| Role | Persona |
|---|---|
| Student | Friendly Academic Assistant |
| Parent | Caring Parent Support Assistant |
| Teacher | Professional Teaching Assistant |
| Principal | Professional Management Assistant |

---

## 🌐 Supported Languages

XYZ AI is designed to support:

- English
- Hindi
- Tamil
- Telugu
- Marathi
- Bengali
- Gujarati
- Punjabi
- Kannada
- Malayalam
- Urdu

---

## 🔐 Security

XYZ AI uses application-level authorization instead of relying only on
the AI model.

Security features include:

- Session-based authentication
- Role-based permissions
- API-level authorization
- Protection against unauthorized student-data access
- Frontend role information is not trusted
- Sensitive configuration stored using environment variables
- API credentials are not hard-coded
- Unauthorized actions return HTTP 403
- Authentication failures return HTTP 401

---

## 📞 Human Escalation

If the AI cannot satisfy a user or human assistance is required, the user can
request assistance from:

- Teacher
- School Management

The system creates a mock support/call request and returns a request ID.

XYZ AI does not claim that a teacher or management representative has been
contacted unless the mock service confirms the request.

---

## 🏗️ Project Structure

```text
XYZ-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   └── chat.html
│
└── static/
    ├── css/
    ├── js/
    └── avatar/
