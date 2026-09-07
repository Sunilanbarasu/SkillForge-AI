from app.models.question import Question

ROLE_QUESTIONS = [

    # =========================
    # JAVASCRIPT
    # =========================

    {
        "skill": "JavaScript",
        "question_text": "Which keyword declares a block-scoped variable that can be reassigned?",
        "option_a": "var",
        "option_b": "let",
        "option_c": "const",
        "option_d": "static",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "JavaScript",
        "question_text": "What does Array.prototype.map() return?",
        "option_a": "The original array only",
        "option_b": "A new array",
        "option_c": "A boolean",
        "option_d": "A string",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "JavaScript",
        "question_text": "Which value represents an explicitly empty or missing value in JavaScript?",
        "option_a": "undefined",
        "option_b": "empty",
        "option_c": "voided",
        "option_d": "missing",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "JavaScript",
        "question_text": "What is the result of typeof [] in JavaScript?",
        "option_a": "array",
        "option_b": "list",
        "option_c": "object",
        "option_d": "collection",
        "correct_answer": "C",
        "difficulty": "Intermediate"
    },
    {
        "skill": "JavaScript",
        "question_text": "Which feature allows asynchronous code to be written using await?",
        "option_a": "Generators",
        "option_b": "Async functions",
        "option_c": "Prototypes",
        "option_d": "Closures",
        "correct_answer": "B",
        "difficulty": "Intermediate"
    },

    # =========================
    # REACT
    # =========================

    {
        "skill": "React",
        "question_text": "What is a React component?",
        "option_a": "A reusable UI building block",
        "option_b": "A database table",
        "option_c": "A CSS file",
        "option_d": "A server process",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "React",
        "question_text": "Which hook is commonly used to store local component state?",
        "option_a": "useRoute",
        "option_b": "useState",
        "option_c": "useStyle",
        "option_d": "useServer",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "React",
        "question_text": "What are props primarily used for in React?",
        "option_a": "Passing data to components",
        "option_b": "Creating database tables",
        "option_c": "Starting a server",
        "option_d": "Compiling CSS",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "React",
        "question_text": "Which hook is commonly used for side effects such as API calls?",
        "option_a": "useEffect",
        "option_b": "useHTML",
        "option_c": "useFetchOnly",
        "option_d": "useComponent",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "React",
        "question_text": "Why should list items in React have stable keys?",
        "option_a": "To improve database security",
        "option_b": "To help React identify changed elements",
        "option_c": "To encrypt the component",
        "option_d": "To create API routes",
        "correct_answer": "B",
        "difficulty": "Intermediate"
    },

    # =========================
    # APIS
    # =========================

    {
        "skill": "APIs",
        "question_text": "What does REST commonly use to represent resources?",
        "option_a": "HTTP endpoints",
        "option_b": "CPU registers",
        "option_c": "CSS selectors",
        "option_d": "File extensions",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "APIs",
        "question_text": "Which HTTP method is normally used to retrieve data?",
        "option_a": "POST",
        "option_b": "DELETE",
        "option_c": "GET",
        "option_d": "PATCH",
        "correct_answer": "C",
        "difficulty": "Beginner"
    },
    {
        "skill": "APIs",
        "question_text": "Which HTTP status code normally indicates a successful request?",
        "option_a": "200",
        "option_b": "404",
        "option_c": "500",
        "option_d": "301",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "APIs",
        "question_text": "Which HTTP status code indicates that a requested resource was not found?",
        "option_a": "201",
        "option_b": "400",
        "option_c": "404",
        "option_d": "204",
        "correct_answer": "C",
        "difficulty": "Intermediate"
    },
    {
        "skill": "APIs",
        "question_text": "What is JSON primarily used for in web APIs?",
        "option_a": "Styling web pages",
        "option_b": "Representing structured data",
        "option_c": "Compiling JavaScript",
        "option_d": "Managing CPU memory",
        "correct_answer": "B",
        "difficulty": "Intermediate"
    },

    # =========================
    # HTML/CSS
    # =========================

    {
        "skill": "HTML/CSS",
        "question_text": "Which HTML element is used for the main heading of a page?",
        "option_a": "<h1>",
        "option_b": "<head>",
        "option_c": "<title>",
        "option_d": "<header1>",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "HTML/CSS",
        "question_text": "Which CSS property changes the text color?",
        "option_a": "font-style",
        "option_b": "text-color",
        "option_c": "color",
        "option_d": "foreground",
        "correct_answer": "C",
        "difficulty": "Beginner"
    },
    {
        "skill": "HTML/CSS",
        "question_text": "Which CSS layout system is designed for one-dimensional layouts?",
        "option_a": "Flexbox",
        "option_b": "Table",
        "option_c": "Float-only layout",
        "option_d": "Inline layout",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "HTML/CSS",
        "question_text": "Which CSS property controls the space inside an element's border?",
        "option_a": "margin",
        "option_b": "padding",
        "option_c": "spacing",
        "option_d": "inner-margin",
        "correct_answer": "B",
        "difficulty": "Intermediate"
    },
    {
        "skill": "HTML/CSS",
        "question_text": "Which HTML attribute provides alternative text for an image?",
        "option_a": "src",
        "option_b": "href",
        "option_c": "alt",
        "option_d": "description",
        "correct_answer": "C",
        "difficulty": "Beginner"
    },

    # =========================
    # WEB
    # =========================

    {
        "skill": "Web",
        "question_text": "What does HTTP stand for?",
        "option_a": "HyperText Transfer Protocol",
        "option_b": "High Transfer Text Process",
        "option_c": "Hyperlink Transmission Program",
        "option_d": "Host Transfer Technology Protocol",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Web",
        "question_text": "Which protocol is used to securely transfer HTTP traffic?",
        "option_a": "FTP",
        "option_b": "HTTPS",
        "option_c": "SMTP",
        "option_d": "SSH",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Web",
        "question_text": "What does DNS primarily do?",
        "option_a": "Encrypt passwords",
        "option_b": "Translate domain names to IP addresses",
        "option_c": "Store HTML files",
        "option_d": "Compress images",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Web",
        "question_text": "What is a browser primarily responsible for?",
        "option_a": "Rendering and interacting with web content",
        "option_b": "Managing database indexes",
        "option_c": "Compiling operating systems",
        "option_d": "Replacing web servers",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Web",
        "question_text": "Which HTTP status code indicates that a resource was permanently redirected?",
        "option_a": "200",
        "option_b": "301",
        "option_c": "404",
        "option_d": "503",
        "correct_answer": "B",
        "difficulty": "Intermediate"
    },

    # =========================
    # GIT
    # =========================

    {
        "skill": "Git",
        "question_text": "Which command creates a new Git repository in the current directory?",
        "option_a": "git start",
        "option_b": "git init",
        "option_c": "git create",
        "option_d": "git repo",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Git",
        "question_text": "Which command shows the current working-tree status?",
        "option_a": "git state",
        "option_b": "git status",
        "option_c": "git check",
        "option_d": "git inspect",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Git",
        "question_text": "Which command records staged changes in a local Git repository?",
        "option_a": "git save",
        "option_b": "git commit",
        "option_c": "git push",
        "option_d": "git record",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Git",
        "question_text": "Which command uploads local commits to a remote repository?",
        "option_a": "git upload",
        "option_b": "git send",
        "option_c": "git push",
        "option_d": "git publish-local",
        "correct_answer": "C",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Git",
        "question_text": "What is a Git branch primarily used for?",
        "option_a": "Separating lines of development",
        "option_b": "Compressing files",
        "option_c": "Creating database tables",
        "option_d": "Installing packages",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },

    # =========================
    # STATISTICS
    # =========================

    {
        "skill": "Statistics",
        "question_text": "What is the mean of 2, 4, and 6?",
        "option_a": "3",
        "option_b": "4",
        "option_c": "5",
        "option_d": "6",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Statistics",
        "question_text": "Which measure is the middle value when data is ordered?",
        "option_a": "Mean",
        "option_b": "Median",
        "option_c": "Variance",
        "option_d": "Range",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Statistics",
        "question_text": "What does standard deviation measure?",
        "option_a": "Central value only",
        "option_b": "Spread of data around the mean",
        "option_c": "Number of observations",
        "option_d": "Maximum value only",
        "correct_answer": "B",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Statistics",
        "question_text": "What is the probability of getting heads on a fair coin toss?",
        "option_a": "0",
        "option_b": "0.25",
        "option_c": "0.5",
        "option_d": "1",
        "correct_answer": "C",
        "difficulty": "Beginner"
    },
    {
        "skill": "Statistics",
        "question_text": "What does correlation measure?",
        "option_a": "The strength and direction of association between variables",
        "option_b": "Only the average of a variable",
        "option_c": "The number of rows in a dataset",
        "option_d": "The largest observation",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },

    # =========================
    # DATA VISUALIZATION
    # =========================

    {
        "skill": "Data Visualization",
        "question_text": "Which chart is commonly used to compare values across categories?",
        "option_a": "Bar chart",
        "option_b": "Scatter plot only",
        "option_c": "Histogram only",
        "option_d": "Map only",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Data Visualization",
        "question_text": "Which chart is commonly used to show trends over time?",
        "option_a": "Pie chart",
        "option_b": "Line chart",
        "option_c": "Box plot",
        "option_d": "Tree map",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Data Visualization",
        "question_text": "Which chart is useful for showing the distribution of numerical data?",
        "option_a": "Histogram",
        "option_b": "Pie chart",
        "option_c": "Network diagram",
        "option_d": "Flowchart",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Data Visualization",
        "question_text": "Which visualization is useful for examining the relationship between two numerical variables?",
        "option_a": "Scatter plot",
        "option_b": "Pie chart",
        "option_c": "Bar chart only",
        "option_d": "Gauge",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Data Visualization",
        "question_text": "Why should unnecessary visual elements be avoided in a data visualization?",
        "option_a": "They can distract from the actual data",
        "option_b": "They always improve accuracy",
        "option_c": "They increase database speed",
        "option_d": "They remove missing values",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },

    # =========================
    # EXCEL
    # =========================

    {
        "skill": "Excel",
        "question_text": "Which Excel function adds a range of numbers?",
        "option_a": "COUNT",
        "option_b": "SUM",
        "option_c": "AVERAGEIF",
        "option_d": "TEXT",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Excel",
        "question_text": "Which Excel function calculates the arithmetic mean?",
        "option_a": "SUM",
        "option_b": "AVERAGE",
        "option_c": "TOTAL",
        "option_d": "MEANVALUE",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Excel",
        "question_text": "What is a PivotTable mainly used for?",
        "option_a": "Summarizing and analyzing data",
        "option_b": "Writing operating-system code",
        "option_c": "Creating APIs",
        "option_d": "Encrypting files",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Excel",
        "question_text": "Which feature can restrict the type of data entered into a cell?",
        "option_a": "Data Validation",
        "option_b": "Conditional Formatting",
        "option_c": "Freeze Panes",
        "option_d": "Page Layout",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Excel",
        "question_text": "Which function counts cells containing numbers?",
        "option_a": "COUNTA",
        "option_b": "COUNT",
        "option_c": "NUMBER",
        "option_d": "NUMCOUNT",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },

    # =========================
    # MACHINE LEARNING
    # =========================

    {
        "skill": "Machine Learning",
        "question_text": "What is supervised learning?",
        "option_a": "Learning from labeled training data",
        "option_b": "Learning without any data",
        "option_c": "Only clustering data",
        "option_d": "Manually programming every prediction",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Machine Learning",
        "question_text": "What is classification used for?",
        "option_a": "Predicting discrete categories",
        "option_b": "Only sorting files",
        "option_c": "Compressing images",
        "option_d": "Creating database indexes",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Machine Learning",
        "question_text": "What is overfitting?",
        "option_a": "A model performing well on training data but poorly on unseen data",
        "option_b": "A model with no parameters",
        "option_c": "A dataset with no labels",
        "option_d": "A model that cannot train",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Machine Learning",
        "question_text": "Why is a test set used?",
        "option_a": "To estimate performance on unseen data",
        "option_b": "To increase the training labels",
        "option_c": "To replace the training set",
        "option_d": "To remove all features",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Machine Learning",
        "question_text": "Which algorithm is commonly used for binary classification?",
        "option_a": "Logistic Regression",
        "option_b": "Linear Search",
        "option_c": "Merge Sort",
        "option_d": "Depth-First Search",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },

    # =========================
    # LINUX
    # =========================

    {
        "skill": "Linux",
        "question_text": "Which command lists files in a Linux directory?",
        "option_a": "dirlist",
        "option_b": "ls",
        "option_c": "show",
        "option_d": "files",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Linux",
        "question_text": "Which command prints the current working directory?",
        "option_a": "pwd",
        "option_b": "where",
        "option_c": "cwd",
        "option_d": "location",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Linux",
        "question_text": "Which command changes the current directory?",
        "option_a": "mvdir",
        "option_b": "cd",
        "option_c": "changedir",
        "option_d": "switch",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Linux",
        "question_text": "Which command is commonly used to change file permissions?",
        "option_a": "chmod",
        "option_b": "chperm",
        "option_c": "permission",
        "option_d": "setmode",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Linux",
        "question_text": "Which symbol represents the root directory in Linux?",
        "option_a": "~",
        "option_b": "/",
        "option_c": ".",
        "option_d": "#",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },

    # =========================
    # CLOUD
    # =========================

    {
        "skill": "Cloud",
        "question_text": "What is cloud computing?",
        "option_a": "Using computing resources over a network on demand",
        "option_b": "Only storing files on a USB drive",
        "option_c": "Programming without hardware",
        "option_d": "A type of local compiler",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Cloud",
        "question_text": "Which model provides virtual machines, storage, and networking resources?",
        "option_a": "SaaS",
        "option_b": "IaaS",
        "option_c": "PaaS",
        "option_d": "DBaaS only",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Cloud",
        "question_text": "What does scalability mean in cloud systems?",
        "option_a": "Ability to handle changing workload demands",
        "option_b": "Deleting unused files",
        "option_c": "Changing programming languages",
        "option_d": "Disabling networking",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Cloud",
        "question_text": "What is a cloud region?",
        "option_a": "A geographic area containing cloud infrastructure",
        "option_b": "A programming language",
        "option_c": "A database table",
        "option_d": "A local browser setting",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Cloud",
        "question_text": "Which cloud model provides a platform for deploying applications without managing the underlying infrastructure directly?",
        "option_a": "IaaS",
        "option_b": "PaaS",
        "option_c": "Bare metal",
        "option_d": "LAN",
        "correct_answer": "B",
        "difficulty": "Intermediate"
    },

    # =========================
    # CI/CD
    # =========================

    {
        "skill": "CI/CD",
        "question_text": "What does CI stand for?",
        "option_a": "Continuous Integration",
        "option_b": "Code Installation",
        "option_c": "Central Integration",
        "option_d": "Continuous Inspection",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "CI/CD",
        "question_text": "What is the main purpose of continuous integration?",
        "option_a": "Frequently integrate and test code changes",
        "option_b": "Manually deploy once a year",
        "option_c": "Remove version control",
        "option_d": "Disable automated tests",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "CI/CD",
        "question_text": "What does CD commonly refer to in modern software delivery?",
        "option_a": "Continuous Delivery or Continuous Deployment",
        "option_b": "Code Deletion",
        "option_c": "Central Database",
        "option_d": "Compiled Distribution only",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "CI/CD",
        "question_text": "Why are automated tests useful in a CI pipeline?",
        "option_a": "They help detect regressions automatically",
        "option_b": "They eliminate source control",
        "option_c": "They replace developers",
        "option_d": "They prevent all production failures",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "CI/CD",
        "question_text": "What normally happens when a CI pipeline fails?",
        "option_a": "The failure can be reported so the change can be investigated",
        "option_b": "All source code is permanently deleted",
        "option_c": "The database is automatically destroyed",
        "option_d": "The repository becomes read-only forever",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },

    # =========================
    # NETWORKING
    # =========================

    {
        "skill": "Networking",
        "question_text": "What does IP stand for in computer networking?",
        "option_a": "Internet Protocol",
        "option_b": "Internal Process",
        "option_c": "Internet Program",
        "option_d": "Interface Port",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Networking",
        "question_text": "Which protocol is connection-oriented and reliable?",
        "option_a": "UDP",
        "option_b": "TCP",
        "option_c": "IP",
        "option_d": "ARP",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Networking",
        "question_text": "Which device commonly forwards packets between different networks?",
        "option_a": "Router",
        "option_b": "Keyboard",
        "option_c": "Monitor",
        "option_d": "Printer",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Networking",
        "question_text": "What is a subnet primarily used for?",
        "option_a": "Dividing a network into smaller logical networks",
        "option_b": "Encrypting passwords",
        "option_c": "Rendering web pages",
        "option_d": "Compiling code",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Networking",
        "question_text": "Which protocol translates domain names into IP addresses?",
        "option_a": "DNS",
        "option_b": "FTP",
        "option_c": "SMTP",
        "option_d": "SSH",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },

    # =========================
    # SECURITY
    # =========================

    {
        "skill": "Security",
        "question_text": "What is authentication?",
        "option_a": "Verifying who a user is",
        "option_b": "Determining what a user can access",
        "option_c": "Compressing a file",
        "option_d": "Backing up a database",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Security",
        "question_text": "What is authorization?",
        "option_a": "Verifying identity",
        "option_b": "Determining permitted actions or resources",
        "option_c": "Encrypting every file",
        "option_d": "Creating a password",
        "correct_answer": "B",
        "difficulty": "Beginner"
    },
    {
        "skill": "Security",
        "question_text": "Which practice helps protect passwords if a password database is compromised?",
        "option_a": "Storing passwords as plain text",
        "option_b": "Hashing passwords with a suitable password-hashing algorithm",
        "option_c": "Putting passwords in source code",
        "option_d": "Using the same password everywhere",
        "correct_answer": "B",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Security",
        "question_text": "What is multi-factor authentication?",
        "option_a": "Using multiple independent authentication factors",
        "option_b": "Using multiple usernames",
        "option_c": "Using two passwords only",
        "option_d": "Logging in twice",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Security",
        "question_text": "Which principle recommends giving users only the access they need?",
        "option_a": "Least privilege",
        "option_b": "Open access",
        "option_c": "Maximum privilege",
        "option_d": "Shared privilege",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },

    # =========================
    # CYBERSECURITY
    # =========================

    {
        "skill": "Cybersecurity",
        "question_text": "What is phishing?",
        "option_a": "A social-engineering technique used to trick users",
        "option_b": "A database optimization method",
        "option_c": "A network routing protocol",
        "option_d": "A backup strategy",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Cybersecurity",
        "question_text": "What does the CIA triad represent?",
        "option_a": "Confidentiality, Integrity, Availability",
        "option_b": "Control, Inspection, Authentication",
        "option_c": "Confidentiality, Internet, Authorization",
        "option_d": "Cybersecurity, Integrity, Access",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Cybersecurity",
        "question_text": "What is a vulnerability?",
        "option_a": "A weakness that could be exploited",
        "option_b": "A successful backup",
        "option_c": "A secure password",
        "option_d": "A firewall rule that blocks traffic",
        "correct_answer": "A",
        "difficulty": "Beginner"
    },
    {
        "skill": "Cybersecurity",
        "question_text": "What is SQL injection?",
        "option_a": "An attack that manipulates SQL through unsafe input handling",
        "option_b": "A method for indexing SQL tables",
        "option_c": "A database backup method",
        "option_d": "A type of network cable",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
    {
        "skill": "Cybersecurity",
        "question_text": "Which practice is important for reducing common web security vulnerabilities?",
        "option_a": "Validating and safely handling untrusted input",
        "option_b": "Disabling authentication",
        "option_c": "Using plain-text passwords",
        "option_d": "Granting every user administrator access",
        "correct_answer": "A",
        "difficulty": "Intermediate"
    },
]


def seed_role_questions(db_session):
    """Add missing role-specific questions without modifying existing questions."""

    existing_questions = {
        (q.skill, q.question_text)
        for q in db_session.query(Question).all()
    }

    added_count = 0

    for q_data in ROLE_QUESTIONS:
        question_key = (
            q_data["skill"],
            q_data["question_text"]
        )

        if question_key in existing_questions:
            continue

        db_session.add(Question(**q_data))
        existing_questions.add(question_key)
        added_count += 1

    if added_count > 0:
        db_session.commit()

    print(
        f"ROLE_QUESTIONS_ADDED={added_count}; "
        f"TOTAL_QUESTIONS={db_session.query(Question).count()}"
    )
