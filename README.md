# 🅿️ Parking Management System (DBMS Project)

A full-stack, database-driven **Parking Management System** built with **Flask** and **MySQL**. It handles the complete lifecycle of a multi-floor parking facility — parking and exiting cars, tracking spot occupancy in real time, calculating payments, generating revenue and analytics reports, and managing a lost-and-found desk.

> Built as a DBMS course project to demonstrate relational schema design, complex SQL queries (joins, aggregates, subqueries), and a real-world web application on top of them.

---

## ✨ Features

- **Real-time spot occupancy** — track which spots are occupied/free across every floor, and auto-sync occupancy status with active cars.
- **Park & exit workflow** — assign a car to a spot on entry, and automatically calculate duration + payment on exit.
- **Automated billing** — fare is computed from parked duration at a fixed per-minute rate at checkout.
- **Revenue & analytics dashboard** — total revenue collected, average payment per car, busiest floors, longest-parked vehicles, and more.
- **Parking history log** — every completed parking session (entry, exit, spot, floor, payment) is archived for reporting.
- **Car locator** — find exactly which floor and coordinate a car is parked at.
- **Lost & Found desk** — log found items with floor/location, search by description or floor, and mark items as claimed.
- **Floor-level insights** — see active car counts per floor and flag floors that are nearly full (busy floors).

---

## 🏗️ Tech Stack

| Layer          | Technology              |
|----------------|--------------------------|
| Backend        | Python, Flask            |
| Database       | MySQL (`mysql-connector-python`) |
| Frontend       | HTML, CSS, Jinja2 templates |
| Architecture   | Flask Blueprints (`routes.py`) + REST-style JSON APIs |

---

## 🗂️ Project Structure

```
Parking_Management_System_DBMS/
├── main.py              # App entry point — creates the Flask app, registers routes
├── routes.py             # All page routes + REST API endpoints (Blueprint)
├── db.py                 # MySQL connection helper
├── static/               # CSS, JS, and static assets
├── templates/             # Jinja2 HTML templates (index, revenue, parking_info, lost_found)
└── README.md
```

---

## 🗄️ Database Schema (Overview)

The system is built around a relational schema with the following core entities:

| Table              | Purpose                                                   |
|---------------------|------------------------------------------------------------|
| `Floor`             | Floor metadata — floor number, total spots, available spots |
| `Parking_Spot`      | Individual spots, their coordinates, floor, and occupancy status |
| `Car`               | Cars currently parked — license plate, entry time, assigned spot |
| `Payment`           | Payment records — amount paid, exit time, payment/exit status |
| `Parking_History`   | Archived record of every completed parking session |
| `Lost_and_Found`    | Items found on premises — location, description, claim status |

Key relationships: a `Car` occupies one `Parking_Spot`, each `Parking_Spot` belongs to a `Floor`, and every completed visit generates a `Payment` and a `Parking_History` entry.

> 💡 You'll need to create these tables in your MySQL instance before running the app (see [Setup](#-setup--installation)).

---

## 🔌 API Endpoints

### Core operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/park-car` | Park a car — assigns it to a spot, marks the spot occupied |
| `POST` | `/api/exit-car/<car_id>` | Exit a car — calculates duration/fare, records payment & history, frees the spot |
| `GET`  | `/api/unoccupied-parking-spots` | List all currently free spots |
| `GET`  | `/api/find-car-location/<car_id>` | Locate a parked car (floor + coordinates) |
| `GET/POST` | `/api/mark-spots-as-occupied` | Resync spot occupancy flags against actual car assignments |

### Analytics & reporting
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/max-parked` | Car that has been parked the longest |
| `GET` | `/api/floor-count` | Active car count per floor |
| `GET` | `/api/long-parked/<hours>` | Cars parked longer than `hours`, grouped by floor |
| `GET` | `/api/cars-on-busy-floors` | Cars parked on floors that are nearly full |
| `GET` | `/api/parking-spots-data` | Usage count per spot (most/least used) |
| `GET` | `/api/spot-occupancy-duration` | How long each currently occupied spot has been in use |
| `GET` | `/api/average-parking-time` | Average parking duration across all historical sessions |
| `GET` | `/api/total-cars-parked` | Total number of cars ever recorded |
| `GET` | `/api/avg-payment` | Average payment collected per car |
| `GET` | `/api/total-payment-collected` | Total revenue collected |

### Lost & Found
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/lost-found-not-claimed-yet` | List all unclaimed items |
| `GET`  | `/api/find-item` | Search items by description and/or floor |
| `POST` | `/api/add-lost-item` | Log a newly found item |
| `POST` | `/api/claim-item/<item_id>` | Mark an item as claimed |

### Pages
| Route | Page |
|-------|------|
| `/` | Home / dashboard |
| `/revenue` | Revenue analytics screen |
| `/parking-info` | Parking spot & floor info screen |
| `/lost-found` | Lost & Found screen |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/MadhavGaur123/Parking_Management_System_DBMS.git
cd Parking_Management_System_DBMS
```

### 2. Install dependencies
```bash
pip install flask mysql-connector-python
```

### 3. Set up the database
Create a MySQL database and the tables described in the [schema](#️-database-schema-overview) section (`Floor`, `Parking_Spot`, `Car`, `Payment`, `Parking_History`, `Lost_and_Found`).

Update the connection details in `db.py` to match your local MySQL setup:
```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="your_database_name"
    )
```

> ⚠️ **Security note:** Credentials in `db.py` are hardcoded for local development. For anything beyond a local class project, move them into environment variables (e.g. via `python-dotenv`) instead of committing them to source control.

### 4. Run the app
```bash
python main.py
```

The app will start in debug mode at `http://127.0.0.1:5000/`.

---

## 🚀 Usage

1. Start the server and open `http://127.0.0.1:5000/` in your browser.
2. Use the **Park a Car** flow to assign an incoming vehicle to a free spot.
3. When a vehicle leaves, hit the exit endpoint/page for that car to auto-calculate its fare and free up the spot.
4. Visit `/revenue` for billing analytics and `/parking-info` for live occupancy stats.
5. Use `/lost-found` to log or search for misplaced items.

---

## 🛣️ Roadmap / Ideas for Improvement

- [ ] Move DB credentials to environment variables / a config file
- [ ] Add authentication for admin-only endpoints (e.g. marking items claimed)
- [ ] Add automated tests for the API layer
- [ ] Configurable/tiered pricing instead of a flat per-minute rate
- [ ] Dockerize the app + database for one-command setup

---

## 🤝 Contributing

Contributions, issues, and feature suggestions are welcome! Feel free to fork the repo and open a pull request.


