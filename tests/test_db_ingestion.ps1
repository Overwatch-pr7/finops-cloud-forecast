# tests/test_db_ingestion.ps1
# This script verifies that the CSV ingestion was successful by counting the rows in the database.

$ContainerName = "finops-postgres"
$DbUser = "finops_user"
$DbName = "finops_db"

Write-Host "Running automated test: Verifying row count in cloud_billing table..."

# We execute a SQL query inside the container and get just the number back (using -t for tuples only)
$query = "SELECT COUNT(*) FROM cloud_billing;"
$rowCount = docker exec -i $ContainerName psql -U $DbUser -d $DbName -t -c $query

# Clean up whitespace from output (docker exec returns an array of lines. Trim works on strings so we gotta type cast it)
$rowCount = ($rowCount -join "").Trim()

if ([int]$rowCount -eq 365) {
    Write-Host "SUCCESS: Expected 365 rows, found $rowCount rows in the database." -ForegroundColor Green
} else {
    Write-Host "FAILURE: Expected 365 rows, but found $rowCount rows." -ForegroundColor Red
    exit 1
}
