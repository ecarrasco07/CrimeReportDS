CREATE TABLE Crime(
Call_Number         VARCHAR2(255),
Date_Time           VARCHAR2(255) NOT NULL,
Address             VARCHAR2(255) NOT NULL,   
Police_District     VARCHAR2(255),
Nature_of_Call      VARCHAR2(255),
Status              VARCHAR2(255) NOT NULL,
Latitude            FLOAT,
Longitude           FLOAT,
PRIMARY KEY (Date_Time, Address, Status)
);
