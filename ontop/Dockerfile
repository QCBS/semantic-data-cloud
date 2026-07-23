FROM ontop/ontop:5.5.0

ARG DUCKDB_JDBC_VERSION="1.5.2.1"

USER root

RUN apt-get update && apt-get install -y ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/ontop/.duckdb \
    && chown -R ontop:ontop /opt/ontop/.duckdb

ADD "https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/${DUCKDB_JDBC_VERSION}/duckdb_jdbc-${DUCKDB_JDBC_VERSION}.jar" /opt/ontop/jdbc/

RUN chmod 644 "/opt/ontop/jdbc/duckdb_jdbc-${DUCKDB_JDBC_VERSION}.jar"

ENV CLASSPATH="/opt/ontop/jdbc/duckdb_jdbc-${DUCKDB_JDBC_VERSION}.jar:${CLASSPATH}"

USER ontop