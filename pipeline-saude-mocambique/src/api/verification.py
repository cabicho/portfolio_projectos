from fastapi import APIRouter
from src.verify.data_sources_verification import DataSourcesVerification

router = APIRouter()

@router.get("/verify/sources")
async def verify_data_sources():
    verifier = DataSourcesVerification()
    return await verifier.verify_all_sources()

@router.get("/verify/status")
async def get_data_sources_status():
    verifier = DataSourcesVerification()
    report = await verifier.verify_all_sources()
    return {
        "overall_status": report['summary']['overall_status'],
        "active_sources": report['summary']['active_sources'],
        "total_sources": report['summary']['total_sources'],
        "total_records": report['summary']['total_records']
    }
