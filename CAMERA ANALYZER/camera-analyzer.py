# Project Overview: The code below allows a user to analyze Chicago Traffic Camera data 
# collected from 2014-2024. There are 9 different commands that each provide a different
# aspect of the data. SQLite3 and Python are combined to execute these commands. At the 
# beginning of the program the general statistics of the database are provided. 

import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    # The number of Red Light cameras in the database
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Cameras:", f"{row[0]:,}")

    # The number of Speed Cameras in the database
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Speed Cameras:", f"{row[0]:,}")

    # The number of Red Light Violation entries recorded by every red light camera in the database
    dbCursor.execute("SELECT Num_Violations FROM RedViolations;")
    rows = dbCursor.fetchall()
    print(f"  Number of Red Light Camera Violation Entries:", f"{len(rows):,}")

    # The number of Speed Violation entries recorded by every speed camera in the database
    dbCursor.execute("SELECT Num_Violations FROM SpeedViolations;")
    rows = dbCursor.fetchall()
    print("  Number of Speed Camera Violation Entries:", f"{len(rows):,}")

    # The start and end date in the database
    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM RedViolations;")
    red_min, red_max = dbCursor.fetchone()

    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM SpeedViolations;")
    speed_min, speed_max = dbCursor.fetchone()

    start_date = min(red_min, speed_min)
    end_date = max(speed_min, speed_max)

    print(f"  Range of Dates in the Database: {start_date} - {end_date}")

    # The total number of red light violations recorded by red light cameras in the database
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Red Light Camera Violations:", f"{row[0]:,}")

    # The total number of speed violations recorded by speed cameras in the database
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Speed Camera Violations:", f"{row[0]:,}")
    
##################################################################  
#
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')

print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Spring 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()

# The menu options showing the user the different commands that can be performed on the database
print("Select a menu option: ")
print("  1. Find an intersection by name")
print("  2. Find all cameras at an intersection")
print("  3. Percentage of violations for a specific date")
print("  4. Number of cameras at each intersection")
print("  5. Number of violations at each intersection, given a year")
print("  6. Number of violations by year, given a camera ID")
print("  7. Number of violations by month, given a camera ID and year")
print("  8. Compare the number of red light and speed violations, given a year")
print("  9. Find cameras located on a street")
print("or x to exit the program.")

choice = input()

# Choosing the first command accesses this function
def FindIntersection(dbConn, IntersectionName):

    dbCursor = dbConn.cursor()

    IntersectionName = IntersectionName.upper()
    
    # The SQL query retrieves the the names of intersections containing the provided string 
    # and the intersection ID associated with those intersections
    sq1 = "SELECT Intersection_ID, Intersection FROM Intersections WHERE Intersection LIKE ? ORDER BY Intersection ASC"

    dbCursor.execute(sq1, (f"{IntersectionName}",))

    rows = dbCursor.fetchall()

    # If the query retrieved no information the following error is given
    if not rows:
        print("No intersections matching that name were found.")
    else:
        # If the query does return information it is printed into the consol in the form:
        # Intersection ID : Intersection Name
        for i in rows:
            print(i[0], ":", i[1])
    print()

# Choosing the second command accesses this function
def FindCameras(dbConn, intersection_name):

    dbCursor = dbConn.cursor()
    
    # The SQL Query retrieves the Intersection ID for the Intersection entered by the user
    dbCursor.execute("SELECT Intersection_ID FROM Intersections WHERE Intersection = ?", (intersection_name,))
    row = dbCursor.fetchone()
    
    # If the SQL Query does not return any information the code returns the following error
    if row is None:
        print("No red light cameras found at that intersection.")
        print()
        print("No speed cameras found at that intersection.")
        return

    intersection_id = row[0] # Variable storing the Intersection ID

    # The SQL Query retrieves the Camera IDs and Addresses of the Red Light Cameras that 
    # match the stored Intersection ID
    dbCursor.execute("""
        SELECT Camera_ID, Address FROM RedCameras 
        WHERE Intersection_ID = ?
        ORDER BY Camera_ID ASC;
    """, (intersection_id,))
    red_cameras = dbCursor.fetchall()

    # The SQL Query retrieves the Camera IDs and Addresses of the Speed Cameras that match
    # the stored Intersection ID
    dbCursor.execute("""
        SELECT Camera_ID, Address FROM SpeedCameras 
        WHERE Intersection_ID = ?
        ORDER BY Camera_ID ASC;
    """, (intersection_id,))
    speed_cameras = dbCursor.fetchall()

    # Printing the retrieved information
    print(f"\nCameras at {intersection_name}:\n")

    # If the SQL Query has rtetrieved information it is presented in the form:
    # Camera ID : Camera Address
    if red_cameras:
        print("Red Light Cameras:")
        for cam in red_cameras:
            print(f"  {cam[0]} : {cam[1]}")
    else: # If no information has been retrieved the following error is presented
        print("No red light cameras found at that intersection.")

    # If the SQL Query has rtetrieved information it is presented in the form:
    # Camera ID : Camera Address
    if speed_cameras:
        print("\nSpeed Cameras:")
        for cam in speed_cameras:
            print(f"  {cam[0]} : {cam[1]}")
    else: # If no information has been retrieved the following error is presented
        print("No speed cameras found at that intersection.")

    print()

