from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.urls import reverse
from urllib.parse import quote_plus
from .models import UserProgress, RoadmapStep, CareerRoadmap ,UserStreak
from django.urls import reverse
from urllib.parse import quote_plus
from datetime import date, timedelta
from xhtml2pdf import pisa
from io import BytesIO
import re

# -------------------------------------------------------------------
# PYTHON – detailed multi-stage roadmap
# -------------------------------------------------------------------

PYTHON_BEGINNER_STEPS = [
    {
        "number": 1,
        "title": "Week 1 · Setup & First Steps",
        "duration": "Week 1",
        "done": False,
        "summary": "Go from zero to running your first Python programs.",
        "topics": [
            "Install Python (or Anaconda) and set up a virtual environment",
            "Set up a code editor (VS Code recommended)",
            'Write your first program: print(\"Hello, World!\")',
            "Understand variables and basic data types (int, float, str, bool)",
            "Use input() to read simple user input",
            "Run Python scripts from the editor or terminal",
        ],
    },
    {
        "number": 2,
        "title": "Week 2 · Operators & Strings",
        "duration": "Week 2",
        "done": False,
        "summary": "Learn how to perform calculations and work with text.",
        "topics": [
            "Use arithmetic operators (+, -, *, /, //, %, **)",
            "Use comparison operators (==, !=, <, >, <=, >=)",
            "Use logical operators (and, or, not)",
            "Work with strings: concatenation, indexing, slicing",
            "Use string methods: .upper(), .lower(), .strip(), .replace()",
            "Format strings using f-strings",
            "Mini-project: Tip calculator that computes the final bill per person",
        ],
    },
    {
        "number": 3,
        "title": "Week 3 · Lists & Tuples",
        "duration": "Week 3",
        "done": False,
        "summary": "Master ordered collections to store groups of values.",
        "topics": [
            "Create lists and access items by index",
            "Use slicing (my_list[1:4]) to get sublists",
            "Use list methods: .append(), .insert(), .pop(), .remove(), .sort()",
            "Understand tuples and why they are immutable",
            "Convert between lists and tuples when needed",
            "Mini-project: Favorite movies manager (add/remove/list movies)",
        ],
    },
    {
        "number": 4,
        "title": "Week 4 · Dictionaries & Sets",
        "duration": "Week 4",
        "done": False,
        "summary": "Use key–value pairs and unique collections.",
        "topics": [
            "Create dictionaries and access values by key",
            "Add, update and delete dictionary entries",
            "Use .keys(), .values(), .items() to iterate over dictionaries",
            "Create sets and understand uniqueness of elements",
            "Use set operations: add, remove, union, intersection",
            "Mini-project: Simple contact book (name → phone number) in a dict",
        ],
    },
    {
        "number": 5,
        "title": "Week 5 · Control Flow: Conditionals",
        "duration": "Week 5",
        "done": False,
        "summary": "Make your programs react differently based on conditions.",
        "topics": [
            "Write if, elif, else blocks",
            "Use nested conditionals for more complex decision trees",
            "Combine conditions with logical operators",
            "Plan simple decision-based algorithms using flowcharts or pseudocode",
            "Mini-project: Number guessing game with hints (too high / too low)",
        ],
    },
    {
        "number": 6,
        "title": "Week 6 · Control Flow: Loops",
        "duration": "Week 6",
        "done": False,
        "summary": "Repeat actions efficiently with loops.",
        "topics": [
            "Use for loops with range()",
            "Iterate over lists, tuples, dictionaries and strings",
            "Use while loops for repeated actions until a condition is met",
            "Understand break, continue and how to avoid infinite loops",
            "Mini-project: Improved number guessing game with a limited number of tries",
        ],
    },
    {
        "number": 7,
        "title": "Week 7 · Functions",
        "duration": "Week 7",
        "done": False,
        "summary": "Organise code into reusable, testable blocks.",
        "topics": [
            "Define functions with def and call them from other code",
            "Understand parameters vs. arguments",
            "Use return values to send results back to the caller",
            "Understand local vs. global variables",
            "Write docstrings to document your functions",
            "Mini-project: Refactor tip calculator or guessing game into functions",
        ],
    },
    {
        "number": 8,
        "title": "Week 8 · Error Handling & File I/O",
        "duration": "Week 8",
        "done": False,
        "summary": "Write programs that handle errors and work with files safely.",
        "topics": [
            "Use try, except, else, finally blocks",
            "Handle common errors like ValueError and TypeError",
            "Open files safely with with open(...) as f:",
            "Read text files with .read(), .readline(), .readlines()",
            "Write to files with .write() and .writelines()",
            "Mini-project: Extend contact book to load/save contacts from a file",
        ],
    },
    {
        "number": 9,
        "title": "Week 9 · Modules & Packages",
        "duration": "Week 9",
        "done": False,
        "summary": "Leverage Python’s ecosystem with modules and third-party packages.",
        "topics": [
            "Understand what a module is and why we use them",
            "Import built-in modules like math, random, datetime",
            "Create your own simple module and import it",
            "Use pip to install external packages",
            "Mini-project: Use the requests library to call a simple public API",
        ],
    },
    {
        "number": 10,
        "title": "Week 10 · Beginner Capstone Project",
        "duration": "Week 10",
        "done": False,
        "summary": "Combine everything you’ve learned into a small end-to-end project.",
        "topics": [
            "Plan a small project (inputs, outputs, main features)",
            "Break the project into functions and modules",
            "Handle errors and store data in files",
            "Ideas:",
            " • To-Do List CLI app (add, view, complete, delete tasks, save to file)",
            " • Command-line calculator supporting multiple operations and history",
        ],
    },
]

