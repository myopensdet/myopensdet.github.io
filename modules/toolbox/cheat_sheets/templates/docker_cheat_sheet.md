<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Docker cheat sheet for testers

An **image** is the packed app. A **container** is one running copy of it. Testers mostly start what the team built, look inside when something fails, and clean up.

## Start and stop

| You want | Write |
| --- | --- |
| Start a database for tests, in the background | `docker run -d --name test-db -e POSTGRES_PASSWORD=local_only_password -p 5433:5432 postgres:17` |
| Start, and delete it when it stops | `docker run --rm -d --name test-db -p 5433:5432 -e POSTGRES_PASSWORD=local_only_password postgres:17` |
| What's running | `docker ps` |
| Everything, also stopped | `docker ps -a` |
| Stop it | `docker stop test-db` |
| Start it again | `docker start test-db` |
| Delete a stopped container | `docker rm test-db` |

`-p 5433:5432` means: port 5433 on **your** computer goes to port 5432 **inside** the container. Pick a free port on the left.

## Look inside

| You want | Write |
| --- | --- |
| Its logs | `docker logs test-db` |
| Follow new log lines | `docker logs -f --tail 50 test-db` |
| Run a command inside | `docker exec -it test-db psql -U postgres` |
| A shell inside | `docker exec -it test-db sh` |
| Its settings, ports, health | `docker inspect test-db` |
| CPU and memory | `docker stats --no-stream` |

## Images

| You want | Write |
| --- | --- |
| Download an image | `docker pull postgres:17` |
| Build one from a Dockerfile here | `docker build -t shop-tests .` |
| List images | `docker images` |

Pin a version (`postgres:17`), not `latest`: tests should get the same database every run.

## Docker Compose (several containers together)

| You want | Write |
| --- | --- |
| Start everything in `docker-compose.yml` | `docker compose up -d` |
| Start, and wait until healthy | `docker compose up -d --wait` |
| What's running | `docker compose ps` |
| Logs of one service | `docker compose logs -f api` |
| Stop and remove | `docker compose down` |
| Stop, remove, **and delete the data** | `docker compose down -v` |

## Clean up (careful)

| You want | Write |
| --- | --- |
| How much space Docker uses | `docker system df` |
| Remove stopped containers | `docker container prune` |
| Remove unused images | `docker image prune` |

Prune commands ask before deleting. They remove **everyone's** stopped containers and unused images on that computer, not only yours: on a shared machine, ask first.
