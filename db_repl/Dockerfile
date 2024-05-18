FROM postgres:latest

ARG DB_REPL_HOST
ARG DB_REPL_PORT
ARG DB_REPL_USER
ARG DB_REPL_PASSWORD
ARG DB_PORT
ARG DB_HOST

RUN echo "listen_addresses = '*'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "port = ${DB_REPL_PORT}" >> /usr/share/postgresql/postgresql.conf.sample

RUN echo "#!/bin/bash" > /usr/local/bin/initrep.sh \
    && echo "rm -rf /var/lib/postgresql/data/*" >> /usr/local/bin/initrep.sh \
    && echo "PGPASSWORD=${DB_REPL_PASSWORD} pg_basebackup -h ${DB_HOST} -U ${DB_REPL_USER} -D /var/lib/postgresql/data --wal-method=stream --write-recovery-conf" >> /usr/local/bin/initrep.sh \
    && echo "echo 'Starting replication'" >> /usr/local/bin/initrep.sh \
    && echo "chown -R postgres:postgres /var/lib/postgresql/data" >> /usr/local/bin/initrep.sh \
    && echo "chmod 700 /var/lib/postgresql/data" >> /usr/local/bin/initrep.sh \
    && echo "su - postgres -c '/usr/lib/postgresql/16/bin/postgres -D /var/lib/postgresql/data'" >> /usr/local/bin/initrep.sh

RUN chmod +x /usr/local/bin/initrep.sh

CMD ["/usr/local/bin/initrep.sh"]
