from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


# ---------------------------------------------------------
# ADMIN USER
# ---------------------------------------------------------
class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    full_name = Column(String(150), nullable=True)
    role = Column(String(50), default="admin")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ---------------------------------------------------------
# STUDENTS
# ---------------------------------------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    admission_no = Column(String(100), unique=True, nullable=False, index=True)
    roll_no = Column(String(50), nullable=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)

    father_name = Column(String(150), nullable=True)
    mother_name = Column(String(150), nullable=True)

    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)

    class_name = Column(String(50), nullable=True)
    section = Column(String(20), nullable=True)

    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)

    address = Column(Text, nullable=True)
    photo = Column(String(255), nullable=True)

    admission_date = Column(Date, nullable=True)
    status = Column(String(30), default="active")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ---------------------------------------------------------
# TEACHERS
# ---------------------------------------------------------
class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String(100), unique=True, nullable=False, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)

    email = Column(String(150), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)

    qualification = Column(String(255), nullable=True)
    subject = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)

    joining_date = Column(Date, nullable=True)

    address = Column(Text, nullable=True)
    photo = Column(String(255), nullable=True)

    status = Column(String(30), default="active")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ---------------------------------------------------------
# ADMISSIONS
# ---------------------------------------------------------
class Admission(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True, index=True)

    student_name = Column(String(150), nullable=False)
    father_name = Column(String(150), nullable=True)
    mother_name = Column(String(150), nullable=True)

    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)

    applying_class = Column(String(50), nullable=False)

    phone = Column(String(20), nullable=False)
    email = Column(String(150), nullable=True)

    address = Column(Text, nullable=True)
    previous_school = Column(String(255), nullable=True)

    status = Column(String(30), default="pending")
    submitted_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------
# ATTENDANCE
# ---------------------------------------------------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    attendance_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)
    remarks = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student")


# ---------------------------------------------------------
# FEES
# ---------------------------------------------------------
class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    fee_type = Column(String(100), nullable=False)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)

    payment_status = Column(String(30), default="pending")

    due_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=True)

    receipt_number = Column(String(100), nullable=True)
    remarks = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student")


# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------
class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    exam_name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)

    marks_obtained = Column(Float, nullable=False)
    maximum_marks = Column(Float, nullable=False)

    grade = Column(String(10), nullable=True)
    remarks = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student")


# ---------------------------------------------------------
# NOTICES
# ---------------------------------------------------------
class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)

    attachment = Column(String(255), nullable=True)

    is_published = Column(Boolean, default=True)
    is_important = Column(Boolean, default=False)

    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ---------------------------------------------------------
# GALLERY
# ---------------------------------------------------------
class Gallery(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)

    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------
# CONTACT / ENQUIRY
# ---------------------------------------------------------
class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)

    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)

    status = Column(String(30), default="new")
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------
# SCHOOL SETTINGS
# ---------------------------------------------------------
class SchoolSetting(Base):
    __tablename__ = "school_settings"

    id = Column(Integer, primary_key=True, index=True)

    school_name = Column(
        String(255),
        default="CBS Sr. Sec. School"
    )
    address = Column(
        Text,
        default="Gwalior, Madhya Pradesh"
    )
    phone = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)
    website = Column(
        String(150),
        default="cbsschool.org"
    )
    principal_name = Column(String(150), nullable=True)
    logo_path = Column(String(255), nullable=True)
    academic_session = Column(String(50), nullable=True)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ---------------------------------------------------------
# DOCUMENTS
# ---------------------------------------------------------
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=True)

    is_published = Column(Boolean, default=True)
    is_important = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
