FROM postgres:latest

COPY init.sql /docker-entrypoint-initdb.d/init.sql

RUN apt-get update && apt-get install -y sed gettext-base && rm -rf /var/lib/apt/lists/*

ARG DB_REPL_USER
ARG DB_REPL_PASSWORD
ARG DB_DATABASE
ARG DB_PORT

RUN mkdir -p /var/lib/postgresql/data/pg_archive/ \
    && chown postgres:postgres /var/lib/postgresql/data/pg_archive/

RUN sed -i "s/\${DB_REPL_USER}/${DB_REPL_USER}/g" /docker-entrypoint-initdb.d/init.sql \
    && sed -i "s/\${DB_REPL_PASSWORD}/${DB_REPL_PASSWORD}/g" /docker-entrypoint-initdb.d/init.sql \
    && sed -i "s/\${DB_DATABASE}/${DB_DATABASE}/g" /docker-entrypoint-initdb.d/init.sql \
    && sed -i "s/\${DB_PORT}/${DB_PORT}/g" /docker-entrypoint-initdb.d/init.sql

RUN echo "listen_addresses = '*'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "port = ${DB_PORT}" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "archive_mode = on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "archive_command = 'mkdir -p /var/lib/postgresql/data/pg_archive/ && cp %p /var/lib/postgresql/data/pg_archive/%f'" >> /var/lib/postgresql/data/postgresql.conf.sample \
    && echo "log_destination = 'stderr'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "logging_collector = on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "log_directory = '/var/log/postgresql/'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "log_filename = 'postgresql.log'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "max_wal_senders=10" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "wal_level=replica" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "wal_log_hints = on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "hot_standby=on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "max_replication_slots=10" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "hot_standby_feedback=on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "log_replication_commands=on" >> /usr/share/postgresql/postgresql.conf.sample

RUN echo "host replication all 11.0.0.0/24 md5" >> /var/lib/postgresql/data/pg_hba.conf

EXPOSE $DB_PORT