PYTHON_INTERMEDIATE_STEPS = [
    {
        "number": 11,
        "title": "Weeks 11–12 · Advanced Python & OOP",
        "duration": "Weeks 11–12",
        "done": False,
        "summary": "Move from simple scripts to more structured, object-oriented code.",
        "topics": [
            "List comprehensions and dictionary comprehensions",
            "Lambda functions, map(), filter() and sorted() with key functions",
            "Define your own classes and objects with __init__",
            "Instance attributes and instance methods",
            "OOP pillars: inheritance, polymorphism, encapsulation",
            "Mini-project: Refactor your To-Do List to use a Task class",
        ],
    },
    {
        "number": 12,
        "title": "Weeks 13–14 · OOP Deep Dive & Special Methods",
        "duration": "Weeks 13–14",
        "done": False,
        "summary": "Write more Pythonic classes using dunder (magic) methods.",
        "topics": [
            "Difference between class attributes and instance attributes",
            "Use __str__ and __repr__ for readable object representations",
            "Implement __len__, __eq__ and other useful magic methods",
            "Use @staticmethod and @classmethod",
            "Mini-project: BankAccount class with deposit/withdraw and nice __str__",
        ],
    },
    {
        "number": 13,
        "title": "Weeks 15–16 · Standard Library Deep Dive",
        "duration": "Weeks 15–16",
        "done": False,
        "summary": "Explore powerful modules that ship with Python.",
        "topics": [
            "os and sys for working with the operating system",
            "pathlib for clean path handling",
            "json for reading/writing JSON data",
            "collections (Counter, defaultdict, OrderedDict)",
            "itertools for advanced looping patterns",
            "Mini-project: Script that organises files into folders by extension",
        ],
    },
    {
        "number": 14,
        "title": "Weeks 17–19 · Testing, Environments & Git",
        "duration": "Weeks 17–19",
        "done": False,
        "summary": "Start working like a real software developer.",
        "topics": [
            "Create and activate virtual environments with venv",
            "Understand why isolating dependencies is important",
            "Git basics: git init, add, commit, push, pull, clone",
            "Create a GitHub repository for your project",
            "Write unit tests with unittest or pytest",
            "Mini-project: Put your BankAccount project on GitHub and add tests",
        ],
    },
    {
        "number": 15,
        "title": "Weeks 20–22 · Web Development Path (Option A)",
        "duration": "Weeks 20–22",
        "done": False,
        "summary": "Build web applications using Flask and basic frontend skills.",
        "topics": [
            "HTTP basics: requests, responses, status codes",
            "Flask: routes, views, templates and Jinja2 basics",
            "Handle form submissions and user input",
            "Use HTML and CSS to structure and style your pages",
            "Mini-project: Personal portfolio website built with Flask + HTML/CSS",
        ],
    },
    {
        "number": 16,
        "title": "Weeks 20–22 · Data Science Path (Option B)",
        "duration": "Weeks 20–22",
        "done": False,
        "summary": "Alternatively, start using Python for data analysis.",
        "topics": [
            "NumPy: arrays, slicing and vectorised operations",
            "Pandas: Series, DataFrames, reading CSVs, filtering and grouping",
            "Matplotlib/Seaborn: simple line, bar and scatter plots",
            "Mini-project: Clean and visualise a real dataset (e.g., Titanic dataset)",
        ],
    },
    {
        "number": 17,
        "title": "Weeks 23–24 · Intermediate Capstone",
        "duration": "Weeks 23–24",
        "done": False,
        "summary": "Create a portfolio-worthy project that ties together many concepts.",
        "topics": [
            "Choose one path and go deeper:",
            " • Web: Blog engine in Flask with SQLite (create/edit/delete posts)",
            " • Data: End-to-end data analysis project with a written summary",
            "Use Git and virtual environments to manage the project",
            "Write basic documentation (README.md) for your repository",
        ],
    },
]

PYTHON_EXPERT_STEPS = [
    {
        "number": 18,
        "title": "Area 1 · Deep Language & System Mastery",
        "duration": "Ongoing",
        "done": False,
        "summary": "Understand Python internals, performance and advanced language features.",
        "topics": [
            "Concurrency & parallelism: threading, multiprocessing, asyncio",
            "Understand the Global Interpreter Lock (GIL)",
            "Metaprogramming: metaclasses, descriptors and advanced decorators",
            "Memory model, garbage collection and profiling with cProfile",
            "Intro to C extensions with ctypes or Cython for performance-critical code",
        ],
    },
    {
        "number": 19,
        "title": "Area 2 · Advanced Frameworks & Architectures",
        "duration": "Ongoing",
        "done": False,
        "summary": "Specialise either in web backends or data/machine learning.",
        "topics": [
            "Web path: Master Django or FastAPI",
            "Architectural patterns: REST, GraphQL, microservices and message queues",
            "DevOps: Docker, CI/CD, deployment to AWS/GCP/Azure",
            "Data path: Deep dive into scikit-learn, TensorFlow or PyTorch",
            "Big data: Explore tools like Dask or Apache Spark",
            "Advanced database concepts (SQL + NoSQL)",
        ],
    },
    {
        "number": 20,
        "title": "Area 3 · Software Engineering Excellence",
        "duration": "Ongoing",
        "done": False,
        "summary": "Write clean, maintainable and scalable software.",
        "topics": [
            "Learn and apply SOLID principles",
            "Implement common design patterns (Factory, Observer, Strategy, etc.)",
            "Study Clean Code and Clean Architecture ideas",
            "Practice system design for larger applications",
            "Focus on reliability, scalability and security in designs",
        ],
    },
    {
        "number": 21,
        "title": "Area 4 · Community, Leadership & Contribution",
        "duration": "Ongoing",
        "done": False,
        "summary": "Grow as a professional by giving back and leading others.",
        "topics": [
            "Contribute to open-source projects you use",
            "Fix documentation issues, then small bugs, then add features",
            "Mentor beginner and intermediate developers",
            "Write blog posts, give talks, or create tutorials",
            "Follow Python news, read PEPs and keep up with new releases",
        ],
    },
]

# C
C_BEGINNER_STEPS = [
    {
        "number": 1,
        "title": "Weeks 1–2 · Setup & Basic C Program",
        "duration": "Weeks 1–2",
        "done": False,
        "summary": "Get your C toolchain ready and write your first programs.",
        "topics": [
            "Install a C compiler (GCC/Clang) and an editor/IDE",
            "Understand compilation: source → object → executable",
            "Structure of a C program (main, headers, includes)",
            "Primitive types, variables and printf/scanf basics",
        ],
    },
    {
        "number": 2,
        "title": "Weeks 3–4 · Control Flow & Functions",
        "duration": "Weeks 3–4",
        "done": False,
        "summary": "Use conditions, loops and functions to structure your code.",
        "topics": [
            "if / else / switch statements",
            "for, while, do–while loops and break/continue",
            "Defining and calling functions, passing parameters",
            "Header files and splitting code into multiple .c/.h files",
        ],
    },
    {
        "number": 3,
        "title": "Weeks 5–6 · Arrays, Strings & Pointer Basics",
        "duration": "Weeks 5–6",
        "done": False,
        "summary": "Work with contiguous memory and pointer fundamentals.",
        "topics": [
            "1D arrays and multi-dimensional arrays",
            "Working with C strings and string.h functions",
            "Pointer syntax, dereferencing and pointer arithmetic (intro)",
            "Mini-project: Menu-based student marks calculator",
        ],
    },
    {
        "number": 4,
        "title": "Weeks 7–8 · Beginner Capstone",
        "duration": "Weeks 7–8",
        "done": False,
        "summary": "Apply all beginner concepts in a small console project.",
        "topics": [
            "Plan a console-based management system (e.g., library/inventory)",
            "Use functions and header files to organise the code",
            "Practice clean input validation and menu design",
            "Compile and run on different machines/IDEs",
        ],
    },
]

