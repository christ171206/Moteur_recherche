-- Migration script to add metadata column to documents table
-- Run this after updating the schema_v2.sql

USE moteur_recherche;

-- Add metadata column if it doesn't exist
SET @sql = (
    SELECT IF(
        (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
         WHERE TABLE_SCHEMA = DATABASE()
         AND TABLE_NAME = 'documents'
         AND COLUMN_NAME = 'metadata') = 0,
        'ALTER TABLE documents ADD COLUMN metadata JSON AFTER active',
        'SELECT "metadata column already exists"'
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;