# Choosing the third command accesses this function
def PercentViolations(dbConn, date_selected):

    dbCursor = dbConn.cursor()

    # The date entered in split into year, month and day. The sizes of the individual strings
    # is checked to ensure they meet the given format for each field
    year, month, day = date_selected.split('-')
    if len(year) != 4 or len(month) != 2 or len(day) != 2:
        print("No violations on record for that date.")

    # The SQL Query retrieves the red light violations on the date entered
    dbCursor.execute(f"SELECT SUM(Num_Violations) FROM RedViolations WHERE Violation_Date = ?", (date_selected,))
    row = dbCursor.fetchone()

    # If the query returns no information then the number of red light violations is set to 0
    if row == None:
        red_violations = 0
    else: # If information is retrieved its stored in the red_violations variable
        red_violations = row[0]

    # The SQL Query retrieves the speed violations on the date entered
    dbCursor.execute(f"SELECT SUM(Num_Violations) FROM SpeedViolations WHERE Violation_Date = ?", (date_selected,))
    row = dbCursor.fetchone()

    # If the query returns no information then the number of speed violations is set to 0
    if row == None:
        speed_violations = 0
    else: # If information is retrieved its stored in the speed_violations variable
        speed_violations = row[0]

    # The total violations are calculated by adding the red light violations and the speed violations
    if red_violations != None or speed_violations != None:
        total_violations = red_violations + speed_violations
    else:
        total_violations = 0

    # If the total violations comes out to 0 then the following error is returned
    if total_violations == 0:
        print("No violations on record for that date.")
        return
    
    # The percentage of speed and red light violations from the total violations is calculated
    # in the following equations
    red_percentage = (red_violations / total_violations) * 100
    speed_percentage = (speed_violations / total_violations) * 100

    # Prints the information in the form:
    # Number of Red Light Violations: <number> (<percentage>%)
    # Number of Speed Violations: <number> (<percentage>%)
    print(f"Number of Red Light Violations: {red_violations:,} ({red_percentage:.3f}%)")
    print(f"Number of Speed Violations: {speed_violations:,} ({speed_percentage:.3f}%)")
    print(f"Total Number of Violations: {total_violations:,}")

