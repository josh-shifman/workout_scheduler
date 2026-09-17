#Workout Scheduler 
#Date: 2/08/2021
#Version: v15
#Author: Joshua Shifman
#Purpose: Lets the user create workouts
import csv
import PySimpleGUI as sg
import images
import os
from PySimpleGUI.PySimpleGUI import theme_background_color
sg.theme('DefaultNoMoreNagging')


def login_screen():
    try:
        with open("userCredentials.csv","r") as f:
            reader = csv.reader(f)
            usernamePassword = list(reader)
            if usernamePassword[0] == ["username", "password"]:
                signUpDisabled = False
            else:
                signUpDisabled = True
    
    except IOError:
        signUpDisabled = False
        with open("userCredentials.csv","w") as g:
            writer = csv.writer(g)
            writer.writerow(["username","password"])
    
    middle_column = [[sg.Text("Username: ", font = ("Helvetica", 20), pad = (0,10)), sg.Input(key = "-USERNAME-", font = ("Helvetica", 20), pad = (0,10))],  
        [sg.Text("Password: ", font = ("Helvetica", 20), pad = (0,10)), sg.Input(key = "-PASSWORD-", font = ("Helvetica", 20), pad = (0,10))]]
    
    bottom_column = [[sg.Button("Log in", key = "-LOGIN-", pad = (30,0), size = (10,1), font = ("Helvetica", 20)), sg.Button("Sign up", key = "-SIGNUP-", disabled = signUpDisabled, size = (10,1), font = ("Helvetica", 20))]]
    layout = [[sg.Image(data = images.ws_Title, pad = (260,10))], [sg.Column(middle_column, element_justification = "c", pad = (150,30))], 
             [sg.Column(bottom_column, element_justification = "c", pad = (390, 0))]]
            
            
    loginWindow = sg.Window("Login screen", layout, size = (1280, 720))
    while True:
        event, values = loginWindow.read()
        if event == None:
            break
        
        if event == "-SIGNUP-":
            username = values["-USERNAME-"]
            password = values["-PASSWORD-"]
            if not username.strip() or not password.strip():
                sg.Popup("ERROR- BLANK USERNAME OR PASSWORD")
                loginWindow.close()
                login_screen()
            else:
                spaceInUsername = username.split(" ")
                spaceInPassword = password.split(" ")
                if len(spaceInUsername) > 1 or len(spaceInPassword) > 1: 
                    sg.Popup("ERROR- CANNOT HAVE A SPACE IN THE USERNAME OR PASSWORD")
                    loginWindow.close()
                    login_screen()
                else:
                    with open("userCredentials.csv", "w") as signUpFile:
                        writer = csv.writer(signUpFile)
                        writer.writerow([username, password])
                    
                    signUpDisabled = True
                    loginWindow["-SIGNUP-"].update(disabled = signUpDisabled)
        
        if event == "-LOGIN-":
            with open("userCredentials.csv", "r") as loginFile:
                reader = csv.reader(loginFile)
                accountCredentials = list(reader)
                username = values["-USERNAME-"]
                password = values["-PASSWORD-"]
                if username == accountCredentials[0][0] and password == accountCredentials[0][1]:
                    loginWindow.close()
                    main()
                else:
                    sg.Popup("INCORRECT USERNAME OR PASSWORD")
                    loginWindow.close()
                    login_screen()


