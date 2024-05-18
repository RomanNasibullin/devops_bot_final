CREATE USER ${DB_REPL_USER} WITH REPLICATION LOGIN PASSWORD '${DB_REPL_PASSWORD}';

\connect ${DB_DATABASE};

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE
);

INSERT INTO emails (email) VALUES ('roman@mail.ru'), ('ptstart@yandex.com');

INSERT INTO phones (phone_number) VALUES ('+78124955252'), ('+73552812125');