# Choosing the fourth command accesses this function
def CameraAtIntersection(dbConn):
    dbCursor = dbConn.cursor()

    # The SQL Query retrieves the total number of Red Light Cameras
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    total_red_cameras = dbCursor.fetchone()[0]

    # The SQL Query retrieves the total number of Speed Cameras
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    total_speed_cameras = dbCursor.fetchone()[0]

    print("\nNumber of Red Light Cameras at Each Intersection\n")

    # The SQL Query counts the number of Red Light Cameras at every intersection retrieving
    # the intersection name and the intersection id as well
    dbCursor.execute("""
        SELECT Intersections.Intersection, Intersections.Intersection_ID, COUNT(RedCameras.Camera_ID)
        FROM Intersections
        JOIN RedCameras ON Intersections.Intersection_ID = RedCameras.Intersection_ID
        GROUP BY Intersections.Intersection_ID, Intersections.Intersection
        ORDER BY COUNT(RedCameras.Camera_ID) DESC, Intersections.Intersection_ID DESC;
    """)
    red_camera_count = dbCursor.fetchall()

    # The information is separated and printed in the format:
    # Intersection Name (Intersection ID) : Number of Red Light Cameras (<percentage>%)
    for intersection_name, intersection_id, count in red_camera_count:
        percentage = (count / total_red_cameras) * 100 # Calculates the percentage of red light cameras at each intersection from the total number of red light cameras
        print(f"  {intersection_name} ({intersection_id}) : {count} ({percentage:.3f}%)") 

    print("\nNumber of Speed Cameras at Each Intersection\n")

    # The SQL Query counts the number of Spped Cameras at every intersection retrieving
    # the intersection name and the intersection id as well
    dbCursor.execute("""
        SELECT Intersections.Intersection, Intersections.Intersection_ID, COUNT(SpeedCameras.Camera_ID)
        FROM Intersections
        JOIN SpeedCameras ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
        GROUP BY Intersections.Intersection_ID, Intersections.Intersection
        ORDER BY COUNT(SpeedCameras.Camera_ID) DESC, Intersections.Intersection_ID DESC;
    """)
    speed_camera_count = dbCursor.fetchall()

    # The information is separated and printed in the format:
    # Intersection Name (Intersection ID) : Number of Speed Cameras (<percentage>%)
    for intersection_name, intersection_id, count in speed_camera_count:
        percentage = (count / total_speed_cameras) * 100 # Calculates the percentage of speed cameras at each intersection from the total number of speed cameras
        print(f"  {intersection_name} ({intersection_id}) : {count} ({percentage:.3f}%)")

    print()

# Choosing the fifth command accesses this function
def YearlyViolations(dbConn, year):
    
    # Ensures that the year entered is in the correct format. If not the error is given
    if len(year) != 4:
        print("No red light violations on record for that year.")
        print()
        print("No speed violations on record for that year.")
    
    dbCursor = dbConn.cursor()

    # The SQL Query returns the total number of red light violations for the year
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations WHERE strftime('%Y', Violation_Date) = ?;", [year,])

    total_red_violations = dbCursor.fetchone()

    # The SQL Query returns the total number of speed violations for the year
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations WHERE strftime('%Y', Violation_Date) = ?;", [year,])

    total_speed_violations = dbCursor.fetchone()

    # The SQL Query retrieves the intersection name, the intersection ID and the number of red light violations for each intersection
    # for the entered year
    dbCursor.execute("""SELECT Intersections.Intersection, Intersections.Intersection_ID, SUM(RedViolations.Num_Violations)
FROM Intersections
JOIN RedCameras ON Intersections.Intersection_ID = RedCameras.Intersection_ID
JOIN RedViolations ON RedCameras.Camera_ID = RedViolations.Camera_ID
WHERE strftime('%Y', Violation_Date) = ?
GROUP BY Intersections.Intersection
ORDER BY SUM(RedViolations.Num_Violations) DESC, Intersections.Intersection_ID DESC;""", [year,])
    
    rows = dbCursor.fetchall()

    # The information is retrieved in printed in the form:
    # Intersection name (Intersection ID) : Number of Red Light Violations for the year (<percentage of red light violations for the intersection from the total red light violations of the year>%)
    print(f"\nNumber of Red Light Violations at Each Intersection for {year}")
    for intersection, intersection_id, violations_per_year in rows:
        percentage = (violations_per_year / total_red_violations[0]) * 100
        print(f" {intersection} ({intersection_id}) : {violations_per_year} ({percentage:.3f}%)")

    # The SQL Query retrieves the intersection name, the intersection ID and the number of speed violations for each intersection
    # for the entered year
    dbCursor.execute("""SELECT Intersections.Intersection, Intersections.Intersection_ID, SUM(SpeedViolations.Num_Violations)
FROM Intersections
JOIN SpeedCameras ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
JOIN SpeedViolations ON SpeedCameras.Camera_ID = SpeedViolations.Camera_ID
WHERE strftime('%Y', Violation_Date) = ?
GROUP BY Intersections.Intersection
ORDER BY SUM(SpeedViolations.Num_Violations) DESC, Intersections.Intersection_ID DESC;""", [year,])
    
    rows = dbCursor.fetchall()

    # The information is retrieved in printed in the form:
    # Intersection name (Intersection ID) : Number of Speed Violations for the year (<percentage of speed violations for the intersection from the total speed violations of the year>%)
    print(f"\nNumber of Speed Violations at Each Intersection for {year}")
    for intersection, intersection_id, violations_per_year in rows:
        percentage = (violations_per_year / total_speed_violations[0]) * 100
        print(f" {intersection} ({intersection_id}) : {violations_per_year} ({percentage:.3f}%)")
    
    print()

