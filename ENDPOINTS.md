## Employee API

| Method | Path                   | Description                         |
|--------|------------------------|-------------------------------------|
| GET    | `/employee`            | List employees (supports filters).  |
| POST   | `/employee`            | Create a new employee entry.        |
| GET    | `/employee/{id}`       | Retrieve an employee by ID.         |
| PUT    | `/employee/{id}`       | Update employee fields.             |
| DELETE | `/employee/{id}`       | Remove an employee.                 |
| GET    | `/employee/clerk/{id}` | Look up an employee by Clerk user.  |

Filtering supported via query parameters: `role`, `access_status`, and `clerk_id`.

## Service API

| Method | Path                   | Description                         |
|--------|------------------------|-------------------------------------|
| GET    | `/service`            | List services. |
| POST   | `/service`            | Create a new service entry.        |
| GET    | `/service/{id}`       | Retrieve a service by ID.         |
| PUT    | `/service/{id}`       | Update service fields.             |
| DELETE | `/service/{id}`       | Remove a service.                 |


## Reservation API

| Method | Path                   | Description                         |
|--------|------------------------|-------------------------------------|
| GET    | `/reservation`            | List reservations. |
| POST   | `/reservation`            | Create a new reservation entry.        |
| GET    | `/reservation/{id}`       | Retrieve a reservation by ID.         |
| PUT    | `/reservation/{id}`       | Update reservation fields.             |
| DELETE | `/reservation/{id}`       | Remove a reservation.                 |


## Banquet API

| Method | Path                   | Description                         |
|--------|------------------------|-------------------------------------|
| GET    | `/banquet/table`            | List tables. |
| POST   | `/banquet/table`            | Create a new table entry with its seats.        |
| GET    | `/banquet/table/{id}`       | Retrieve a table and seats by ID.         |
| PUT    | `/banquet/table/{id}`       | Update table fields.             |
| DELETE | `/banquet/table/{id}`       | Remove a table with its seats.                 |
| GET    | `/banquet/seat`            | List all seats. |
| GET    | `/banquet/seat/{id}`       | Retrieve a seat by ID.         |
