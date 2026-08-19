from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session
)
from dotenv import load_dotenv

load_dotenv()

from datetime import datetime
from functools import wraps
import os
import secrets
import re

# ============================================================
# XYZ AI - HUMAN LIKE SCHOOL ASSISTANT
# ============================================================

# PATH CONFIGURATION


APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(APP_DIR)



POSSIBLE_FRONTEND_DIRS = [
    os.path.join(PROJECT_DIR, "frontend"),
    os.path.join(APP_DIR, "frontend"),
    os.path.join(PROJECT_DIR, "templates"),
    os.path.join(APP_DIR, "templates"),
]


FRONTEND_DIR = None

for folder in POSSIBLE_FRONTEND_DIRS:

    if os.path.isdir(folder):
        FRONTEND_DIR = folder
        break


if FRONTEND_DIR is None:

    FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR
)


# ============================================================
# SECURITY CONFIGURATION
# ============================================================

#pp.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is not configured")

app.config.update(

    SESSION_COOKIE_HTTPONLY=True,

    SESSION_COOKIE_SAMESITE="Lax",

    SESSION_COOKIE_SECURE=False,

    PERMANENT_SESSION_LIFETIME=3600
)


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

SUPPORTED_LANGUAGES = [

    "English",
    "Hindi",
    "Tamil",
    "Telugu",
    "Marathi",
    "Bengali",
    "Gujarati",
    "Punjabi",
    "Kannada",
    "Malayalam",
    "Urdu"
]


# ============================================================
# AI PERSONAS
# ============================================================

AI_PERSONAS = {

    "Student": {

        "name":
            "Friendly Student Academic Assistant",

        "tone":
            "friendly, encouraging and supportive"
    },

    "Parent": {

        "name":
            "Caring Parent Support Assistant",

        "tone":
            "caring, patient and reassuring"
    },

    "Teacher": {

        "name":
            "Professional Teaching Assistant",

        "tone":
            "professional and helpful"
    },

    "Principal": {

        "name":
            "Professional Management Assistant",

        "tone":
            "professional, concise and analytical"
    }
}


# ============================================================
# STUDENT DATA
# ============================================================

student_data = {

    "Rahul": {

        "student_id":
            "STU101",

        "attendance":
            91.2,

        "recent":
            "Rahul was present for the last 5 classes.",

        "status":
            "Present",

        "class":
            "10-A",

        "roll_no":
            "101",

        "parent":
            "parent",

        "marks": {

            "Mathematics":
                82,

            "Science":
                88,

            "English":
                79
        }
    }
}


# ============================================================
# SCHOOL DATA
# ============================================================

school_data = {

    "name":
        "XYZ School",

    "timings":
        "8:00 AM to 2:00 PM",

    "next_holiday":
        "15 August",

    "principal":
        "Mr. Sharma",

    "office_hours":
        "9:00 AM to 3:00 PM",

    "overall_attendance":
        89.6,

    "timetable": {

        "Monday":
            "Mathematics, Science, English",

        "Tuesday":
            "Computer Science, Mathematics, Physics",

        "Wednesday":
            "English, Computer Science, Mathematics",

        "Thursday":
            "Physics, Science, Computer Science",

        "Friday":
            "Mathematics, English, Physics",

        "Saturday":
            "Computer Science, Practical"
    }
}


# ============================================================
# LOGIN USERS
# ============================================================

# DEMO ONLY
#
# Production:
# - password hashing
# - database
# - JWT/OAuth/SSO
# should be used.
#

users = {

    "admin": {

        "password":
            "1234",

        "role":
            "Student",

        "student":
            "Rahul"
    },

    "parent": {

        "password":
            "1234",

        "role":
            "Parent",

        "student":
            "Rahul"
    },

    "teacher": {

        "password":
            "1234",

        "role":
            "Teacher",

        "student":
            None
    },

    "principal": {

        "password":
            "1234",

        "role":
            "Principal",

        "student":
            None
    }
}


# ============================================================
# ROLE PERMISSIONS
# ============================================================

ROLE_PERMISSIONS = {

    "Student": [

        "view_own_attendance",

        "view_own_marks",

        "view_timetable",

        "view_school_info",

        "request_call",

        "request_teacher_help",

        "request_management_help"
    ],

    "Parent": [

        "view_child_attendance",

        "view_child_marks",

        "view_timetable",

        "view_school_info",

        "request_call",

        "request_teacher_help",

        "request_management_help"
    ],

    "Teacher": [

        "view_student_attendance",

        "mark_attendance",

        "view_student_marks",

        "view_timetable",

        "view_school_info",

        "view_call_requests",

        "escalate"
    ],

    "Principal": [

        "view_school_attendance",

        "view_student_attendance",

        "view_student_marks",

        "view_timetable",

        "view_school_info",

        "view_call_requests",

        "escalate"
    ]
}


