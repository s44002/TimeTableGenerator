import random
import json
from tabulate import tabulate

# Custom exception class for handling scheduling errors


class SchedulingError(Exception):
    pass

# Class to represent a school class


class SchoolClass:
    def __init__(self, name, sections, periods, subject_teacher_pairs):
        self.name = name
        self.sections = sections
        self.periods = periods
        self.subject_teacher_pairs = subject_teacher_pairs
        self.timetable = {
            section: [[[None, None] for _ in periods] for _ in range(6)]
            for section in sections
        }
        self.class_teachers = {}

    # Assigns a class teacher to a section
    def assign_class_teacher(self, section, class_teacher):
        class_teacher_subject = None
        for subject, teacher in self.subject_teacher_pairs:
            if teacher == class_teacher:
                class_teacher_subject = subject
                break
        if class_teacher_subject is None:
            raise SchedulingError(
                f"No subject-teacher pair found for Class {self.name} Section {section} and teacher {class_teacher}"
            )
        self.class_teachers[section] = [class_teacher_subject, class_teacher]

    # Generates the timetable for the school class
    def generate_timetable(self, teacher_schedule_dict, subject_limits, first_class_taken_by_class_teacher):
        for section in self.sections:
            # If the first class is taken by the class teacher
            if first_class_taken_by_class_teacher and section in self.class_teachers:
                class_teacher_subject, class_teacher = self.class_teachers[section]
                # Assign the class teacher to the first period of each day in the timetable
                for day in range(6):
                    teacher_schedule_dict[class_teacher][day][0] = True
                    self.timetable[section][day][0] = [
                        class_teacher_subject, class_teacher]
            # If the first class is not taken by the class teacher
            elif not first_class_taken_by_class_teacher:
                available_pairs = self.subject_teacher_pairs.copy()
                random.shuffle(available_pairs)  # Shuffle for randomness
                for subject, class_teacher in available_pairs:
                    if subject in self.class_subjects:
                        self.class_teachers[section] = [subject, class_teacher]
                        self.class_subjects.remove(subject)
                        # Assign the subject-teacher pair to the first period of each day in the timetable
                        for day in range(6):
                            teacher_schedule_dict[class_teacher][day][0] = True
                            self.timetable[section][day][0] = [
                                subject, class_teacher]
                        break
                else:
                    raise SchedulingError(
                        f"No available subject-teacher pairs for Class {self.name} Section {section}"
                    )
            else:
                raise SchedulingError(
                    f"No class teacher assigned for Class {self.name} Section {section}"
                )

            # Generate timetable for the remaining periods of each day
            for day in range(6):  # Assuming a 6-day week
                daily_subject_count = {}
                previous_subject = None
                for period in range(1, len(self.periods)):
                    available_pairs = self.subject_teacher_pairs.copy()
                    random.shuffle(available_pairs)  # Shuffle for randomness
                    for pair in available_pairs:
                        subject, teacher = pair
                        # Check if the teacher is already scheduled for the current day and period
                        if (
                            teacher_schedule_dict[teacher][day][period]
                            # Check if the subject has reached the maximum daily limit
                            or daily_subject_count.get(subject, 0) >= subject_limits[subject]["max_daily"]
                            # Check if the subject has reached the maximum weekly limit
                            or sum(day.count(subject) for day in self.timetable[section]) >= subject_limits[subject]["max_weekly"]
                            # Check if the subject is the same as the previous subject (to avoid consecutive periods)
                            or subject == previous_subject
                        ):
                            continue
                        # Assign the subject-teacher pair to the current day and period in the timetable
                        teacher_schedule_dict[teacher][day][period] = True
                        daily_subject_count[subject] = daily_subject_count.get(
                            subject, 0) + 1
                        self.timetable[section][day][period] = list(pair)
                        previous_subject = subject
                        break
                    else:
                        raise SchedulingError(
                            f"No available subject-teacher pairs for Class {self.name} Section {section} on Day {day + 1} Period {self.periods[period]}"
                        )

    # Saves the timetable to a text file
    def save_timetable_to_txt(self, filename):
        with open(filename, "a") as f:
            for section, timetable in self.timetable.items():
                f.write(f"{self.name} - Section {section}\n")
                table = [["Day/Period"] +
                         [f"Period {period}" for period in self.periods]]
                for day in range(6):
                    row = [f"Day {day + 1}"]
                    for period in timetable[day]:
                        subject, teacher = period
                        row.append(f"{subject or ''} - {teacher}")
                    table.append(row)
                f.write(tabulate(table, headers="firstrow", tablefmt="grid"))
                f.write("\n\n")

# Class to represent a school


class School:
    def __init__(self, classes, teachers, periods):
        self.classes = classes
        self.teachers = teachers
        self.teacher_schedule = {
            teacher: [[False for _ in periods] for _ in range(6)] for teacher in teachers
        }

    # Generates timetables for all school classes
    def generate_timetables(self, first_class_taken_by_class_teacher=True):
        try:
            for school_class in self.classes:
                school_class.generate_timetable(
                    self.teacher_schedule, subject_limits, first_class_taken_by_class_teacher
                )
        except SchedulingError as e:
            print(e)

    # Saves timetables for all school classes to a text file
    def save_timetables_to_txt(self, filename):
        with open(filename, "w") as f:
            pass
        for school_class in self.classes:
            school_class.save_timetable_to_txt(filename)

    # Saves timetables for all school classes to a JSON file
    def save_timetables_to_json(self, filename):
        timetable_data = []
        for school_class in self.classes:
            class_data = {
                "class_name": school_class.name,
                "sections": school_class.sections,
                "timetable": school_class.timetable
            }
            timetable_data.append(class_data)
        with open(filename, "w") as f:
            json.dump(timetable_data, f, indent=4)

