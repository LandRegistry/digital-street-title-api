from title_api.extensions import db
from sqlalchemy.sql import func
from datetime import datetime
import json


class Title(db.Model):
    __tablename__ = 'title'

    # Fields
    title_number = db.Column(db.String, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    lock = db.Column(db.DateTime, nullable=True)
    owner_identity = db.Column(db.Integer, db.ForeignKey('owner.identity'), nullable=False)
    address_id = db.Column(db.Integer,
                           db.ForeignKey('address.address_id', ondelete="CASCADE", onupdate="CASCADE"),
                           nullable=False)

    # Relationships
    owner = db.relationship("Owner", backref=db.backref('title', lazy='dynamic'),
                            foreign_keys='Title.owner_identity', uselist=False, cascade="save-update")
    address = db.relationship("Address", backref=db.backref('title', lazy='dynamic'),
                              foreign_keys='Title.address_id', uselist=False, cascade="save-update")
    price_history = db.relationship("PriceHistory", back_populates="title", cascade="all, delete-orphan")
    restrictions = db.relationship("Restriction", back_populates="title", cascade="all, delete-orphan")
    charges = db.relationship("Charge", back_populates="title", cascade="all, delete-orphan")

    # Methods
    def __init__(self, title_number, owner, address):
        self.title_number = title_number.upper()
        self.created_at = datetime.utcnow()
        self.owner = owner
        self.address = address

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        restrictions_dict = [r.as_dict() for r in self.restrictions]

        charges_dict = []
        for charge in self.charges:
            if charge.restriction is None:
                charges_dict.append(charge.as_dict())

        restriction_consenting_parties_dict = []
        for restriction in self.restrictions:
            restriction_consenting_parties_dict.append(X500Name.from_string(restriction.consenting_party).as_dict())

        price_history_dict = [r.as_dict() for r in self.price_history]

        return {
            "title_number": self.title_number,
            "owner": self.owner.as_dict(),
            "address": self.address.as_dict(),
            "restrictions": restrictions_dict,
            "charges": charges_dict,
            "restriction_consenting_parties": restriction_consenting_parties_dict,
            "price_history": price_history_dict,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else self.updated_at,
            "locked_at": self.lock.isoformat() if self.lock else self.lock
        }


class PriceHistory(db.Model):
    __tablename__ = 'price_history'

    # Fields
    title_number = db.Column(db.String, db.ForeignKey('title.title_number'), primary_key=True)
    date = db.Column(db.DateTime, nullable=False, server_default=func.now(), primary_key=True)
    price_amount = db.Column(db.Integer, nullable=False)
    price_currency = db.Column(db.String, nullable=False)

    # Relationships
    title = db.relationship("Title", back_populates="price_history")

    # Methods
    def __init__(self, title_number, price_amount, price_currency, date):
        self.title_number = title_number.upper()
        self.price_amount = price_amount
        self.price_currency = price_currency
        if date:
            self.date = date
        else:
            self.date = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "amount": self.price_amount,
            "currency_code": self.price_currency,
            "date_iso": self.date.isoformat(),
            "date": int(self.date.strftime('%s'))
        }


class Owner(db.Model):
    __tablename__ = 'owner'

    # Fields
    identity = db.Column(db.String, primary_key=True)
    forename = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True, index=True)
    phone = db.Column(db.String, nullable=False)
    owner_type = db.Column(db.String, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)

    # Relationships
    address = db.relationship("Address", backref=db.backref('owner', lazy='dynamic'),
                              foreign_keys='Owner.address_id', uselist=False)

    # Methods
    def __init__(self, identity, forename, surname, email, phone, owner_type, address):
        self.identity = identity
        self.forename = forename
        self.surname = surname
        self.email = email.lower()
        self.phone = phone
        self.owner_type = owner_type
        self.address = address

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "identity": self.identity,
            "first_name": self.forename,
            "last_name": self.surname,
            "email_address": self.email,
            "phone_number": self.phone,
            "type": self.owner_type,
            "address": self.address.as_dict()
        }


class Address(db.Model):
    __tablename__ = 'address'

    # Fields
    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    house_name_or_number = db.Column(db.String, nullable=False)
    street_name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    county = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    postcode = db.Column(db.String, nullable=False)

    # Methods
    def __init__(self, house_name_number, street_name, city, county, country, postcode):
        self.house_name_or_number = house_name_number
        self.street_name = street_name
        self.city = city
        self.county = county
        self.country = country
        self.postcode = postcode

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "house_name_number": self.house_name_or_number,
            "street": self.street_name,
            "town_city": self.city,
            "county": self.county,
            "country": self.country,
            "postcode": self.postcode
        }


