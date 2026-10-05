import sqlite3
import json
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_PATH = BASE_DIR / "payflow.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables(connection):

    cursor = connection.cursor()

    # ========================================================
    # PAYMENTS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            payment_id TEXT UNIQUE,

            amount REAL,

            currency TEXT,

            beneficiary TEXT,

            street TEXT,

            building TEXT,

            postal_code TEXT,

            town TEXT,

            country TEXT,

            address_line TEXT,

            debtor TEXT,

            debtor_street TEXT,

            debtor_building TEXT,

            debtor_postal_code TEXT,

            debtor_town TEXT,

            debtor_country TEXT,

            debtor_address_line TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    # ========================================================
    # VALIDATION RESULTS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS validation_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            payment_id TEXT,

            status TEXT,

            validation_score INTEGER,

            errors TEXT,

            warnings TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

# ============================================================
# CREATE AUDIT LOG TABLE
# ============================================================

def create_audit_table(connection):

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            payment_id TEXT,

            event_type TEXT NOT NULL,

            event_status TEXT,

            description TEXT,

            details TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )
# ============================================================
# MIGRATE PAYMENTS TABLE
# ============================================================

def migrate_payments_table(connection):

    cursor = connection.cursor()

    cursor.execute(
        "PRAGMA table_info(payments)"
    )

    existing_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    required_columns = {

        "payment_id": "TEXT",

        "amount": "REAL",

        "currency": "TEXT",

        "beneficiary": "TEXT",

        "street": "TEXT",

        "building": "TEXT",

        "postal_code": "TEXT",

        "town": "TEXT",

        "country": "TEXT",

        "address_line": "TEXT",

        "debtor": "TEXT",

        "debtor_street": "TEXT",

        "debtor_building": "TEXT",

        "debtor_postal_code": "TEXT",

        "debtor_town": "TEXT",

        "debtor_country": "TEXT",

        "debtor_address_line": "TEXT"

    }

    for column_name, column_type in required_columns.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE payments
                ADD COLUMN {column_name} {column_type}
                """
            )


# ============================================================
# MIGRATE VALIDATION TABLE
# ============================================================

def migrate_validation_results_table(connection):

    cursor = connection.cursor()

    cursor.execute(
        "PRAGMA table_info(validation_results)"
    )

    existing_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    required_columns = {

        "payment_id": "TEXT",

        "status": "TEXT",

        "validation_score": "INTEGER",

        "errors": "TEXT",

        "warnings": "TEXT"

    }

    for column_name, column_type in required_columns.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE validation_results
                ADD COLUMN {column_name} {column_type}
                """
            )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    try:

        create_tables(
            connection
        )

        create_audit_table(
            connection
        )

        migrate_payments_table(
            connection
        )

        migrate_validation_results_table(
            connection
        )

        connection.commit()

    finally:

        connection.close()


# ============================================================
# SAVE PAYMENT + VALIDATION RESULT
# ============================================================