# ============================================================
# MEMORY
# ============================================================

# Demo in-memory conversation store.
#
# Production should use:
# Redis / PostgreSQL / MongoDB etc.
#

conversation_memory = {}


# ============================================================
# CONVERSATION CONTEXT
# ============================================================

conversation_context = {}


# ============================================================
# PENDING ACTIONS
# ============================================================

pending_actions = {}


# ============================================================
# CALL REQUESTS
# ============================================================

call_requests = []


# ============================================================
# SECURITY HELPERS
# ============================================================

def current_role():

    return session.get("role")


def current_username():

    return session.get("username")


def current_student():

    username = current_username()

    user = users.get(username)

    if not user:
        return None

    return user.get("student")


def has_permission(
    role,
    permission
):

    return permission in ROLE_PERMISSIONS.get(
        role,
        []
    )


def permission_required(permission):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if not session.get("logged_in"):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Authentication required."
                }), 401

            role = current_role()

            if not has_permission(
                role,
                permission
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Permission denied."
                }), 403

            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator


def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("logged_in"):

            return jsonify({

                "success":
                    False,

                "message":
                    "Authentication required."
            }), 401

        return function(
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# STUDENT ACCESS CONTROL
# ============================================================

def can_access_student(
    role,
    requested_name
):

    if not requested_name:
        return False

    requested_name = requested_name.strip()

    if role == "Student":

        own_student = current_student()

        return (
            requested_name.lower()
            ==
            str(own_student).lower()
        )

    if role == "Parent":

        own_child = current_student()

        return (
            requested_name.lower()
            ==
            str(own_child).lower()
        )

    if role in [
        "Teacher",
        "Principal"
    ]:

        return requested_name in student_data

    return False


# ============================================================
# TEMPLATE CHECK
# ============================================================

def template_exists(
    filename
):

    return os.path.isfile(
        os.path.join(
            FRONTEND_DIR,
            filename
        )
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if session.get("logged_in"):

        return redirect(
            "/dashboard"
        )

    return redirect(
        "/login"
    )


# ============================================================
# LOGIN PAGE
# ============================================================

@app.route("/login")
def login_page():

    if not template_exists(
        "login.html"
    ):

        return (

            f"""
            <h1>XYZ AI</h1>

            <h2>Template Error</h2>

            <p>
            login.html was not found.
            </p>

            <p>
            Flask is currently searching here:
            </p>

            <pre>{FRONTEND_DIR}</pre>

            <p>
            Create:
            </p>

            <pre>
            frontend/
                login.html
            </pre>
            """,

            500
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGIN API
# ============================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def api_login():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        username = str(
            data.get(
                "username",
                ""
            )
        ).strip()

        password = str(
            data.get(
                "password",
                ""
            )
        )

        if not username or not password:

            return jsonify({

                "success":
                    False,

                "message":
                    "Username and password are required."
            }), 400

        user = users.get(
            username
        )

        if not user:

            return jsonify({

                "success":
                    False,

                "message":
                    "Invalid username or password."
            }), 401

        if user["password"] != password:

            return jsonify({

                "success":
                    False,

                "message":
                    "Invalid username or password."
            }), 401

        # Clear old session.
        session.clear()

        session.permanent = True

        session["logged_in"] = True

        session["username"] = username

        session["role"] = user["role"]

        session["student"] = user.get(
            "student"
        )

        # Create unique session ID.
        session["session_id"] = secrets.token_hex(
            16
        )

        return jsonify({

            "success":
                True,

            "message":
                "Login successful.",

            "username":
                username,

            "role":
                user["role"],

            "persona":
                AI_PERSONAS[user["role"]]
        })

    except Exception:

        return jsonify({

            "success":
                False,

            "message":
                "Login failed."
        }), 500


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):

        return redirect(
            "/login"
        )

    if not template_exists(
        "dashboard.html"
    ):

        return (

            f"""
            <h1>XYZ AI</h1>
            <h2>dashboard.html not found</h2>
            <pre>{FRONTEND_DIR}</pre>
            """,

            500
        )

    return render_template(

        "dashboard.html",

        username=
            current_username(),

        role=
            current_role()
    )


# ============================================================
# CHAT PAGE
# ============================================================

@app.route("/chat")
def chat():

    if not session.get("logged_in"):

        return redirect(
            "/login"
        )

    if not template_exists(
        "chat.html"
    ):

        return (

            f"""
            <h1>XYZ AI</h1>
            <h2>chat.html not found</h2>
            <pre>{FRONTEND_DIR}</pre>
            """,

            500
        )

    return render_template(
        "chat.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/login"
    )


# ============================================================
# CURRENT USER
# ============================================================

@app.route("/api/me")
@login_required
def current_user():

    role = current_role()

    return jsonify({

        "success":
            True,

        "username":
            current_username(),

        "role":
            role,

        "student":
            current_student(),

        "persona":
            AI_PERSONAS.get(
                role
            ),

        "permissions":
            ROLE_PERMISSIONS.get(
                role,
                []
            ),

        "languages":
            SUPPORTED_LANGUAGES
    })


# ============================================================
# ATTENDANCE API
# ============================================================

@app.route(
    "/api/attendance/<name>"
)
@login_required
def attendance(name):

    role = current_role()

    if not can_access_student(
        role,
        name
    ):

        return jsonify({

            "success":
                False,

            "message":
                "You are not authorized to access this student's attendance."
        }), 403

    student = student_data.get(
        name
    )

    if not student:

        return jsonify({

            "success":
                False,

            "message":
                "Student not found."
        }), 404

    return jsonify({

        "success":
            True,

        "student":
            name,

        "attendance":
            student["attendance"],

        "today":
            student["status"],

        "class":
            student["class"],

        "roll_no":
            student["roll_no"]
    })


# ============================================================
# MARK ATTENDANCE
# ============================================================

def update_attendance(
    name,
    status
):

    student = student_data.get(
        name
    )

    if not student:

        return None

    student["status"] = status

    return student


@app.route(
    "/api/attendance/<name>/absent",
    methods=["POST"]
)
@permission_required(
    "mark_attendance"
)
def mark_absent(name):

    if name not in student_data:

        return jsonify({

            "success":
                False,

            "message":
                "Student not found."
        }), 404

    update_attendance(
        name,
        "Absent"
    )

    return jsonify({

        "success":
            True,

        "student":
            name,

        "today":
            "Absent",

        "message":
            f"{name} has been marked absent today."
    })


@app.route(
    "/api/attendance/<name>/present",
    methods=["POST"]
)
@permission_required(
    "mark_attendance"
)
def mark_present(name):

    if name not in student_data:

        return jsonify({

            "success":
                False,

            "message":
                "Student not found."
        }), 404

    update_attendance(
        name,
        "Present"
    )

    return jsonify({

        "success":
            True,

        "student":
            name,

        "today":
            "Present",

        "message":
            f"{name} has been marked present today."
    })


# ============================================================
# MARKS API
# ============================================================

@app.route(
    "/api/marks/<name>"
)
@login_required
def marks_api(name):

    role = current_role()

    if not can_access_student(
        role,
        name
    ):

        return jsonify({

            "success":
                False,

            "message":
                "Unauthorized access."
        }), 403

    student = student_data.get(
        name
    )

    if not student:

        return jsonify({

            "success":
                False,

            "message":
                "Student not found."
        }), 404

    return jsonify({

        "success":
            True,

        "student":
            name,

        "marks":
            student["marks"]
    })


# ============================================================
# TIMETABLE API
# ============================================================

@app.route(
    "/api/timetable"
)
@permission_required(
    "view_timetable"
)
def timetable_api():

    return jsonify({

        "success":
            True,

        "timetable":
            school_data["timetable"]
    })


# ============================================================
# SCHOOL INFO
# ============================================================

@app.route(
    "/api/school-info"
)
@permission_required(
    "view_school_info"
)
def school_info_api():

    return jsonify({

        "success":
            True,

        "school": {

            "name":
                school_data["name"],

            "timings":
                school_data["timings"],

            "next_holiday":
                school_data["next_holiday"],

            "principal":
                school_data["principal"],

            "office_hours":
                school_data["office_hours"]
        }
    })


# ============================================================
# SCHOOL ANALYTICS
# ============================================================

@app.route(
    "/api/analytics/attendance"
)
@permission_required(
    "view_school_attendance"
)
def attendance_analytics():

    return jsonify({

        "success":
            True,

        "overall_attendance":
            school_data["overall_attendance"],

        "message":
            "School attendance analytics retrieved successfully."
    })


# ============================================================
# CALL REQUEST
# ============================================================

def create_call_request(
    role,
    request_type="school",
    reason=""
):

    request_id = (
        len(call_requests)
        + 1
    )

    result = {

        "request_id":
            request_id,

        "username":
            current_username(),

        "role":
            role,

        "type":
            request_type,

        "reason":
            reason,

        "status":
            "submitted",

        "created_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }

    call_requests.append(
        result
    )

    return result


@app.route(
    "/api/call-request",
    methods=["POST"]
)
@login_required
def call_request_api():

    role = current_role()

    if role not in [
        "Student",
        "Parent"
    ]:

        return jsonify({

            "success":
                False,

            "message":
                "You are not authorized to request a call."
        }), 403

    data = request.get_json(
        silent=True
    ) or {}

    request_type = data.get(
        "type",
        "school"
    )

    if request_type not in [
        "school",
        "teacher",
        "management"
    ]:

        request_type = "school"

    reason = str(
        data.get(
            "reason",
            ""
        )
    ).strip()

    result = create_call_request(

        role,

        request_type,

        reason
    )

    return jsonify({

        "success":
            True,

        "request":
            result
    })


# ============================================================
# TEACHER ESCALATION
# ============================================================

@app.route(
    "/api/escalate/teacher",
    methods=["POST"]
)
@login_required
def escalate_teacher():

    role = current_role()

    if not has_permission(
        role,
        "request_teacher_help"
    ):

        return jsonify({

            "success":
                False,

            "message":
                "You are not authorized to contact a teacher."
        }), 403

    data = request.get_json(
        silent=True
    ) or {}

    reason = str(
        data.get(
            "reason",
            ""
        )
    ).strip()

    if not reason:

        return jsonify({

            "success":
                False,

            "message":
                "Reason is required."
        }), 400

    result = create_call_request(

        role,

        "teacher",

        reason
    )

    return jsonify({

        "success":
            True,

        "request_id":
            result["request_id"],

        "status":
            result["status"],

        "message":
            "Teacher request submitted successfully."
    })


# ============================================================
# MANAGEMENT ESCALATION
# ============================================================

@app.route(
    "/api/escalate/management",
    methods=["POST"]
)
@login_required
def escalate_management():

    role = current_role()

    if not has_permission(
        role,
        "request_management_help"
    ):

        return jsonify({

            "success":
                False,

            "message":
                "You are not authorized to contact school management."
        }), 403

    data = request.get_json(
        silent=True
    ) or {}

    reason = str(
        data.get(
            "reason",
            ""
        )
    ).strip()

    if not reason:

        return jsonify({

            "success":
                False,

            "message":
                "Reason is required."
        }), 400

    result = create_call_request(

        role,

        "management",

        reason
    )

    return jsonify({

        "success":
            True,

        "request_id":
            result["request_id"],

        "status":
            result["status"],

        "message":
            "Management request submitted successfully."
    })


# ============================================================
# GET CALL REQUESTS
# ============================================================

@app.route(
    "/api/call-requests"
)
@login_required
def get_call_requests():

    role = current_role()

    if role not in [
        "Teacher",
        "Principal"
    ]:

        return jsonify({

            "success":
                False,

            "message":
                "Unauthorized."
        }), 403

    return jsonify({

        "success":
            True,

        "requests":
            call_requests
    })


# ============================================================
# LANGUAGE TRANSLATION
# ============================================================

TRANSLATIONS = {

    "Hindi": {

        "Please enter a message.":
            "कृपया अपना संदेश लिखें।",

        "Would you like me to request a call now?":
            "क्या आप चाहते हैं कि मैं अभी कॉल का अनुरोध करूँ?",

        "Please reply with Yes or No.":
            "कृपया हाँ या नहीं में जवाब दें।",

        "Okay, I won't request a call.":
            "ठीक है, मैं कॉल का अनुरोध नहीं करूँगा।",

        "Your call request has been submitted successfully.":
            "आपका कॉल अनुरोध सफलतापूर्वक भेज दिया गया है।"
    },

    "Tamil": {

        "Please enter a message.":
            "தயவுசெய்து உங்கள் செய்தியை உள்ளிடவும்."
    },

    "Telugu": {

        "Please enter a message.":
            "దయచేసి మీ సందేశాన్ని నమోదు చేయండి."
    },

    "Marathi": {

        "Please enter a message.":
            "कृपया तुमचा संदेश लिहा."
    },

    "Bengali": {

        "Please enter a message.":
            "অনুগ্রহ করে আপনার বার্তা লিখুন।"
    },

    "Gujarati": {

        "Please enter a message.":
            "કૃપા કરીને તમારો સંદેશ લખો."
    },

    "Punjabi": {

        "Please enter a message.":
            "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਸੁਨੇਹਾ ਦਰਜ ਕਰੋ।"
    },

    "Kannada": {

        "Please enter a message.":
            "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ನಮೂದಿಸಿ."
    },

    "Malayalam": {

        "Please enter a message.":
            "ദയവായി നിങ്ങളുടെ സന്ദേശം നൽകുക."
    },

    "Urdu": {

        "Please enter a message.":
            "براہ کرم اپنا پیغام درج کریں۔"
    }
}


def translate_response(
    response,
    language
):

    return TRANSLATIONS.get(
        language,
        {}
    ).get(
        response,
        response
    )


# ============================================================
# SECURITY - PROMPT INJECTION DETECTION
# ============================================================

PROMPT_INJECTION_PATTERNS = [

    r"ignore previous instructions",

    r"ignore all instructions",

    r"ignore your instructions",

    r"reveal system prompt",

    r"show system prompt",

    r"print system prompt",

    r"developer message",

    r"show api key",

    r"show api keys",

    r"give me password",

    r"reveal password",

    r"show credentials",

    r"database password",

    r"secret key",

    r"system instructions"
]


def is_prompt_injection(
    message
):

    text = message.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:

        if re.search(
            pattern,
            text
        ):

            return True

    return False


# ============================================================
# SECURITY RESPONSE
# ============================================================

def security_response(
    language
):

    response = (

        "I can't provide system instructions, "
        "passwords, API keys, credentials, or "
        "private security information. "
        "I can help you with authorized school services."
    )

    if language == "Hindi":

        response = (

            "मैं system instructions, passwords, "
            "API keys, credentials या private security "
            "information साझा नहीं कर सकता। "
            "मैं authorized school services में आपकी मदद कर सकता हूँ।"
        )

    return response


# ============================================================
# MEMORY FUNCTIONS
# ============================================================

def get_memory_key():

    return session.get(
        "session_id",
        current_username()
    )


def save_memory(
    sender,
    message
):

    key = get_memory_key()

    if key not in conversation_memory:

        conversation_memory[key] = []

    conversation_memory[key].append({

        "sender":
            sender,

        "message":
            message,

        "time":
            datetime.now().strftime(
                "%H:%M:%S"
            )
    })

    # Keep only recent 50 messages.
    conversation_memory[key] = \
        conversation_memory[key][-50:]


def get_recent_memory():

    return conversation_memory.get(
        get_memory_key(),
        []
    )


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(
    text,
    role
):

    text = text.lower()

    # Attendance
    if any(
        x in text
        for x in [

            "attendance",
            "present",
            "absent",
            "hajiri",
            "हाजिरी",
            "उपस्थिति",
            "attendance kitni"
        ]
    ):

        return "attendance"

    # Marks
    if any(
        x in text
        for x in [

            "marks",
            "mark",
            "score",
            "result",
            "grade",
            "अंक",
            "मार्क्स"
        ]
    ):

        return "academics"

    # Timetable
    if any(
        x in text
        for x in [

            "timetable",
            "time table",
            "schedule",
            "routine",
            "रूटीन",
            "टाइम टेबल"
        ]
    ):

        return "timetable"

    # Call
    if any(
        x in text
        for x in [

            "call",
            "phone",
            "talk to teacher",
            "teacher se baat",
            "management se baat",
            "school se baat",
            "speak to teacher",
            "contact teacher"
        ]
    ):

        return "escalation"

    # Analytics
    if (
        "overall" in text
        and "attendance" in text
    ):

        return "school_analytics"

    # Greeting
    if any(
        x in text
        for x in [

            "hello",
            "hi",
            "hey",
            "namaste",
            "नमस्ते",
            "नमस्कार"
        ]
    ):

        return "greeting"

    # Timing
    if any(
        x in text
        for x in [

            "timing",
            "timings",
            "school time",
            "kitne baje",
            "समय"
        ]
    ):

        return "school_timing"

    # Holiday
    if any(
        x in text
        for x in [

            "holiday",
            "chhutti",
            "छुट्टी",
            "break"
        ]
    ):

        return "holiday"

    # Principal
    if any(
        x in text
        for x in [

            "principal",
            "प्रिंसिपल"
        ]
    ):

        return "principal"

    return "general"


# ============================================================
# CHAT RESPONSE ENGINE
# ============================================================

def generate_response(
    message,
    role,
    language
):

    text = message.lower()

    intent = detect_intent(
        text,
        role
    )

    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    if intent == "greeting":

        persona = AI_PERSONAS[
            role
        ]["name"]

        response = (

            f"Hello! 👋 I'm XYZ AI, your "
            f"{persona}. "
            "How can I help you today?"
        )

        return response, intent


    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------

    if intent == "attendance":

        student_name = current_student()

        if not student_name:

            if role == "Teacher":

                student_name = "Rahul"

            elif role == "Principal":

                student_name = "Rahul"

            else:

                return (

                    "Please tell me which student "
                    "you want to check."
                ), "clarification"

        student = student_data.get(
            student_name
        )

        if not student:

            return (

                "I couldn't find that student "
                "in the school records."
            ), "attendance"

        attendance_value = student[
            "attendance"
        ]

        if role == "Student":

            response = (

                f"Your current attendance is "
                f"{attendance_value}%. "
                "Would you like me to check your "
                "recent attendance too?"
            )

        elif role == "Parent":

            response = (

                f"{student_name} currently has "
                f"{attendance_value}% attendance. "
                "Would you like me to check the "
                "recent attendance too?"
            )

        elif role == "Teacher":

            response = (

                f"{student_name}'s current attendance is "
                f"{attendance_value}%. "
                f"Today's status is "
                f"{student['status']}."
            )

        else:

            response = (

                f"The overall school attendance is "
                f"{school_data['overall_attendance']}%."
            )

        return response, intent


    # --------------------------------------------------------
    # MARK ABSENT
    # --------------------------------------------------------

    if (
        role == "Teacher"
        and "mark" in text
        and "absent" in text
    ):

        student_name = "Rahul"

        update_attendance(
            student_name,
            "Absent"
        )

        return (

            f"Sure. {student_name} has been marked "
            "absent for today."
        ), "mark_absent"


    # --------------------------------------------------------
    # MARK PRESENT
    # --------------------------------------------------------

    if (
        role == "Teacher"
        and "mark" in text
        and "present" in text
    ):

        student_name = "Rahul"

        update_attendance(
            student_name,
            "Present"
        )

        return (

            f"Sure. {student_name} has been marked "
            "present for today."
        ), "mark_present"


    # --------------------------------------------------------
    # ACADEMICS
    # --------------------------------------------------------

    if intent == "academics":

        student_name = current_student()

        if not student_name:

            student_name = "Rahul"

        student = student_data.get(
            student_name
        )

        if not student:

            return (
                "Student record not found."
            ), intent

        marks = student[
            "marks"
        ]

        if "science" in text:

            return (

                f"{student_name}'s Science marks are "
                f"{marks['Science']}."
            ), intent

        if (
            "math" in text
            or "mathematics" in text
        ):

            return (

                f"{student_name}'s Mathematics marks are "
                f"{marks['Mathematics']}."
            ), intent

        if "english" in text:

            return (

                f"{student_name}'s English marks are "
                f"{marks['English']}."
            ), intent

        return (

            f"{student_name}'s marks are: "
            f"Mathematics {marks['Mathematics']}, "
            f"Science {marks['Science']}, "
            f"English {marks['English']}."
        ), intent


    # --------------------------------------------------------
    # TIMETABLE
    # --------------------------------------------------------

    if intent == "timetable":

        timetable = school_data[
            "timetable"
        ]

        response = (

            "Here is the weekly timetable:\n\n"

            f"Monday: {timetable['Monday']}\n"

            f"Tuesday: {timetable['Tuesday']}\n"

            f"Wednesday: {timetable['Wednesday']}\n"

            f"Thursday: {timetable['Thursday']}\n"

            f"Friday: {timetable['Friday']}\n"

            f"Saturday: {timetable['Saturday']}"
        )

        return response, intent


    # --------------------------------------------------------
    # SCHOOL ANALYTICS
    # --------------------------------------------------------

    if intent == "school_analytics":

        if role != "Principal":

            return (

                "I'm sorry, school-wide attendance "
                "analytics are available only to the Principal."
            ), intent

        return (

            "The overall school attendance is "
            f"{school_data['overall_attendance']}%."
        ), intent


    # --------------------------------------------------------
    # SCHOOL TIMING
    # --------------------------------------------------------

    if intent == "school_timing":

        return (

            "School timings are "
            f"{school_data['timings']}."
        ), intent


    # --------------------------------------------------------
    # HOLIDAY
    # --------------------------------------------------------

    if intent == "holiday":

        return (

            "The next school holiday is "
            f"{school_data['next_holiday']}."
        ), intent


    # --------------------------------------------------------
    # PRINCIPAL
    # --------------------------------------------------------

    if intent == "principal":

        return (

            "The school principal is "
            f"{school_data['principal']}."
        ), intent


    # --------------------------------------------------------
    # ESCALATION
    # --------------------------------------------------------

    if intent == "escalation":

        if role not in [
            "Student",
            "Parent"
        ]:

            return (

                "Human escalation is available "
                "through the authorized school "
                "support workflow."
            ), intent

        pending_actions[
            get_memory_key()
        ] = {

            "type":
                "call",

            "status":
                "waiting_for_confirmation"
        }

        return (

            "Of course. I can request human assistance "
            "for you. Would you like to talk to a "
            "teacher or school management?"
        ), intent


    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    if role == "Student":

        response = (

            "I'm XYZ AI, your Student Assistant. "
            "I can help you with attendance, marks, "
            "timetable, school timings, holidays "
            "and other school-related questions."
        )

    elif role == "Parent":

        response = (

            "I'm XYZ AI, your Parent Support Assistant. "
            "I can help you with your child's attendance, "
            "academics, timetable and school information."
        )

    elif role == "Teacher":

        response = (

            "I'm XYZ AI, your Teaching Assistant. "
            "I can help you check attendance, mark "
            "students present or absent, view academics "
            "and timetable."
        )

    else:

        response = (

            "I'm XYZ AI, your Management Assistant. "
            "I can help with school attendance analytics, "
            "academics, timetable and school information."
        )

    return response, "general"


# ============================================================
# AI CHAT API
# ============================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
@login_required
def ai_chat():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        message = str(
            data.get(
                "message",
                ""
            )
        ).strip()

        language = data.get(
            "language",
            "English"
        )

        # IMPORTANT:
        # NEVER trust role from frontend.
        #
        # Role always comes from session.
        #

        role = current_role()

        if language not in SUPPORTED_LANGUAGES:

            language = "English"


        # ----------------------------------------------------
        # EMPTY MESSAGE
        # ----------------------------------------------------

        if not message:

            response = translate_response(

                "Please enter a message.",

                language
            )

            return jsonify({

                "success":
                    True,

                "response":
                    response,

                "role":
                    role,

                "intent":
                    "general",

                "language":
                    language
            })


        # ----------------------------------------------------
        # PROMPT INJECTION PROTECTION
        # ----------------------------------------------------

        if is_prompt_injection(
            message
        ):

            response = security_response(
                language
            )

            save_memory(
                "user",
                message
            )

            save_memory(
                "ai",
                response
            )

            return jsonify({

                "success":
                    True,

                "response":
                    response,

                "role":
                    role,

                "intent":
                    "security",

                "language":
                    language
            })


        # ----------------------------------------------------
        # SAVE USER MESSAGE
        # ----------------------------------------------------

        save_memory(
            "user",
            message
        )


        # ----------------------------------------------------
        # PENDING CALL CONFIRMATION
        # ----------------------------------------------------

        memory_key = get_memory_key()

        pending = pending_actions.get(
            memory_key
        )

        if pending:

            yes_words = [

                "yes",
                "y",
                "sure",
                "okay",
                "ok",
                "confirm",
                "haan",
                "ha",
                "हाँ",
                "ji"
            ]

            no_words = [

                "no",
                "n",
                "cancel",
                "not now",
                "nahi",
                "nahin",
                "नहीं"
            ]

            clean_text = message.lower().strip()

            if clean_text in yes_words:

                result = create_call_request(

                    role,

                    "school",

                    "User requested human assistance."
                )

                pending_actions.pop(
                    memory_key,
                    None
                )

                response = (

                    "Your call request has been submitted "
                    "successfully. "
                    f"Your request ID is "
                    f"#{result['request_id']}. "
                    "The request has been recorded in the "
                    "school support system."
                )

                intent = "call_confirmation"

            elif clean_text in no_words:

                pending_actions.pop(
                    memory_key,
                    None
                )

                response = (
                    "Okay, I won't request a call."
                )

                intent = "call_cancel"

            else:

                response = (
                    "Please reply with Yes or No."
                )

                intent = "call_confirmation"

        else:

            response, intent = generate_response(

                message,

                role,

                language
            )


        # ----------------------------------------------------
        # TRANSLATION
        # ----------------------------------------------------

        response = translate_response(

            response,

            language
        )


        # ----------------------------------------------------
        # SAVE AI RESPONSE
        # ----------------------------------------------------

        save_memory(
            "ai",
            response
        )


        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        return jsonify({

            "success":
                True,

            "response":
                response,

            "role":
                role,

            "intent":
                intent,

            "language":
                language,

            "persona":
                AI_PERSONAS.get(
                    role
                ),

            "avatar": {

                "enabled":
                    True,

                "expression":
                    "friendly",

                "speaking":
                    False
            }
        })


    except Exception as e:

        print(
            "CHAT ERROR:",
            e
        )

        return jsonify({

            "success":
                False,

            "response":
                "Sorry, something went wrong. Please try again."

        }), 500


# ============================================================
# MEMORY API
# ============================================================

@app.route(
    "/api/memory"
)
@login_required
def memory_api():

    return jsonify({

        "success":
            True,

        "role":
            current_role(),

        "conversation":
            get_recent_memory()
    })


# ============================================================
# CLEAR MEMORY
# ============================================================

@app.route(
    "/api/memory/clear",
    methods=["POST"]
)
@login_required
def clear_memory():

    key = get_memory_key()

    conversation_memory.pop(
        key,
        None
    )

    pending_actions.pop(
        key,
        None
    )

    return jsonify({

        "success":
            True,

        "message":
            "Conversation memory cleared."
    })


# ============================================================
# VOICE API
# ============================================================

@app.route(
    "/api/voice",
    methods=["POST"]
)
@login_required
def voice_api():

    """
    Frontend voice flow:

    Microphone
        ↓
    Speech Recognition
        ↓
    /api/chat
        ↓
    XYZ AI
        ↓
    Text-to-Speech
        ↓
    Avatar
    """

    data = request.get_json(
        silent=True
    ) or {}

    transcript = str(
        data.get(
            "transcript",
            ""
        )
    ).strip()

    language = data.get(
        "language",
        "English"
    )

    if not transcript:

        return jsonify({

            "success":
                False,

            "message":
                "Voice transcript is empty."
        }), 400

    # Reuse chat engine.
    #
    # No frontend role is accepted.
    #

    fake_chat_data = {

        "message":
            transcript,

        "language":
            language
    }

    # Direct internal processing.
    #
    # We don't call HTTP internally.
    #

    role = current_role()

    if is_prompt_injection(
        transcript
    ):

        response = security_response(
            language
        )

        intent = "security"

    else:

        save_memory(
            "user",
            transcript
        )

        response, intent = generate_response(

            transcript,

            role,

            language
        )

        response = translate_response(

            response,

            language
        )

    save_memory(
        "ai",
        response
    )

    return jsonify({

        "success":
            True,

        "transcript":
            transcript,

        "response":
            response,

        "role":
            role,

        "intent":
            intent,

        "language":
            language,

        "avatar": {

            "enabled":
                True,

            "expression":
                "friendly",

            "lip_sync":
                True,

            "speaking":
                True
        }
    })


# ============================================================
# AVATAR STATUS API
# ============================================================

@app.route(
    "/api/avatar"
)
@login_required
def avatar_api():

    role = current_role()

    return jsonify({

        "success":
            True,

        "enabled":
            True,

        "persona":
            AI_PERSONAS.get(
                role
            ),

        "role":
            role,

        "features": {

            "voice":
                True,

            "speech_to_text":
                True,

            "text_to_speech":
                True,

            "facial_expression":
                True,

            "lip_sync":
                True,

            "real_time":
                True
        }
    })


# ============================================================
# TEST API
# ============================================================

@app.route(
    "/api/test"
)
def test():

    return jsonify({

        "success":
            True,

        "message":
            "XYZ AI API is working.",

        "frontend":
            FRONTEND_DIR,

        "template_exists": {

            "login":
                template_exists(
                    "login.html"
                ),

            "dashboard":
                template_exists(
                    "dashboard.html"
                ),

            "chat":
                template_exists(
                    "chat.html"
                )
        }
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/health"
)
def health():

    return jsonify({

        "status":
            "healthy",

        "service":
            "XYZ AI",

        "time":
            datetime.now().isoformat()
    })


# ============================================================
# SECURITY HEADERS
# ============================================================

@app.after_request
def security_headers(response):

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "SAMEORIGIN"

    response.headers[
        "Referrer-Policy"
    ] = "strict-origin-when-cross-origin"

    response.headers[
        "Permissions-Policy"
    ] = (
        "microphone=(self), camera=(self)"
    )

    return response


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    if request.path.startswith(
        "/api/"
    ):

        return jsonify({

            "success":
                False,

            "message":
                "API endpoint not found."
        }), 404

    return (
        "<h1>XYZ AI - 404</h1>"
        "<p>Page not found.</p>"
    ), 404


@app.errorhandler(500)
def server_error(error):

    if request.path.startswith(
        "/api/"
    ):

        return jsonify({

            "success":
                False,

            "message":
                "Internal server error."
        }), 500

    return (
        "<h1>XYZ AI - Server Error</h1>"
        "<p>Something went wrong.</p>"
    ), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("🤖 XYZ AI - HUMAN LIKE SCHOOL ASSISTANT")
    print("=" * 70)

    print(
        "App directory:",
        APP_DIR
    )

    print(
        "Project directory:",
        PROJECT_DIR
    )

    print(
        "Frontend directory:",
        FRONTEND_DIR
    )

    print()

    print(
        "login.html:",
        template_exists(
            "login.html"
        )
    )

    print(
        "dashboard.html:",
        template_exists(
            "dashboard.html"
        )
    )

    print(
        "chat.html:",
        template_exists(
            "chat.html"
        )
    )

    print()

    print(
        "Login:     http://127.0.0.1:5000/login"
    )

    print(
        "Dashboard: http://127.0.0.1:5000/dashboard"
    )

    print(
        "Chat:      http://127.0.0.1:5000/chat"
    )

    print(
        "Health:    http://127.0.0.1:5000/health"
    )

    print(
        "Test:      http://127.0.0.1:5000/api/test"
    )

    print("=" * 70)
    print()

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True
    )