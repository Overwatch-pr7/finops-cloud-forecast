# db/run_db.ps1
# This script spins up the PostgreSQL Docker container, sets up a volume for the data,
# and executes the initialization SQL script.

$ContainerName = "finops-postgres"
$DbUser = "finops_user"
$DbPassword = "finops_password"
$DbName = "finops_db"
$Port = 5432

# Get the absolute path to the project root directory
$ProjectRoot = Resolve-Path "..\."

Write-Host "Checking if container '$ContainerName' is already running..."
# Stop and remove the container if it exists so we start fresh every time
docker rm -f $ContainerName 2>$null

Write-Host "Starting PostgreSQL container..."
# docker run command explained:
# --name: names our container
# -e: sets environment variables for Postgres (user, password, DB name)
# -p: maps the container port 5432 to our local host port 5432
# -v: mounts our local data directory to /data in the container
# -v: mounts our local db directory to /docker-entrypoint-initdb.d (will run on first start!) 
#     Wait, we will just manually run it for better control and debugging.
# -d: runs in detached mode (background)
# postgres:15-alpine is a lightweight image
$DockerArgs = @(
    "run", "--name", $ContainerName,
    "-e", "POSTGRES_USER=$DbUser",
    "-e", "POSTGRES_PASSWORD=$DbPassword",
    "-e", "POSTGRES_DB=$DbName",
    "-p", "$($Port):5432",
    "-v", "$($ProjectRoot.Path)\data:/data",
    "-d", "postgres:15-alpine"
)
docker @DockerArgs

Write-Host "Waiting for database to start up (giving it 5 seconds)..."
Start-Sleep -Seconds 5

Write-Host "Executing SQL ingestion script..."
# docker exec command runs a command inside the running container
# psql -U ... connects to the DB using the user we created
# -f /db_script.sql executes our script 
# (Wait, we need to pass the script in, we can map it via a second -v flag, or pipe it in)

# Let's pipe the SQL script directly into the container's psql command
cat ".\init_schema.sql" | docker exec -i $ContainerName psql -U $DbUser -d $DbName

Write-Host "Database is ready on localhost:$Port! Data has been ingested."
Write-Host "Credentials: User=$DbUser, Password=$DbPassword, DB=$DbName"
