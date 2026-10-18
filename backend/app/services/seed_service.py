from sqlalchemy.orm import Session
from app.models.entities import User, RoleCompetency, AssessmentTask, SkillEvidence, SkillStatus
from app.core.security import get_password_hash

def seed_database_data(db: Session):
    # 1. Seed Demo Students & Instructor
    if not db.query(User).filter(User.username == "student_demo").first():
        demo_student = User(
            email="demo@meridian.edu",
            username="student_demo",
            full_name="Aarav Sharma (Demo Student)",
            hashed_password=get_password_hash("meridian2026"),
            target_role="Junior Python Developer",
            is_active=True,
            is_instructor=False
        )
        instructor = User(
            email="prof@meridian.edu",
            username="prof_admin",
            full_name="Dr. Sunita Rao (Course Examiner)",
            hashed_password=get_password_hash("examiner2026"),
            target_role="Junior Python Developer",
            is_active=True,
            is_instructor=True
        )
        db.add_all([demo_student, instructor])
        db.commit()
        db.refresh(demo_student)

        # Initialize baseline skill evidence for demo student
        initial_evidence = [
            SkillEvidence(
                user_id=demo_student.id,
                skill_id="python_basics",
                skill_name="Python Syntax & Control Flow",
                status=SkillStatus.DEMONSTRATED_INDEPENDENT,
                mastery_score=92.0,
                assisted_attempts_count=1,
                independent_attempts_count=1,
                evidence_notes="Verified via unassisted conditional and loop challenge."
            ),
            SkillEvidence(
                user_id=demo_student.id,
                skill_id="python_oop",
                skill_name="Object-Oriented Programming (Classes & Inheritance)",
                status=SkillStatus.DEMONSTRATED_ASSISTED,
                mastery_score=68.0,
                assisted_attempts_count=2,
                independent_attempts_count=0,
                evidence_notes="Completed assisted exercise using 2 graduated hints. Requires independent verification."
            ),
            SkillEvidence(
                user_id=demo_student.id,
                skill_id="python_fastapi",
                skill_name="FastAPI & REST Architecture",
                status=SkillStatus.NEEDS_DEVELOPMENT,
                mastery_score=35.0,
                assisted_attempts_count=1,
                independent_attempts_count=0,
                evidence_notes="Initial baseline indicates difficulty with request validation and status codes."
            )
        ]
        db.add_all(initial_evidence)
        db.commit()

    # 2. Seed Role Competency Maps
    if db.query(RoleCompetency).count() == 0:
        competencies = [
            # Junior Python Developer
            RoleCompetency(role_name="Junior Python Developer", skill_id="python_basics", skill_name="Python Syntax & Data Structures", category="Core Language", prerequisites=[], priority_weight=1.0),
            RoleCompetency(role_name="Junior Python Developer", skill_id="python_oop", skill_name="Object-Oriented Design & Encapsulation", category="Core Language", prerequisites=["python_basics"], priority_weight=1.5),
            RoleCompetency(role_name="Junior Python Developer", skill_id="python_fastapi", skill_name="FastAPI & REST Endpoints", category="Backend Frameworks", prerequisites=["python_basics", "python_oop"], priority_weight=2.0),
            RoleCompetency(role_name="Junior Python Developer", skill_id="python_sql", skill_name="Relational Databases & ORM", category="Data Persistence", prerequisites=["python_basics"], priority_weight=1.8),

            # Junior Java Developer
            RoleCompetency(role_name="Junior Java Developer", skill_id="java_syntax", skill_name="Java Types, Variables & Conditionals", category="Language Fundamentals", prerequisites=[], priority_weight=1.0),
            RoleCompetency(role_name="Junior Java Developer", skill_id="java_loops", skill_name="Iteration, Arrays & Loop Control", category="Algorithms", prerequisites=["java_syntax"], priority_weight=1.4),
            RoleCompetency(role_name="Junior Java Developer", skill_id="java_oop", skill_name="Classes, Interfaces & Polymorphism", category="OOP Principles", prerequisites=["java_syntax", "java_loops"], priority_weight=2.0),

            # Entry-Level Web Developer
            RoleCompetency(role_name="Entry-Level Web Developer", skill_id="web_html_css", skill_name="Semantic HTML5 & Responsive CSS", category="Frontend Foundation", prerequisites=[], priority_weight=1.0),
            RoleCompetency(role_name="Entry-Level Web Developer", skill_id="web_js_basics", skill_name="JavaScript DOM & Async Fetch", category="Client Logic", prerequisites=["web_html_css"], priority_weight=1.5),
            RoleCompetency(role_name="Entry-Level Web Developer", skill_id="web_react", skill_name="React Components & State Hooks", category="Modern UI", prerequisites=["web_html_css", "web_js_basics"], priority_weight=2.0),
        ]
        db.add_all(competencies)
        db.commit()

    # 3. Seed Assessment Tasks (Assisted and Independent pairs)
    if db.query(AssessmentTask).count() == 0:
        tasks = [
            AssessmentTask(
                id="task_python_basics_baseline",
                role_name="Junior Python Developer",
                skill_id="python_basics",
                title="Baseline: Filter Even Numbers and Calculate Sum",
                task_type="baseline",
                prompt="Write a Python function `sum_even_numbers(numbers: list[int]) -> int` that takes a list of integers and returns the sum of all positive even integers.",
                instructions="Use standard iteration or list comprehensions with modulo arithmetic.",
                initial_code_or_template="def sum_even_numbers(numbers: list[int]) -> int:\n    # Implement logic here\n    pass",
                expected_output_or_answer="sum([n for n in numbers if n > 0 and n % 2 == 0])",
                evaluation_criteria={"required_keywords": ["def", "sum_even_numbers", "% 2", "return"]},
                hints_available=[
                    "Consider checking if number is greater than zero and has remainder zero when divided by 2.",
                    "Use the `%` modulo operator: `n % 2 == 0`."
                ],
                is_independent=False
            ),
            AssessmentTask(
                id="task_python_oop_assisted",
                role_name="Junior Python Developer",
                skill_id="python_oop",
                title="Assisted Practice: Encapsulated Bank Account Class",
                task_type="assisted",
                prompt="Create a `BankAccount` class with private `_balance: float` initialized to 0.0. Provide `deposit(amount)` and `withdraw(amount)` methods with validation that rejects negative values.",
                instructions="Ensure encapsulation conventions are followed. Raise ValueError or return False on invalid withdrawals.",
                initial_code_or_template="class BankAccount:\n    def __init__(self, initial_deposit: float = 0.0):\n        self._balance = initial_deposit\n    \n    def deposit(self, amount: float) -> bool:\n        pass",
                expected_output_or_answer="class BankAccount with deposit and withdraw checks",
                evaluation_criteria={"required_keywords": ["class BankAccount", "def deposit", "def withdraw", "self._balance"]},
                hints_available=[
                    "Initialize `self._balance` inside `__init__`.",
                    "In `deposit`, ensure `amount > 0` before updating `self._balance`.",
                    "In `withdraw`, check both `amount > 0` and `amount <= self._balance`."
                ],
                is_independent=False
            ),
            AssessmentTask(
                id="task_python_oop_independent",
                role_name="Junior Python Developer",
                skill_id="python_oop",
                title="Independent Verification: Library Inventory Manager Class",
                task_type="independent",
                prompt="Write a `LibraryInventory` class encapsulating a private dictionary `_books: dict[str, int]`. Implement `add_stock(isbn, qty)` and `borrow_book(isbn, qty)`. Hints are disabled to verify independent competency.",
                instructions="Strict independent conditions. No AI assistance or hints permitted during this evaluation.",
                initial_code_or_template="class LibraryInventory:\n    def __init__(self):\n        self._books = {}\n        \n    def add_stock(self, isbn: str, quantity: int) -> None:\n        # Write independent implementation\n        pass\n        \n    def borrow_book(self, isbn: str, quantity: int) -> bool:\n        pass",
                expected_output_or_answer="class LibraryInventory",
                evaluation_criteria={"required_keywords": ["class LibraryInventory", "self._books", "add_stock", "borrow_book"]},
                hints_available=[], # Strict unassisted policy
                is_independent=True
            ),
            AssessmentTask(
                id="task_java_loops_assisted",
                role_name="Junior Java Developer",
                skill_id="java_loops",
                title="Assisted Practice: Find Maximum In Array",
                task_type="assisted",
                prompt="Implement a Java method `public static int findMax(int[] arr)` that returns the largest value in an array.",
                instructions="Handle empty array edge case appropriately.",
                initial_code_or_template="public class ArrayUtils {\n    public static int findMax(int[] arr) {\n        // Iterate through elements\n        return 0;\n    }\n}",
                expected_output_or_answer="for loop scanning elements",
                evaluation_criteria={"required_keywords": ["public static int findMax", "for", "arr.length"]},
                hints_available=[
                    "Declare `int max = arr[0];` before the loop.",
                    "Iterate from index 1 to `arr.length - 1` and update `max` when an element is larger."
                ],
                is_independent=False
            ),
            AssessmentTask(
                id="task_web_js_assisted",
                role_name="Entry-Level Web Developer",
                skill_id="web_js_basics",
                title="Assisted Practice: Asynchronous Data Fetch Handler",
                task_type="assisted",
                prompt="Write an async function `fetchUserData(userId)` that fetches `/api/v1/users/${userId}` and returns the parsed JSON payload.",
                instructions="Use modern `async/await` and handle HTTP response `ok` flag.",
                initial_code_or_template="async function fetchUserData(userId) {\n    // Implement fetch and JSON parse\n}",
                expected_output_or_answer="async await fetch",
                evaluation_criteria={"required_keywords": ["async function", "await fetch", ".json()"]},
                hints_available=[
                    "Remember that `fetch()` returns a Promise that resolves to a Response object.",
                    "Use `await response.json()` to parse the payload body."
                ],
                is_independent=False
            )
        ]
        db.add_all(tasks)
        db.commit()
