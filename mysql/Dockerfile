FROM mysql:8.0


COPY bbdd/creacion_bbdd.sql /docker-entrypoint-initdb.d/
RUN chmod -R 775 /docker-entrypoint-initdb.d