C_INTERMEDIATE_STEPS = [
    {
        "number": 5,
        "title": "Weeks 9–10 · Pointers & Dynamic Memory",
        "duration": "Weeks 9–10",
        "done": False,
        "summary": "Learn how C manages memory manually.",
        "topics": [
            "Pointer to pointer, pointer arrays",
            "malloc, calloc, realloc, free",
            "Memory leaks and how to avoid them",
            "Mini-lab: Simple dynamic array / vector implementation",
        ],
    },
    {
        "number": 6,
        "title": "Weeks 11–12 · Structs, Unions & Enums",
        "duration": "Weeks 11–12",
        "done": False,
        "summary": "Model more complex data using C’s composite types.",
        "topics": [
            "Defining structs and nested structs",
            "Using typedef for cleaner APIs",
            "Unions and memory sharing basics",
            "Enums for readable constant sets",
        ],
    },
    {
        "number": 7,
        "title": "Weeks 13–14 · Files & Data Structures",
        "duration": "Weeks 13–14",
        "done": False,
        "summary": "Persist data and implement core data structures.",
        "topics": [
            "Text vs binary file I/O",
            "Linked lists and basic operations",
            "Stacks/queues using arrays or linked lists",
            "Mini-project: Persistent contact manager using structs + files",
        ],
    },
    {
        "number": 8,
        "title": "Weeks 15–16 · Intermediate Capstone",
        "duration": "Weeks 15–16",
        "done": False,
        "summary": "Build a medium-sized program combining multiple modules.",
        "topics": [
            "Split project into modules and headers",
            "Use makefiles or simple build scripts",
            "Add error handling and logging",
            "Example: terminal-based game or management tool",
        ],
    },
]

C_ADVANCED_STEPS = [
    {
        "number": 9,
        "title": "Area 1 · Systems Programming",
        "duration": "Ongoing",
        "done": False,
        "summary": "Use C close to the operating system.",
        "topics": [
            "Process and memory layout basics",
            "POSIX APIs (files, processes, signals) – Unix-like systems",
            "Low-level I/O and buffering",
            "Writing small command-line utilities in C",
        ],
    },
    {
        "number": 10,
        "title": "Area 2 · Performance & Safety",
        "duration": "Ongoing",
        "done": False,
        "summary": "Write high-performance, safe C code.",
        "topics": [
            "Profiling C code with tools like gprof/valgrind",
            "Cache awareness and data locality",
            "Defensive programming to avoid UB and security issues",
            "Static analysis tools (cppcheck, clang-tidy – overview)",
        ],
    },
    {
        "number": 11,
        "title": "Area 3 · Concurrency & Networking",
        "duration": "Ongoing",
        "done": False,
        "summary": "Add parallelism and networking capabilities.",
        "topics": [
            "Threads and synchronization primitives (mutex, semaphore – overview)",
            "Basic socket programming",
            "Simple client/server examples",
            "Event-driven vs multi-threaded architectures (high-level view)",
        ],
    },
    {
        "number": 12,
        "title": "Area 4 · Interview & Project Excellence",
        "duration": "Ongoing",
        "done": False,
        "summary": "Prepare for systems-oriented interviews and real projects.",
        "topics": [
            "Common C interview questions and pitfalls",
            "Data structures & algorithms practice in C",
            "Contribute to a small open-source C project",
            "Documenting and packaging your C utilities",
        ],
    },
]

# C++
CPP_BEGINNER_STEPS = [
    {
        "number": 1,
        "title": "Weeks 1–2 · C++ Basics & Setup",
        "duration": "Weeks 1–2",
        "done": False,
        "summary": "Learn what C++ adds on top of C and set up your tools.",
        "topics": [
            "Install a C++ compiler and IDE (VS Code / CLion / CodeBlocks)",
            "Write and compile a simple C++ program with iostream",
            "Basic syntax, namespaces and using std::cout / std::cin",
            "Variables, types, operators and basic expressions",
        ],
    },
    {
        "number": 2,
        "title": "Weeks 3–4 · Control Flow & Functions",
        "duration": "Weeks 3–4",
        "done": False,
        "summary": "Use conditions and loops to control program behaviour.",
        "topics": [
            "if / else / switch",
            "for / while / do–while loops",
            "Functions, default arguments and overloading basics",
            "Mini-project: Simple calculator or menu-based program",
        ],
    },
    {
        "number": 3,
        "title": "Weeks 5–6 · Intro to OOP",
        "duration": "Weeks 5–6",
        "done": False,
        "summary": "Start writing code using classes and objects.",
        "topics": [
            "Classes vs structs in modern C++",
            "Constructors and destructors",
            "this pointer, member functions and encapsulation",
            "Mini-project: Simple class-based model (e.g., Student, Course)",
        ],
    },
    {
        "number": 4,
        "title": "Weeks 7–8 · STL Basics & Beginner Project",
        "duration": "Weeks 7–8",
        "done": False,
        "summary": "Use common standard library containers in a small project.",
        "topics": [
            "std::string, std::vector and std::array",
            "Range-based for loops",
            "Basic STL algorithms (sort, find, count)",
            "Beginner project: small inventory or library system using classes + vector",
        ],
    },
]

CPP_INTERMEDIATE_STEPS = [
    {
        "number": 5,
        "title": "Weeks 9–10 · Inheritance & Polymorphism",
        "duration": "Weeks 9–10",
        "done": False,
        "summary": "Use OOP to design more flexible systems.",
        "topics": [
            "Base and derived classes",
            "Virtual functions and dynamic dispatch",
            "Abstract classes and interfaces",
            "Mini-project: small polymorphic hierarchy (e.g., Shapes, Employees)",
        ],
    },
    {
        "number": 6,
        "title": "Weeks 11–12 · Deeper STL & RAII",
        "duration": "Weeks 11–12",
        "done": False,
        "summary": "Write safer C++ using RAII and the STL.",
        "topics": [
            "std::list, std::map, std::unordered_map",
            "Iterators and iterator categories (intro)",
            "RAII concept and deterministic destruction",
            "Mini-project: configuration loader using maps and RAII wrappers",
        ],
    },
    {
        "number": 7,
        "title": "Weeks 13–14 · Templates & Generic Code",
        "duration": "Weeks 13–14",
        "done": False,
        "summary": "Generalise your code using templates.",
        "topics": [
            "Function templates and class templates (intro)",
            "Template specialisation (basic idea)",
            "std::optional / std::variant overview (C++17+)",
            "Refactor a data structure or algorithm using templates",
        ],
    },
    {
        "number": 8,
        "title": "Weeks 15–16 · Intermediate Capstone",
        "duration": "Weeks 15–16",
        "done": False,
        "summary": "Build a small multi-file C++ application.",
        "topics": [
            "CMake / build system basics (very high-level)",
            "Organise code into headers and source files",
            "Use Git to version your C++ project",
            "Example: small game engine core or console tool using OOP + STL",
        ],
    },
]

CPP_ADVANCED_STEPS = [
    {
        "number": 9,
        "title": "Area 1 · Modern C++ Patterns",
        "duration": "Ongoing",
        "done": False,
        "summary": "Adopt modern C++ idioms for safer, clearer code.",
        "topics": [
            "Smart pointers: unique_ptr, shared_ptr, weak_ptr",
            "Move semantics and rvalue references (intro)",
            "Rule of 0/3/5 and resource management patterns",
            "Effective use of const and references",
        ],
    },
    {
        "number": 10,
        "title": "Area 2 · Concurrency & Performance",
        "duration": "Ongoing",
        "done": False,
        "summary": "Use C++ for high-performance and parallel systems.",
        "topics": [
            "std::thread and basic synchronisation primitives",
            "Futures and async (intro)",
            "Profiling and optimising C++ code",
            "Cache-friendly data structures and algorithms (high-level)",
        ],
    },
    {
        "number": 11,
        "title": "Area 3 · Large-Scale Design",
        "duration": "Ongoing",
        "done": False,
        "summary": "Apply C++ in bigger real-world systems.",
        "topics": [
            "Dependency management and interface-based design",
            "Common design patterns in C++ (Factory, Strategy, Observer etc.)",
            "Working with large codebases and coding guidelines",
            "Reading and contributing to an open-source C++ project",
        ],
    },
    {
        "number": 12,
        "title": "Area 4 · Interview & Competitive Programming",
        "duration": "Ongoing",
        "done": False,
        "summary": "Use C++ effectively in DS/Algo heavy environments.",
        "topics": [
            "DSA practice with STL containers",
            "Time/space complexity awareness",
            "Typical C++ interview caveats (copy vs move, undefined behaviour)",
            "Implementing common algorithm templates quickly",
        ],
    },
]