def main(): #Menu function
    global newExercises
    newExercises = []   
    f = open("workoutList.txt", "a") #Creates workoutList.txt if it does not exist
    f.close()
    try:
        g = open("assignedWorkout.csv", "r") #Checks to see if assignedWorkout.csv exists
        g.close()
    except IOError: #If assignedWorkout.csv does not exist
        with open("assignedWorkout.csv", "w", newline = "") as g: #Creates and writes to the file
            writer = csv.writer(g)
            for i in range(1, 15): #Creates 14 lines
                tempList = [i, "Unassigned workout"] #Contains the line number and "Unassigned workout" in each row
                writer.writerow(tempList)   

    menuLeftCol = [[sg.Button("View Workout", size = (75,5), pad = (10,50), key = "-WORKOUTS-", font = ('Helvetica', 10))],
            [sg.Button("View schedule", size = (75,5), pad = (10,50), font = ('Helvetica', 10))]]
        
    menuRightCol = [[sg.Button("Add workout", size = (75,5), pad = (10,50), key = "-ADD WORKOUT-", font = ('Helvetica', 10))],
                    [sg.Button("Import workout", size = (75,5), pad = (10,50), key = "-IMPORT-", font = ('Helvetica', 10))]]
    menuTopLeft = [[sg.Button(image_data = images.return_button, button_color = (sg.theme_background_color(), sg.theme_background_color()), key = "return button", border_width = 0, pad = (30,30))]]
    menuTitle = [[sg.Image(data = images.ws_Title)]]
    layout = [[sg.Column(menuTopLeft, element_justification = "c"), sg.Column(menuTitle, element_justification = "c", pad = (80, 0))],
    [sg.Column(menuLeftCol, size = (600,600)), sg.Column(menuRightCol, size = (600, 600))]]

    #create window
    global homeScreenWindow #Global variable so it can be closed after a workout has been selected in selected_workout_screen()
    homeScreenWindow = sg.Window("Home screen", layout, size = (1280, 720))

    #read window
    while True:
        event, values = homeScreenWindow.Read()
        if event == None: #If the user clicks exit or the window is closed
            exit()
        if event == "-ADD WORKOUT-":
            homeScreenWindow.close()
            create_workout("", "", False)
            break
        if event == "-WORKOUTS-":
            select_workout_screen()
        if event == "return button":
            homeScreenWindow.close()
            login_screen()
        
        if event == "View schedule":
            homeScreenWindow.close()
            workout_scheduler()
        if event == "-IMPORT-":
            importFile = sg.popup_get_file("Filename to open", no_window = True, file_types=(("CSV Files","*.csv"),))
            if not importFile or not importFile.strip():
                sg.Popup("ERROR- NO FILE SELECTED")
            else:
                import_workout_file(importFile)
        
def import_workout_file(importFile):
    importFileName = os.path.basename(importFile)
    if importFileName[-4:] == ".csv":
        if not importFileName[0:-4] or not importFileName[0:-4].strip():
            sg.Popup("ERROR- WORKOUT NAME IS BLANK")
            main()
        else:
            with open(importFile, "r") as f:
                reader = csv.reader(f)
                workoutData = list(reader)
                for i in range(0, len(workoutData)):
                    if len(workoutData[i]) != 4:
                        sg.Popup("ERROR- NOT A VALID WORKOUT FILE")
                        homeScreenWindow.close()
                        main()
                    
            try: 
                f = open(importFileName, "x")
                f.close()
            except IOError:
                sg.Popup("ERROR- WORKOUT WITH THIS NAME ALREADY EXISTS. PLEASE CHANGE THE FILE NAME THEN RETRY.")
                main()
            
            with open(importFileName, "w",newline="") as g:
                writer = csv.writer(g)
                writer.writerows(workoutData)

            with open("workoutList.txt", "a") as workoutFile:
                workoutFile.write(importFileName[0:-4] + "\n") #Appends the workout name to the workoutList txt file
            sg.Popup("WORKOUT SUCCESSFULLY IMPORTED")
    else:
        sg.Popup("ERROR- NOT A CSV FILE")

def select_workout_screen():
    #Displays a list of workouts to the user. Once the user selects a workout, displays its contents.
    with open("workoutList.txt", "r") as f: #Opens the file containing the workout names
        workoutsList = []
        for line in f:
            strip_lines = line.strip() #Removes the spaces between the lines
            workoutsList.append(strip_lines) #Append the workout to the workoutsList
        
    layout = [[sg.Text("Saved workouts")], 
              [sg.Listbox(values = workoutsList, key = "-EXERCISELIST-", size = (100,5), enable_events = True)]]
    selectWorkoutWindow = sg.Window("Select workout", layout)
    while True:
        event, values = selectWorkoutWindow.read()
        if event == None:
            homeScreenWindow.close()
            main()
            break

        if event == "-EXERCISELIST-":
            userSelectedWorkout = values["-EXERCISELIST-"]
            homeScreenWindow.close()
            selectWorkoutWindow.close()
            selectedWorkout = str(userSelectedWorkout[0]) + ".csv"
            view_workout(selectedWorkout, str(userSelectedWorkout[0]))

