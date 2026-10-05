import xml.etree.ElementTree as ET


# ============================================================
# XML UTILITY FUNCTIONS
# ============================================================

def remove_namespace(tag):
    """
    Remove XML namespace from an XML tag.

    Example:
        {namespace}CdtTrfTxInf

    becomes:
        CdtTrfTxInf
    """

    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def get_text(element):
    """
    Safely extract and clean text from an XML element.
    """

    if element is None:
        return None

    if element.text is None:
        return None

    value = element.text.strip()

    if not value:
        return None

    return " ".join(value.split())


def find_first(element, names):
    """
    Find the first descendant element whose
    namespace-independent tag matches one of
    the supplied names.
    """

    if element is None:
        return None

    names = set(names)

    for child in element.iter():

        tag = remove_namespace(child.tag)

        if tag in names:
            return child

    return None


def find_all(element, names):
    """
    Find all descendant elements whose
    namespace-independent tag matches one of
    the supplied names.
    """

    if element is None:
        return []

    names = set(names)

    results = []

    for child in element.iter():

        tag = remove_namespace(child.tag)

        if tag in names:
            results.append(child)

    return results


# ============================================================
# ADDRESS EXTRACTION
# ============================================================

def extract_address(address_element):
    """
    Extract and normalize address information.

    Supports structured ISO 20022 address fields:

        StrtNm
        BldgNb
        PstCd
        TwnNm
        Ctry

    Also supports unstructured address lines:

        AdrLine
    """

    # --------------------------------------------------------
    # No address
    # --------------------------------------------------------

    if address_element is None:

        return {
            "street": None,
            "building": None,
            "postal_code": None,
            "town": None,
            "country": None,
            "address_line": None
        }

    # --------------------------------------------------------
    # Street
    # --------------------------------------------------------

    street_element = find_first(
        address_element,
        [
            "StrtNm",
            "Street",
            "street"
        ]
    )

    street = get_text(
        street_element
    )

    # --------------------------------------------------------
    # Building
    # --------------------------------------------------------

    building_element = find_first(
        address_element,
        [
            "BldgNb",
            "Building",
            "building"
        ]
    )

    building = get_text(
        building_element
    )

    # --------------------------------------------------------
    # Postal Code
    # --------------------------------------------------------

    postal_code_element = find_first(
        address_element,
        [
            "PstCd",
            "PostalCode",
            "postal_code"
        ]
    )

    postal_code = get_text(
        postal_code_element
    )

    # --------------------------------------------------------
    # Town / City
    # --------------------------------------------------------

    town_element = find_first(
        address_element,
        [
            "TwnNm",
            "Town",
            "town",
            "City",
            "city"
        ]
    )

    town = get_text(
        town_element
    )

    # --------------------------------------------------------
    # Country
    # --------------------------------------------------------

    country_element = find_first(
        address_element,
        [
            "Ctry",
            "Country",
            "country"
        ]
    )

    country = get_text(
        country_element
    )

    # --------------------------------------------------------
    # Unstructured address lines
    # --------------------------------------------------------

    address_lines = find_all(
        address_element,
        [
            "AdrLine",
            "AddressLine",
            "address_line"
        ]
    )

    address_line_values = []

    for line in address_lines:

        text = get_text(line)

        if text:
            address_line_values.append(text)

    # --------------------------------------------------------
    # Combine address lines
    # --------------------------------------------------------

    if address_line_values:

        address_line = ", ".join(
            address_line_values
        )

    else:

        address_line = None

    # --------------------------------------------------------
    # Normalize values
    # --------------------------------------------------------

    if street:
        street = " ".join(
            street.split()
        )

    if building:
        building = " ".join(
            building.split()
        )

    if postal_code:
        postal_code = " ".join(
            postal_code.split()
        )

    if town:
        town = " ".join(
            town.split()
        )

    if country:
        country = country.strip().upper()

    if address_line:
        address_line = " ".join(
            address_line.split()
        )

    # --------------------------------------------------------
    # Return address
    # --------------------------------------------------------

    return {
        "street": street,
        "building": building,
        "postal_code": postal_code,
        "town": town,
        "country": country,
        "address_line": address_line
    }


# ============================================================
# PAYMENT ID EXTRACTION
# ============================================================

