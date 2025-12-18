# BMSTU Absolute Cinema

![Absolute Cinema](https://images.steamusercontent.com/ugc/10636923113798537174/A00D5523123A37A47F4651EA9C567159C890239C/?imw=512&&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false)

# What is this?

This is a final project for BMSTU's "Data Bases" subject. It is an information system for managing
a cinema unit. It is written in **Python 3.13** using __Flask__ framework, with MySQL as DB backend
and Redis for cache. It also uses NodeJS + Tailwind CSS for styling at build time.

# Why Tailwind CSS?

I use Tailwind because I like its syntax and I find it easier to use for consistent styles than CSS variables.
Other than that there is no good reason, it's purely cosmetical and I don't use any extensions or custom styles.

# Build & Run

## Setup

Keep in mind that this repo does not include multiple files needed to actually run the project such as `.env`
, `mysql-init` folder with DB schema and procedures and `data` with configs.

All configs like access to DB and Redis are managed via environment variables, including paths to them.
If you're not from BMSTU and have no idea what kind of configuration there is - good luck, see the code
for reference.

## Dev

To run this project in dev mode:
1. DB: `docker container start mysql:8.2.0`
2. Redis: `docker container start redis:latest`
3. __(optional)__ Tailwind hot reload: `npm run watch`, blocks the CLI so run in a separate terminal
4. App: `python -m app`

## Production

To run this project in prod:
1. Docker Compose: `docker-compose up --remove-orphans --force-recreate --build -d`
2. That's all, it's just Docker magic

The app uses Gunicorn for production.