# Java
JAVA_BEGINNER_STEPS = [
    {
        "number": 1,
        "title": "Weeks 1–2 · Java Setup & Basics",
        "duration": "Weeks 1–2",
        "done": False,
        "summary": "Install Java and write simple programs.",
        "topics": [
            "Install JDK and configure PATH",
            "Use an IDE like IntelliJ IDEA / Eclipse",
            "Write and run your first Java program",
            "Understand classes with public static void main(String[] args)",
            "Primitive types, variables, operators and console I/O",
        ],
    },
    {
        "number": 2,
        "title": "Weeks 3–4 · Control Flow & Methods",
        "duration": "Weeks 3–4",
        "done": False,
        "summary": "Control program logic and reuse code with methods.",
        "topics": [
            "if / else / switch constructs",
            "for, while, do–while loops",
            "Defining methods, parameters and return values",
            "Method overloading",
            "Mini-project: simple menu-based calculator",
        ],
    },
    {
        "number": 3,
        "title": "Weeks 5–6 · Arrays, Strings & Basic OOP",
        "duration": "Weeks 5–6",
        "done": False,
        "summary": "Work with collections of data and basic object-orientation.",
        "topics": [
            "1D and 2D arrays",
            "java.lang.String and common methods",
            "Defining simple classes and creating objects",
            "Encapsulation with private fields and getters/setters",
        ],
    },
    {
        "number": 4,
        "title": "Weeks 7–8 · Beginner Java Project",
        "duration": "Weeks 7–8",
        "done": False,
        "summary": "Build a small console-based Java application.",
        "topics": [
            "Design a small domain model (e.g., Library, Student, Course)",
            "Use multiple classes interacting together",
            "Read/write from console or simple file APIs",
            "Compile and run via IDE and command line",
        ],
    },
]

JAVA_INTERMEDIATE_STEPS = [
    {
        "number": 5,
        "title": "Weeks 9–10 · OOP Deep Dive",
        "duration": "Weeks 9–10",
        "done": False,
        "summary": "Use advanced OOP features to design flexible systems.",
        "topics": [
            "Inheritance and composition",
            "Interfaces and abstract classes",
            "Polymorphism in Java",
            "Mini-project: role-based class hierarchy (e.g., Employees/Accounts)",
        ],
    },
    {
        "number": 6,
        "title": "Weeks 11–12 · Exceptions, Packages & Collections",
        "duration": "Weeks 11–12",
        "done": False,
        "summary": "Organise code and handle errors properly.",
        "topics": [
            "Checked vs unchecked exceptions",
            "try–catch–finally and custom exceptions",
            "Packages and organizing large projects",
            "Java Collections (List, Set, Map) and Iterators",
        ],
    },
    {
        "number": 7,
        "title": "Weeks 13–14 · File I/O & Build Tools",
        "duration": "Weeks 13–14",
        "done": False,
        "summary": "Persist data and manage dependencies.",
        "topics": [
            "java.io and java.nio basics for file reading/writing",
            "Serialisation concepts",
            "Intro to Maven or Gradle",
            "Mini-project: CLI app with configuration stored in files",
        ],
    },
    {
        "number": 8,
        "title": "Weeks 15–16 · Intermediate Java Application",
        "duration": "Weeks 15–16",
        "done": False,
        "summary": "Build a medium-sized Java application.",
        "topics": [
            "Multi-layer structure: model, service, UI/CLI",
            "Use collections and generics throughout the code",
            "Basic logging and error-handling strategy",
            "Store data in a simple database or file, document with README",
        ],
    },
]

JAVA_ADVANCED_STEPS = [
    {
        "number": 9,
        "title": "Area 1 · Advanced Java & JVM Internals",
        "duration": "Ongoing",
        "done": False,
        "summary": "Dive deeper into how Java and the JVM work.",
        "topics": [
            "Generics in depth",
            "JVM memory model and garbage collection (high level)",
            "Java streams and functional style (lambdas)",
            "Performance tuning basics (profilers, heap analysis – overview)",
        ],
    },
    {
        "number": 10,
        "title": "Area 2 · Multithreading & Concurrency",
        "duration": "Ongoing",
        "done": False,
        "summary": "Write concurrent applications safely.",
        "topics": [
            "Threads and Runnable",
            "synchronized, locks and concurrent collections (overview)",
            "Executor framework basics",
            "Mini-labs on race conditions and avoiding them",
        ],
    },
    {
        "number": 11,
        "title": "Area 3 · Enterprise & Frameworks",
        "duration": "Ongoing",
        "done": False,
        "summary": "Use Java in real-world backend systems.",
        "topics": [
            "Spring / Spring Boot fundamentals (high level)",
            "REST APIs and JSON",
            "Connecting to databases with JDBC or JPA",
            "Packaging and deploying a simple Spring Boot service",
        ],
    },
    {
        "number": 12,
        "title": "Area 4 · Interview & Professional Practice",
        "duration": "Ongoing",
        "done": False,
        "summary": "Prepare for Java developer roles.",
        "topics": [
            "Common Java interview questions and pitfalls",
            "Data structures & algorithms practice in Java",
            "Contribute to or study an open-source Java project",
            "Refine portfolio projects and documentation",
        ],
    },
]

# HTML
HTML_BEGINNER_STEPS = [
    {
        "number": 1,
        "title": "Weeks 1–2 · HTML Foundations",
        "duration": "Weeks 1–2",
        "done": False,
        "summary": "Learn how a basic web page is structured.",
        "topics": [
            "HTML document structure (doctype, html, head, body)",
            "Headings, paragraphs, links, images and lists",
            "Inline vs block-level elements",
            "Create your first multi-section page",
        ],
    },
    {
        "number": 2,
        "title": "Weeks 3–4 · Semantic HTML",
        "duration": "Weeks 3–4",
        "done": False,
        "summary": "Write readable and meaningful HTML.",
        "topics": [
            "header, nav, main, section, article, footer",
            "When to use div vs semantic tags",
            "Basic accessibility concepts (alt text, labels)",
            "Mini-project: simple blog layout with semantic sections",
        ],
    },
    {
        "number": 3,
        "title": "Weeks 5–6 · Forms & Tables",
        "duration": "Weeks 5–6",
        "done": False,
        "summary": "Collect structured data from users.",
        "topics": [
            "Form elements: input, textarea, select, checkbox, radio",
            "Labels and basic validation attributes",
            "Tables: tr, th, td for tabular data",
            "Mini-project: contact form + simple table of submissions (static)",
        ],
    },
    {
        "number": 4,
        "title": "Weeks 7–8 · Static Website Capstone",
        "duration": "Weeks 7–8",
        "done": False,
        "summary": "Build a small multi-page website using clean HTML.",
        "topics": [
            "Create Home, About, Projects and Contact pages",
            "Use nav bars and internal links",
            "Prepare HTML to be styled later with CSS",
            "Host on GitHub Pages (optional) as a basic portfolio",
        ],
    },
]

