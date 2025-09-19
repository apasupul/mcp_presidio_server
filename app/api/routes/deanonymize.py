from fastapi import APIRouter, HTTPException
from ...models.schemas import DeanonymizeRequest, DeanonymizeResponse
from ...services.anonymization import ensure_union_input, deanonymize_text, split_back

router = APIRouter()

@router.post("/deanonymize", response_model=DeanonymizeResponse)
async def api_deanonymize(req: DeanonymizeRequest):
    try:
        joined, msgs, is_msgs = ensure_union_input(req.text, req.messages)
        if req.reverse_map:
            rmap = req.reverse_map
        elif req.entity_map:
            rmap = {v: k for ent in req.entity_map.values() for k, v in ent.items()}
        else:
            raise HTTPException(status_code=400, detail="Provide reverse_map or entity_map")

        dean = deanonymize_text(joined, rmap)
        if is_msgs and msgs is not None:
            return DeanonymizeResponse(session_id=req.session_id, messages=split_back(dean, msgs))
        else:
            return DeanonymizeResponse(session_id=req.session_id, text=dean)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
