import time
import uuid
from fastapi import APIRouter
from backend.app.schemas.incident import IncidentReport, IncidentResponse
from backend.app.core.logging import logger

router = APIRouter()

_INCIDENTS_STORE = []


@router.post("/report", response_model=IncidentResponse, summary="Report/Inject Traffic Incident")
async def report_incident(report: IncidentReport):
    inc_id = f"inc_{str(uuid.uuid4())[:8]}"
    item = {
        "incident_id": inc_id,
        "incident_type": report.incident_type,
        "edge_id": report.edge_id,
        "severity": report.severity,
        "status": "active",
        "rerouting_triggered": report.severity >= 3,
        "created_at_s": time.time()
    }
    _INCIDENTS_STORE.append(item)
    logger.info(f"Incident reported: {report.incident_type} on {report.edge_id} (severity {report.severity})")
    return IncidentResponse(**item)


@router.get("/active", summary="List Active Incidents")
async def list_active_incidents():
    return [i for i in _INCIDENTS_STORE if i["status"] == "active"]