HTML_INTERMEDIATE_STEPS = [
    {
        "number": 5,
        "title": "Weeks 9–10 · Accessibility & SEO Basics",
        "duration": "Weeks 9–10",
        "done": False,
        "summary": "Make pages more usable and discoverable.",
        "topics": [
            "ARIA attributes (overview)",
            "Landmarks and heading hierarchy",
            "Meta tags and favicons",
            "Semantic markup for better SEO",
        ],
    },
    {
        "number": 6,
        "title": "Weeks 11–12 · Forms in Depth",
        "duration": "Weeks 11–12",
        "done": False,
        "summary": "Use modern form features effectively.",
        "topics": [
            "HTML5 input types (email, number, date, etc.)",
            "Client-side validation attributes",
            "Form structure and usability considerations",
            "Mini-project: fully featured contact/order form mockup",
        ],
    },
    {
        "number": 7,
        "title": "Weeks 13–14 · Media & Embeds",
        "duration": "Weeks 13–14",
        "done": False,
        "summary": "Integrate rich content into your pages.",
        "topics": [
            "Using <audio>, <video> with controls",
            "Embedding content with iframe",
            "Lazy loading images (attribute overview)",
            "Best practices for performance-friendly media",
        ],
    },
    {
        "number": 8,
        "title": "Weeks 15–16 · Intermediate Site Project",
        "duration": "Weeks 15–16",
        "done": False,
        "summary": "Design a more complex multi-page HTML site.",
        "topics": [
            "Plan navigation structure and sitemap",
            "Use semantic sections consistently",
            "Ensure basic accessibility and metadata for all pages",
            "Example: documentation site or simple product landing page",
        ],
    },
]

HTML_ADVANCED_STEPS = [
    {
        "number": 9,
        "title": "Area 1 · Advanced HTML & Standards",
        "duration": "Ongoing",
        "done": False,
        "summary": "Keep up with modern HTML features and patterns.",
        "topics": [
            "Custom data-* attributes and microdata (overview)",
            "Newer semantic tags or spec changes (high level)",
            "Progressive enhancement mindset",
            "Review HTML specs / MDN documentation regularly",
        ],
    },
    {
        "number": 10,
        "title": "Area 2 · Accessibility Deep Dive",
        "duration": "Ongoing",
        "done": False,
        "summary": "Design inclusive and accessible experiences.",
        "topics": [
            "Common accessibility issues and audits",
            "ARIA roles for more complex widgets (high level)",
            "Screen reader considerations",
            "Test pages with accessibility checkers",
        ],
    },
    {
        "number": 11,
        "title": "Area 3 · HTML in Modern Frontends",
        "duration": "Ongoing",
        "done": False,
        "summary": "Use HTML effectively with CSS/JS frameworks.",
        "topics": [
            "Component-based thinking (cards, modals, navigation)",
            "HTML structure for responsive layouts (grid/flex basics, conceptually)",
            "Working with design systems or UI libraries",
            "Refining existing HTML for framework integration",
        ],
    },
    {
        "number": 12,
        "title": "Area 4 · Interview & Portfolio",
        "duration": "Ongoing",
        "done": False,
        "summary": "Showcase strong frontend fundamentals.",
        "topics": [
            "Rebuild a real website’s layout using your own HTML",
            "Document accessibility improvements you made",
            "Publish and maintain a personal site or blog",
            "Prepare for basic frontend interview questions on HTML",
        ],
    },
]

# JavaScript
JS_BEGINNER_STEPS = [
    {
        "number": 1,
        "title": "Weeks 1–2 · JS Basics & Where It Runs",
        "duration": "Weeks 1–2",
        "done": False,
        "summary": "Understand how JavaScript fits into the web.",
        "topics": [
            "Adding JS to a page (script tag)",
            "Console.log and basic debugging",
            "Variables with let/const, primitive types",
            "Basic operators and expressions",
        ],
    },
    {
        "number": 2,
        "title": "Weeks 3–4 · Control Flow & Functions",
        "duration": "Weeks 3–4",
        "done": False,
        "summary": "Control logic and reuse code with functions.",
        "topics": [
            "if / else / switch",
            "for / while loops",
            "Defining functions and arrow functions (=>)",
            "Scope basics (block vs function scope overview)",
        ],
    },
    {
        "number": 3,
        "title": "Weeks 5–6 · Arrays & Objects",
        "duration": "Weeks 5–6",
        "done": False,
        "summary": "Use arrays and objects to represent data.",
        "topics": [
            "Array methods: push, pop, map, filter, forEach",
            "Objects as key-value stores",
            "Accessing and updating nested data",
            "Mini-project: to-do list data model in plain JS",
        ],
    },
    {
        "number": 4,
        "title": "Weeks 7–8 · DOM Basics & Beginner Project",
        "duration": "Weeks 7–8",
        "done": False,
        "summary": "Manipulate web pages from JavaScript.",
        "topics": [
            "Selecting elements with querySelector",
            "Changing text and attributes from JS",
            "Handling basic events (click, input)",
            "Project: simple interactive page (e.g., to-do list with DOM updates)",
        ],
    },
]

JS_INTERMEDIATE_STEPS = [
    {
        "number": 5,
        "title": "Weeks 9–10 · Asynchronous JavaScript",
        "duration": "Weeks 9–10",
        "done": False,
        "summary": "Handle operations that take time without blocking.",
        "topics": [
            "setTimeout, setInterval basics",
            "Promises and .then() chains",
            "async/await syntax",
            "Mini-lab: simulate async API calls",
        ],
    },
    {
        "number": 6,
        "title": "Weeks 11–12 · Working with APIs",
        "duration": "Weeks 11–12",
        "done": False,
        "summary": "Fetch remote data and show it on the page.",
        "topics": [
            "fetch() API and JSON parsing",
            "Error handling and loading states",
            "Mini-project: small dashboard pulling data from a public API",
            "Basic CORS concept (high level)",
        ],
    },
    {
        "number": 7,
        "title": "Weeks 13–14 · Better Structure & Modules",
        "duration": "Weeks 13–14",
        "done": False,
        "summary": "Keep code organised in larger scripts.",
        "topics": [
            "Splitting code into modules (ES modules overview)",
            "Reusing functions across files",
            "Intro to bundlers (Webpack/Vite – high level idea)",
            "Refactor an earlier project into modules",
        ],
    },
    {
        "number": 8,
        "title": "Weeks 15–16 · Intermediate SPA Behaviour",
        "duration": "Weeks 15–16",
        "done": False,
        "summary": "Add single-page-app-like behaviour without frameworks.",
        "topics": [
            "Client-side routing idea (section show/hide)",
            "State objects and simple state management",
            "Smooth UI updates for a small multi-section app",
            "Project: small SPA-style page (tabs/sections) using vanilla JS",
        ],
    },
]

