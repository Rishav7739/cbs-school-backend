import os
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import (
    AdminUser,
    Student,
    Teacher,
    Admission,
    Attendance,
    Fee,
    Result,
    Notice,
    Gallery,
    Enquiry,
    SchoolSetting,
    Document,
)
from auth import (
    hash_password,
    authenticate_admin,
    create_access_token,
    get_current_admin,
)
import schemas

load_dotenv()

# Database Setup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CBS Sr. Sec. School API",
    description="REST API backend for CBS Sr. Sec. School",
    version="2.0.0",
)

# CORS Setup
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    origins.append(FRONTEND_URL.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory configuration
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_BASE = Path("/tmp/uploads") if os.getenv("VERCEL") else BASE_DIR / "uploads"
NOTICE_UPLOAD_DIR = UPLOAD_BASE / "notices"
DOCUMENT_UPLOAD_DIR = UPLOAD_BASE / "documents"
GALLERY_UPLOAD_DIR = UPLOAD_BASE / "gallery"
STUDENT_UPLOAD_DIR = UPLOAD_BASE / "students"
TEACHER_UPLOAD_DIR = UPLOAD_BASE / "teachers"

for d in [NOTICE_UPLOAD_DIR, DOCUMENT_UPLOAD_DIR, GALLERY_UPLOAD_DIR, STUDENT_UPLOAD_DIR, TEACHER_UPLOAD_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

if UPLOAD_BASE.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_BASE)), name="uploads")


