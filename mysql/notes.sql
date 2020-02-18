create schema UMiami;

use umiami;

select * from generator;
describe generator;
select count(datetimeSampled) from generator;

select * from fawn;
describe fawn;
select count(datetimeSampled) from fawn;


select * from users;

select * from userspk;

select * from userscompositepk;

INSERT INTO Generator (FAWN_Station, Observation_Time, 60cm_T_air___F__, dateTimeSampled) 
VALUES ('Homestead', 'Mar 1 2007  12:15 AM', '70.39', '2007-03-01 00:15:00');

INSERT INTO Generator (FAWN_Station, Observation_Time, 60cm_T_air___F__, 2m_T_air___F__, 
    10m_T_air___F__, __10cm_T_soil___F__, 2m_DewPt___F__, 2m_Rel_Hum___pct__, 2m_Rain___in__, 
    2m_SolRad___w__m__2__, 10m_Wind___mph__, 10m_Wind_min___mph__, 10m_Wind_max___mph__, 
    10m_WDir___deg__, BP___mb__, 2m_WetBulb___F__, dateTimeSampled) 
VALUES ('Homestead', 'Mar 1 2007  12:15 AM', '70.39', '70.79', 
'70.5', '68.68', '68.12', '91.0', '0.0', 
'1.16', NULL, NULL, NULL, 
'102.9', NULL, '68.96', '2007-03-01 00:15:00');
