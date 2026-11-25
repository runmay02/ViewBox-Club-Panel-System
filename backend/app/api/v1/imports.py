import csv, io, json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.permissions import require_role
from app.models.user import RoleEnum, User
from app.models.member import MemberProfile
from app.models.import_job import ImportJob, ImportRowError
from app.models.source import AcquisitionSource
from app.utils.normalizer import normalize_phone, normalize_city, normalize_gender, parse_date, normalize_source, normalize_income_range, calculate_age

router=APIRouter(prefix="/admin/imports",tags=["CSV Imports"])
admin=Depends(require_role([RoleEnum.ADMIN.value]))
MAX_UPLOAD_BYTES=10*1024*1024

@router.post("/upload")
async def upload_csv(file:UploadFile=File(...), db:Session=Depends(get_db), user:User=admin):
    if not file.filename or not file.filename.lower().endswith(".csv"): raise HTTPException(415,"Upload a .csv file")
    try: contents=await file.read(MAX_UPLOAD_BYTES+1)
    except Exception: raise HTTPException(400,"Unable to read uploaded CSV")
    if len(contents)>MAX_UPLOAD_BYTES: raise HTTPException(413,"CSV files must be 10 MB or smaller")
    try: text=contents.decode("utf-8-sig")
    except UnicodeDecodeError: raise HTTPException(400,"CSV must use UTF-8 encoding")
    reader=csv.DictReader(io.StringIO(text),strict=True)
    if not reader.fieldnames: raise HTTPException(400,"CSV header row is required")
    headers={str(h or "").strip().lower().replace(" ","_") for h in reader.fieldnames}
    if not ({"full_name","name"}&headers) or not ({"phone","mobile"}&headers):
        raise HTTPException(422,"CSV must include name/full_name and phone/mobile columns")
    job=ImportJob(file_name=file.filename,created_by_user_id=user.id,status="IN_PROGRESS"); db.add(job); db.flush()
    valid=imported=skipped=errors=0
    row_num=1
    try:
        for row_num,raw in enumerate(reader,start=2):
            job.total_rows+=1
            row={str(k or "").strip().lower().replace(" ","_"): (v or "").strip() for k,v in raw.items() if k is not None}
            phone=normalize_phone(row.get("phone") or row.get("mobile")); name=" ".join((row.get("full_name") or row.get("name") or "").split()); dob=parse_date(row.get("date_of_birth") or row.get("dob")); city=normalize_city(row.get("city")); gender=normalize_gender(row.get("gender")); income=normalize_income_range(row.get("income_range") or row.get("income"))
            invalid=[k for k,v in [("phone",phone),("full_name",name if len(name)>=2 else None),("date_of_birth",dob),("city",city),("gender",gender),("income_range",income)] if not v]
            if dob and (dob>datetime.now().date() or calculate_age(dob)<13): invalid.append("date_of_birth")
            if invalid:
                errors+=1; db.add(ImportRowError(job_id=job.id,row_number=row_num,raw_phone=row.get("phone") or row.get("mobile"),error_column=invalid[0],error_reason="Invalid or missing: "+", ".join(dict.fromkeys(invalid)),raw_data=json.dumps(raw))); continue
            valid+=1
            raw_member_id=row.get("member_id")
            duplicate=db.query(MemberProfile).filter((MemberProfile.phone==phone) | (MemberProfile.member_id==raw_member_id if raw_member_id else False)).first()
            if duplicate:
                skipped+=1;errors+=1;db.add(ImportRowError(job_id=job.id,row_number=row_num,raw_member_id=raw_member_id,raw_phone=phone,error_column="phone",error_reason=f"Duplicate respondent; existing member {duplicate.member_id} was preserved",raw_data=json.dumps(raw)));continue
            from app.models.user import User as UserModel
            account=db.query(UserModel).filter_by(phone=phone).first()
            if not account:
                from app.core.security import get_hash
                account=UserModel(phone=phone,role="RESPONDENT",is_active=True,hashed_otp=get_hash("123456"));db.add(account);db.flush()
            source_name=normalize_source(row.get("source"));source=db.query(AcquisitionSource).filter_by(name=source_name,is_active=True).first() or db.query(AcquisitionSource).filter_by(name="Website").first()
            member_id=raw_member_id or f"VB{10001+(db.query(MemberProfile).count())}"
            profile=MemberProfile(member_id=member_id,user_id=account.id,full_name=name,phone=phone,email=row.get("email") or None,gender=gender,date_of_birth=dob,city=city,income_range=income,interests=";".join(x.strip() for x in (row.get("interests") or "").split(";") if x.strip()),acquisition_source_id=source.id if source else None)
            db.add(profile);db.flush();imported+=1
    except csv.Error as exc:
        errors+=1
        db.add(ImportRowError(job_id=job.id,row_number=row_num+1,error_reason=f"Malformed CSV row: {exc}"))
    job.valid_rows=valid; job.imported_rows=imported; job.skipped_rows=skipped; job.error_count=errors; job.status="COMPLETED"; job.completed_at=datetime.now(timezone.utc); db.commit(); db.refresh(job)
    return {"id":job.id,"file_name":job.file_name,"total_rows":job.total_rows,"valid_rows":valid,"imported_rows":imported,"skipped_rows":skipped,"error_count":errors,"status":job.status,"errors":[{"row_number":e.row_number,"column":e.error_column,"reason":e.error_reason} for e in job.errors]}

@router.get("")
def list_imports(db:Session=Depends(get_db), user:User=admin):
    return [{"id":j.id,"file_name":j.file_name,"total_rows":j.total_rows,"valid_rows":j.valid_rows,"imported_rows":j.imported_rows,"skipped_rows":j.skipped_rows,"error_count":j.error_count,"status":j.status,"created_at":j.created_at} for j in db.query(ImportJob).order_by(ImportJob.created_at.desc()).all()]

@router.get("/{job_id}/report")
def import_error_report(job_id:str, db:Session=Depends(get_db), user:User=admin):
    import io
    from fastapi.responses import StreamingResponse
    job=db.query(ImportJob).filter_by(id=job_id).first()
    if not job: raise HTTPException(404,"Import job not found")
    output=io.StringIO();writer=csv.writer(output);writer.writerow(["row_number","member_id","phone","column","reason"])
    for error in job.errors: writer.writerow([error.row_number,error.raw_member_id or "",error.raw_phone or "",error.error_column or "",error.error_reason])
    return StreamingResponse(iter([output.getvalue()]),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="import-{job.id}-errors.csv"'})
