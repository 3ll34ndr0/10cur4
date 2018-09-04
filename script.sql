-- Costruir las tablas
CREATE TABLE SUPLIER (SNO INTEGER, SNAME CHAR(127), CITY CHAR(127), PRIMARY KEY (SNO));
CREATE TABLE SELLS (SNO INTEGER, PNO INTEGER);
CREATE TABLE PART (PNO INTEGER, PNAME CHAR(127), PRICE FLOAT, PRIMARY KEY (PNO));

-- Agrego las columnas que faltan
ALTER TABLE SELLS ADD COLUMN SDATE Date;
ALTER TABLE SELLS ADD COLUMN SQUANTITY Integer;

-- Empiezo a poblarlas
INSERT INTO SUPPLIER VALUES (1, 'Smith', 'London');
INSERT INTO SUPPLIER VALUES (2, 'Jones', 'Paris');
INSERT INTO SUPPLIER VALUES (3, 'Adams', 'Vienna');
INSERT INTO SUPPLIER VALUES (4, 'Blake', 'Rome');
INSERT INTO PART VALUES (1, 'Tornillos', 10); 
INSERT INTO PART VALUES (2, 'Tuercas', 8); 
INSERT INTO PART VALUES (3, 'Cerrojos', 15); 
INSERT INTO PART VALUES (4, 'Levas', 25); 
INSERT INTO SELLS VALUES (1, 1, NULL, NULL); 
INSERT INTO SELLS VALUES (1, 2, NULL, NULL); 
INSERT INTO SELLS VALUES (2, 4, NULL, NULL); 
INSERT INTO SELLS VALUES (3, 1, NULL, NULL); 
INSERT INTO SELLS VALUES (3, 3, NULL, NULL); 
INSERT INTO SELLS VALUES (4, 2, NULL, NULL); 
INSERT INTO SELLS VALUES (4, 3, NULL, NULL); 
INSERT INTO SELLS VALUES (4, 4, NULL, NULL);


-- Consultas
-- Obtener las ciudades donde existen proveedores.
 
SELECT CITY
FROM SUPPLIER;

--Obtener los nombres de los proveedores que no son de Roma.
 
SELECT SNAME
FROM SUPPLIER
WHERE CITY !='Rome';


-- Obtener los números y nombres de las partes cuyo precio es mayor a 10.
SELECT PNO, PNAME
FROM PART
WHERE PRICE > 10;


-- Obtener los nombres de los proveedores que venden la pieza número 1.
SELECT SNAME
FROM SUPPLIER, SELLS
WHERE 
PNO=1 AND
SELLS.SNO = SUPPLIER.SNO; -- agrego los nombres de las tablas para evitar ambiguedad.

-- Obtener los nombres de los proveedores que nos proveen piezas que se vendieron en agosto del 2013.

select supplier.sname
from sells, supplier 
where extract(month from sdate) = '08' 
  and extract(year from sdate) = '2013'
  and sells.sno=supplier.sno
group by supplier.sname;

-- Obtener los nombres de los proveedores que nos proveen piezas cuyo nombre empiece
con 'T'.
SELECT SNAME
FROM SUPPLIER
WHERE SNAME LIKE 'T%' ;


-- Obtener el precio promedio de las piezas.
SELECT AVG(PRICE)
FROM PART;

-- Obtener el número y el nombre de la pieza más cara.
SELECT MAX(PRICE)
FROM PART -- TODO: Falta el nombre de ese producto 


-- Escribir las sentencias UPDATE para modificar la fecha de venta al día de hoy. Y la cantidad vendida a 10 artículos en cada venta.
 
UPDATE SELLS
SET SDATE='20180831';
 
UPDATE SELLS
SET SQUANTITY=10;