# Choosing to plot the information accesses this function
def PlotYearlyViolations(combined_violations, camera_id):

    # The years are placed along the x axis and the number of violations on the
    # y axis
    x_values = list(combined_violations.keys())
    y_values = list(combined_violations.values())

    # Plot styling and labeling
    plt.figure(figsize=(8,8))
    plt.plot(x_values, y_values, color = 'blue')

    plt.title(f'Yearly Violations for Camera {camera_id}')
    plt.ylabel('Number of Violations')
    plt.xlabel('Year')

    plt.show()

# Choosing the sixth command accesses this function
def RecordedViolations(dbConn, camera_id):

    dbCursor = dbConn.cursor()
    
    # The SQL Query checks if the Camera ID entered retrieves a red light camera
    dbCursor.execute("SELECT Camera_ID FROM RedCameras WHERE Camera_ID = ?", (camera_id,))
    is_red_camera = dbCursor.fetchone()

    # The SQL Query checks if the Camera ID entered retrieves a speed camera
    dbCursor.execute("SELECT Camera_ID FROM SpeedCameras WHERE Camera_ID = ?", (camera_id,))
    is_speed_camera = dbCursor.fetchone()

    # If the entered Camera ID returns nothing for either query the following error is printed
    if not is_red_camera and not is_speed_camera:
        print("No cameras matching that ID were found in the database.")
        return

    print(f"\nYearly Violations for Camera {camera_id}")

    # The SQL Query retrieves the number of red light violations recorded by the camera
    dbCursor.execute("""
        SELECT strftime('%Y', Violation_Date) AS Year, SUM(Num_Violations) 
        FROM RedViolations 
        WHERE Camera_ID = ? 
        GROUP BY Year
        ORDER BY Year ASC;
    """, (camera_id,))
    red_violations = dbCursor.fetchall()

    # The SQL Query retrieves the number of speed violations recorded by the camera
    dbCursor.execute("""
        SELECT strftime('%Y', Violation_Date) AS Year, SUM(Num_Violations) 
        FROM SpeedViolations 
        WHERE Camera_ID = ? 
        GROUP BY Year
        ORDER BY Year ASC;
    """, (camera_id,))
    speed_violations = dbCursor.fetchall()

    combined_violations = {}

    # The number of red light and speed violations are combined and stored per year in a dictionary
    for year, count in red_violations:
        combined_violations[year] = count

    for year, count in speed_violations:
        if year in combined_violations:
            combined_violations[year] += count  
        else:
            combined_violations[year] = count

    # If the dictionary is empty the following error is printed
    if not combined_violations:
        print("No recorded violations for this camera.")
    else:
        # The information of the dictionary is printed in the form:
        # Year : Number of total violations for the year
        for year in sorted(combined_violations.keys()):
            print(f"{year} : {combined_violations[year]:,}")

    print()

    # The user is asked if they would like to plot the presented information
    plot_choose = input("Plot? (y/n) ")

    if plot_choose == 'y':
        PlotYearlyViolations(combined_violations, camera_id)
    else:
        return

def PlotMonthlyData(monthly_violations, camera_id, year):

    # The x axis is set to the months of the year. The y axis is set to the number of
    # violations
    x_values = list(monthly_violations.keys())
    y_values = list(monthly_violations.values())

    # Styling and labling for the plot
    plt.figure(figsize=(8,8))
    plt.plot(x_values, y_values, color = 'blue')

    plt.title(f'Monthly Violations for Camera {camera_id} ({year})')
    plt.ylabel('Number of Violations')
    plt.xlabel('Month')

    plt.show()

