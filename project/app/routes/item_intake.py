from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import ItemIntake, ItemIntakeCreate
from app.services import ItemIntakeService

ItemIntakeRouter = APIRouter()


@ItemIntakeRouter.get("/", response_model=list[ItemIntake])
async def list_item_intakes(session: AsyncSession = Depends(get_session)):
    return await ItemIntakeService.list_item_intakes(session)


@ItemIntakeRouter.post(
    "/", response_model=ItemIntake, status_code=status.HTTP_201_CREATED
)
async def create_item_intake(
    item_intake: ItemIntakeCreate, session: AsyncSession = Depends(get_session)
):
    try:
        return await ItemIntakeService.create_item_intake(item_intake, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@ItemIntakeRouter.get("/{intake_id}", response_model=ItemIntake)
async def get_item_intake(intake_id: int, session: AsyncSession = Depends(get_session)):
    intake = await ItemIntakeService.get_item_intake(intake_id, session)
    if not intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ItemIntake not found"
        )
    return intake


@ItemIntakeRouter.delete("/{intake_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_intake(
    intake_id: int, session: AsyncSession = Depends(get_session)
):
    ok = await ItemIntakeService.delete_item_intake(intake_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ItemIntake not found"
        )
    return None
