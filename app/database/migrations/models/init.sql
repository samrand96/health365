-- upgrade --
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(50) NOT NULL,
    "last_name" VARCHAR(50),
    "email" VARCHAR(50) NOT NULL UNIQUE,
    "password_hash" VARCHAR(128) NOT NULL,
    "mobile_number" VARCHAR(13) UNIQUE,
    "status" VARCHAR(50),
    "role" VARCHAR(50) NOT NULL,
    "is_active" BOOL DEFAULT False
);
CREATE TABLE IF NOT EXISTS "usertoken" (
    "token" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);

insert into "user" (
     first_name,
     last_name,
     email,
     password_hash,
     mobile_number,
     status,
     roles,
     is_active
)
values (
    "Samrad",
    "Hassan",
    "samrand96@gmail.com",
    "$2a$12$839ekk0oVfcX5SM5r.LfIeO/SRmKlEi79JKHlH4rDjzzCcMIHVoN6",
    "07511646852",
    "active",
    "admin",
    true
);