def view_workout(selectedWorkout, workoutName):
    #Displays the exercise details of a selected workout
    workoutContents = []
    workoutTemp = []
    finalPrint = ""
    with open(selectedWorkout, "r+") as workout: #Opens the selected workout file
        reader = csv.reader(workout)
        workoutExerciseContents = list(reader) #Turns the workout csv into a 2D list

        for i in range(0, len(workoutExerciseContents)): #For each exercise in the selected workout
            exerciseName = workoutExerciseContents[i][0]
            exerciseReps = workoutExerciseContents[i][1]
            exerciseSets = workoutExerciseContents[i][2]
            exerciseWeight = workoutExerciseContents[i][3]
            finalPrint = f"{exerciseName}, Reps: {exerciseReps}, Sets: {exerciseSets}, Weight: {exerciseWeight}"
            workoutContents.append(finalPrint)
            workoutTemp.append([exerciseName, exerciseReps, exerciseSets, exerciseWeight])
            #Adds each exercise to workoutTemp which is used when determining which exercise index to display


    left_col =  [[sg.Button(image_data = images.return_button, button_color = (sg.theme_background_color(), sg.theme_background_color()), key = "-RETURN-", border_width = 0)]]
    right_col = [[sg.Text(workoutName, font = ('Helvetica', 30))]]
                
    layout = [[sg.Column(left_col, element_justification = "l"), sg.Column(right_col, element_justification = "c")],
             [sg.Listbox(values = workoutContents, key = "-WORKOUT-", size = (200,10), enable_events = True)]]

    workoutContentsWindow = sg.Window("Workout", layout, size = (1280, 720))

    while True:
        event, values = workoutContentsWindow.read()
        if event == None:
            break
        if event == "-WORKOUT-":
            workoutDetails = values["-WORKOUT-"]
            workoutIndex = workoutContents.index(str(workoutDetails[0])) #Gets the index of the exercise details string
            selectedWorkoutDetails = workoutTemp[workoutIndex]
            #Using workoutIndex, accesses the index in the 2D list of exercise details
            workoutContentsWindow.close()   
            exercise_details(selectedWorkoutDetails[0], selectedWorkoutDetails[1], selectedWorkoutDetails[2], selectedWorkoutDetails[3], True, selectedWorkout, workoutName)
        if event == "-RETURN-":
            workoutContentsWindow.close()
            main()

def create_workout(workoutName, fileName, buttonDisabled):
    if buttonDisabled == False:
        addExerciseDisabled = True
    if buttonDisabled == True:
        addExerciseDisabled = False

    with open("workoutList.txt", "r") as f: #Opens the text file containing the workout names
        workoutsList = [] #Creates a list which the workout names will be appended to
        for line in f: 
            strip_lines = line.strip() #Removes the spaces between the lines
            workoutsList.append(strip_lines) #Appends each workout to the workoutsList

    left_col = [[sg.Button(image_data = images.return_button, button_color = (sg.theme_background_color(), sg.theme_background_color()), key = "-RETURN-", border_width = 0)]]
    workouts_col = [[sg.Text("Workout name: ", key = "-OUT-"), sg.InputText(workoutName, key="-IN-", size = (30,1),disabled=buttonDisabled), sg.Button("Save Name", key = "-SAVENAME-", disabled=buttonDisabled)]]
    middle_col = [[sg.Listbox(values = newExercises, key = "-NEWEXERCISES-", size = (100,20))],
                [sg.Button("Add exercise", key = "-ADD EXERCISE-",disabled = addExerciseDisabled)]]
    layout = [[sg.Column(left_col, element_justification = "l"), sg.Column(workouts_col, pad = (250,0))], [sg.Column(middle_col, element_justification = "c", pad = (250,0))]]
    
    global workoutWindow
    workoutWindow = sg.Window("Workout screen", layout, size = (1280,720))
    while True:
        event, values = workoutWindow.read()
        if event == None:
            break

        if event == "-RETURN-":
            workoutWindow.close()
            main()
        if event == "-SAVENAME-":
            if len(values["-IN-"]) > 30:
                sg.Popup("ERROR- Name is too long")
                workoutWindow["-IN-"].update((values["-IN-"])[0:30])
            else:
                if not values["-IN-"] or not (values["-IN-"]).strip(): #If the workout name is blank
                    sg.Popup("ERROR- BLANK NAME")
                else:
                    try: 
                        workoutName = values["-IN-"] #Accesses the workout name in the input box
                        fileName = values["-IN-"] + ".csv"
                        FILE = open(fileName, "x") #Attempts to create a file with the inputted workout name
                        FILE.close()
                        with open("workoutList.txt", "a") as workoutFile:
                            workoutFile.write(workoutName + "\n") #Appends the workout name to the workoutList txt file
                        
                        workoutWindow["-IN-"].update(disabled=True)
                        workoutWindow["-SAVENAME-"].update(disabled=True)
                        workoutWindow["-ADD EXERCISE-"].update(disabled=False)
                        sg.Popup("Successfully created the workout- You can now add exercises")
                        

                    except IOError: #If a file with the inputted workout name already exists
                        sg.Popup("ERROR- Workout with this name already exists")


        if event == "-ADD EXERCISE-":
            add_exercise(fileName, workoutName)

