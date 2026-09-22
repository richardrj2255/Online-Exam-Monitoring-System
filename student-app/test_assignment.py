from models.assignment_model import AssignmentModel

exam = AssignmentModel.get_assigned_exam(4)

print(exam)