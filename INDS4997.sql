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

INSERT INTO Crime SELECT * FROM Calls;


CREATE TABLE Historic_Real_Estate(
PropertyID          VARCHAR2(255),
PropType            VARCHAR2(255),
Address             VARCHAR2(255),
District            INT,
Sale_Date           DATE,
Sale_Price          INT
);