class Conveyancer(db.Model):
    __tablename__ = 'conveyancer'

    # Fields
    conveyancer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    x500_name = db.Column(db.String, unique=True, nullable=False)
    company_name = db.Column(db.String, nullable=False)

    # Methods
    def __init__(self, x500_name_string, company_name):
        self.x500_name = str(X500Name.from_string(x500_name_string))
        self.company_name = company_name

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "conveyancer_id": self.conveyancer_id,
            "x500": X500Name.from_string(self.x500_name).as_dict(),
            "x500_string": str(X500Name.from_string(self.x500_name)),
            "company_name": self.company_name
        }


class X500Name(object):
    """Class representation of an X500Name."""

    # Fields
    organisation = None
    locality = None
    country = None
    state = None
    organisational_unit = None
    common_name = None

    # Methods
    def __init__(self, organisation, locality, country):
        self.organisation = organisation
        self.locality = locality
        self.country = country

    @staticmethod
    def from_string(str_obj):
        items = {}
        for item in str_obj.split(','):
            k, v = item.split('=')
            items[k.replace(' ', '')] = v

        organisation = items.get('O')
        locality = items.get('L')
        country = items.get('C')
        state = items.get('ST')
        organisational_unit = items.get('OU')
        common_name = items.get('CN')

        x500name = X500Name(organisation, locality, country)
        x500name.state = state
        x500name.organisational_unit = organisational_unit
        x500name.common_name = common_name

        x500name.validate()
        return x500name

    @staticmethod
    def from_dict(dict_obj):
        organisation = dict_obj['organisation']
        locality = dict_obj['locality']
        country = dict_obj['country']
        state = dict_obj.get('state')
        organisational_unit = dict_obj.get('organisational_unit')
        common_name = dict_obj.get('common_name')

        x500name = X500Name(organisation, locality, country)
        x500name.state = state
        x500name.organisational_unit = organisational_unit
        x500name.common_name = common_name

        x500name.validate()
        return x500name

    # Based on: https://docs.corda.net/releases/release-V3.3/generating-a-node.html#node-naming
    def validate(self):
        # Check 3 required values exist
        if not self.organisation:
            raise TypeError("Missing: organisation")
        if not self.locality:
            raise TypeError("Missing: locality")
        if not self.country:
            raise TypeError("Missing: country")

        # Check value length
        if len(self.organisation) < 2 or len(self.organisation) > 128:
            raise ValueError("Wrong length: organisation (min: 2, max: 128)")
        if len(self.locality) < 2 or len(self.locality) > 64:
            raise ValueError("Wrong length: locality (min: 2, max: 64)")
        if len(self.country) != 2:
            raise ValueError("Wrong length: country (min: 2, max: 2)")
        if self.state and (len(self.state) < 2 or len(self.state) > 64):
            raise ValueError("Wrong length: state (min: 2, max: 64)")
        if self.organisational_unit and (len(self.organisational_unit) < 2 or len(self.organisational_unit) > 64):
            raise ValueError("Wrong length: organisational_unit (min: 2, max: 64)")
        if self.common_name and (len(self.common_name) < 2 or len(self.common_name) > 64):
            raise ValueError("Wrong length: common_name (min: 2, max: 64)")

        for name, item in self.as_dict(False).items():
            if not item:
                continue

            # Check value's first letter is upper case
            if not item[0].isupper():
                raise ValueError("First character is not uppercase: " + name)

            # Check value has no leading or trailing whitespace
            if item.strip() != item:
                raise ValueError("Has leading or trailing whitespace: " + name)

            # Check value has invalid characters
            invalid_chars = [',', '=', '$', '"', '\'', '\\']
            if any(char in item for char in invalid_chars):
                raise ValueError("Contains invalid characters: " + name)

            # Check value has invalid characters
            if '\00' in item:
                raise ValueError("Contains null character: " + name)
        return True

    def __str__(self, should_validate=True):
        if should_validate:
            self.validate()

        items = []
        items.append("O=" + self.organisation)
        items.append("L=" + self.locality)
        items.append("C=" + self.country)
        if self.state:
            items.append("ST=" + self.state)
        if self.organisational_unit:
            items.append("OU=" + self.organisational_unit)
        if self.common_name:
            items.append("CN=" + self.common_name)

        return ','.join(items)

    def __repr__(self):
        return str(self)

    def as_dict(self, should_validate=True):
        if should_validate:
            self.validate()

        return {
            "organisation": self.organisation,
            "locality": self.locality,
            "country": self.country,
            "state": self.state,
            "organisational_unit": self.organisational_unit,
            "common_name": self.common_name,
        }