def selection_sort(list_a): # function that takes a sequence called list_a
	indexing_length = range(0, len(list_a)-1) # range to length of list -1, once only 1 left assumes highest value

	for i in indexing_length:
		min_value = i    # each iteration to be the default min

		for j in range (i+1, len(list_a)): # j (every element) to right of position 
			if list_a[j] < list_a [min_value]: # if list_a in j position is less than min value then change to min value
				min_value = j
		
		if min_value != i: # find an item with a lower value than default we switch by...
			list_a [min_value], list_a[i] = list_a [i], list_a [min_value] # swap positions...

	return list_a # return list_a


def add_exercise(fileName, workoutName):
    exerciseList = []
    with open("exerciseList.csv","r") as eFile:
        eReader = csv.reader(eFile)
        exerciseContents = list(eReader)
        for i in range(0,len(exerciseContents)):
            exerciseList.append(exerciseContents[i][1])

    layout = [[sg.Listbox(values = selection_sort(exerciseList), key = "-EXERCISE LIST-", enable_events = True, size = (100,20))],
             [sg.Button("Add custom exercise", key = "-CUSTOMEXERCISE-")]]
    exerciseNameWindow = sg.Window("Exercise screen", layout)

    while True:
        event, values = exerciseNameWindow.read()
        if event == None:
            break
        if event == "-EXERCISE LIST-": #If the user selects an exercise from the listBox
            workoutWindow.close()
            exerciseNameWindow.close()
            newExerciseName =  values["-EXERCISE LIST-"]
            exercise_details(str(newExerciseName[0]), 0, 0, 0, False, fileName, workoutName) 
        
        if event == "-CUSTOMEXERCISE-":
            create_custom_exercise()
            exerciseList = []
            with open("exerciseList.csv","r") as eFile:
                eReader = csv.reader(eFile)
                exerciseContents = list(eReader)
                for i in range(0,len(exerciseContents)):
                    exerciseList.append(exerciseContents[i][1])
            
            exerciseNameWindow["-EXERCISE LIST-"].update(values = selection_sort(exerciseList))

def create_custom_exercise():
    addCustomValidation = True
    layout = [[sg.Text("Enter workout name: "), sg.In(key="-CUSTOM-"), sg.Button("Add exercise", key = "-CONFIRM-")]]
    customWorkoutWindow = sg.Window("Add custom exercise", layout)
    while True:
        event, values = customWorkoutWindow.read()
        if event == None:
            break
        
        if event == "-CONFIRM-":
            customExercise = values["-CUSTOM-"]
            exerciseList = []
            with open("exerciseList.csv","r") as eFile:
                eReader = csv.reader(eFile)
                exerciseContents = list(eReader)
                for i in range(0,len(exerciseContents)):
                    exerciseList.append(exerciseContents[i][1])
            
            for i in exerciseList:
                if customExercise == i:
                    sg.Popup("ERORR- EXERCISE ALREADY IN LIST")
                    customWorkoutWindow.close()
                    addCustomValidation = False
                    break


            if addCustomValidation == True:
                with open("exerciseList.csv", "a", newline = "") as f:
                    writer = csv.writer(f)
                    appendCustomExercise = [len(exerciseContents)+1, customExercise]
                    writer.writerow(appendCustomExercise)
                
                customWorkoutWindow.close()
            break




