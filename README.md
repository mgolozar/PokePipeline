# **Coding Challenge: Build a PokéPipeline**

Welcome, future innovator\! At Aventa, we frequently build data pipelines for our clients in the insurance sector. This often involves fetching data from various sources (like REST APIs), transforming it, and loading it into different systems (like databases or exposing it via GraphQL). This challenge is designed to see your approach to such tasks.

# **Your Mission:**

Your core task is to design and build a data pipeline that fetches data about Pokémon from the public PokeAPI (pokeapi.co), transforms this data in a meaningful way, and stores it in a SQL database.

This is an open-ended challenge. We're interested in seeing how you approach the problem and the choices you make. You can decide on the complexity and scope of your solution.

# **Core Requirements:**

1. Data Extraction: Fetch data for at least 10-20 Pokémon from the PokeAPI. You can choose which specific data points you want to extract (e.g., name, types, abilities, stats, evolution chain, etc.).  
2. Data Transformation & Mapping: This is a key part\! Transform the raw data from the API into a more structured format suitable for a relational database. Think about how you would map the often nested and varied API responses to your chosen database schema. Document your mapping decisions.  
3. Data Loading: Store the transformed Pokémon data in a SQL database of your choice (e.g., SQLite, PostgreSQL). You'll need to define the database schema.  
4. README.md: This is mandatory. Your README.md file should include:  
   1. A clear description of your project.  
   2. Instructions on how to set up and run your solution.  
   3. An explanation of your design choices, especially regarding data transformation, mapping, and database schema.  
   4. Any assumptions you made.  
   5. A brief discussion of potential improvements or features you'd add if you had more time.

# **Showcase Your Skills (Optional Components):**

We encourage you to go beyond the core requirements if you wish. These optional components can help you demonstrate a broader range of your skills:

* Pythonic & Robust Code: Write clean, well-documented, and testable Python code for the pipeline.  
* Containerization: Provide a Dockerfile (or docker-compose.yml) to easily build and run your application.  
* Interactive Front-End: Develop a simple web interface (e.g., using HTML/CSS/JavaScript, Next.js, Tailwind CSS, ShadCN) that could, for example:  
  * Trigger the data pipeline.  
  * Display some of the Pokémon data from your database.  
  * Allow basic filtering or searching of the Pokémon.  
* GraphQL Endpoint: Instead of or in addition to the SQL database, (or by reading from your SQL DB), expose some of the transformed Pokémon data via a GraphQL API.  
* Advanced Data Handling: Implement more complex data transformations, handle relationships (e.g., evolutions, types), or incorporate error handling and logging.

# **What We're Looking For:**

* Problem-Solving: How you approach an open-ended task and make design decisions.  
* Data Handling Skills: Your ability to work with APIs, transform data, and design a database schema.  
* Code Quality: Clarity, organization, and efficiency of your code.  
* Understanding of Concepts: Your grasp of data pipelines, REST APIs, SQL, and (if attempted) front-end/GraphQL/Docker concepts.  
* Communication: The clarity and completeness of your README.md.

# **Evaluation:**

You can choose how much time and effort you invest – we value quality and thoughtful solutions over sheer quantity of features. A well-executed core task with a clear explanation can be more impressive than a feature-rich but flawed submission. The optional components are opportunities to shine, but a solid fulfillment of the core requirements is paramount.

# **Submission:**

* Please provide us with a link to a Git repository (e.g., on GitHub, GitLab) containing your solution.  
* We're excited to see what you build\! Good luck\! 

# **Time Expectations:**

We understand that your time is valuable. We estimate that this challenge can be completed to a good standard within 6-8 hours. This timeframe is a guideline to help manage expectations regarding the scope and depth of the solution. Please focus on a quality implementation of the core requirements and any optional components you feel best showcase your skills within this timeframe.

# **Scheduling Your Challenge:**

To help us organize the review process, please let us know which day within the next 10 working days you plan to dedicate to this coding challenge. This allows us to anticipate when we can expect your submission.

# **Use of Coding Assistants/AI Agents:**

You are welcome to use AI-powered coding assistants (e.g., GitHub Copilot, ChatGPT, etc.) to help you with this challenge. If you do use such tools, please be prepared to explain the code you submit and the design choices made, demonstrating your understanding of the solution. Our primary interest is in your ability to solve the problem and articulate your approach.

# **Your Code, Your Portfolio:**

You are welcome and encouraged to publish the code for this challenge on your personal public repository (e.g., GitHub). We believe that the work you do should benefit you beyond this application process. Regardless of the outcome, this allows you to showcase your skills and add another project to your portfolio.