JS_ADVANCED_STEPS = [
    {
        "number": 9,
        "title": "Area 1 · Advanced JS Concepts",
        "duration": "Ongoing",
        "done": False,
        "summary": "Master modern JavaScript behaviour and patterns.",
        "topics": [
            "Closures and lexical scope",
            "Prototype chain and prototypal inheritance",
            "this keyword and common pitfalls",
            "Functional patterns and immutability (overview)",
        ],
    },
    {
        "number": 10,
        "title": "Area 2 · Frameworks & Tooling",
        "duration": "Ongoing",
        "done": False,
        "summary": "Use JS in real-world web applications.",
        "topics": [
            "Intro to a modern framework (React/Vue/Angular – pick one)",
            "Component-based architecture",
            "Basic build and deployment workflow",
            "Mini project: small app in your chosen framework",
        ],
    },
    {
        "number": 11,
        "title": "Area 3 · Performance & Best Practices",
        "duration": "Ongoing",
        "done": False,
        "summary": "Write JS that is robust and efficient.",
        "topics": [
            "Debugging tools in browser devtools",
            "Analysing bundle size and network usage",
            "Avoiding layout thrashing and unnecessary re-renders (conceptual)",
            "Testing JS code with popular tools (overview)",
        ],
    },
    {
        "number": 12,
        "title": "Area 4 · Interview & Portfolio",
        "duration": "Ongoing",
        "done": False,
        "summary": "Show strong frontend skills in interviews.",
        "topics": [
            "Common JS interview questions and coding tasks",
            "Rebuilding UI components from design mocks",
            "Publishing small JS experiments or libraries",
            "Keeping up with ECMAScript releases",
        ],
    },
]

# Node.js
NODE_BEGINNER_STEPS = [
    {
        "number": 1,
        "title": "Weeks 1–2 · Node.js Basics & Environment",
        "duration": "Weeks 1–2",
        "done": False,
        "summary": "Run JavaScript outside the browser.",
        "topics": [
            "Install Node.js and npm",
            "Run simple JS files with node",
            "Understand package.json and npm init",
            "Write a basic CLI script (e.g., greeter)",
        ],
    },
    {
        "number": 2,
        "title": "Weeks 3–4 · Core Modules & Async Patterns",
        "duration": "Weeks 3–4",
        "done": False,
        "summary": "Use built-in Node modules and callbacks.",
        "topics": [
            "fs module for basic file I/O",
            "path module and working with file paths",
            "Callbacks vs Promises in Node",
            "Mini-project: CLI tool that reads/writes from files",
        ],
    },
    {
        "number": 3,
        "title": "Weeks 5–6 · HTTP Servers with Node",
        "duration": "Weeks 5–6",
        "done": False,
        "summary": "Serve basic HTTP responses.",
        "topics": [
            "http module basics",
            "Create a simple HTTP server returning text or JSON",
            "Routing by URL path manually",
            "Understand request/response lifecycle at a high level",
        ],
    },
    {
        "number": 4,
        "title": "Weeks 7–8 · Intro to Express.js",
        "duration": "Weeks 7–8",
        "done": False,
        "summary": "Move to a more productive web framework.",
        "topics": [
            "Express app setup",
            "Routing and middleware basics",
            "Handling query params and POST data",
            "Beginner project: simple REST API with 2–3 endpoints",
        ],
    },
]

NODE_INTERMEDIATE_STEPS = [
    {
        "number": 5,
        "title": "Weeks 9–10 · Working with Databases",
        "duration": "Weeks 9–10",
        "done": False,
        "summary": "Persist data for your Node applications.",
        "topics": [
            "High-level overview of SQL vs NoSQL",
            "Connect to MongoDB or a relational DB",
            "Implement CRUD operations",
            "Mini-project: TODO API backed by a database",
        ],
    },
    {
        "number": 6,
        "title": "Weeks 11–12 · Authentication & Security Basics",
        "duration": "Weeks 11–12",
        "done": False,
        "summary": "Protect your API and handle identity.",
        "topics": [
            "Basic auth vs token-based auth (JWT overview)",
            "Password hashing concept (bcrypt or similar)",
            "Input validation to avoid common attacks",
            "Handling errors and logging in Express",
        ],
    },
    {
        "number": 7,
        "title": "Weeks 13–14 · Structuring Production-Style Projects",
        "duration": "Weeks 13–14",
        "done": False,
        "summary": "Organise code for maintainability.",
        "topics": [
            "Separating routes, controllers, models and config",
            "Environment variables with dotenv",
            "Basic config for different environments (dev/prod)",
            "Refactor your API into this structure",
        ],
    },
    {
        "number": 8,
        "title": "Weeks 15–16 · Intermediate Backend Project",
        "duration": "Weeks 15–16",
        "done": False,
        "summary": "Build a small but real-world style backend.",
        "topics": [
            "Design API endpoints and data models",
            "Use a database driver or ORM",
            "Add logging and basic tests",
            "Example: notes app, blog API or simple e-commerce backend",
        ],
    },
]

NODE_ADVANCED_STEPS = [
    {
        "number": 9,
        "title": "Area 1 · Scaling & Performance",
        "duration": "Ongoing",
        "done": False,
        "summary": "Make Node services robust and fast.",
        "topics": [
            "Node event loop and concurrency model (high level)",
            "Clustering and horizontal scaling concepts",
            "Caching with in-memory stores or Redis (overview)",
            "Performance profiling for slow endpoints",
        ],
    },
    {
        "number": 10,
        "title": "Area 2 · Testing & DevOps",
        "duration": "Ongoing",
        "done": False,
        "summary": "Treat your Node app like a production service.",
        "topics": [
            "Testing strategy (unit vs integration tests overview)",
            "Continuous integration basics",
            "Containerising Node apps with Docker (conceptual)",
            "Monitoring and logging best practices (overview)",
        ],
    },
    {
        "number": 11,
        "title": "Area 3 · Advanced Architectures",
        "duration": "Ongoing",
        "done": False,
        "summary": "Use Node.js in larger systems.",
        "topics": [
            "Microservices vs monolith discussion",
            "Message queues (RabbitMQ/Kafka – conceptual)",
            "API gateway patterns",
            "Refactor a medium project into clearer boundaries/modules",
        ],
    },
    {
        "number": 12,
        "title": "Area 4 · Interview & Open Source",
        "duration": "Ongoing",
        "done": False,
        "summary": "Show your Node skills publicly.",
        "topics": [
            "Common Node.js interview questions and caveats",
            "Security considerations (OWASP-style overview)",
            "Contribute to an Express or Node.js ecosystem project",
            "Maintain a public backend project on GitHub",
        ],
    },
]