# Predefined data


# Days of the week
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Periods in a day
periods = [1, 2, 3, 4, 5, 6, 7, 8]

# List of subjects taught in the school
subjects = [
    "Math", "Science", "English", "History", "Geography", "Art", "Music", "Physical Education"
]

# List of teachers in the school
teachers = [
    "Mr. Smith", "Mrs. Johnson", "Mr. Davis", "Mrs. Anderson", "Mr. Wilson",
    "Mrs. Martinez", "Mr. Thompson", "Mrs. Garcia", "Mr. White", "Mrs. Lee",
    "Mr. Clark", "Mrs. Hall", "Mr. Lewis", "Mrs. Walker", "Mr. Young", "Mrs. Hill"
]

# List of subject-teacher pairs
subject_teacher_pairs = [
    ("Math", "Mr. Smith"),
    ("Science", "Mrs. Johnson"),
    ("English", "Mr. Davis"),
    ("History", "Mrs. Anderson"),
    ("Geography", "Mr. Wilson"),
    ("Art", "Mrs. Martinez"),
    ("Music", "Mr. Thompson"),
    ("Physical Education", "Mrs. Garcia"),
    ("Physics", "Mr. White"),
    ("Chemistry", "Mrs. Lee"),
    ("Biology", "Mr. Clark"),
    ("Computer Science", "Mrs. Hall"),
    ("Literature", "Mr. Lewis"),
    ("Spanish", "Mrs. Walker"),
    ("Social Studies", "Mr. Young"),
    ("Social Studies", "Mrs. Hill")
]

# Dictionary defining maximum daily and weekly limits for each subject
subject_limits = {
    "Math": {"max_daily": 2, "max_weekly": 6},
    "Science": {"max_daily": 2, "max_weekly": 6},
    "English": {"max_daily": 2, "max_weekly": 6},
    "History": {"max_daily": 2, "max_weekly": 6},
    "Geography": {"max_daily": 2, "max_weekly": 6},
    "Art": {"max_daily": 2, "max_weekly": 6},
    "Music": {"max_daily": 2, "max_weekly": 6},
    "Physical Education": {"max_daily": 2, "max_weekly": 6},
    "Physics": {"max_daily": 2, "max_weekly": 6},
    "Chemistry": {"max_daily": 2, "max_weekly": 6},
    "Biology": {"max_daily": 2, "max_weekly": 6},
    "Computer Science": {"max_daily": 2, "max_weekly": 6},
    "Literature": {"max_daily": 2, "max_weekly": 6},
    "Spanish": {"max_daily": 2, "max_weekly": 6},
    "Social Studies": {"max_daily": 2, "max_weekly": 6}
}

# List of school classes
classes = [
    SchoolClass("Grade 1", ["Grade 1.A", "Grade 1.B",
                "Grade 1.C"], periods, subject_teacher_pairs),
    SchoolClass("Grade 2", ["Grade 2.A", "Grade 2.B",
                "Grade 2.C"], periods, subject_teacher_pairs),
    SchoolClass("Grade 3", ["Grade 3.A", "Grade 3.B",
                "Grade 3.C"], periods, subject_teacher_pairs),
    SchoolClass("Grade 4", ["Grade 4.A", "Grade 4.B",
                "Grade 4.C"], periods, subject_teacher_pairs)
]

# Mapping of class names to the subjects taught in each class
class_subjects = {
    "Grade 1": ["Math", "Science", "English"],
    "Grade 2": ["History", "Geography", "Art"],
    "Grade 3": ["Music", "Physical Education"],
    "Grade 4": ["Physics", "Chemistry", "Biology"]
}

# Mapping of class sections to their respective class teachers
class_teachers = {
    "Grade 1.A": "Mr. Smith",
    "Grade 1.B": "Mrs. Johnson",
    "Grade 1.C": "Mr. Davis",
    "Grade 2.A": "Mrs. Anderson",
    "Grade 2.B": "Mr. Wilson",
    "Grade 2.C": "Mrs. Martinez",
    "Grade 3.A": "Mr. Thompson",
    "Grade 3.B": "Mrs. Garcia",
    "Grade 3.C": "Mr. White",
    "Grade 4.A": "Mrs. Lee",
    "Grade 4.B": "Mr. Clark",
    "Grade 4.C": "Mrs. Hall"
}

# Mapping of class sections to class teachers for the first class
first_class_teachers = class_teachers

# Assign class teachers to school classes
for school_class in classes:
    school_class.class_subjects = set(
        class_subjects.get(school_class.name, []))
    for section in school_class.sections:
        if section in first_class_teachers:
            class_teacher = first_class_teachers[section]
            school_class.assign_class_teacher(section, class_teacher)
        elif section in class_teachers:
            class_teacher = class_teachers[section]
            school_class.assign_class_teacher(section, class_teacher)
        else:
            raise SchedulingError(
                f"No class teacher assigned for Class {school_class.name} Section {section}"
            )

# Create a School object
my_school = School(classes, teachers, periods)

# Generate timetables for all school classes
my_school.generate_timetables(True)

# Save timetables to text and JSON files
my_school.save_timetables_to_txt("timetable.txt")
my_school.save_timetables_to_json("timetable.json")