def exercise_details(exerciseName, selectedReps, selectedSets, selectedWeight, loopBool, selectedFile, selectedWorkoutName):
    layout = [[sg.Text("Exercise Details", font = ("Helvetica", "10"))], [sg.Text("Reps:"), sg.Slider(key = "-REPS-", enable_events = True, range = (1,50), default_value = selectedReps, size = (100,30), orientation = "horizontal")],
              [sg.Text("Sets:"), sg.Slider(key = "-SETS-", enable_events = True, range = (1,50), default_value = selectedSets, size = (100,30), orientation = "horizontal")],
              [sg.Text("Weight: "), sg.Input(selectedWeight,key="-WEIGHT-", enable_events = True)],
              [sg.Button("Return")]
    ]

    exerciseDetailsWindow = sg.Window("Exercise Details", layout, size = (1280,720))
    while True:

        event, values = exerciseDetailsWindow.read()
        if event == None or event == "Return":
            exerciseDetailsWindow.close()
            break
        if event == "-REPS-": #If the user moves the reps slider
            selectedReps = values["-REPS-"]
        if event == "-SETS-": #If the user moves the sets slider
            selectedSets = values["-SETS-"]
        if event == "-WEIGHT-": #If the user enters into the weight input box
            try: #Tries to convert the weight to a float
                selectedWeight = float(values["-WEIGHT-"])
            except ValueError: #If the input is not an integer/float
                sg.Popup("ERROR- PLEASE ENTER A NUMBER")
                exerciseDetailsWindow["-WEIGHT-"].update("") #Change the input box to blank


    newExerciseDetails = [exerciseName, selectedReps, selectedSets, selectedWeight]
    if loopBool == False: #If an exercise is being added
        with open(selectedFile, "a", newline = "") as g:
            writer = csv.writer(g)
            writer.writerow(newExerciseDetails) #Append the new exercise to the csv
        
        addNewExercise = f"{exerciseName}, Reps: {selectedReps}, Sets: {selectedSets}, Weight: {selectedWeight}"
        newExercises.append(addNewExercise)
        create_workout(selectedWorkoutName,selectedFile, True)

    if loopBool == True: #If an exercise is being modified
        with open(selectedFile, "r") as h:
            reader = csv.reader(h)
            exercisesInWorkout = list(reader) #Converts the workout file to a 2D list
            for i in range(0, len(exercisesInWorkout)): #Iterates through the 2D list
                if exercisesInWorkout[i][0] == exerciseName: #If the selected exercise is in the 2D list
                    selectedExercise = i #Set the selectedExercise variable equal to the index
            
            exerciseDetailsWindow.close()
                
        with open(selectedFile, "w", newline = "") as g: 
            writer = csv.writer(g)
            exercisesInWorkout[selectedExercise] = newExerciseDetails #Modify the selected exercise with the new exercise details   
            writer.writerows(exercisesInWorkout)#Rewrites to the selected file
            exerciseDetailsWindow.close()
        
        view_workout(selectedFile, selectedWorkoutName)
        