# -------------------------------------------------------------------
# OTHER LANGUAGES – same as your file (C, C++, Java, HTML, JS, Node)
# -------------------------------------------------------------------
#  🔴 To keep this answer short, I’ll summarise:
#  Paste here exactly the C_*, CPP_*, JAVA_*, HTML_*, JS_*, NODE_* arrays
#  that you already have – they are fine and unchanged.
# -------------------------------------------------------------------

#  ❗ DO NOT delete your existing C_*, CPP_*, JAVA_*, HTML_*, JS_*, NODE_* blocks.
#  Leave them as they are, right here.
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Map all language roadmaps together
# -------------------------------------------------------------------

LANGUAGE_ROADMAPS = {
    "Python": {
        "Beginner": PYTHON_BEGINNER_STEPS,
        "Intermediate": PYTHON_INTERMEDIATE_STEPS,
        "Advanced": PYTHON_EXPERT_STEPS,
    },
    "C": {
        "Beginner": C_BEGINNER_STEPS,
        "Intermediate": C_INTERMEDIATE_STEPS,
        "Advanced": C_ADVANCED_STEPS,
    },
    "C++": {
        "Beginner": CPP_BEGINNER_STEPS,
        "Intermediate": CPP_INTERMEDIATE_STEPS,
        "Advanced": CPP_ADVANCED_STEPS,
    },
    "Java": {
        "Beginner": JAVA_BEGINNER_STEPS,
        "Intermediate": JAVA_INTERMEDIATE_STEPS,
        "Advanced": JAVA_ADVANCED_STEPS,
    },
    "HTML": {
        "Beginner": HTML_BEGINNER_STEPS,
        "Intermediate": HTML_INTERMEDIATE_STEPS,
        "Advanced": HTML_ADVANCED_STEPS,
    },
    "JavaScript": {
        "Beginner": JS_BEGINNER_STEPS,
        "Intermediate": JS_INTERMEDIATE_STEPS,
        "Advanced": JS_ADVANCED_STEPS,
    },
    "Node.js": {
        "Beginner": NODE_BEGINNER_STEPS,
        "Intermediate": NODE_INTERMEDIATE_STEPS,
        "Advanced": NODE_ADVANCED_STEPS,
    },
}
# -------------------------------------------------------------------
# Resource links (per language+level and per career role)
# -------------------------------------------------------------------

LANGUAGE_RESOURCE_LINKS = {
    "Python": {
        "Beginner": [
            {
                "label": "Python Official Tutorial",
                "url": "https://docs.python.org/3/tutorial/"
            },
            {
                "label": "Automate the Boring Stuff (free online book)",
                "url": "https://automatetheboringstuff.com/"
            },
            {
                "label": "Corey Schafer – Python Playlist (YouTube)",
                "url": "https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc"
            },
        ],
        "Intermediate": [
            {
                "label": "Real Python – Intermediate Articles",
                "url": "https://realpython.com/"
            },
            {
                "label": "Effective Python (Item-based tips)",
                "url": "https://effectivepython.com/"
            },
        ],
        "Advanced": [
            {
                "label": "Fluent Python (OOP & advanced topics)",
                "url": "https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/"
            },
            {
                "label": "Python docs – asyncio, threading, multiprocessing",
                "url": "https://docs.python.org/3/library/asyncio.html"
            },
        ],
    },

    "Java": {
        "Beginner": [
            {"label": "Java Tutorial – Oracle", "url": "https://docs.oracle.com/javase/tutorial/"},
            {"label": "Bro Code Java Playlist (YouTube)", "url": "https://www.youtube.com/playlist?list=PLZPZq0r_RZOMHoXIcxze_lP97j2Ase2on"},
        ],
        "Intermediate": [
            {"label": "Java Collections & Generics – Baeldung", "url": "https://www.baeldung.com/java-collections"},
        ],
        "Advanced": [
            {"label": "Spring Boot Guides", "url": "https://spring.io/guides"},
        ],
    },

    # you can add more languages similarly:
    # "C": {"Beginner": [...], "Intermediate": [...], "Advanced": [...]},
    # "JavaScript": {...},
    # etc.
}

CAREER_RESOURCE_LINKS = {
    "Python Developer": [
        {"label": "Roadmap.sh – Python Developer", "url": "https://roadmap.sh/python"},
        {"label": "Awesome Python (GitHub)", "url": "https://github.com/vinta/awesome-python"},
    ],
    "Java Developer": [
        {"label": "Roadmap.sh – Java Developer", "url": "https://roadmap.sh/java"},
        {"label": "Baeldung – Java & Spring", "url": "https://www.baeldung.com/"},
    ],
    "Full Stack Developer": [
        {"label": "roadmap.sh – Full Stack", "url": "https://roadmap.sh/full-stack"},
    ],
    "Frontend Developer": [
        {"label": "roadmap.sh – Frontend", "url": "https://roadmap.sh/frontend"},
    ],
    "Backend Developer": [
        {"label": "roadmap.sh – Backend", "url": "https://roadmap.sh/backend"},
    ],
    # add entries for other roles if you want:
    # "Data Analyst": [...],
    # "Mobile App Developer": [...],
}


# -------------------------------------------------------------------
# Helper – build language roadmap from dict + DB progress
# -------------------------------------------------------------------

def build_language_roadmap(user, language, raw_level):
    language = (language or "Python").strip()
    level_label = (raw_level or "Beginner").capitalize()
    if level_label not in ["Beginner", "Intermediate", "Advanced"]:
        level_label = "Beginner"

    lang_map = LANGUAGE_ROADMAPS.get(language, LANGUAGE_ROADMAPS["Python"])
    base_steps = lang_map.get(level_label) or lang_map.get("Beginner")
    steps = [s.copy() for s in base_steps]

    completed_ids = set()
    if user.is_authenticated:
        completed_ids = set(
            UserProgress.objects.filter(user=user, completed=True)
            .values_list("roadmap_step_id", flat=True)
        )

    for s in steps:
        db_step, _ = RoadmapStep.objects.get_or_create(
            language=language,
            level=level_label,
            week=s["number"],
            defaults={"title": s["title"]},
        )
        s["db_id"] = db_step.id
        s["is_completed"] = db_step.id in completed_ids

    title = f"{language} Learning Roadmap"
    subtitle = (
        f"This roadmap covers the key stages to learn {language} from {level_label} level. "
        f"You selected {language} at {level_label} level."
    )

    return language, level_label, steps, title, subtitle


# -------------------------------------------------------------------
# Views
# -------------------------------------------------------------------

def home(request):
    languages = ["C", "C++", "Java", "Python", "HTML", "JavaScript", "Node.js"]
    roles = [
        "Java Developer",
        "Python Developer",
        "Full Stack Developer",
        "Frontend Developer",
        "Backend Developer",
        "Data Analyst",
        "Data Scientist / ML Engineer",
        "DevOps / Cloud Engineer",
        "Mobile App Developer",
    ]

    selected = {"mode": "", "language": "", "level": "", "role": ""}

    return render(
        request,
        "core/home.html",
        {"selected": selected, "languages": languages, "roles": roles},
    )