def save_payment_with_validation(
    payment,
    validation_result
):
    """
    Save payment and validation result.

    If the payment_id already exists, the payment is skipped
    instead of causing the API to return a 500 error.

    This allows the same XML file to be tested repeatedly.
    """

    connection = get_connection()

    cursor = connection.cursor()

    try:

        payment_id = payment.get(
            "payment_id"
        )

        # ====================================================
        # CHECK WHETHER PAYMENT ALREADY EXISTS
        # ====================================================

        cursor.execute(
            """
            SELECT id
            FROM payments
            WHERE payment_id = ?
            """,
            (payment_id,)
        )

        existing_payment = cursor.fetchone()

        # ====================================================
        # INSERT ONLY IF IT DOES NOT EXIST
        # ====================================================

        if existing_payment is None:

            cursor.execute(
                """
                INSERT INTO payments (

                    payment_id,

                    amount,

                    currency,

                    beneficiary,

                    street,

                    building,

                    postal_code,

                    town,

                    country,

                    address_line,

                    debtor,

                    debtor_street,

                    debtor_building,

                    debtor_postal_code,

                    debtor_town,

                    debtor_country,

                    debtor_address_line

                )

                VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,

                (

                    payment.get(
                        "payment_id"
                    ),

                    payment.get(
                        "amount"
                    ),

                    payment.get(
                        "currency"
                    ),

                    payment.get(
                        "beneficiary"
                    ),

                    payment.get(
                        "street"
                    ),

                    payment.get(
                        "building"
                    ),

                    payment.get(
                        "postal_code"
                    ),

                    payment.get(
                        "town"
                    ),

                    payment.get(
                        "country"
                    ),

                    payment.get(
                        "address_line"
                    ),

                    payment.get(
                        "debtor"
                    ),

                    payment.get(
                        "debtor_street"
                    ),

                    payment.get(
                        "debtor_building"
                    ),

                    payment.get(
                        "debtor_postal_code"
                    ),

                    payment.get(
                        "debtor_town"
                    ),

                    payment.get(
                        "debtor_country"
                    ),

                    payment.get(
                        "debtor_address_line"
                    )

                )
            )

        # ====================================================
        # PAYMENT ALREADY EXISTS
        # ====================================================

        else:

            print(
                f"Payment {payment_id} already exists. "
                f"Skipping duplicate payment."
            )


        # ====================================================
        # VALIDATION RESULT
        # ====================================================

        errors = json.dumps(
            validation_result.get(
                "errors",
                []
            )
        )

        warnings = json.dumps(
            validation_result.get(
                "warnings",
                []
            )
        )


        # ====================================================
        # INSERT VALIDATION RESULT
        # ====================================================

        cursor.execute(
            """
            INSERT INTO validation_results (

                payment_id,

                status,

                validation_score,

                errors,

                warnings

            )

            VALUES (?, ?, ?, ?, ?)
            """,

            (

                validation_result.get(
                    "payment_id"
                ),

                validation_result.get(
                    "status"
                ),

                validation_result.get(
                    "validation_score"
                ),

                errors,

                warnings

            )
        )


        # ====================================================
        # COMMIT
        # ====================================================

        connection.commit()


    except Exception:

        connection.rollback()

        raise


    finally:

        connection.close()


# ============================================================
# GET ALL PAYMENTS
# ============================================================

def get_all_payments():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM payments
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# GET ALL VALIDATION RESULTS
# ============================================================

def get_all_validation_results():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM validation_results
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    results = []

    for row in rows:

        result = dict(row)

        # ====================================================
        # ERRORS
        # ====================================================

        try:

            result["errors"] = json.loads(
                result["errors"]
            )

        except Exception:

            result["errors"] = []


        # ====================================================
        # WARNINGS
        # ====================================================

        try:

            result["warnings"] = json.loads(
                result["warnings"]
            )

        except Exception:

            result["warnings"] = []


        results.append(
            result
        )

    return results

# ============================================================
# LOG AUDIT EVENT
# ============================================================

def log_audit_event(
    payment_id=None,
    event_type="UNKNOWN",
    event_status="SUCCESS",
    description="",
    details=None
):
    """
    Store an event in the audit trail.

    Parameters
    ----------
    payment_id : str
        Payment associated with the event.

    event_type : str
        Type of event, for example:
        XML_UPLOAD
        XML_PARSE
        VALIDATION
        PAYMENT_STORED

    event_status : str
        SUCCESS / FAILED / WARNING

    description : str
        Human-readable description.

    details : str/dict/list
        Additional information about the event.
    """

    connection = get_connection()

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # CONVERT DETAILS TO JSON
        # ----------------------------------------------------

        if details is None:

            details_json = None

        elif isinstance(
            details,
            (dict, list)
        ):

            details_json = json.dumps(
                details
            )

        else:

            details_json = str(
                details
            )


        # ----------------------------------------------------
        # INSERT AUDIT EVENT
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO audit_logs (

                payment_id,

                event_type,

                event_status,

                description,

                details

            )

            VALUES (?, ?, ?, ?, ?)
            """,

            (

                payment_id,

                event_type,

                event_status,

                description,

                details_json

            )
        )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        connection.commit()


    except Exception:

        connection.rollback()

        raise


    finally:

        connection.close()

# ============================================================
# GET AUDIT LOGS
# ============================================================

def get_audit_logs(
    payment_id=None
):
    """
    Retrieve audit events.

    If payment_id is supplied, only events
    for that payment are returned.

    Otherwise, all audit events are returned.
    """

    connection = get_connection()

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # SPECIFIC PAYMENT
        # ----------------------------------------------------

        if payment_id:

            cursor.execute(
                """
                SELECT *
                FROM audit_logs
                WHERE payment_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (payment_id,)
            )

        # ----------------------------------------------------
        # ALL PAYMENTS
        # ----------------------------------------------------

        else:

            cursor.execute(
                """
                SELECT *
                FROM audit_logs
                ORDER BY created_at DESC, id DESC
                """
            )


        rows = cursor.fetchall()


        return [
            dict(row)
            for row in rows
        ]


    finally:

        connection.close()