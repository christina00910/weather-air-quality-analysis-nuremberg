WITH lücken_identifiziert AS (
    SELECT 
        datum,
        stunde,
        NO2,
        COUNT(CASE WHEN NO2 IS NOT NULL THEN 1 END) 
            OVER(ORDER BY datum, stunde) AS lücken_gruppe
    FROM schadstoffwetter
),
lücken_gruppen_details AS (
    -- 2. Gruppiert die zusammenhängenden NULL-Werte
    SELECT 
        lücken_gruppe,
        MIN(datum) AS start_datum,
        MIN(stunde) AS start_stunde,
        MAX(datum) AS ende_datum,
        MAX(stunde) AS ende_stunde,
        COUNT(*) AS lücken_größe_stunden
    FROM lücken_identifiziert
    WHERE NO2 IS NULL
    GROUP BY lücken_gruppe
)
-- 3. Ausgabe sortiert nach der Größe der Lücke (größte Lücken zuerst)
SELECT 
    start_datum,
    ende_datum,
    lücken_größe_stunden
FROM lücken_gruppen_details
ORDER BY lücken_größe_stunden DESC;