def extract_payment_id(payment):
    """
    Extract a reliable payment identifier.

    Priority:

    1. InstrId
    2. EndToEndId
    3. PaymentId
    4. PaymentID
    5. payment_id
    """

    # --------------------------------------------------------
    # Instruction ID
    # --------------------------------------------------------

    instruction_id = find_first(
        payment,
        [
            "InstrId"
        ]
    )

    instruction_id = get_text(
        instruction_id
    )

    if instruction_id:
        return instruction_id

    # --------------------------------------------------------
    # End-to-End ID
    # --------------------------------------------------------

    end_to_end_id = find_first(
        payment,
        [
            "EndToEndId"
        ]
    )

    end_to_end_id = get_text(
        end_to_end_id
    )

    if end_to_end_id:
        return end_to_end_id

    # --------------------------------------------------------
    # Other formats
    # --------------------------------------------------------

    payment_id_element = find_first(
        payment,
        [
            "PaymentId",
            "PaymentID",
            "payment_id"
        ]
    )

    payment_id = get_text(
        payment_id_element
    )

    if payment_id:
        return payment_id

    return None


# ============================================================
# AMOUNT AND CURRENCY EXTRACTION
# ============================================================

def extract_amount_and_currency(payment):
    """
    Extract and normalize transaction amount and currency.

    ISO 20022 example:

        <InstdAmt Ccy="USD">1500.00</InstdAmt>

    Also supports:

        <Amount>1500.00</Amount>
        <Currency>USD</Currency>
    """

    amount_element = find_first(
        payment,
        [
            "InstdAmt",
            "Amount",
            "amount"
        ]
    )

    amount = None
    currency = None

    # --------------------------------------------------------
    # Extract amount
    # --------------------------------------------------------

    if amount_element is not None:

        amount_text = get_text(
            amount_element
        )

        if amount_text:

            amount_text = (
                amount_text
                .replace(",", "")
                .strip()
            )

            try:

                amount = float(
                    amount_text
                )

            except (
                ValueError,
                TypeError
            ):

                amount = None

        # ----------------------------------------------------
        # ISO 20022 currency attribute
        # ----------------------------------------------------

        currency = (
            amount_element.attrib.get("Ccy")
            or amount_element.attrib.get("ccy")
            or amount_element.attrib.get("currency")
        )

    # --------------------------------------------------------
    # Currency stored separately
    # --------------------------------------------------------

    if currency is None:

        currency_element = find_first(
            payment,
            [
                "Currency",
                "currency",
                "Ccy"
            ]
        )

        currency = get_text(
            currency_element
        )

    # --------------------------------------------------------
    # Normalize currency
    # --------------------------------------------------------

    if currency:

        currency = (
            currency
            .strip()
            .upper()
        )

    return amount, currency


# ============================================================
# BENEFICIARY / CREDITOR EXTRACTION
# ============================================================

def extract_beneficiary(payment):
    """
    Extract beneficiary / creditor information.

    Supports ISO 20022:

        <Cdtr>
            <Nm>...</Nm>
            <PstlAdr>...</PstlAdr>
        </Cdtr>

    Also supports simpler structures:

        <Beneficiary>
            <Name>...</Name>
            <Address>...</Address>
        </Address>
    """

    # --------------------------------------------------------
    # Find beneficiary
    # --------------------------------------------------------

    beneficiary_element = find_first(
        payment,
        [
            "Cdtr",
            "Creditor",
            "Beneficiary",
            "beneficiary"
        ]
    )

    # --------------------------------------------------------
    # Beneficiary not found
    # --------------------------------------------------------

    if beneficiary_element is None:

        return {
            "beneficiary": None,
            "street": None,
            "building": None,
            "postal_code": None,
            "town": None,
            "country": None,
            "address_line": None
        }

    # --------------------------------------------------------
    # Beneficiary name
    # --------------------------------------------------------

    beneficiary_name_element = find_first(
        beneficiary_element,
        [
            "Nm",
            "Name",
            "name"
        ]
    )

    beneficiary_name = get_text(
        beneficiary_name_element
    )

    # --------------------------------------------------------
    # Beneficiary address
    # --------------------------------------------------------

    address_element = find_first(
        beneficiary_element,
        [
            "PstlAdr",
            "PostalAddress",
            "Address",
            "address"
        ]
    )

    address = extract_address(
        address_element
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "beneficiary": beneficiary_name,

        "street":
            address["street"],

        "building":
            address["building"],

        "postal_code":
            address["postal_code"],

        "town":
            address["town"],

        "country":
            address["country"],

        "address_line":
            address["address_line"]
    }


