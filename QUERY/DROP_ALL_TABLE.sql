-- Generate drop statements in correct dependency order
DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql += N'
PRINT ''Dropping ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + ''';
DROP TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) + ';'
FROM sys.tables
ORDER BY 
    CASE WHEN name IN ('User', 'Wallet') THEN 0 ELSE 1 END, -- Drop dependent tables first
    name;

EXEC sp_executesql @sql;
GO