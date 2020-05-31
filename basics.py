student_grades = [9, 8, 7 ]
mySum = sum(student_grades)
length = len(student_grades)
mean = mySum / length
print("Average=",mean)

max_value = max(student_grades)
print("Max Value=",max_value)

print(student_grades.count(8))

#capitalize letter
text1 = "This Text should be in capital"
print(text1.upper())

#student grades using dictionary
student_grades2 = {"marry":9, "Sim": 8 ,"Gary":7}
mySum2 = sum (student_grades2.values()) #values is a method in dict
length2 = len (student_grades2)
mean2 = mySum2 / length2
print(mean2)
print (student_grades2.keys())
#This line is edited Online
