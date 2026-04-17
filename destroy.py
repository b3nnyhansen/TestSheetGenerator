import docker_db as ddb

def main():
    _, __ = ddb.run_sql("DROP SCHEMA public CASCADE;")
    _, __ = ddb.run_sql("CREATE SCHEMA public;")
    _, __ = ddb.run_sql("GRANT ALL ON SCHEMA public TO postgres;")
    _, __ = ddb.run_sql("GRANT ALL ON SCHEMA public TO public;")

if __name__ == "__main__":
    main()