def roadmap(request):
    mode = (request.GET.get("mode") or "language").strip() or "language"

    # ==================== CAREER MODE ====================
    if mode == "career":
        role = (request.GET.get("role") or "").strip()

        steps = CareerRoadmap.objects.filter(
            role__iexact=role
        ).order_by("step_number")

        title = f"Career Path · {role or 'Software Developer'}"
        subtitle = (
            f"This roadmap outlines the major stages to grow into a strong {role}."
            if role
            else "This roadmap outlines the major stages to grow as a software developer."
        )

        resources = CAREER_RESOURCE_LINKS.get(role, [])

        pdf_url = reverse("roadmap_pdf")
        pdf_download_url = f"{pdf_url}?mode=career&role={quote_plus(role)}"

        return render(
            request,
            "core/career_roadmap.html",
            {
                "mode": "career",
                "role": role,
                "language": "",
                "level": "",
                "title": title,
                "subtitle": subtitle,
                "steps": steps,
                "resources": resources,
                "pdf_download_url": pdf_download_url,
            },
        )

    # ==================== LANGUAGE MODE ====================
    raw_language = request.GET.get("language") or "Python"
    raw_level = request.GET.get("level") or "Beginner"

    # use helper to get STATIC steps (with topics) + DB progress
    language, level, steps, title, subtitle = build_language_roadmap(
        request.user, raw_language, raw_level
    )

    # resource links for this language + level
    resources = LANGUAGE_RESOURCE_LINKS.get(language, {}).get(level, [])

    # PDF link for this language roadmap
    pdf_url = reverse("roadmap_pdf")
    pdf_download_url = (
        f"{pdf_url}?mode=language"
        f"&language={quote_plus(language)}"
        f"&level={quote_plus(level)}"
    )

    return render(
        request,
        "core/roadmap.html",
        {
            "mode": "language",
            "language": language,
            "level": level,
            "title": title,
            "subtitle": subtitle,
            "steps": steps,               # has topics, db_id, is_completed
            "resources": resources,
            "pdf_download_url": pdf_download_url,
        },
    )




def roadmap_pdf(request):
    mode = request.GET.get("mode", "career")

    if mode == "career":
        role = request.GET.get("role", "").strip()
        steps = CareerRoadmap.objects.filter(role__iexact=role).order_by("step_number")
        context = {
            "mode": "career",
            "role": role,
            "steps": steps,
        }
        template_name = "core/career_roadmap_pdf.html"
        filename = f"{role.replace(' ', '_')}_roadmap.pdf" or "career_roadmap.pdf"

    else:
        language = request.GET.get("language", "Python").strip()
        level = request.GET.get("level", "beginner").strip()
        steps = RoadmapStep.objects.filter(
            language__iexact=language,
            level__iexact=level,
        ).order_by("week")
        context = {
            "mode": "language",
            "language": language,
            "level": level,
            "steps": steps,
        }
        template_name = "core/roadmap_pdf.html"
        filename = f"{language}_{level}_roadmap.pdf".replace(" ", "_")

    pdf = render_to_pdf(template_name, context)
    if not pdf:
        return HttpResponse("Error generating PDF", status=500)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def render_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.CreatePDF(html, dest=result)
    if pdf.err:
        return None
    return result.getvalue()

# ---------------- Auth views ----------------

def sign_in(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username") or ""
        password = request.POST.get("password") or ""

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            error = "Invalid username or password."

    return render(request, "core/sign_in.html", {"error": error})


def sign_up(request):
    error = None
    password_hint = (
        "Password must be at least 8 characters and include at least one uppercase "
        "letter, one lowercase letter, one number, and one special character."
    )

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        if not username or not password1 or not password2:
            error = "All fields except email are required."
        elif password1 != password2:
            error = "Passwords do not match."
        elif len(password1) < 8:
            error = "Password must be at least 8 characters long."
        elif not re.search(r"[A-Z]", password1):
            error = "Password must contain at least one uppercase letter."
        elif not re.search(r"[a-z]", password1):
            error = "Password must contain at least one lowercase letter."
        elif not re.search(r"\d", password1):
            error = "Password must contain at least one number."
        elif not re.search(r"[^A-Za-z0-9]", password1):
            error = "Password must contain at least one special character."
        elif User.objects.filter(username=username).exists():
            error = "Username already taken. Choose a different one."
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
            )
            login(request, user)
            return redirect("home")

    return render(
        request,
        "core/sign_up.html",
        {"error": error, "password_hint": password_hint},
    )


# ---------------- Progress views ----------------

@login_required(login_url="sign_in")

@login_required(login_url="sign_in")
def profile(request):
    # streak
    streak = getattr(request.user, "userstreak", None)


    # progress summary
    qs = UserProgress.objects.select_related("roadmap_step").filter(user=request.user)

    summary = {}
    for p in qs:
        step = p.roadmap_step
        key = (step.language, step.level)
        if key not in summary:
            summary[key] = {"total": 0, "completed": 0}
        summary[key]["total"] += 1
        if p.completed:
            summary[key]["completed"] += 1

    # prepare display format
    progress_data = []
    for (language, level), data in summary.items():
        total = data["total"]
        completed = data["completed"]
        percentage = int((completed / total) * 100) if total > 0 else 0
        progress_data.append(
            {"language": language, "level": level, "percentage": percentage}
        )

    return render(
        request,
        "core/profile.html",
        {
            "user": request.user,
            "streak": streak,
            "progress_data": progress_data,
        },
    )

def my_progress(request):
    qs = UserProgress.objects.select_related("roadmap_step").filter(user=request.user)

    summary = {}
    for p in qs:
        step = p.roadmap_step
        key = (step.language, step.level)
        if key not in summary:
            summary[key] = {"total": 0, "completed": 0}
        summary[key]["total"] += 1
        if p.completed:
            summary[key]["completed"] += 1

    example_progress = []
    for (language, level), data in summary.items():
        total = data["total"]
        completed = data["completed"]
        percentage = int((completed / total) * 100) if total > 0 else 0
        example_progress.append(
            {"language": language, "level": level, "completed": percentage}
        )
    streak = UserStreak.objects.filter(user=request.user).first()

    return render(
        request,
        "core/my_progress.html",
        {"user": request.user, "example_progress": example_progress},
    )


@login_required(login_url="sign_in")
def toggle_progress(request, step_id):
    step = get_object_or_404(RoadmapStep, id=step_id)
    progress, _ = UserProgress.objects.get_or_create(user=request.user, roadmap_step=step)
    progress.completed = not progress.completed
    progress.save()

    today = date.today()
    streak, _ = UserStreak.objects.get_or_create(user=request.user)

    if progress.completed:
        # completed step today → update streak
        if streak.last_completed_date == today - timedelta(days=1):
            streak.current_streak += 1  # continue streak
        elif streak.last_completed_date == today:
            pass  # already counted today
        else:
            streak.current_streak = 1  # reset streak

        streak.last_completed_date = today

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

    streak.save()

    return redirect("roadmap")


# ---------------- Ajax for career roadmap (if you still use it) ----------------

def get_career_roadmap(request):
    role = request.GET.get("role")
    steps = CareerRoadmap.objects.filter(role=role).order_by("step_number")
    data = list(steps.values("step_number", "title", "description"))
    return JsonResponse({"roadmap": data})

