from fastapi import APIRouter, HTTPException
from ...models.schemas import AnonymizeRequest, AnonymizeResponse
from ...services.anonymization import ensure_union_input, anonymize_text, split_back

router = APIRouter()

@router.post("/anonymize", response_model=AnonymizeResponse)
async def api_anonymize(req: AnonymizeRequest):
    try:
        joined, msgs, is_msgs = ensure_union_input(req.text, req.messages)
        anonymized, entity_map, reverse_map = anonymize_text(req.session_id, joined, req.language)
        if is_msgs and msgs is not None:
            return AnonymizeResponse(
                session_id=req.session_id,
                messages=split_back(anonymized, msgs),
                entity_map=entity_map,
                reverse_map=reverse_map,
            )
        else:
            return AnonymizeResponse(
                session_id=req.session_id,
                text=anonymized,
                entity_map=entity_map,
                reverse_map=reverse_map,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
