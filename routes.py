# backend/routes.py
from flask import Blueprint, request, jsonify ,render_template
from db import get_connection

bp = Blueprint('routes', __name__)

#implemented
@bp.route("/api/max-parked")
def max_parked():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.car_id, c.license_plate, c.entry_time,
               TIMESTAMPDIFF(HOUR, c.entry_time, NOW()) AS hours_parked
        FROM Car c
        JOIN Parking_Spot ps ON c.spot_id = ps.spot_id
        WHERE ps.is_occupied = TRUE
        ORDER BY hours_parked DESC
        LIMIT 1;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)

#implemented
@bp.route("/api/floor-count")
def get_floor_count():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.floor_id, f.number AS floor_number, COUNT(c.car_id) AS active_cars
        FROM Car c
        JOIN Parking_Spot ps ON c.spot_id = ps.spot_id
        JOIN Floor f ON ps.floor_id = f.floor_id
        LEFT JOIN Payment p ON c.car_id = p.car_id
        WHERE ps.is_occupied = TRUE AND p.car_id IS NULL
        GROUP BY f.floor_id, f.number
        ORDER BY f.floor_id;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/long-parked/<int:hours>")
def long_parked(hours):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.floor_id, f.number AS floor_number, COUNT(c.car_id) AS active_cars_over_hour
        FROM Car c
        JOIN Parking_Spot ps ON c.spot_id = ps.spot_id
        JOIN Floor f ON ps.floor_id = f.floor_id
        LEFT JOIN Payment p ON c.car_id = p.car_id
        WHERE ps.is_occupied = TRUE AND p.car_id IS NULL
              AND TIMESTAMPDIFF(HOUR, c.entry_time, NOW()) > %s
        GROUP BY f.floor_id, f.number
        ORDER BY f.floor_id;
    """, (hours,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/avg-payment")
def avg_payment():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(""" SELECT 
    SUM(amount_paid) / COUNT(DISTINCT car_id) AS average_payment_per_car
FROM 
    Payment
WHERE 
    is_paid = TRUE;""")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/lost-found-not-claimed-yet")
def lost_found_unclaimed():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT item_id, floor_id, found_at_coord_x, found_at_coord_y, description
        FROM Lost_and_Found
        WHERE claimed = FALSE;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/total-cars-parked")
def total_cars_parked():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total_cars_parked FROM Car;")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/parking-spots-data")
def parking_spots_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ps.spot_id, ps.floor_id, COUNT(ph.history_id) AS total_uses
        FROM Parking_Spot ps
        LEFT JOIN Parking_History ph ON ps.spot_id = ph.spot_id
        GROUP BY ps.spot_id, ps.floor_id
        ORDER BY total_uses DESC;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/cars-on-busy-floors")
def cars_on_busy_floors():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.car_id, c.license_plate, c.entry_time, f.number AS floor_number,
               f.available_spots, f.total_spots
        FROM Car c
        JOIN Parking_Spot ps ON c.spot_id = ps.spot_id
        JOIN Floor f ON ps.floor_id = f.floor_id
        WHERE ps.is_occupied = TRUE
              AND f.floor_id IN (
                  SELECT floor_id FROM Floor WHERE available_spots < (0.93 * total_spots)
              )
        ORDER BY c.entry_time;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/mark-spots-as-occupied", methods=["GET", "POST"])
def mark_spots_as_occupied():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Mark spots as occupied where a car is currently assigned
    cursor.execute("""
        UPDATE Parking_Spot ps
        JOIN Car c ON ps.spot_id = c.spot_id
        SET ps.is_occupied = TRUE
        WHERE c.spot_id IS NOT NULL;
    """)

    # Mark spots as unoccupied where no car is currently assigned
    cursor.execute("""
        UPDATE Parking_Spot ps
        LEFT JOIN Car c ON ps.spot_id = c.spot_id
        SET ps.is_occupied = FALSE
        WHERE c.spot_id IS NULL;
    """)

    # Fetch the updated state of the parking spots
    cursor.execute("SELECT * FROM Parking_Spot;")
    result = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(result)



@bp.route("/api/unoccupied-parking-spots")
def unoccupied_spots():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT spot_id, floor_id, x_coord, y_coord
        FROM Parking_Spot
        WHERE is_occupied = FALSE;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/total-payment-collected")
def total_payment():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT SUM(amount_paid) AS total_payment_collected
        FROM Payment
        WHERE is_paid = TRUE;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/spot-occupancy-duration")
def spot_occupancy_duration():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.car_id, c.license_plate, c.entry_time,
               TIMESTAMPDIFF(MINUTE, c.entry_time, NOW()) AS duration_minutes,
               ps.spot_id, f.number AS floor_number
        FROM Car c
        JOIN Parking_Spot ps ON c.spot_id = ps.spot_id
        JOIN Floor f ON ps.floor_id = f.floor_id
        WHERE c.spot_id IS NOT NULL;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/find-car-location/<int:car_id>")
def find_car_location(car_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.number AS floor_number, ps.x_coord, ps.y_coord
        FROM Car c
        JOIN Parking_Spot ps ON c.spot_id = ps.spot_id
        JOIN Floor f ON ps.floor_id = f.floor_id
        WHERE c.car_id = %s;
    """, (car_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/average-parking-time")
def average_parking_time():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT AVG(TIMESTAMPDIFF(MINUTE, entry_time, exit_time)) AS average_duration_minutes
        FROM Parking_History;
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)