# Choosing the seventh command accesses this function
def MonthlyViolations(dbConn, camera_id, input_year):

    dbCursor = dbConn.cursor()

    # The SQL Query checks if the camera ID is for a red light camera
    dbCursor.execute("SELECT Camera_ID FROM RedCameras WHERE Camera_ID = ?", [camera_id,])
    is_red_camera = dbCursor.fetchone()

    # The SQL Query checks if the camera ID is for a speed camera
    dbCursor.execute("SELECT Camera_ID FROM SpeedCameras WHERE Camera_ID = ?", [camera_id,])
    is_speed_camera = dbCursor.fetchone()

    # If it is neither the following error is printed
    if not is_red_camera and not is_speed_camera:
        print("No cameras matching that ID were found in the database.")
        return

    print(f"\nMonthly Violations for Camera {camera_id} in {input_year}")

    # The SQL Query finds the red light violations for each month in the given year for the entered Camera ID
    dbCursor.execute("""SELECT strftime('%m', Violation_Date) as Month, SUM(Num_Violations)
                        FROM RedViolations
                        WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
                        GROUP BY Month
                        ORDER BY Month ASC;
                    """, [camera_id, input_year])

    red_violations = dbCursor.fetchall()

    # The SQL Query finds the speeed violations for each month in the given year for the entered Camera ID
    dbCursor.execute("""SELECT strftime('%m', Violation_Date) as Month, SUM(Num_Violations)
                        FROM SpeedViolations
                        WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
                        GROUP BY Month
                        ORDER BY Month ASC;
                    """, [camera_id, input_year])

    speed_violations = dbCursor.fetchall()

    # TThe red light and speed violations are added together for each month and stored in a dictionary
    monthly_violations = {str(i).zfill(2): 0 for i in range (1, 13)}

    for month, value in red_violations:
        monthly_violations[month] += value

    for month, value in speed_violations:
        monthly_violations[month] += value


    # If the dictionary has data it is separated and printed in the form:
    # MM/YYYY : Number of Violations
    has_data = False

    for month, count in sorted(monthly_violations.items()):
        if count > 0:
            has_data = True
            print(f'{month}/{input_year} : {count:,}')

    # If there is no data in the dictionary then the following error is printed
    if not has_data:
        print("No recorded violations for this camera in the selected year.")

    print()

    # The user is asked if they want a plot for the data
    plot = input("Plot (y/n) ")

    if plot == 'y':
        PlotMonthlyData(monthly_violations, camera_id, input_year)
    else:
        return

# Choosing the eight command accesses this function
def CompareViolations(dbConn, year):

    dbCursor = dbConn.cursor()

    # The SQL Query retrieves the red light violations for each day in the entered year
    dbCursor.execute("""
        SELECT Violation_Date, SUM(Num_Violations) 
        FROM RedViolations
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY Violation_Date
        ORDER BY Violation_Date ASC;
    """, (year,))
    red_violations = dbCursor.fetchall()

    # The SQL Query retrieves the speed violations for each day in the entered year
    dbCursor.execute("""
        SELECT Violation_Date, SUM(Num_Violations) 
        FROM SpeedViolations
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY Violation_Date
        ORDER BY Violation_Date ASC;
    """, (year,))
    speed_violations = dbCursor.fetchall()

    # Combine data into a dictionary
    violations_by_date = {}

    for date, count in red_violations:
        violations_by_date[date] = {"Red": count, "Speed": 0}

    for date, count in speed_violations:
        if date in violations_by_date:
            violations_by_date[date]["Speed"] = count
        else:
            violations_by_date[date] = {"Red": 0, "Speed": count}

    sorted_dates = sorted(violations_by_date.keys())

    # Prints the number of red light violations for the first five days
    # of the year in the form:
    # <Violation Date> <Number of Red Light Violations>
    print("Red Light Violations:")
    for date in sorted_dates[:5]:  # First 5 days
        print(f"{date} {violations_by_date[date]['Red']}")
    for date in sorted_dates[-5:]:  # Last 5 days
        print(f"{date} {violations_by_date[date]['Red']}")

    # Prints the number of red light violations for the first five days
    # of the year in the form:
    # <Violation Date> <Number of Speed Violations>
    print("\nSpeed Violations:")
    for date in sorted_dates[:5]:  # First 5 days
        print(f"{date} {violations_by_date[date]['Speed']}")
    for date in sorted_dates[-5:]:  # Last 5 days
        print(f"{date} {violations_by_date[date]['Speed']}")

    print()
    # Ask user if they want a plot of the information
    plot_choice = input("Plot? (y/n) ") 
    
    if plot_choice.lower() == 'y':
        PlotViolationComparison(dbConn, year)