def workout_scheduler():
    userAssignedWorkout = []
    with open("assignedWorkout.csv", "r") as assignedFile:
        reader = csv.reader(assignedFile)
        assignedList = list(reader)
        for i in range(0, len(assignedList)):
            userAssignedWorkout.append(assignedList[i][1])
            
    top_left_col =  [[sg.Button(image_data = images.return_button, button_color = (sg.theme_background_color(), sg.theme_background_color()), key = "-RETURN-", border_width = 0, pad = (30,30))]]
    schedule_title = [[sg.Image(data = images.sch_title)]]
    left_col = [[sg.Text(" Day 1: "), sg.Button(userAssignedWorkout[0], key = "-WORKOUT1-", font = ('Helvetica', 20))],
                [sg.Text(" Day 2: "), sg.Button(userAssignedWorkout[1], key = "-WORKOUT2-", font = ('Helvetica', 20))],
                [sg.Text(" Day 3: "), sg.Button(userAssignedWorkout[2], key = "-WORKOUT3-", font = ('Helvetica', 20))],
                [sg.Text(" Day 4: "), sg.Button(userAssignedWorkout[3], key = "-WORKOUT4-", font = ('Helvetica', 20))],
                [sg.Text(" Day 5: "), sg.Button(userAssignedWorkout[4], key = "-WORKOUT5-", font = ('Helvetica', 20))],
                [sg.Text(" Day 6: "), sg.Button(userAssignedWorkout[5], key = "-WORKOUT6-", font = ('Helvetica', 20))],
                [sg.Text(" Day 7: "), sg.Button(userAssignedWorkout[6], key = "-WORKOUT7-", font = ('Helvetica', 20))]]

    right_col = [[sg.Text("Day 8: "), sg.Button(userAssignedWorkout[7], key = "-WORKOUT8-", font = ('Helvetica', 20))],
                [sg.Text("Day 9: "), sg.Button(userAssignedWorkout[8], key = "-WORKOUT9-", font = ('Helvetica', 20))],
                [sg.Text("Day 10:"), sg.Button(userAssignedWorkout[9], key = "-WORKOUT10-", font = ('Helvetica', 20))],
                [sg.Text("Day 11:"), sg.Button(userAssignedWorkout[10], key = "-WORKOUT11-", font = ('Helvetica', 20))],
                [sg.Text("Day 12:"), sg.Button(userAssignedWorkout[11], key = "-WORKOUT12-", font = ('Helvetica', 20))],
                [sg.Text("Day 13:"), sg.Button(userAssignedWorkout[12], key = "-WORKOUT13-", font = ('Helvetica', 20))],
                [sg.Text("Day 14:"), sg.Button(userAssignedWorkout[13], key = "-WORKOUT14-", font = ('Helvetica', 20))]]
    layout = [[sg.Column(top_left_col), sg.Column(schedule_title, pad = (280, 0))],
        [sg.Column(left_col, pad = (100,0)), sg.VSeperator(pad = (80,0)), sg.Column(right_col, pad = (20, 0))]]

    schedulerWindow = sg.Window("Scheduler", layout, size = (1280, 720))

    while True:
        event, values = schedulerWindow.read()
        if event == None:
            schedulerWindow.close()
            break
        if event == "-RETURN-":
            schedulerWindow.close()
            main()
        if event == "-WORKOUT1-":
            schedulerWindow.close()
            assign_workout(0)

        if event == "-WORKOUT2-":
            schedulerWindow.close()
            assign_workout(1)
        if event == "-WORKOUT3-":
            assign_workout(2)
            schedulerWindow.close()
        if event == "-WORKOUT4-":
            schedulerWindow.close()
            assign_workout(3)
        if event == "-WORKOUT5-":
            schedulerWindow.close()
            assign_workout(4)
        if event == "-WORKOUT6-":
            assign_workout(5)
            schedulerWindow.close()
        if event == "-WORKOUT7-":
            assign_workout(6)
            schedulerWindow.close()
        if event == "-WORKOUT8-":
            assign_workout(7)
            schedulerWindow.close()
        if event == "-WORKOUT9-":
            assign_workout(8)
            schedulerWindow.close()
        if event == "-WORKOUT10-":
            assign_workout(9)
            schedulerWindow.close()
        if event == "-WORKOUT11-":
            assign_workout(10)
            schedulerWindow.close()
        if event == "-WORKOUT12-":
            assign_workout(11)
            schedulerWindow.close()
        if event == "-WORKOUT13-":
            assign_workout(12)
            schedulerWindow.close()
        if event == "-WORKOUT14-":
            assign_workout(13)
            schedulerWindow.close()



def assign_workout(workoutIndex):
    with open("workoutList.txt", "r") as f: #Opens the txt file containing the workout names
        workoutsList = []
        for line in f: #For each workout in the file
            strip_lines = line.strip() #Removes the spaces between the lines
            workoutsList.append(strip_lines) #Append the workout to the workoutsList

    workoutsList.append("Rest")
    with open("assignedWorkout.csv", "r") as assignedFile:
        reader = csv.reader(assignedFile)
        assignedList = list(reader) #Converts the assignedWorkout file to a 2D list
        
    layout = [[sg.Listbox(values = workoutsList, key = "-WORKOUTLIST-", size = (100,5), enable_events = True)]]
    assignWindow = sg.Window("Assign workout", layout, size = (1280, 720))
    while True:
        event, values = assignWindow.read()
        if event == "-WORKOUTLIST-": #If the user clicks on a workout
            userSelectedAssignment = values["-WORKOUTLIST-"] 
            assignedList[workoutIndex][1] = str(userSelectedAssignment[0]) #Modifies the workout name at the selected day to the selected workout
            with open("assignedWorkout.csv", "w", newline = "") as assignedFile:
                writer = csv.writer(assignedFile)
                writer.writerows(assignedList) #Rewrites to 2D list to assignedWorkout.csv

            assignWindow.close()
            workout_scheduler()
        
        
        if event == None:
            break
                
        
login_screen()