class Restriction(db.Model):
    """Class representation of a Restriction."""
    __tablename__ = 'restriction'

    # Fields
    restriction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restriction_code = db.Column(db.String, nullable=False)
    restriction_type = db.Column(db.String, nullable=False)
    restriction_text = db.Column(db.String, nullable=False)
    consenting_party = db.Column(db.String, nullable=False)
    restriction_date = db.Column(db.DateTime, nullable=False, server_default=func.now())
    title_number = db.Column(db.String, db.ForeignKey('title.title_number'))
    charge_id = db.Column(db.Integer,
                          db.ForeignKey('charge.charge_id', ondelete="CASCADE", onupdate="CASCADE"),
                          nullable=True)

    # Relationships
    title = db.relationship("Title", back_populates="restrictions")
    charge = db.relationship("Charge", back_populates="restriction", uselist=False)

    # Methods
    def __init__(self, date, restriction_code, restriction_type, restriction_text, consenting_party, title_number):
        self.restriction_code = restriction_code.upper()
        self.restriction_type = restriction_type.upper()
        self.restriction_text = restriction_text
        if isinstance(consenting_party, dict):
            self.consenting_party = str(X500Name.from_dict(consenting_party))
        else:
            self.consenting_party = str(X500Name.from_string(consenting_party))
        self.restriction_date = datetime.now()  # date,  # TODO(parse to datetime)
        self.title_number = title_number

    @staticmethod
    def from_dict(dict_obj, title_number):
        r_code = dict_obj['restriction_id']
        r_type = dict_obj['restriction_type']
        r_text = dict_obj['restriction_text']
        r_date = dict_obj['date']
        if 'consenting_party_string' in dict_obj:
            consenting_party = str(X500Name.from_string(dict_obj['consenting_party_string']))
        else:
            consenting_party = str(X500Name.from_dict(dict_obj['consenting_party']))

        restriction = Restriction(r_date, r_code, r_type, r_text, consenting_party, title_number)

        if 'charge' in dict_obj and dict_obj['charge']:
            restriction.charge = Charge.from_dict(dict_obj['charge'], title_number)

        return restriction

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "restriction_id": self.restriction_code,
            "restriction_type": self.restriction_type,
            "restriction_text": self.restriction_text,
            "consenting_party": X500Name.from_string(self.consenting_party).as_dict(),
            "consenting_party_string": str(X500Name.from_string(self.consenting_party)),
            "date": self.restriction_date.isoformat(),
            "charge": self.charge.as_dict() if self.charge else None
        }


class Charge(db.Model):
    """Class representation of a Charge."""
    __tablename__ = 'charge'

    # Fields
    charge_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    charge_date = db.Column(db.DateTime, nullable=False, server_default=func.now())
    charge_lender = db.Column(db.String, nullable=False)
    charge_amount = db.Column(db.Float, nullable=False)
    charge_currency_type = db.Column(db.String, nullable=False)
    title_number = db.Column(db.String, db.ForeignKey('title.title_number'))
    # restriction_id = db.Column(db.String, db.ForeignKey('restriction.restriction_id'), nullable=True)

    # Relationships
    title = db.relationship("Title", back_populates="charges")
    restriction = db.relationship("Restriction", back_populates="charge", uselist=False)

    # Methods
    def __init__(self, charge_date, charge_lender, charge_amount, charge_currency_type, title_number):
        self.charge_date = datetime.now()  # charge_date  # TODO(parse to datetime)
        if isinstance(charge_lender, dict):
            self.charge_lender = str(X500Name.from_dict(charge_lender))
        else:
            self.charge_lender = str(X500Name.from_string(charge_lender))
        self.charge_amount = float(charge_amount)
        self.charge_currency_type = charge_currency_type.upper()
        self.title_number = title_number

    @staticmethod
    def from_dict(dict_obj, title_number):
        date = dict_obj['date']
        if 'lender_string' in dict_obj:
            lender = str(X500Name.from_string(dict_obj['lender_string']))
        else:
            lender = str(X500Name.from_dict(dict_obj['lender']))
        amount = dict_obj['amount']
        amount_currency_code = dict_obj.get('amount_currency_code')

        return Charge(date, lender, amount, amount_currency_code, title_number)

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "date": self.charge_date.isoformat(),
            "lender": X500Name.from_string(self.charge_lender).as_dict(),
            "lender_string": str(X500Name.from_string(self.charge_lender)),
            "amount": self.charge_amount,
            "amount_currency_code": self.charge_currency_type
        }
