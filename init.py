import pandas as pd
import docker_db as ddb

DF_TABLES = pd.read_csv("data/tables.csv").fillna("")
DF_TABLES

def main():
    for row in DF_TABLES.values:
        table_name, column_id_name, columns, foreign_keys, many_to_many_primary_keys = row
        queries = []

        table_contents = []
        if column_id_name:
            table_contents.append(f"\n  {column_id_name} SERIAL PRIMARY KEY")
        
        for column in columns.split("||"):
            column_name, column_datatype = column.split("|")
            table_contents.append(f"\n  {column_name} {column_datatype}")
        
        if many_to_many_primary_keys:
            pk_name, col_a, col_b = many_to_many_primary_keys.split("|")
            table_contents.append(f"\n  CONSTRAINT {pk_name} PRIMARY KEY ({col_a}, {col_b})")
        else:
            col_a = ""
        
        indexes_queries = []
        if foreign_keys:
            for foreign_key in foreign_keys.split("||"):
                fk_name, fk_column, fk_table = foreign_key.split("|")
                table_contents.append(f"\n  CONSTRAINT {fk_name} FOREIGN KEY ({fk_column}) REFERENCES {fk_table}({fk_column}) ON DELETE CASCADE")
                if fk_column != col_a:
                    indexes_queries.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{fk_column} ON {table_name}({fk_column});")
        
        queries.append(
            "CREATE TABLE IF NOT EXISTS {} (\n{}\n);".format(table_name, ",".join(table_contents))
        )
        queries.extend(indexes_queries)
        for query in queries:
            _, err = ddb.run_sql(query)
            if err:
                print(err)
            else:
                print(f"Successfully perform {query[:12]}...")
        

if __name__ == "__main__":
    main()