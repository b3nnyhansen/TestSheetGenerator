from pathlib import Path
import json
import docker_db as ddb
import utility as util

BASE_CHECK_QUERY = "SELECT * FROM {} WHERE {} = '{}';"
COURSE_DATA_PATH = "./data/courses.txt"
COURSE_INSERT_QUERY = "INSERT INTO {} ({}) VALUES ('{}');"
COURSE_ID_COLUMN = "course_id"
COURSE_NAME_COLUMN = "course_name"
QUESTION_DATA_PATH = "./data/questions.json"
QUESTION_TEXT_COLUMN = "question_text"
QUESTION_CHECKSUM_COLUMN = "checksum"
QUESTION_INSERT_QUERY = "INSERT INTO {} ({}, {}, {}) VALUES ({}, '{}', '{}');"

def main():
    insert_course_data()
    insert_question_data()

def insert_course_data():
    table_name = Path(COURSE_DATA_PATH).stem
    with open(COURSE_DATA_PATH, "r") as f:
        items = f.read().split(";")
        for item in items:
            res, err = ddb.run_sql(BASE_CHECK_QUERY.format(table_name, COURSE_NAME_COLUMN, item))
            if err:
                print(f"Skipping '{item}' because of an error: {err}")
                continue
            
            if res:
                print(f"Skipping '{item}' because it's already inserted")
                continue

            _, err = ddb.run_sql(COURSE_INSERT_QUERY.format(table_name, COURSE_NAME_COLUMN, item))
            if err:
                print(f"Failing to insert '{item}' because of an error: {err}")
                continue

            print(f"Successfully inserting course '{item}' into the database")

def insert_question_data():
    course_table_name = Path(COURSE_DATA_PATH).stem

    with open(QUESTION_DATA_PATH, "r") as f:
        data = json.load(f)
    
    for question_table_name in data.keys():
        items = data[question_table_name]
        
        for item in items:
            foreign_key_name = item[COURSE_NAME_COLUMN]
            res, err = ddb.run_sql(BASE_CHECK_QUERY.format(course_table_name, COURSE_NAME_COLUMN, foreign_key_name))
            
            if err:
                print(f"Aborting insertion from '{foreign_key_name}' in '{question_table_name}' because of an error: {err}")
                continue

            course_id = res[0][0]
            texts = item[QUESTION_TEXT_COLUMN]
            
            cur_count = 0
            item_count = len(texts)
            for text in texts:
                cur_count += 1
                checksum = util.get_text_hash(
                    ":".join([foreign_key_name, text])
                )

                check, err = ddb.run_sql(BASE_CHECK_QUERY.format(question_table_name, QUESTION_CHECKSUM_COLUMN, checksum))
                if err:
                    print(f"Skipping ({cur_count}/{item_count}) question(s) for '{foreign_key_name}' because of an error: {err}")
                    continue

                if check:
                    print(f"Skipping ({cur_count}/{item_count}) question(s) for '{foreign_key_name}' because it's already inserted")
                    continue

                _, err = ddb.run_sql(
                    QUESTION_INSERT_QUERY.format(
                        question_table_name,
                        COURSE_ID_COLUMN, QUESTION_TEXT_COLUMN, QUESTION_CHECKSUM_COLUMN,
                        course_id, text, checksum
                    )
                )

                if err:
                    print(f"Failing to insert ({cur_count}/{item_count}) question(s) for '{foreign_key_name}' because of an error: {err}")
                    continue
                print(f"Successfully inserting ({cur_count}/{item_count}) question(s) for '{foreign_key_name}' into the database")

if __name__ == "__main__":
    main()