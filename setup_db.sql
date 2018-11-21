
INSERT INTO "address" (address_id, house_name_or_number, street_name, city, county, country, postcode)
VALUES	(1, '1', 'Digital Street', 'Bristol', 'Avon', 'England', 'BS2 8EN'),

		(2, '10', 'Digital Street', 'Bristol', 'Avon', 'England', 'BS2 8EN'),
		(3, '11', 'Digital Street', 'Bristol', 'Avon', 'England', 'BS2 8EN'),

		(4, '20', 'Digital Street', 'Bristol', 'Avon', 'England', 'BS2 8EN'),
		(5, '21', 'Digital Street', 'Bristol', 'Avon', 'England', 'BS2 8EN'),

		(6, '30', 'Digital Street', 'Bristol', 'Avon', 'England', 'BS2 8EN'),
		(7, '31', 'Digital Street', 'Bristol', 'Avon', 'England', 'BS2 8EN'),
		(8, '32', 'Digital Street', 'Bristol', 'Avon', 'England', 'BS2 8EN');
ALTER SEQUENCE "address_address_id_seq" RESTART WITH 9;

INSERT INTO "owner" (identity, forename, surname, email, phone, owner_type, address_id)
VALUES	(1, 'Lisa', 'White', 'lisa.white@example.com', '07700900354', 'individual', 2),
		(2, 'David', 'Jones', 'david.jones@example.com', '07700900827', 'individual', 3),

		(3, 'Natasha', 'Powell', 'natasha.powell@example.com', '07700900027', 'individual', 4),
		(4, 'Samuel', 'Barnes', 'samuel.barnes@example.com', '07700900534', 'individual', 5),

		(5, 'Jim', 'Smith', 'jim.smith@example.com', '07700900815', 'individual', 6),
		(6, 'Martin', 'Keats', 'martin.keats@example.com', '07700900133', 'individual', 7),
		(7, 'Holly', 'Windsor', 'holly.windsor@example.com', '07700900970', 'individual', 8);

INSERT INTO "title" (title_number, owner_identity, address_id)
VALUES	('ZQV888860', 1, 1),
		('ZQV888861', 5, 6),
		('ZQV888862', 6, 7),
		('ZQV888863', 7, 8),
		('RTV237231', 1, 2),
		('RTV237232', 2, 3),
		('RTV237233', 3, 4),
		('RTV237234', 4, 5);

INSERT INTO "conveyancer" (conveyancer_id, x500_name, company_name)
VALUES	(1, 'O=Conveyancer1,L=Plymouth,C=GB', 'Conveyit4u'),
		(2, 'O=Conveyancer2,L=Plymouth,C=GB', 'Propertylaw.net');
ALTER SEQUENCE "conveyancer_conveyancer_id_seq" RESTART WITH 3;