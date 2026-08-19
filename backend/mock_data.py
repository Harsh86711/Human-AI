students = {
    "Rahul": {
        "attendance": 91.2,
        "today": "Present",
        "class": "B.Tech CSE",
        "roll_no": "CSE101"
    },

    "Aman": {
        "attendance": 86.5,
        "today": "Present",
        "class": "B.Tech CSE",
        "roll_no": "CSE102"
    },

    "Priya": {
        "attendance": 78.4,
        "today": "Absent",
        "class": "B.Tech CSE",
        "roll_no": "CSE103"
    }
}


def get_attendance(name):
    student = students.get(name)

    if student is None:
        return None

    return student["attendance"], student["today"]


def mark_absent(name):
    student = students.get(name)

    if student is None:
        return None

    student["today"] = "Absent"

    return student