# Initialize default admin & default settings
def initialize_system():
    db = next(get_db())
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        default_pwd = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@CBS2026!")
        if not admin:
            admin = AdminUser(
                username="admin",
                email="admin@cbsschool.org",
                password_hash=hash_password(default_pwd),
                full_name="School Administrator",
                role="super_admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()

        setting = db.query(SchoolSetting).first()
        if not setting:
            setting = SchoolSetting(
                school_name="CBS Sr. Sec. School",
                address="Near City Center, Gwalior, Madhya Pradesh - 474011",
                phone="+91 98765 43210",
                email="info@cbsschool.org",
                website="https://cbsschool.org",
                principal_name="Dr. R. K. Sharma",
                academic_session="2026-2027",
            )
            db.add(setting)
            db.commit()
    except Exception as e:
        print("Initialization note:", e)
        db.rollback()
    finally:
        db.close()


initialize_system()


# =========================================================
# AUTH ENDPOINTS
# =========================================================
@app.post("/api/auth/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, login_data.username, login_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    access_token = create_access_token(data={"sub": admin.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin_info": {
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "email": admin.email,
            "role": admin.role,
        },
    }


@app.get("/api/auth/me", response_model=schemas.AdminUserOut)
def get_me(current_admin: AdminUser = Depends(get_current_admin)):
    return current_admin


# =========================================================
# PUBLIC ENDPOINTS (Website)
# =========================================================
@app.get("/api/public/settings", response_model=schemas.SchoolSettingOut)
def get_public_settings(db: Session = Depends(get_db)):
    setting = db.query(SchoolSetting).first()
    if not setting:
        return {
            "id": 1,
            "school_name": "CBS Sr. Sec. School",
            "address": "Gwalior, MP",
            "phone": "+91 98765 43210",
            "email": "info@cbsschool.org",
            "website": "cbsschool.org",
            "principal_name": "Dr. R. K. Sharma",
            "academic_session": "2026-2027",
        }
    return setting


@app.get("/api/public/notices", response_model=List[schemas.NoticeOut])
def get_public_notices(
    category: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Notice).filter(Notice.is_published == True)
    if category and category != "All":
        query = query.filter(Notice.category == category)
    return query.order_by(Notice.is_important.desc(), Notice.published_at.desc()).limit(limit).all()


@app.get("/api/public/gallery", response_model=List[schemas.GalleryOut])
def get_public_gallery(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Gallery).filter(Gallery.is_published == True)
    if category and category != "All":
        query = query.filter(Gallery.category == category)
    return query.order_by(Gallery.created_at.desc()).all()


@app.get("/api/public/documents", response_model=List[schemas.DocumentOut])
def get_public_documents(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document).filter(Document.is_published == True)
    if category and category != "All":
        query = query.filter(Document.category == category)
    return query.order_by(Document.is_important.desc(), Document.created_at.desc()).all()


@app.post("/api/public/admissions", response_model=schemas.AdmissionOut)
def submit_admission(admission_in: schemas.AdmissionCreate, db: Session = Depends(get_db)):
    new_admission = Admission(**admission_in.dict())
    db.add(new_admission)
    db.commit()
    db.refresh(new_admission)
    return new_admission


@app.post("/api/public/enquiry", response_model=schemas.EnquiryOut)
def submit_enquiry(enquiry_in: schemas.EnquiryCreate, db: Session = Depends(get_db)):
    new_enquiry = Enquiry(**enquiry_in.dict())
    db.add(new_enquiry)
    db.commit()
    db.refresh(new_enquiry)
    return new_enquiry


# =========================================================
# ADMIN: DASHBOARD STATS
# =========================================================
@app.get("/api/admin/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    total_students = db.query(Student).filter(Student.status == "active").count()
    total_teachers = db.query(Teacher).filter(Teacher.status == "active").count()
    total_admissions = db.query(Admission).count()
    pending_admissions = db.query(Admission).filter(Admission.status == "pending").count()
    total_enquiries = db.query(Enquiry).count()
    new_enquiries = db.query(Enquiry).filter(Enquiry.status == "new").count()
    total_notices = db.query(Notice).count()

    recent_admissions = db.query(Admission).order_by(Admission.submitted_at.desc()).limit(5).all()
    recent_enquiries = db.query(Enquiry).order_by(Enquiry.created_at.desc()).limit(5).all()

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_admissions": total_admissions,
        "pending_admissions": pending_admissions,
        "total_enquiries": total_enquiries,
        "new_enquiries": new_enquiries,
        "total_notices": total_notices,
        "recent_admissions": recent_admissions,
        "recent_enquiries": recent_enquiries,
    }


# =========================================================
# ADMIN: STUDENTS
# =========================================================
@app.get("/api/admin/students", response_model=List[schemas.StudentOut])
def list_students(
    search: Optional[str] = None,
    class_name: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    q = db.query(Student)
    if search:
        term = f"%{search}%"
        q = q.filter((Student.first_name.ilike(term)) | (Student.admission_no.ilike(term)) | (Student.phone.ilike(term)))
    if class_name and class_name != "All":
        q = q.filter(Student.class_name == class_name)
    return q.order_by(Student.created_at.desc()).all()


@app.post("/api/admin/students", response_model=schemas.StudentOut)
def create_student(
    student_in: schemas.StudentCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    exists = db.query(Student).filter(Student.admission_no == student_in.admission_no).first()
    if exists:
        raise HTTPException(status_code=400, detail="Admission number already exists")
    student = Student(**student_in.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@app.put("/api/admin/students/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int,
    student_in: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    for field, val in student_in.dict(exclude_unset=True).items():
        setattr(student, field, val)
    db.commit()
    db.refresh(student)
    return student


@app.delete("/api/admin/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


# =========================================================
# ADMIN: TEACHERS
# =========================================================
@app.get("/api/admin/teachers", response_model=List[schemas.TeacherOut])
def list_teachers(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    q = db.query(Teacher)
    if search:
        term = f"%{search}%"
        q = q.filter((Teacher.first_name.ilike(term)) | (Teacher.employee_id.ilike(term)) | (Teacher.subject.ilike(term)))
    return q.order_by(Teacher.created_at.desc()).all()


@app.post("/api/admin/teachers", response_model=schemas.TeacherOut)
def create_teacher(
    teacher_in: schemas.TeacherCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    exists = db.query(Teacher).filter(Teacher.employee_id == teacher_in.employee_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    teacher = Teacher(**teacher_in.dict())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@app.put("/api/admin/teachers/{teacher_id}", response_model=schemas.TeacherOut)
def update_teacher(
    teacher_id: int,
    teacher_in: schemas.TeacherUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    for field, val in teacher_in.dict(exclude_unset=True).items():
        setattr(teacher, field, val)
    db.commit()
    db.refresh(teacher)
    return teacher


@app.delete("/api/admin/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted successfully"}


# =========================================================
# ADMIN: ADMISSIONS
# =========================================================
@app.get("/api/admin/admissions", response_model=List[schemas.AdmissionOut])
def list_admissions(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    q = db.query(Admission)
    if status and status != "All":
        q = q.filter(Admission.status == status)
    return q.order_by(Admission.submitted_at.desc()).all()


@app.patch("/api/admin/admissions/{admission_id}/status", response_model=schemas.AdmissionOut)
def update_admission_status(
    admission_id: int,
    status_update: schemas.AdmissionStatusUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    admission = db.query(Admission).filter(Admission.id == admission_id).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission record not found")
    admission.status = status_update.status
    db.commit()
    db.refresh(admission)
    return admission


# =========================================================
# ADMIN: ATTENDANCE
# =========================================================
@app.get("/api/admin/attendance", response_model=List[schemas.AttendanceOut])
def get_attendance(
    attendance_date: Optional[date] = None,
    class_name: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    target_date = attendance_date or date.today()
    q = db.query(Attendance).join(Student).filter(Attendance.attendance_date == target_date)
    if class_name and class_name != "All":
        q = q.filter(Student.class_name == class_name)
    return q.all()


@app.post("/api/admin/attendance/batch")
def save_batch_attendance(
    batch: schemas.AttendanceBatchCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    for rec in batch.records:
        student_id = rec.get("student_id")
        status_val = rec.get("status", "present")
        remarks = rec.get("remarks", "")
        existing = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.attendance_date == batch.attendance_date
        ).first()
        if existing:
            existing.status = status_val
            existing.remarks = remarks
        else:
            new_att = Attendance(
                student_id=student_id,
                attendance_date=batch.attendance_date,
                status=status_val,
                remarks=remarks,
            )
            db.add(new_att)
    db.commit()
    return {"message": "Attendance records saved successfully"}


# =========================================================
# ADMIN: FEES
# =========================================================
@app.get("/api/admin/fees", response_model=List[schemas.FeeOut])
def list_fees(
    payment_status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    q = db.query(Fee).join(Student)
    if payment_status and payment_status != "All":
        q = q.filter(Fee.payment_status == payment_status)
    return q.order_by(Fee.created_at.desc()).all()


@app.post("/api/admin/fees", response_model=schemas.FeeOut)
def record_fee(
    fee_in: schemas.FeeCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    fee = Fee(**fee_in.dict())
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee


@app.patch("/api/admin/fees/{fee_id}", response_model=schemas.FeeOut)
def update_fee(
    fee_id: int,
    fee_in: schemas.FeeUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    for field, val in fee_in.dict(exclude_unset=True).items():
        setattr(fee, field, val)
    db.commit()
    db.refresh(fee)
    return fee


# =========================================================
# ADMIN: RESULTS
# =========================================================
@app.get("/api/admin/results", response_model=List[schemas.ResultOut])
def list_results(
    exam_name: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    q = db.query(Result).join(Student)
    if exam_name and exam_name != "All":
        q = q.filter(Result.exam_name == exam_name)
    return q.order_by(Result.created_at.desc()).all()


@app.post("/api/admin/results", response_model=schemas.ResultOut)
def create_result(
    result_in: schemas.ResultCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    result = Result(**result_in.dict())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


# =========================================================
# ADMIN: NOTICES
# =========================================================
@app.get("/api/admin/notices", response_model=List[schemas.NoticeOut])
def list_admin_notices(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    return db.query(Notice).order_by(Notice.created_at.desc()).all()


@app.post("/api/admin/notices", response_model=schemas.NoticeOut)
async def create_notice(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("General"),
    is_published: bool = Form(True),
    is_important: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    attachment_path = None
    if file and file.filename:
        ext = Path(file.filename).suffix.lower()
        filename = f"{uuid4().hex}{ext}"
        dest = NOTICE_UPLOAD_DIR / filename
        data = await file.read()
        with open(dest, "wb") as f:
            f.write(data)
        attachment_path = f"/uploads/notices/{filename}"

    notice = Notice(
        title=title,
        content=content,
        category=category,
        is_published=is_published,
        is_important=is_important,
        attachment=attachment_path,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice


@app.delete("/api/admin/notices/{notice_id}")
def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    db.delete(notice)
    db.commit()
    return {"message": "Notice deleted"}


# =========================================================
# ADMIN: GALLERY
# =========================================================
@app.post("/api/admin/gallery", response_model=schemas.GalleryOut)
async def upload_gallery_image(
    title: str = Form(...),
    category: str = Form("Campus"),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid4().hex}{ext}"
    dest = GALLERY_UPLOAD_DIR / filename
    data = await file.read()
    with open(dest, "wb") as f:
        f.write(data)

    item = Gallery(
        title=title,
        description=description,
        category=category,
        image_path=f"/uploads/gallery/{filename}",
        is_published=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/admin/gallery/{item_id}")
def delete_gallery_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    item = db.query(Gallery).filter(Gallery.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    db.delete(item)
    db.commit()
    return {"message": "Gallery item deleted"}


# =========================================================
# ADMIN: DOCUMENTS
# =========================================================
@app.post("/api/admin/documents", response_model=schemas.DocumentOut)
async def upload_document(
    title: str = Form(...),
    category: str = Form("Academic"),
    description: Optional[str] = Form(None),
    is_important: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid4().hex}{ext}"
    dest = DOCUMENT_UPLOAD_DIR / filename
    data = await file.read()
    with open(dest, "wb") as f:
        f.write(data)

    doc = Document(
        title=title,
        description=description,
        category=category,
        file_path=f"/uploads/documents/{filename}",
        file_type=ext.lstrip("."),
        is_published=True,
        is_important=is_important,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@app.delete("/api/admin/documents/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}


# =========================================================
# ADMIN: ENQUIRIES
# =========================================================
@app.get("/api/admin/enquiries", response_model=List[schemas.EnquiryOut])
def list_enquiries(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    q = db.query(Enquiry)
    if status and status != "All":
        q = q.filter(Enquiry.status == status)
    return q.order_by(Enquiry.created_at.desc()).all()


@app.patch("/api/admin/enquiries/{enquiry_id}/status", response_model=schemas.EnquiryOut)
def update_enquiry_status(
    enquiry_id: int,
    status_update: schemas.EnquiryStatusUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    enquiry.status = status_update.status
    db.commit()
    db.refresh(enquiry)
    return enquiry


# =========================================================
# ADMIN: SETTINGS
# =========================================================
@app.put("/api/admin/settings", response_model=schemas.SchoolSettingOut)
def update_school_settings(
    settings_in: schemas.SchoolSettingUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    setting = db.query(SchoolSetting).first()
    if not setting:
        setting = SchoolSetting()
        db.add(setting)
    for field, val in settings_in.dict(exclude_unset=True).items():
        setattr(setting, field, val)
    db.commit()
    db.refresh(setting)
    return setting


@app.get("/")
def api_root():
    return {
        "school": "CBS Sr. Sec. School",
        "api_version": "2.0.0",
        "status": "Online",
        "docs": "/docs",
    }
