## estanix
[ ] Add rationsConsumed to banquet seat and service
[ ] Add occupies to banquet table
[ ] Validate endtime > starttime in reservation
[ ] Rating in reservation
[ ] `getAvailableServices(query?: string)` add query to function to get available services
[ ] Function to get available time slots for a service on a specific date `getAvailableTimeSlots(serviceId: string, date: Date)`
[ ] Function to book a service for a venue account at a specific date and time:
```
bookService(
  serviceId: string,
  accountId: string,
  date: Date,
  time: string,
)
```
[ ] `getBanquetReservationsForDate(date: string)`
[ ] `createBanquetReservation({tableId, seatNumber, date, time, accountId}`
[ ] Display availableSeats and rationsconsumed `getBanquetTables()`
[ ] `getReservations({serviceId, date, timeSlot})`
[ ] Agregar estos timeslots universales `['09:00 AM', '10:00 AM', '11:00 AM', '01:00 PM', '03:00 PM', '05:00 PM'];`

## samuelColorado
[ ] Add venueaccount relationship to reservation

## juanpa
[ ] 👍👍👍😎🥶🥶