# If the user does want to plot the cameras on the chicago map this function is accessed
def PlotViolationComparison(dbConn, year):
   
    # SQL Query to get red light violations by day
    dbCursor = dbConn.cursor()
    dbCursor.execute("""
        SELECT Violation_Date, SUM(Num_Violations) 
        FROM RedViolations
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY Violation_Date;
    """, (year,))
    red_violations = {row[0]: row[1] for row in dbCursor.fetchall()}

    # SQL Query to get speed violations by day
    dbCursor.execute("""
        SELECT Violation_Date, SUM(Num_Violations) 
        FROM SpeedViolations
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY Violation_Date;
    """, (year,))
    speed_violations = {row[0]: row[1] for row in dbCursor.fetchall()}

    # Create a list of all days in the year using the datetime library and the
    # timedelta module from the datetime library
    start_date = datetime.strptime(f"{year}-01-01", "%Y-%m-%d")
    end_date = datetime.strptime(f"{year}-12-31", "%Y-%m-%d")
    all_dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end_date - start_date).days + 1)]

    # Ensure all dates have entries, even if they have zero violations
    red_counts = [red_violations.get(date, 0) for date in all_dates]
    speed_counts = [speed_violations.get(date, 0) for date in all_dates]
    day_numbers = [i + 1 for i in range(len(all_dates))]

    # Calculate the maximum number of violations to set the y-axis limit
    max_violations = max(max(red_counts), max(speed_counts)) + 500

    # Plotting the data. Red Light Violations are colored red and Speed Violations are colored orange
    plt.figure(figsize=(8, 6))
    plt.plot(day_numbers, red_counts, label="Red Light", color="red", linewidth=2)
    plt.plot(day_numbers, speed_counts, label="Speed", color="orange", linewidth=2)

    # Plot labels and legend
    plt.xlabel("Day")
    plt.ylabel("Number of Violations")
    plt.title(f"Violations Each Day of {year}")
    plt.legend()

    # Set x and y axis ranges and ticks
    plt.xticks(range(0, 351, 50))
    plt.yticks(range(0, max_violations + 1, 1000))
    plt.xlim(-10, 400)
    plt.ylim(-200, max_violations)

    plt.tight_layout()
    plt.show()

# Choosing the ninth command accesses this function
def PlotCamerasOnMap(dbConn, street_name):
    dbCursor = dbConn.cursor()

    # SQL Query to find red light cameras on the given street
    dbCursor.execute("""
        SELECT Camera_ID, Latitude, Longitude
        FROM RedCameras
        WHERE Address LIKE ?
        ORDER BY Camera_ID ASC
    """, (f"%{street_name.upper()}%",))
    red_cameras = dbCursor.fetchall()

    # SQL Query to find speed cameras on the given street
    dbCursor.execute("""
        SELECT Camera_ID, Latitude, Longitude
        FROM SpeedCameras
        WHERE Address LIKE ?
        ORDER BY Camera_ID ASC
    """, (f"%{street_name.upper()}%",))
    speed_cameras = dbCursor.fetchall()

    # Ensure the camera data is retrieved to plot
    if not red_cameras and not speed_cameras:
        print(f"No cameras found on {street_name}.")
        return


    plt.figure(figsize=(10, 10))

    # Plot red light cameras with red color points and lines connecting them
    if red_cameras:
        red_ids, red_lats, red_longs = zip(*red_cameras)
        plt.scatter(red_longs, red_lats, c='red', label='Red Light Cameras', s=20, alpha=0.7)
        for camera_id, lat, long in red_cameras:
            plt.text(long, lat, str(camera_id), fontsize=8, color='black', ha='right')
        plt.plot(red_longs, red_lats, c='red', linewidth=1, alpha=0.7)

    # Plot speed cameras with orange color points and lines connecting them
    if speed_cameras:
        speed_ids, speed_lats, speed_longs = zip(*speed_cameras)
        plt.scatter(speed_longs, speed_lats, c='orange', label='Speed Cameras', s=20, alpha=0.7)
        for camera_id, lat, long in speed_cameras:
            plt.text(long, lat, str(camera_id), fontsize=8, color='black', ha='right')
        plt.plot(speed_longs, speed_lats, c='orange', linewidth=1, alpha=0.7)

    # Show the plot over the provided Chicago map image
    image = plt.imread("chicago.png")
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868] # Size of the map
    plt.imshow(image, extent=xydims)
    plt.title(f"Cameras on Street: {street_name}")

    plt.show()