@bp.route("/api/find-item")
def find_item():
    search_term = request.args.get("description", "")
    floor_id = request.args.get("floor_id")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT item_id, floor_id, found_at_coord_x, found_at_coord_y, description, claimed
        FROM Lost_and_Found
        WHERE 1=1
    """
    params = []

    if search_term:
        query += " AND description LIKE %s"
        params.append(f"%{search_term}%")

    if floor_id:
        query += " AND floor_id = %s"
        params.append(floor_id)

    cursor.execute(query, tuple(params))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)
@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/revenue')
def revenue_screen():
    return render_template('revenue.html')  # We'll make this next

@bp.route('/parking-info')
def parking_info_screen():
    return render_template('parking_info.html')

@bp.route('/lost-found')
def lost_found_screen():
    return render_template('lost_found.html')

@bp.route("/api/add-lost-item", methods=["POST"])
def add_lost_item():
    data = request.get_json()

    floor_id = data.get("floor_id")
    x = data.get("x_coord")
    y = data.get("y_coord")
    description = data.get("description")

    if not all([floor_id, x, y, description]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Lost_and_Found (floor_id, found_at_coord_x, found_at_coord_y, description)
            VALUES (%s, %s, %s, %s)
        """, (floor_id, x, y, description))
        conn.commit()
        return jsonify({"message": "Item successfully added"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@bp.route("/api/claim-item/<int:item_id>", methods=["POST"])
def claim_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Lost_and_Found
            SET claimed = TRUE
            WHERE item_id = %s
        """, (item_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Item not found"}), 404

        return jsonify({"message": f"Item {item_id} marked as claimed."}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@bp.route("/api/park-car", methods=["POST"])
def park_car():
    data = request.get_json()
    license_plate = data.get("license_plate")
    spot_id = data.get("spot_id")

    if not all([license_plate, spot_id]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert into Car and associate the spot
        cursor.execute("""
            INSERT INTO Car (license_plate, entry_time, spot_id)
            VALUES (%s, NOW(), %s)
        """, (license_plate, spot_id))

        # Mark the spot as occupied
        cursor.execute("""
            UPDATE Parking_Spot SET is_occupied = TRUE WHERE spot_id = %s
        """, (spot_id,))

        conn.commit()
        return jsonify({"message": "Car parked successfully."}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@bp.route("/api/exit-car/<int:car_id>", methods=["POST"])
def exit_car(car_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Get car and spot
        cursor.execute("""
            SELECT entry_time, spot_id FROM Car WHERE car_id = %s
        """, (car_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Car not found."}), 404
        entry_time, spot_id = row

        # Check if already exited
        cursor.execute("""
            SELECT COUNT(*) FROM Payment WHERE car_id = %s AND has_exited = TRUE
        """, (car_id,))
        if cursor.fetchone()[0]:
            return jsonify({"error": "Car already exited."}), 400

        # Duration + Payment
        cursor.execute("SELECT TIMESTAMPDIFF(MINUTE, %s, NOW())", (entry_time,))
        duration_minutes = cursor.fetchone()[0]
        rate_per_min = 2
        amount = round(duration_minutes * rate_per_min, 2)

        # Insert into Payment
        cursor.execute("""
            INSERT INTO Payment (car_id, exit_time, amount_paid, is_paid, has_exited)
            VALUES (%s, NOW(), %s, TRUE, TRUE)
        """, (car_id, amount))
        payment_id = cursor.lastrowid

        # Get floor_id from Parking_Spot
        cursor.execute("""
            SELECT floor_id FROM Parking_Spot WHERE spot_id = %s
        """, (spot_id,))
        floor_id = cursor.fetchone()[0]

        # Insert into Parking_History
        cursor.execute("""
            INSERT INTO Parking_History (car_id, spot_id, floor_id, payment_id, entry_time, exit_time, amount_paid)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (car_id, spot_id, floor_id, payment_id, entry_time, amount))

        # Free the spot and unlink car
        cursor.execute("UPDATE Parking_Spot SET is_occupied = FALSE WHERE spot_id = %s", (spot_id,))
        cursor.execute("UPDATE Car SET spot_id = NULL WHERE car_id = %s", (car_id,))

        conn.commit()
        return jsonify({
            "message": "Car exited, payment collected, and history recorded.",
            "duration_minutes": duration_minutes,
            "amount_paid": amount
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