# ============================================================
# DEBTOR EXTRACTION
# ============================================================

def extract_debtor(payment):
    """
    Extract debtor / sender information.

    Supports ISO 20022:

        <Dbtr>
            <Nm>...</Nm>
            <PstlAdr>...</PstlAdr>
        </Dbtr>
    """

    debtor_element = find_first(
        payment,
        [
            "Dbtr",
            "Debtor",
            "Sender",
            "sender"
        ]
    )

    # --------------------------------------------------------
    # Debtor not found
    # --------------------------------------------------------

    if debtor_element is None:

        return {
            "debtor": None,
            "debtor_street": None,
            "debtor_building": None,
            "debtor_postal_code": None,
            "debtor_town": None,
            "debtor_country": None,
            "debtor_address_line": None
        }

    # --------------------------------------------------------
    # Debtor name
    # --------------------------------------------------------

    debtor_name_element = find_first(
        debtor_element,
        [
            "Nm",
            "Name",
            "name"
        ]
    )

    debtor_name = get_text(
        debtor_name_element
    )

    # --------------------------------------------------------
    # Debtor address
    # --------------------------------------------------------

    address_element = find_first(
        debtor_element,
        [
            "PstlAdr",
            "PostalAddress",
            "Address",
            "address"
        ]
    )

    address = extract_address(
        address_element
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "debtor": debtor_name,

        "debtor_street":
            address["street"],

        "debtor_building":
            address["building"],

        "debtor_postal_code":
            address["postal_code"],

        "debtor_town":
            address["town"],

        "debtor_country":
            address["country"],

        "debtor_address_line":
            address["address_line"]
    }


# ============================================================
# SINGLE PAYMENT PARSER
# ============================================================

def parse_payment_element(payment):
    """
    Parse one payment XML element.

    Returns a normalized payment dictionary.
    """

    # --------------------------------------------------------
    # Payment ID
    # --------------------------------------------------------

    payment_id = extract_payment_id(
        payment
    )

    # --------------------------------------------------------
    # Amount + currency
    # --------------------------------------------------------

    amount, currency = (
        extract_amount_and_currency(
            payment
        )
    )

    # --------------------------------------------------------
    # Beneficiary
    # --------------------------------------------------------

    beneficiary_data = (
        extract_beneficiary(
            payment
        )
    )

    # --------------------------------------------------------
    # Debtor
    # --------------------------------------------------------

    debtor_data = (
        extract_debtor(
            payment
        )
    )

    # --------------------------------------------------------
    # Combine all fields
    # --------------------------------------------------------

    payment_data = {

        "payment_id":
            payment_id,

        "amount":
            amount,

        "currency":
            currency,

        # Beneficiary
        "beneficiary":
            beneficiary_data["beneficiary"],

        "street":
            beneficiary_data["street"],

        "building":
            beneficiary_data["building"],

        "postal_code":
            beneficiary_data["postal_code"],

        "town":
            beneficiary_data["town"],

        "country":
            beneficiary_data["country"],

        "address_line":
            beneficiary_data["address_line"],

        # Debtor
        "debtor":
            debtor_data["debtor"],

        "debtor_street":
            debtor_data["debtor_street"],

        "debtor_building":
            debtor_data["debtor_building"],

        "debtor_postal_code":
            debtor_data["debtor_postal_code"],

        "debtor_town":
            debtor_data["debtor_town"],

        "debtor_country":
            debtor_data["debtor_country"],

        "debtor_address_line":
            debtor_data["debtor_address_line"]
    }

    return payment_data


# ============================================================
# PAYMENT ELEMENT DISCOVERY
# ============================================================

def find_payment_elements(root):
    """
    Locate payment transaction elements.

    Supports:

        payment
        Payment
        CdtTrfTxInf
        CreditTransferTransactionInformation
    """

    payment_elements = []

    for element in root.iter():

        tag = remove_namespace(
            element.tag
        )

        if tag in {
            "payment",
            "Payment",
            "CdtTrfTxInf",
            "CreditTransferTransactionInformation"
        }:

            payment_elements.append(
                element
            )

    return payment_elements


# ============================================================
# PAYMENT NORMALIZATION
# ============================================================

