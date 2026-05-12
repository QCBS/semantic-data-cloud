FROM ontop/ontop:5.5.0

USER root

ADD https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/1.5.2.1/duckdb_jdbc-1.5.2.1.jar /opt/ontop/jdbc/

ENV CLASSPATH="/opt/ontop/jdbc/duckdb_jdbc-1.5.2.1.jar:${CLASSPATH}"