def FindCamerasOnStreet(dbConn, street_name):
    dbCursor = dbConn.cursor()

    # SQL Query to find red light cameras on the given street
    dbCursor.execute("""
        SELECT Camera_ID, Address
        FROM RedCameras
        WHERE Address LIKE ?
        ORDER BY Camera_ID ASC;
    """, (f"%{street_name.upper()}%",))
    red_cameras = dbCursor.fetchall()

    # SQL Query to find speed cameras on the given street
    dbCursor.execute("""
        SELECT Camera_ID, Address
        FROM SpeedCameras
        WHERE Address LIKE ?
        ORDER BY Camera_ID ASC;
    """, (f"%{street_name.upper()}%",))
    speed_cameras = dbCursor.fetchall()


    print(f"\nCameras on {street_name}:\n")

    # If there is data to show it is printed in the form:
    # Camera ID : Address of the camera
    if red_cameras:
        print("Red Light Cameras:")
        for camera in red_cameras:
            print(f"  {camera[0]} : {camera[1]}")
    else: # If there is no data the following error is printed
        print("No red light cameras found on this street.")

    # If there is data to show it is printed in the form:
    # Camera ID : Address of the camera
    if speed_cameras:
        print("\nSpeed Cameras:")
        for camera in speed_cameras:
            print(f"  {camera[0]} : {camera[1]}")
    else: # If there is no data the following error is printed
        print("No speed cameras found on this street.")

    print()

    # The user is asked if they want to plot the camera locations on the map
    if_plot = input("Plot? (y/n) ")

    if if_plot == 'y':
        PlotCamerasOnMap(dbConn, street_name)
    else:
        return

# The while loop handles all command inputs. If the user inputs any number 
# outside of 1-9 or a character that is not 'x' they are shown an error and 
# asked again. Each command input asks for any inputs needed to run the associated
# function(s).
while choice != 'x':
    if choice == '1':

        print("Your choice --> 1")

        choose_intersection = input(f"Enter the name of the intersection to find (wildcards _ and % allowed): ")

        FindIntersection(dbConn, choose_intersection)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()
    
    elif choice == '2':

        print("Your choice --> 2")

        choose_intersection = input("Enter the name of the intersection (no wildcards allowed): ")

        FindCameras(dbConn, choose_intersection)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()

    elif choice == '3':

        print("Your choice --> 3")

        choose_date = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): ")

        PercentViolations(dbConn, choose_date)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()

    elif choice == '4':

        print("Your choice --> 4")

        CameraAtIntersection(dbConn)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()
    
    elif choice == '5':

        print("Your choice --> 5")

        input_year = input("Enter the year that you would like to analyze: ")

        YearlyViolations(dbConn, input_year)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()

    elif choice == '6':

        print("Your choice --> 6")

        choose_camera = input("Enter a camera ID: ")

        RecordedViolations(dbConn, choose_camera)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()

    elif choice == '7':

        print("Your choice --> 7")

        choose_camera = input("Enter a Camera ID: ")
        choose_year = input("Enter a year: ")

        MonthlyViolations(dbConn, choose_camera, choose_year)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()
    
    elif choice == '8':

        print("Your choice --> 8")

        choose_year = input("Enter a year: ")

        CompareViolations(dbConn, choose_year)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()

    elif choice == '9':

        print("Your choice --> 9")

        choose_street = input("Enter a street name: ")

        FindCamerasOnStreet(dbConn, choose_street)

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()
    else:

        print("Your choice --> Error, unknown command, try again...\n")
        
        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        choice = input()

print("Your choice --> Exiting program.")
#
# done
#
