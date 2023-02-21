CREATE TABLE Crime(
Call_Number         VARCHAR2(255),
Date_Time           VARCHAR2(255),
Address             VARCHAR2(255),   
Police_District     VARCHAR2(255),
Nature_of_Call      VARCHAR2(255),
Status              VARCHAR2(255),
Latitude            FLOAT,
Longitude           FLOAT
);

TRUNCATE TABLE Crime;
INSERT INTO Crime SELECT * FROM Calls;


CREATE TABLE Historic_Real_Estate(
PropertyID          VARCHAR2(255),
PropType            VARCHAR2(255),
Address             VARCHAR2(255),
District            INT,
Sale_Date           VARCHAR2(255),
Sale_Price          INT
);

CREATE TABLE Historic_Crime(
Call_Number         VARCHAR2(255),
Date_Time           VARCHAR2(255),
Reported_Year       INT,
Reported_Month      INT,
Address             VARCHAR2(255),
Weapon_Used         VARCHAR2(255),
ALD                 INT,
NSP                 INT,
Distric             INT,
TRACT               INT,
WARD                INT,
ZIP                 INT,
RoughX              VARCHAR2(255),
RoughY              VARCHAR2(255),
Arson               INT,
AssaultOffense      INT,
Burglary            INT,
CriminalDamage      INT,
Homicide            INT,
LockedVehicle	    INT,
Robbery	            INT,
SexOffense	        INT,
Theft	            INT,
VehicleTheft        INT
);

