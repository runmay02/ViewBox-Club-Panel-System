import csv, io
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.core.permissions import require_role
from app.models.user import RoleEnum
from app.models.member import MemberProfile
from app.models.survey import Survey
from app.models.referral import Referral
from app.models.payout import Payout
from app.models.source import AcquisitionSource
from app.models.participation import SurveyParticipation

router = APIRouter(prefix="/admin", tags=["Administration"])
admin = [Depends(require_role([RoleEnum.ADMIN.value]))]
staff = [Depends(require_role([RoleEnum.ADMIN.value, RoleEnum.OPERATIONS.value]))]

@router.get("/respondents", dependencies=staff)
def respondents(search: str = "", city: str = "", source: str = "", page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    q = db.query(MemberProfile).outerjoin(AcquisitionSource)
    if search:
        term=f"%{search}%"
        q=q.filter((MemberProfile.full_name.ilike(term))|(MemberProfile.member_id.ilike(term))|(MemberProfile.city.ilike(term))|(MemberProfile.phone.ilike(term)))
    if city: q=q.filter(MemberProfile.city == city)
    if source: q=q.filter(AcquisitionSource.name == source)
    total=q.count(); rows=q.order_by(MemberProfile.joined_on.desc()).offset((page-1)*page_size).limit(min(page_size,100)).all()
    return {"items":[{"id":m.id,"member_id":m.member_id,"name":m.full_name,"phone":m.phone,"email":m.email,"gender":m.gender,"date_of_birth":m.date_of_birth,"city":m.city,"income_range":m.income_range,"interests":m.interests.split(";") if m.interests else [],"source":m.acquisition_source.name if m.acquisition_source else "Website","referred_by":m.referral_received.referrer.member_id if m.referral_received else None,"joined_on":m.joined_on,"status":"ACTIVE"} for m in rows],"total":total,"page":page,"page_size":page_size,"cities":[r[0] for r in db.query(MemberProfile.city).distinct().all()],"sources":[r[0] for r in db.query(AcquisitionSource.name).distinct().all()]}

@router.get("/respondents/export", dependencies=staff)
def export_respondents(search: str = "", city: str = "", source: str = "", format: str = "csv", db: Session = Depends(get_db)):
    if format not in ("csv", "xlsx"): raise HTTPException(422,"format must be csv or xlsx")
    q=db.query(MemberProfile).outerjoin(AcquisitionSource)
    if search:
        term=f"%{search}%";q=q.filter((MemberProfile.full_name.ilike(term))|(MemberProfile.member_id.ilike(term))|(MemberProfile.city.ilike(term))|(MemberProfile.phone.ilike(term)))
    if city:q=q.filter(MemberProfile.city==city)
    if source:q=q.filter(AcquisitionSource.name==source)
    rows=q.order_by(MemberProfile.joined_on.desc()).all()
    headers=["member_id","name","phone","email","gender","date_of_birth","city","income_range","interests","source","joined_on"]
    values=[[m.member_id,m.full_name,m.phone,m.email or "",m.gender,m.date_of_birth,m.city,m.income_range,m.interests,m.acquisition_source.name if m.acquisition_source else "Website",m.joined_on] for m in rows]
    if format=="csv":
        output=io.StringIO();writer=csv.writer(output);writer.writerow(headers);writer.writerows(values)
        return Response(output.getvalue(),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=respondents.csv"})
    from openpyxl import Workbook
    from openpyxl.styles import Font
    output=io.BytesIO();workbook=Workbook();sheet=workbook.active;sheet.title="Respondents";sheet.append(headers)
    for cell in sheet[1]: cell.font=Font(bold=True)
    for row in values: sheet.append([str(x) if isinstance(x,date) else x for x in row])
    workbook.save(output);output.seek(0)
    return Response(output.getvalue(),media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=respondents.xlsx"})

@router.get("/kpis", dependencies=admin)
def kpis(db: Session = Depends(get_db)):
    total=db.query(MemberProfile).count(); active=db.query(Survey).filter_by(status="ACTIVE").count(); referrals=db.query(Referral).count(); completed=db.query(Referral).filter_by(stage="COMPLETED").count()
    paid=float(db.query(func.sum(Payout.amount)).filter_by(status="PAID").scalar() or 0)
    weekly=db.query(MemberProfile).filter(MemberProfile.joined_on >= date.today()-timedelta(days=7)).count()
    daily=[]
    for offset in range(6,-1,-1):
        day=date.today()-timedelta(days=offset); daily.append({"date":day.strftime("%d %b"),"signups":db.query(MemberProfile).filter_by(joined_on=day).count()})
    sources=db.query(AcquisitionSource).all(); dist=[{"name":s.name,"count":db.query(MemberProfile).filter_by(acquisition_source_id=s.id).count()} for s in sources]
    return {"total_respondents":total,"new_signups_7d":weekly,"active_surveys":active,"completed_surveys":db.query(SurveyParticipation).filter_by(status="COMPLETED").count(),"total_referrals":referrals,"successful_referrals":completed,"pending_ops_tasks":db.query(Referral).filter(Referral.stage.in_(["LEAD","FIT"])).count()+db.query(Payout).filter_by(status="PENDING_APPROVAL").count(),"total_payouts_disbursed":paid,"signup_trend":daily,"source_distribution":dist,"referral_funnel":[{"stage":"Leads (Signups)","count":referrals},{"stage":"Fit Verified","count":db.query(Referral).filter(Referral.stage.in_(["FIT","COMPLETED"])).count()},{"stage":"Completed & Quality Passed","count":completed}]}

@router.get("/analytics/sources", dependencies=admin)
def source_analytics(db: Session=Depends(get_db)):
    from app.services.attribution_service import AttributionService
    return [x.model_dump() for x in AttributionService(db).get_source_performance()]
