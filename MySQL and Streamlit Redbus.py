import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

# Creating a MySQL connection
def create_db_connection(host_name, port_name, user_name, user_password, database_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="Mdms",
            password="Mdms@05072021",
            database="guvi"
        )
    except Error as e:
        st.error(f'Error connecting to MySQL: {e}')
    return connection

# Table creation in MySQL
def create_tables(connection):
    create_redbus_table = """
    CREATE TABLE IF NOT EXISTS Redbus_table (
        ID INT PRIMARY KEY AUTO_INCREMENT,
        route_name TEXT,
        route_link TEXT,
        busname TEXT,
        bustype TEXT,
        departing_time TIME,
        duration TEXT,
        reaching_time TIME,
        star_rating FLOAT,
        price DECIMAL(10, 2),
        seats_available INT
    )
    """
    execute_query(connection, create_redbus_table)

# Function to execute a query
def execute_query(connection, query, data=None):
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
    except Error as e:
        st.error(f"Error executing query: {e}")

# Function to insert data into the Redbus table
def insert_redbus_data(connection, df):
    cursor = connection.cursor()
    query = """
    INSERT INTO Redbus_table (
        route_name, route_link, busname, bustype, departing_time, duration,
        reaching_time, star_rating, price, seats_available
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in df.iterrows():  # Use iterrows() to iterate over DataFrame rows
        data = (
            row['Route_name'], row['Route_link'], row['Bus_name'], row['Bus_type'], 
            row['Start_time'], row['Duration'], row['End_time'], 
            row['Rating'], row['Price'], row['Seats_available']
        )
        cursor.execute(query, data)
    connection.commit()
    st.success("Data loaded successfully into Redbus table")
#Streamlit application
def main():
    st.set_page_config(layout="wide")
    web = option_menu(menu_title="🚌OnlineBus",
                      options=["Introduction", "Load Data", "📍States and Routes"],
                      icons=["house", "upload", "info-circle"],
                      orientation="horizontal")

    if web == "Introduction":
        st.title("Redbus Data Scraping with Selenium & Dynamic Filtering using Streamlit")
        st.subheader(":blue[Domain:] RedBus Transportation")
        st.subheader(":blue[Objective:]")
        st.markdown("""The 'Redbus Data Scraping and Filtering with Streamlit Application' aims to revolutionize
                    the transportation industry by providing a comprehensive solution for collecting, analyzing, and
                    visualizing bus travel data.""")
        st.subheader(":blue[Developed-by:] Sajeetha Begum N")

    elif web == "Load Data":
        st.title("Load Data into Redbus table")
        connection = create_db_connection("localhost", 3306, "Mdms", "Mdms@05072021", "guvi")
    
        if connection:
            create_tables(connection)
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if st.button("Load Data into MySQL"):
                if uploaded_file is not None:
                    df = pd.read_csv(uploaded_file)
                    insert_redbus_data(connection, df)
                else:
                    st.warning("Please upload a CSV file which has data before clicking the button.")
            connection.close()

    elif web == "📍States and Routes":
        st.title("Filter Bus Routes by State")

        connection = create_db_connection("localhost", 3306, "Mdms", "Mdms@05072021", "guvi")
        if connection:
            my_cursor = connection.cursor()

            my_cursor.execute("SELECT DISTINCT route_name FROM Redbus_table")
            states = [row[0] for row in my_cursor.fetchall()]

            selected_state = st.selectbox("Select a State:", states)
            
            fare_range = st.selectbox("Select Fare Range:", ["50-1000", "1000-2000", "2000+"])
            if fare_range == "50-1000":
                fare_min, fare_max = 50, 1000
            elif fare_range == "1000-2000":
                fare_min, fare_max = 1000, 2000
            else:
                fare_min, fare_max = 2000, 100000

            bustype = st.selectbox("Select Bus Type:", ["Sleeper", "Semi-sleeper", "Seater"])
            if bustype == "Sleeper":
                bustype_condition = "bustype LIKE '%Sleeper%'"
            elif bustype == "Semi-sleeper":
                bustype_condition = "bustype LIKE '%A/c Semi Sleeper%'"
            else:
                bustype_condition = "bustype LIKE '%Seater %'"

            if selected_state:
                query = f"""
                SELECT * FROM redbus_table 
                WHERE Route_name = %s 
                AND price BETWEEN %s AND %s 
                AND {bustype_condition}
                """
                my_cursor.execute(query, (selected_state, fare_min, fare_max))
                filtered_data = my_cursor.fetchall()

                if filtered_data:
                    df_filtered = pd.DataFrame(filtered_data, columns=[i[0] for i in my_cursor.description])
                    st.write(f"Displaying data for {selected_state}:")
                    st.dataframe(df_filtered)
                else:
                    st.write(f"No data found for {selected_state}")
        connection.close()

if __name__ == "__main__":
    main()