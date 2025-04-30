import pandas as pd
from Project.configFiles.dbConfig import conn

# Is connected or not check
if conn.is_connected():
    print('Connected')

# cursor to execute queries
cursor = conn.cursor()

# Actual code for data insertion into the target table member_dimension table and source member_dimension csv
# source :- member_dimension csv file
# target table :- member_dimension table
def code(member_file):
    df1 = pd.read_csv(member_file)

    print(df1)

    insert_member = """INSERT INTO member_dimension(MEMBER_ID, FIRST_NAME, LAST_NAME) VALUES(%s, %s, %s)"""

    for index,row in df1.iterrows():
        cursor.execute(insert_member,tuple(row))

    conn.commit()
    cursor.close()
    conn.close()

# Main function for program execution
def main():
    member_file = 'Member_Dimensions.csv'
    code(member_file)


if __name__ == '__main__':
    main()
