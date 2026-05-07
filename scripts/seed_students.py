"""
Seed 30 students, 5 assessments and marks for teacher_id=1.
Run: python scripts/seed_students.py
"""
import sys, os, random
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.db.session import SessionLocal
from app.models.student    import StudentMaster, Gender
from app.models.assessment import Assessment, AssessmentResult, AssessmentType

STUDENTS = [
    ("Aarav Sharma",       "male",   "Rajesh Sharma",    "9876543001"),
    ("Priya Nair",         "female", "Suresh Nair",      "9876543002"),
    ("Mohammed Irfan",     "male",   "Abdul Irfan",      "9876543003"),
    ("Sneha Reddy",        "female", "Venkat Reddy",     "9876543004"),
    ("Karthik Iyer",       "male",   "Ravi Iyer",        "9876543005"),
    ("Anjali Menon",       "female", "Pradeep Menon",    "9876543006"),
    ("Ravi Kumar",         "male",   "Sunil Kumar",      "9876543007"),
    ("Divya Pillai",       "female", "Mohan Pillai",     "9876543008"),
    ("Arjun Singh",        "male",   "Harpreet Singh",   "9876543009"),
    ("Lakshmi Devi",       "female", "Ramaiah Devi",     "9876543010"),
    ("Siddharth Joshi",    "male",   "Anil Joshi",       "9876543011"),
    ("Meera Krishnan",     "female", "Gopal Krishnan",   "9876543012"),
    ("Vikram Patel",       "male",   "Dinesh Patel",     "9876543013"),
    ("Nisha Gupta",        "female", "Sanjay Gupta",     "9876543014"),
    ("Rahul Verma",        "male",   "Mahesh Verma",     "9876543015"),
    ("Pooja Bhatt",        "female", "Vinod Bhatt",      "9876543016"),
    ("Aditya Rao",         "male",   "Krishna Rao",      "9876543017"),
    ("Sunita Pandey",      "female", "Ramesh Pandey",    "9876543018"),
    ("Nikhil Shetty",      "male",   "Suresh Shetty",    "9876543019"),
    ("Kavitha Nambiar",    "female", "Anand Nambiar",    "9876543020"),
    ("Rohan Malhotra",     "male",   "Deepak Malhotra",  "9876543021"),
    ("Deepa Thomas",       "female", "George Thomas",    "9876543022"),
    ("Gaurav Tiwari",      "male",   "Suresh Tiwari",    "9876543023"),
    ("Ananya Bose",        "female", "Subhash Bose",     "9876543024"),
    ("Suresh Babu",        "male",   "Babu Reddy",       "9876543025"),
    ("Rekha Pillai",       "female", "Vijay Pillai",     "9876543026"),
    ("Ajay Chauhan",       "male",   "Ramesh Chauhan",   "9876543027"),
    ("Swathi Nair",        "female", "Krishnan Nair",    "9876543028"),
    ("Prakash Hegde",      "male",   "Mohan Hegde",      "9876543029"),
    ("Bharathi Sundaram",  "female", "Sundaram Pillai",  "9876543030"),
]

ASSESSMENTS = [
    ("Chapter 1 Quiz — The Indian Constitution",  "Chapter 1 - The Indian Constitution",  "quiz",       25.0,  date(2026, 3, 10)),
    ("Unit Test 1 — Secularism & Parliament",      "Chapter 2 - Understanding Secularism", "test",       50.0,  date(2026, 3, 24)),
    ("Mid-Term Examination",                       None,                                   "exam",      100.0,  date(2026, 4,  5)),
    ("Chapter 4 Assignment — Judiciary",           "Chapter 4 - Judiciary",                "assignment", 20.0,  date(2026, 4, 15)),
    ("Chapter 5 Quiz — Marginalisation",           "Chapter 5 - Understanding Marginalisation", "quiz", 25.0,  date(2026, 4, 22)),
]


def seed():
    db = SessionLocal()
    try:
        if db.query(StudentMaster).filter_by(teacher_id=1).count() > 0:
            print("✅ Students already seeded — skipping.")
            return

        # ── Students ──────────────────────────────────────────────────────────
        students = []
        for i, (name, gender, parent, phone) in enumerate(STUDENTS, start=1):
            s = StudentMaster(
                teacher_id=1,
                name=name,
                roll_number=f"8A{str(i).zfill(2)}",
                gender=Gender(gender),
                parent_name=parent,
                parent_phone=phone,
                class_name="8",
                section="A",
            )
            db.add(s)
            students.append(s)
        db.flush()
        print(f"✅ Created {len(students)} students")

        # ── Assessments + Results ─────────────────────────────────────────────
        for title, chapter, atype, max_m, adate in ASSESSMENTS:
            assessment = Assessment(
                teacher_id=1,
                title=title,
                chapter=chapter,
                assessment_type=AssessmentType(atype),
                max_marks=max_m,
                assessment_date=adate,
            )
            db.add(assessment)
            db.flush()

            for student in students:
                # ~10% chance of being absent (null marks)
                absent = random.random() < 0.1
                marks = None if absent else round(
                    random.uniform(max_m * 0.4, max_m), 1
                )
                result = AssessmentResult(
                    assessment_id=assessment.assessment_id,
                    student_id=student.student_id,
                    marks_obtained=marks,
                    remarks="Absent" if absent else None,
                )
                db.add(result)

        db.commit()
        print(f"✅ Created {len(ASSESSMENTS)} assessments with results")
        print("🎉 Seed complete!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
