# Final Project Requirements

**Due Date:** Dec. 19, 2025

---

## Project Options

You have **three options** for your final project. All options should have similar scope and leverage AI techniques covered in class (see **Technical Stack** and **Required AI Techniques** below).

### Option 1: Your Own Project
Design and build an application of your choice that incorporates the techniques we've covered.

### Option 2: Complete the Receipts Application
Extend the receipt parsing application we started in class with **at least one additional AI-powered feature**.

### Option 3: Complete the Reflections Application
Finish the personal reflections app with **embedding-based similarity search and recommendations**.

---

## Technical Stack Requirements

- **Frontend:** FastHTML  
- **Backend:** FastAPI  
- **Data Storage:** Database (e.g., PostgreSQL, SQLite) and/or Vector Store (e.g., ChromaDB)  
- **AI Framework:** Pydantic AI with simple agents  

---

## Required AI Techniques

Your project must incorporate techniques covered in class:

### Structured Output
Use **Pydantic models** to constrain LLM responses for tasks such as:
- Classification
- Data extraction
- Validation  

**Example:** Classifying receipts as `"grocery"` vs `"service"` categories.

### Retrieval Augmented Generation (RAG)
Use **embeddings and vector stores** to retrieve relevant information before generating responses.

---

## Vector Store Integration Ideas

### Reflections App
1. User enters a new reflection  
2. System converts reflection to an embedding  
3. Search vector database for similar past reflections  
4. Display related reflections to help users identify patterns or connections  

### Receipts App  
(*Only one embedding-based feature is required*)

- **Semantic receipt search:**  
  Store itemized receipt data as embeddings, allowing natural language queries like:
  - “Show me all times I bought coffee”
  - “Find receipts at Safeway”

- **Duplicate detection:**  
  Compare new receipt embeddings against existing ones to flag potential duplicates

- **Smart categorization:**  
  Use vector similarity to suggest categories for new items based on past purchases

### Your Own Project
Consider how vector stores could enable:
- Semantic search
- Similarity matching
- Recommendations relevant to your application domain

---

## Code Organization Requirements

### Separation of Concerns
Your code should be organized into logical modules, similar to the receipts application structure:

- Database operations in one module  
- Supabase/external service calls in another  
- Frontend code separate from backend logic  
- AI/agent functionality in dedicated modules  

### Do Not Mix Concerns
Code that mixes database logic with frontend code or combines unrelated responsibilities in a single file will be penalized. Each module should have a **clear, focused purpose**.

### Keep It Focused
Include only:
- Concepts covered in class
- Code necessary for your application to work  

Do **not** include:
- Extensive testing suites  
- Advanced deployment configurations  
- Extra LLM-generated boilerplate not covered in class  

These topics will be addressed in more advanced software engineering courses.

---

## Project Deliverables

1. **Project Description Document** (less than one page)
   - What your application does  
   - AI techniques used and how  
   - Key features and functionality  

2. **Class Diagram**
   - UML class diagram showing main classes and their relationships  

3. **Sequence Diagrams**
   - At least **two** sequence diagrams illustrating key user interactions  
   - Show how components communicate to fulfill user requests  

4. **Code Organization Diagram**
   - Component/module diagram illustrating:
     - Database layer
     - API layer
     - Frontend
     - AI/agent modules  
   - Clearly demonstrates separation of concerns  

---

## Notes

- Pydantic AI usage does **not** need to be complex or fully agentic  
- Simple agents with basic tool calling are acceptable  
- More advanced agentic patterns are welcome but **not required**  
- Focus on building a **complete, working application** demonstrating understanding of AI concepts  

If you’re unsure about code organization or requirements, please reach out to the instructor or TAs **before starting implementation**. They’re happy to help you plan your approach.
