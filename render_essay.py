import json
import docker_db as ddb
import utility as util
import subprocess

util.makedirs("./output/")
DATETIME_STRING = util.get_current_timestamp()
BASE_MD_OUTPUT_FILENAME = "./output/{}_{}.md"
BASE_DOCX_OUTPUT_FILENAME = "./output/{}_{}.docx"

BASE_MD_YAML_BLOCK = """---
papersize: a4
geometry:
- margin=1cm
- top=1cm
- bottom=1cm
---
"""

CONFIG_DATA_PATH = "./data/config.json"
with open(CONFIG_DATA_PATH, "r") as f:
    CONFIG = json.load(f)

BASE_CHECK_QUERY = "SELECT * FROM {} WHERE {} = '{}';"
COURSE_TABLE_NAME = "courses"
COURSE_TABLE_ID_COLUMN = "course_id"
COURSE_TABLE_NAME_COLUMN = "course_name"
QUESTION_TABLE_NAME = "essay_questions"
QUESTION_TABLE_ID_COLUMN = "question_id"
QUESTION_TABLE_TEXT_COLUMN = "question_text"
TEST_AND_QUESTION_TABLE = "essay_test_sheet_questions"
TEST_SHEET_TABLE_NAME = "essay_test_sheets"
TEST_SHEET_ID_COLUMN = "test_id"
BASE_FETCH_ID_QUERY = "SELECT {} FROM {} WHERE {} = {} ORDER BY RANDOM() LIMIT 1;"
BASE_FETCH_MANY_QUERY = "SELECT {} FROM {} a JOIN (SELECT * FROM {} WHERE {} = {}) b ON a.{} = b.{} ORDER BY RANDOM();"

def main():
    render_test_from_config()

def render_test_from_config():
    render_config = CONFIG["generate"][QUESTION_TABLE_NAME]
    for config_idx, config in enumerate(render_config):
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
            print(f"Fail to fetch id from {COURSE_TABLE_NAME_COLUMN} = '{course_name}'. Skipping the rendering of test sheets.")
            continue
        
        res, err = ddb.run_sql(
            BASE_FETCH_ID_QUERY.format(
                TEST_SHEET_ID_COLUMN, TEST_SHEET_TABLE_NAME, COURSE_TABLE_ID_COLUMN, course_id
            )
        )

        if err:
            print(f"Skipping {COURSE_TABLE_ID_COLUMN} = '{course_id}' when fetching test id because of an error: {err}")
            continue
        
        try:
            test_id = res[0][0]
        except:
            print(f"Fail to fetch id from {COURSE_TABLE_ID_COLUMN} = '{course_id}'. Skipping the rendering of test sheets.")
            continue
        
        res, err = ddb.run_sql(
            BASE_FETCH_MANY_QUERY.format(
                QUESTION_TABLE_TEXT_COLUMN, QUESTION_TABLE_NAME,
                TEST_AND_QUESTION_TABLE, TEST_SHEET_ID_COLUMN, test_id,
                QUESTION_TABLE_ID_COLUMN, QUESTION_TABLE_ID_COLUMN
            )
        )

        if err:
            print(f"Fail to render {TEST_SHEET_ID_COLUMN} = '{test_id}': {err}")
            continue
        
        md_filename = BASE_MD_OUTPUT_FILENAME.format(DATETIME_STRING, config_idx+1)
        docx_filename = BASE_DOCX_OUTPUT_FILENAME.format(DATETIME_STRING, config_idx+1)
        with open(md_filename, "w") as f:
            f.write(f"{BASE_MD_YAML_BLOCK}\n\n{course_name}\n\n")
            for question_idx, row in enumerate(res):
                question_text = row[0]
                f.write(f"{question_idx+1}. {question_text}\n")
        
        try:
            subprocess.run(["pandoc", md_filename, "-o", docx_filename])
            print(f"Successfully creating {docx_filename}")
        except Exception as e:
            print(f"Fail to convert markdown {DATETIME_STRING}_{config_idx+1} to docx: {str(e)}")
            continue

if __name__ == "__main__":
    main()