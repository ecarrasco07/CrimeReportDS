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

--Selecting all elements from the Calls table and copying them into Crime for backups(Logan)
INSERT INTO Crime SELECT * FROM Calls;
