from pathlib import Path
import json
import docker_db as ddb
import utility as util

CONTENT_DATA_PATH = "./data/content.json"
with open(CONTENT_DATA_PATH, "r") as f:
    CONTENT = json.load(f)

BASE_CHECK_QUERY = "SELECT * FROM {} WHERE {} = '{}';"
COURSE_TABLE_NAME = "courses"
COURSE_TABLE_NAME_COLUMN = "course_name"
SUB_COURSE_TABLE_NAME = "sub_courses"
SUB_COURSE_TABLE_ID_COLUMN = "sub_course_id"
SUB_COURSE_TABLE_NAME_COLUMN = "sub_course_name"
COURSE_INSERT_QUERY = "INSERT INTO {} ({}) VALUES ('{}');"
QUESTION_TABLE_TEXT_COLUMN = "question_text"
QUESTION_TABLE_CHECKSUM_COLUMN = "checksum"
QUESTION_INSERT_QUERY = "INSERT INTO {} ({}, {}, {}) VALUES ({}, '{}', '{}');"

def main():
    insert_content_data()

def insert_content_data():
    for question_table_name in CONTENT:
        items = CONTENT[question_table_name]
        for item in items:
            course_name = item["course_name"]
            res, err = ddb.run_sql(
                BASE_CHECK_QUERY.format(
                    COURSE_TABLE_NAME, COURSE_TABLE_NAME_COLUMN, course_name
                )
            )

            if err:
                print(f"Skipping {COURSE_TABLE_NAME_COLUMN} = '{course_name}' because of an error: {err}")
                continue
            
            if not res:
                _, err = ddb.run_sql(COURSE_INSERT_QUERY.format(COURSE_TABLE_NAME, COURSE_TABLE_NAME_COLUMN, course_name))
                if err:
                    print(f"Failing to insert {COURSE_TABLE_NAME_COLUMN} = '{course_name}' because of an error: {err}")
                    continue

                print(f"Successfully inserting {COURSE_TABLE_NAME_COLUMN} = '{course_name}' into the database")

            questions = item["questions"]
            for question in questions:
                sub_course_name = question["sub_course_name"]
                res, err = ddb.run_sql(
                    BASE_CHECK_QUERY.format(
                        SUB_COURSE_TABLE_NAME, SUB_COURSE_TABLE_NAME_COLUMN, sub_course_name
                    )
                )

                if err:
                    print(f"Skipping {SUB_COURSE_TABLE_NAME_COLUMN} = '{sub_course_name}' because of an error: {err}")
                    continue
                
                if not res:
                    _, err = ddb.run_sql(COURSE_INSERT_QUERY.format(SUB_COURSE_TABLE_NAME, SUB_COURSE_TABLE_NAME_COLUMN, sub_course_name))
                    if err:
                        print(f"Failing to insert {SUB_COURSE_TABLE_NAME_COLUMN} = '{sub_course_name}' because of an error: {err}")
                        continue

                    print(f"Successfully inserting {SUB_COURSE_TABLE_NAME_COLUMN} = '{sub_course_name}' into the database")
                
                    res, err = ddb.run_sql(
                        BASE_CHECK_QUERY.format(
                            SUB_COURSE_TABLE_NAME, SUB_COURSE_TABLE_NAME_COLUMN, sub_course_name
                        )
                    )
                
                try:
                    sub_course_id = res[0][0]
                except:
                    print(f"Fail to fetch id from {SUB_COURSE_TABLE_NAME_COLUMN} = '{sub_course_name}'. Skipping the insertion of questions.")
                    continue

                texts = question["question_text"]
                cur_count = 0
                item_count = len(texts)
                for text in texts:
                    cur_count += 1
                    checksum = util.get_text_hash(
                        ":".join([sub_course_name, text])
                    )

                    check, err = ddb.run_sql(BASE_CHECK_QUERY.format(question_table_name, QUESTION_TABLE_CHECKSUM_COLUMN, checksum))
                    if err:
                        print(f"Skipping the ({cur_count}/{item_count}) question for '{sub_course_name}' because of an error: {err}")
                        continue

                    if check:
                        print(f"Skipping ({cur_count}/{item_count}) question for '{sub_course_name}' because it's already inserted")
                        continue

                    _, err = ddb.run_sql(
                        QUESTION_INSERT_QUERY.format(
                            question_table_name,
                            SUB_COURSE_TABLE_ID_COLUMN, QUESTION_TABLE_TEXT_COLUMN, QUESTION_TABLE_CHECKSUM_COLUMN,
                            sub_course_id, text, checksum
                        )
                    )

                    if err:
                        print(f"Failing to insert ({cur_count}/{item_count}) question for '{sub_course_name}' because of an error: {err}")
                        continue
                    print(f"Successfully inserting ({cur_count}/{item_count}) question for '{sub_course_name}' into the database")

if __name__ == "__main__":
    main()