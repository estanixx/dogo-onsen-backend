from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Service, ServiceCreate, ServiceUpdate, ItemIntake, Item, InventoryOrder, Reservation
from app.services import ServiceService
from fastapi import Query

ServiceRouter = APIRouter()


@ServiceRouter.get("/", response_model=list[Service])
async def list_services(session: AsyncSession = Depends(get_session), q: str = Query(None)):
    return await ServiceService.list_services(session, q)


@ServiceRouter.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate, session: AsyncSession = Depends(get_session)
):
    return await ServiceService.create_service(service, session)


@ServiceRouter.get("/{service_id}/available_time_slots", response_model=list[str])
async def available_time_slots(
    service_id: str,
    date: str = Query(..., description="Date (YYYY-MM-DD) or ISO datetime"),
    session: AsyncSession = Depends(get_session),
):
    try:
        slots = await ServiceService.get_available_time_slots(service_id, date, session)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format"
        )
    return slots


@ServiceRouter.get("/{service_id}/check-availability")
async def check_service_availability(
    service_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Check if a service has sufficient inventory to fulfill a reservation.
    Returns availability status and details about any insufficient items.
    """
    # Verify service exists
    svc = await ServiceService.get_service(service_id, session)
    if not svc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )

    # Get all items required for this service
    stmt = select(ItemIntake).where(ItemIntake.serviceId == service_id)
    result = await session.execute(stmt)
    intakes = result.scalars().all()

    insufficient_items = []

    for intake in intakes:
        try:
            # Get the item
            item_stmt = select(Item).where(Item.id == intake.itemId)
            item_result = await session.execute(item_stmt)
            item = item_result.scalars().first()

            if not item:
                insufficient_items.append({
                    "itemId": intake.itemId,
                    "itemName": f"Unknown Item {intake.itemId}",
                    "requiredQuantity": intake.quantity,
                    "availableQuantity": 0,
                })
                continue

            # Calculate quantity directly from database queries (avoiding lazy loading)
            # Formula: sum(inventory_order.quantity WHERE redeemed=True) - sum(item_intake.quantity WHERE serviceId=this_service)
            # We only subtract intakes for THIS service multiplied by its reservation count.
            # Banquet seat intakes (seatId-based) are not subtracted here.
            
            # Get sum of redeemed inventory orders
            order_stmt = (
                select(func.coalesce(func.sum(InventoryOrder.quantity), 0))
                .where(
                    (InventoryOrder.idItem == intake.itemId) &
                    (InventoryOrder.redeemed == True)
                )
            )
            order_result = await session.execute(order_stmt)
            ordered_qty = order_result.scalar() or 0
            
            # Get sum of intakes for THIS service only
            service_intake_stmt = (
                select(func.coalesce(func.sum(ItemIntake.quantity), 0))
                .where(
                    (ItemIntake.itemId == intake.itemId) &
                    (ItemIntake.serviceId == service_id)
                )
            )
            service_intake_result = await session.execute(service_intake_stmt)
            intake_qty_per_reservation = service_intake_result.scalar() or 0
            
            # Get number of reservations for this service
            reservation_stmt = (
                select(func.count(Reservation.id))
                .where(Reservation.serviceId == service_id)
            )
            reservation_result = await session.execute(reservation_stmt)
            num_reservations = reservation_result.scalar() or 0
            
            # Total consumed = intake_qty * number_of_reservations
            consumed_qty = intake_qty_per_reservation * num_reservations
            
            available_qty = ordered_qty - consumed_qty
            
            if available_qty < intake.quantity:
                insufficient_items.append({
                    "itemId": intake.itemId,
                    "itemName": item.name,
                    "requiredQuantity": intake.quantity,
                    "availableQuantity": available_qty,
                })
            else:
                pass
        except Exception as e:
            insufficient_items.append({
                "itemId": intake.itemId,
                "itemName": f"Item {intake.itemId}",
                "requiredQuantity": intake.quantity,
                "availableQuantity": 0,
            })

    is_available = len(insufficient_items) == 0
    message = (
        "All items are in stock" if is_available
        else f"{len(insufficient_items)} item(s) have insufficient stock"
    )

    return {
        "isAvailable": is_available,
        "insufficientItems": insufficient_items,
        "message": message,
    }


@ServiceRouter.get("/{service_id}", response_model=Service)
async def get_service(service_id: str, session: AsyncSession = Depends(get_session)):
    svc = await ServiceService.get_service(service_id, session)
    if not svc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return svc


@ServiceRouter.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: str,
    service: ServiceUpdate,
    session: AsyncSession = Depends(get_session),
):
    svc = await ServiceService.update_service(service_id, service, session)
    if not svc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return svc


@ServiceRouter.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: str, session: AsyncSession = Depends(get_session)):
    ok = await ServiceService.delete_service(service_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return None