def normalize_payment(payment):
    """
    Normalize one parsed payment into a
    consistent application-level structure.

    Responsibilities:

    - Clean text
    - Normalize currency
    - Convert amount to float
    - Normalize country
    - Preserve missing values as None
    """

    # --------------------------------------------------------
    # Helper
    # --------------------------------------------------------

    def clean_text(value):

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        return " ".join(
            value.split()
        )

    # --------------------------------------------------------
    # Payment ID
    # --------------------------------------------------------

    payment_id = clean_text(
        payment.get("payment_id")
    )

    # --------------------------------------------------------
    # Amount
    # --------------------------------------------------------

    amount = payment.get(
        "amount"
    )

    if amount is not None:

        try:

            amount = float(
                amount
            )

        except (
            ValueError,
            TypeError
        ):

            amount = None

    # --------------------------------------------------------
    # Currency
    # --------------------------------------------------------

    currency = clean_text(
        payment.get("currency")
    )

    if currency:

        currency = currency.upper()

    # --------------------------------------------------------
    # Beneficiary fields
    # --------------------------------------------------------

    beneficiary = clean_text(
        payment.get("beneficiary")
    )

    street = clean_text(
        payment.get("street")
    )

    building = clean_text(
        payment.get("building")
    )

    postal_code = clean_text(
        payment.get("postal_code")
    )

    town = clean_text(
        payment.get("town")
    )

    country = clean_text(
        payment.get("country")
    )

    address_line = clean_text(
        payment.get("address_line")
    )

    # --------------------------------------------------------
    # Debtor fields
    # --------------------------------------------------------

    debtor = clean_text(
        payment.get("debtor")
    )

    debtor_street = clean_text(
        payment.get("debtor_street")
    )

    debtor_building = clean_text(
        payment.get("debtor_building")
    )

    debtor_postal_code = clean_text(
        payment.get("debtor_postal_code")
    )

    debtor_town = clean_text(
        payment.get("debtor_town")
    )

    debtor_country = clean_text(
        payment.get("debtor_country")
    )

    debtor_address_line = clean_text(
        payment.get("debtor_address_line")
    )

    # --------------------------------------------------------
    # Normalize countries
    # --------------------------------------------------------

    if country:

        country = country.upper()

    if debtor_country:

        debtor_country = (
            debtor_country.upper()
        )

    # --------------------------------------------------------
    # Standard payment object
    # --------------------------------------------------------

    normalized_payment = {

        "payment_id":
            payment_id,

        "amount":
            amount,

        "currency":
            currency,

        # Beneficiary
        "beneficiary":
            beneficiary,

        "street":
            street,

        "building":
            building,

        "postal_code":
            postal_code,

        "town":
            town,

        "country":
            country,

        "address_line":
            address_line,

        # Debtor
        "debtor":
            debtor,

        "debtor_street":
            debtor_street,

        "debtor_building":
            debtor_building,

        "debtor_postal_code":
            debtor_postal_code,

        "debtor_town":
            debtor_town,

        "debtor_country":
            debtor_country,

        "debtor_address_line":
            debtor_address_line
    }

    return normalized_payment


# ============================================================
# MAIN XML FILE PARSER
# ============================================================

def parse_xml_file(file_path):
    """
    Parse an ISO 20022 XML file.

    Returns:

        [
            {
                "payment_id": "...",
                "amount": 1000.0,
                "currency": "USD",
                ...
            }
        ]
    """

    # --------------------------------------------------------
    # Parse XML
    # --------------------------------------------------------

    try:

        tree = ET.parse(
            file_path
        )

        root = tree.getroot()

    except ET.ParseError as error:

        raise ValueError(
            f"Invalid XML file: {error}"
        )

    except FileNotFoundError:

        raise ValueError(
            f"XML file not found: {file_path}"
        )

    except OSError as error:

        raise ValueError(
            f"Unable to read XML file: {error}"
        )

    # --------------------------------------------------------
    # Find payment elements
    # --------------------------------------------------------

    payment_elements = (
        find_payment_elements(
            root
        )
    )

    # --------------------------------------------------------
    # If no payment elements were found,
    # treat root as a payment.
    # --------------------------------------------------------

    if not payment_elements:

        payment_elements = [
            root
        ]

    # --------------------------------------------------------
    # Parse all payments
    # --------------------------------------------------------

    payments = []

    for payment_element in payment_elements:

        payment = parse_payment_element(
            payment_element
        )

        payment = normalize_payment(
            payment
        )

        # ----------------------------------------------------
        # Keep payment if it contains data
        # ----------------------------------------------------

        if any(
            value is not None
            for value in payment.values()
        ):

            payments.append(
                payment
            )

    return payments