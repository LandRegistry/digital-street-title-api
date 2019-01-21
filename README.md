# HM Land Registry Digital Street Proof of Concept - Title API

## Available routes

|Route|What it does|
|---|---|
|**GET** /health|Returns some basic information about the app|
|**GET** /health/cascade/\<depth\>|Returns the app's health information as above but also the health information of any database and HTTP dependencies, down to the specified depth|
|**GET** /v1/titles?owner_email_address=\<owner_email_address\>|Retrieve a list of Titles for a specific Owner's email address|
|**GET** /v1/titles/\<title_number\>|Retrieve a specific Title|
|**PUT** /v1/titles/\<title_number\>|Updates a specific Title|
|**PUT** /v1/titles/\<title_number\>/lock|Locks a specific Title|
|**PUT** /v1/titles/\<title_number\>/unlock|Unlocks a specific Title|
|**GET** /v1/owners/?email_address=\<email_address\>|Retrieve a specific Owner by their email address|
|**GET** /v1/conveyancers/|Retrieve a list of Conveyancers|
|**GET** /v1/conveyancers/\<conveyancer_id\>|Retrieve a specific Conveyancer|

Refer to [OpenAPI Specification](openapi.json) for full details.

## Database Schema

The `titledb` database is set up as follows:

```sql
                     List of relations
 Schema |              Name              |   Type   | Owner 
--------+--------------------------------+----------+-------
 public | address                        | table    | root
 public | address_address_id_seq         | sequence | root
 public | alembic_version                | table    | root
 public | conveyancer                    | table    | root
 public | conveyancer_conveyancer_id_seq | sequence | root
 public | owner                          | table    | root
 public | title                          | table    | root
```

### Address table

```sql
                                         Table "public.address"
        Column        |       Type        |                          Modifiers                           
----------------------+-------------------+--------------------------------------------------------------
 address_id           | integer           | not null default nextval('address_address_id_seq'::regclass)
 house_name_or_number | character varying | not null
 street_name          | character varying | not null
 city                 | character varying | not null
 county               | character varying | not null
 country              | character varying | not null
 postcode             | character varying | not null
Indexes:
    "address_pkey" PRIMARY KEY, btree (address_id)
Referenced by:
    TABLE "owner" CONSTRAINT "owner_address_id_fkey" FOREIGN KEY (address_id) REFERENCES address(address_id)
    TABLE "title" CONSTRAINT "title_address_id_fkey" FOREIGN KEY (address_id) REFERENCES address(address_id) ON UPDATE CASCADE ON DELETE CASCADE
```

### Conveyancer table

```sql
                                        Table "public.conveyancer"
     Column     |       Type        |                              Modifiers                               
----------------+-------------------+----------------------------------------------------------------------
 conveyancer_id | integer           | not null default nextval('conveyancer_conveyancer_id_seq'::regclass)
 x500_name      | character varying | not null
 company_name   | character varying | not null
Indexes:
    "conveyancer_pkey" PRIMARY KEY, btree (conveyancer_id)
    "conveyancer_x500_name_key" UNIQUE CONSTRAINT, btree (x500_name)
```

### Owner table

```sql
            Table "public.owner"
   Column   |       Type        | Modifiers 
------------+-------------------+-----------
 identity   | integer           | not null
 forename   | character varying | not null
 surname    | character varying | not null
 email      | character varying | not null
 phone      | character varying | not null
 owner_type | character varying | not null
 address_id | integer           | not null
Indexes:
    "owner_pkey" PRIMARY KEY, btree (identity)
    "ix_owner_email" UNIQUE, btree (email)
Foreign-key constraints:
    "owner_address_id_fkey" FOREIGN KEY (address_id) REFERENCES address(address_id)
Referenced by:
    TABLE "title" CONSTRAINT "title_identity_fkey" FOREIGN KEY (identity) REFERENCES owner(identity)
```

### Title table

```sql
                        Table "public.title"
    Column    |            Type             |       Modifiers        
--------------+-----------------------------+------------------------
 title_number | character varying           | not null
 created_at   | timestamp without time zone | not null default now()
 updated_at   | timestamp without time zone | 
 lock         | timestamp without time zone | 
 identity     | integer                     | not null
 address_id   | integer                     | not null
Indexes:
    "title_pkey" PRIMARY KEY, btree (title_number)
Foreign-key constraints:
    "title_address_id_fkey" FOREIGN KEY (address_id) REFERENCES address(address_id) ON UPDATE CASCADE ON DELETE CASCADE
    "title_identity_fkey" FOREIGN KEY (identity) REFERENCES owner(identity)
```

## Pre-populated Data

This application uses a Postgres database. To populate it, run the following command from the common-dev-env folder:

```shell
bashin title-api
make db
```

### Addresses

|ID|House name or number|Street name|City or town|County|Country|Postcode|
|---|---|---|---|---|---|---|
|1|1|Digital Street|Bristol|Avon|England|BS2 8EN|
|2|10|Digital Street|Bristol|Avon|England|BS2 8EN|
|3|11|Digital Street|Bristol|Avon|England|BS2 8EN|
|4|20|Digital Street|Bristol|Avon|England|BS2 8EN|
|5|21|Digital Street|Bristol|Avon|England|BS2 8EN|
|6|30|Digital Street|Bristol|Avon|England|BS2 8EN|
|7|31|Digital Street|Bristol|Avon|England|BS2 8EN|
|8|32|Digital Street|Bristol|Avon|England|BS2 8EN|

### Conveyancers

|ID|X500 name|Company name|
|---|---|---|
|1|O=Conveyancer1,L=Plymouth,C=GB|Conveyit4u|
|2|O=Conveyancer2,L=Plymouth,C=GB|Propertylaw.net|

### Owners

|ID|First name|Last name|Email address|Phone number|Type|Address ID|
|---|---|---|---|---|---|---|
|1|Lisa|White|lisa.white@example.com|07700900354|individual|2|
|2|David|Jones|david.jones@example.com|07700900827|individual|3|
|3|Natasha|Powell|natasha.powell@example.com|07700900027|individual|4|
|4|Samuel|Barnes|samuel.barnes@example.com|07700900534|individual|5|
|5|Jim|Smith|jim.smith@example.com|07700900815|individual|6|
|6|Martin|Keats|martin.keats@example.com|07700900133|individual|7|
|7|Holly|Windsor|holly.windsor@example.com|07700900970|individual|8|

### Titles

|Title number|Owner ID|Address ID|
|---|---|---|
|ZQV888860|1|1|
|ZQV888861|5|6|
|ZQV888862|6|7|
|ZQV888863|7|8|
|RTV237231|1|2|
|RTV237232|2|3|
|RTV237233|3|4|
|RTV237234|4|5|

## Quick start

### Docker

This app supports the Land Registry [common development environment](https://github.com/LandRegistry/common-dev-env) so adding the following to your dev-env config file is enough:

```yaml
  title-api:
    repo: git@github.com:LandRegistry/digital-street-title-api.git
    branch: master
```

The Docker image it creates (and runs) will install all necessary requirements and set all environment variables for you.
