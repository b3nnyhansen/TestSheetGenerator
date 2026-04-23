import json
import docker_db as ddb

CONFIG_DATA_PATH = "./data/config.json"
with open(CONFIG_DATA_PATH, "r") as f:
    CONFIG = json.load(f)

BASE_CHECK_QUERY = "SELECT * FROM {} WHERE {} = '{}';"
COURSE_TABLE_NAME = "courses"
COURSE_TABLE_ID_COLUMN = "course_id"
COURSE_TABLE_NAME_COLUMN = "course_name"
SUB_COURSE_TABLE_NAME = "sub_courses"
SUB_COURSE_TABLE_ID_COLUMN = "sub_course_id"
SUB_COURSE_TABLE_NAME_COLUMN = "sub_course_name"
QUESTION_TABLE_NAME = "essay_questions"
QUESTION_TABLE_ID_COLUMN = "question_id"
QUESTION_FETCH_QUERY = "SELECT {} FROM {} WHERE {} = {} ORDER BY RANDOM() LIMIT {};"
TEST_SHEET_TABLE_NAME = "essay_test_sheets"
TEST_SHEET_ID_COLUMN = "test_id"
TEST_SHEET_INSERT_QUERY = "INSERT INTO {} ({}) VALUES ({}) RETURNING {};"
TEST_SHEET_QUESTION_TABLE_NAME = "essay_test_sheet_questions"
TEST_SHEET_QUESTION_INSERT_QUERY = "INSERT INTO {} ({}, {}) VALUES ({}, {});"

def main():
    generate_test_from_config()

def generate_test_from_config():
    for config in CONFIG:
        course_name = config["course_name"]

        res, err = ddb.run_sql(
            BASE_CHECK_QUERY.format(
                COURSE_TABLE_NAME, COURSE_TABLE_NAME_COLUMN, course_name
            )
        )

        if err:
            print(f"Skipping {COURSE_TABLE_NAME_COLUMN} = '{course_name}' because of an error: {err}")
            continue
        
        try:
            course_id = res[0][0]
        except:
            print(f"Fail to fetch id from {COURSE_TABLE_NAME_COLUMN} = '{course_name}'. Skipping the insertion of test sheets.")
            continue
        
        res, err = ddb.run_sql(
            TEST_SHEET_INSERT_QUERY.format(
                TEST_SHEET_TABLE_NAME, COURSE_TABLE_ID_COLUMN, course_id, TEST_SHEET_ID_COLUMN
            )
        )

        if err:
            print(f"Fail to insert test for {COURSE_TABLE_NAME_COLUMN} = '{course_name}'. Skipping the insertion of test sheets.")
            continue

        print(f"Start generating test sheet content for {COURSE_TABLE_NAME_COLUMN} = '{course_name}'.")
        test_id = res[0][0]
        test_configs = config["test_configs"]
        for test_config in test_configs:
            sub_course_name = test_config["sub_course_name"]

            res, err = ddb.run_sql(
                BASE_CHECK_QUERY.format(
                    SUB_COURSE_TABLE_NAME, SUB_COURSE_TABLE_NAME_COLUMN, sub_course_name
                )
            )
            
            if err:
                print(f"Skipping {SUB_COURSE_TABLE_NAME_COLUMN} = '{sub_course_name}' because of an error: {err}")
                continue
            
            try:
                sub_course_id = res[0][0]
            except:
                print(f"Fail to fetch id from {SUB_COURSE_TABLE_NAME_COLUMN} = '{sub_course_name}'. Skipping the insertion of test sheet questions.")
                continue

            item_count = test_config["item_count"]
            res, err = ddb.run_sql(
                QUESTION_FETCH_QUERY.format(
                    QUESTION_TABLE_ID_COLUMN, QUESTION_TABLE_NAME,
                    SUB_COURSE_TABLE_ID_COLUMN, sub_course_id,
                    item_count
                )
            )

            if err:
                print(f"Fail to fetch id from {QUESTION_TABLE_NAME} for {SUB_COURSE_TABLE_NAME_COLUMN} = '{sub_course_name}'. Skipping the insertion of test sheet questions.")
                continue

            cur_count = 0
            for row in res:
                cur_count += 1
                question_id = row[0]
                _, err = ddb.run_sql(
                    TEST_SHEET_QUESTION_INSERT_QUERY.format(
                        TEST_SHEET_QUESTION_TABLE_NAME, TEST_SHEET_ID_COLUMN, QUESTION_TABLE_ID_COLUMN,
                        test_id, question_id
                    )
                )

                if err:
                    print(f"Failing to insert ({cur_count}/{item_count}) '{sub_course_name}' question for test sheet {{{test_id}}} because of an error: {err}")
                    continue
                print(f"Successfully inserting ({cur_count}/{item_count}) '{sub_course_name}' question for test sheet {{{test_id}}} into the database")

if __name__ == "__main__":
    main()