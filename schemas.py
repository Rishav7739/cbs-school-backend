from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str
    admin_info: dict


class LoginRequest(BaseModel):
    username: str
    password: str


class AdminUserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# Student
class StudentBase(BaseModel):
    admission_no: str
    roll_no: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    class_name: Optional[str] = None
    section: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = "active"


class StudentCreate(StudentBase):
    admission_date: Optional[date] = None


class StudentUpdate(BaseModel):
    roll_no: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    class_name: Optional[str] = None
    section: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None


class StudentOut(StudentBase):
    id: int
    photo: Optional[str] = None
    admission_date: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Teacher
class TeacherBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    subject: Optional[str] = None
    designation: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = "active"


class TeacherCreate(TeacherBase):
    joining_date: Optional[date] = None


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    subject: Optional[str] = None
    designation: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None


class TeacherOut(TeacherBase):
    id: int
    photo: Optional[str] = None
    joining_date: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Admission
class AdmissionCreate(BaseModel):
    student_name: str
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    applying_class: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    previous_school: Optional[str] = None


class AdmissionStatusUpdate(BaseModel):
    status: str  # pending, approved, rejected


class AdmissionOut(AdmissionCreate):
    id: int
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True


# Attendance
class AttendanceCreate(BaseModel):
    student_id: int
    attendance_date: date
    status: str  # present, absent, late, leave
    remarks: Optional[str] = None


class AttendanceBatchCreate(BaseModel):
    attendance_date: date
    records: List[dict]  # [{"student_id": 1, "status": "present", "remarks": ""}]


class AttendanceOut(AttendanceCreate):
    id: int
    created_at: Optional[datetime] = None
    student: Optional[StudentOut] = None

    class Config:
        from_attributes = True


# Fee
class FeeCreate(BaseModel):
    student_id: int
    fee_type: str
    total_amount: float
    paid_amount: float = 0.0
    payment_status: str = "pending"
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    receipt_number: Optional[str] = None
    remarks: Optional[str] = None


class FeeUpdate(BaseModel):
    paid_amount: Optional[float] = None
    payment_status: Optional[str] = None
    payment_date: Optional[date] = None
    receipt_number: Optional[str] = None
    remarks: Optional[str] = None


class FeeOut(FeeCreate):
    id: int
    created_at: Optional[datetime] = None
    student: Optional[StudentOut] = None

    class Config:
        from_attributes = True


# Result
class ResultCreate(BaseModel):
    student_id: int
    exam_name: str
    subject: str
    marks_obtained: float
    maximum_marks: float
    grade: Optional[str] = None
    remarks: Optional[str] = None


class ResultOut(ResultCreate):
    id: int
    created_at: Optional[datetime] = None
    student: Optional[StudentOut] = None

    class Config:
        from_attributes = True


# Notice
class NoticeCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = "General"
    is_published: bool = True
    is_important: bool = False


class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_published: Optional[bool] = None
    is_important: Optional[bool] = None


class NoticeOut(NoticeCreate):
    id: int
    attachment: Optional[str] = None
    published_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Gallery
class GalleryOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_path: str
    category: Optional[str] = None
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Document
class DocumentOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    file_path: str
    file_type: Optional[str] = None
    is_published: bool
    is_important: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Enquiry
class EnquiryCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: str


class EnquiryStatusUpdate(BaseModel):
    status: str  # new, contacted, resolved, closed


class EnquiryOut(EnquiryCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# School Settings
class SchoolSettingUpdate(BaseModel):
    school_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    principal_name: Optional[str] = None
    academic_session: Optional[str] = None


class SchoolSettingOut(BaseModel):
    id: int
    school_name: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    principal_name: Optional[str] = None
    logo_path: Optional[str] = None
    academic_session: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Dashboard Stats
class DashboardStats(BaseModel):
    total_students: int
    total_teachers: int
    total_admissions: int
    pending_admissions: int
    total_enquiries: int
    new_enquiries: int
    total_notices: int
    recent_admissions: List[AdmissionOut]
    recent_enquiries: List[EnquiryOut]
