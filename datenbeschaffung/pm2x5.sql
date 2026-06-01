

create table  PM2x5 (
Station varchar (20),
Datum date,
Stunde integer,
PM2x5 double precision
);

select count(*) from pm2x5;

alter table schadstoffwetter
add column pm2x5 double precision;

update schadstoffwetter
set pm2x5 = pm2x5.pm2x5 
from pm2x5 
where schadstoffwetter.datum = pm2x5.datum
and schadstoffwetter.stunde = pm2x5.stunde;



SELECT A.datum, A.stunde
FROM pm2x5 A
LEFT JOIN schadstoffwetter B 
  ON A.datum = B.datum AND A.stunde = B.stunde
WHERE B.datum IS NULL;


