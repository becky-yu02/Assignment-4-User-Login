from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status, Depends

from models.reservation import Reservation, ReservationRequest

from auth.authenticate import authenticate

reservation_router = APIRouter()


@reservation_router.get("")
async def get_all_reservations(user=Depends(authenticate)):
    return await Reservation.find_all().to_list()


@reservation_router.post("", status_code=201)
async def create_new_reservation(reservation: ReservationRequest, user=Depends(authenticate)) -> Reservation:
    # Check for nonsensical time slots
    if reservation.start_time >= reservation.end_time:
        raise HTTPException(
            status_code=400, detail="Start time must be before end time."
        )
    # Check for overlapping reservations
    existing_reservations = await Reservation.find(
        Reservation.room_number == reservation.room_number
    ).to_list()

    for existing in existing_reservations:
        if (
            reservation.start_time < existing.end_time
            and reservation.end_time > existing.start_time
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot make this reservation. Please check room and time availabilities and try again.",
            )

    new_reservation = Reservation(**reservation.model_dump())
    await new_reservation.insert()

    return new_reservation


@reservation_router.put("/{id}")
async def edit_reservation_by_id(id: str, reservation: ReservationRequest, user=Depends(authenticate)):

    existing = await Reservation.get(id)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Item with ID={id} is not found.")

    if reservation.start_time >= reservation.end_time:
        raise HTTPException(
            status_code=400, detail="Start time must be before end time."
        )

    current_reservations = await Reservation.find(
        Reservation.room_number == reservation.room_number,
        Reservation.id != existing.id,
    ).to_list()

    for current in current_reservations:
        if (
            reservation.start_time < current.end_time
            and reservation.end_time > current.start_time
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot make this reservation. Please check room and time availabilities and try again.",
            )

    existing.start_time = reservation.start_time
    existing.end_time = reservation.end_time
    existing.room_number = reservation.room_number
    existing.name = reservation.name
    existing.desc = reservation.desc

    await existing.save()

    return existing


@reservation_router.get("/{id}")
async def get_reservation_by_id(id: str, user=Depends(authenticate)):
    reservation = await Reservation.get(id)

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Item with ID={id} is not found.")

    return reservation


@reservation_router.delete("/{id}")
async def delete_reservation_by_id(id: str, user=Depends(authenticate)):
    reservation = await Reservation.get(id)

    if reservation:
        await reservation.delete()
        return {
            "message": "Reservation has been deleted.",
            "reservation": reservation,
        }

    raise HTTPException(
        status_code=404, detail=f"Reservation with ID={id} was not found."
    )
