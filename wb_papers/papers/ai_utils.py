import openai 
from django.conf import settings
import PyPDF2

def get_gemini_analysis(combined_text, task_type):
    #  Validate key existence before doing anything else
    api_key = getattr(settings, 'OPENROUTER_API_KEY', None) # This line retrieves the OpenRouter API key from the Django settings. It uses getattr to safely access the OPENROUTER_API_KEY attribute, returning None if it doesn't exist. This allows the function to check if the API key is available before attempting to make any API calls, which is crucial for preventing errors and ensuring that the application can provide a meaningful error message if the key is missing. For example, if the OPENROUTER_API_KEY is not set in the settings, this line will return None, and we can handle that case gracefully in the subsequent code.
    # GUARD: Stop execution if there is no content/less content
    if not combined_text or len(combined_text) < 30: # This line checks if the combined_text variable is empty or has less than 30 characters. If either condition is true, it means that there is not enough meaningful content to analyze, and the function will return an error message instead of attempting to call the AI API. This guard clause helps prevent unnecessary API calls with insufficient data, which could lead to errors or irrelevant results. For example, if a user uploads a PDF that doesn't contain much text or selects papers that have very little content, this check will catch that scenario and provide feedback instead of proceeding with an analysis that would likely fail or produce poor results.
        return "Not enough data to analyze. Please upload valid PDF."

    # Initialize the OpenRouter client
    client = openai.OpenAI( # This line initializes the OpenAI client using the OpenRouter API. By creating an instance of openai.OpenAI with the specified base_url and api_key, we can use this client to make requests to the OpenRouter API for various AI tasks. The base_url points to the OpenRouter endpoint, and the api_key is used for authentication. For example, when we later call client.chat.completions.create(), it will use this configuration to send the request to the correct API endpoint with the necessary authentication.
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key, # Key is  in settings.py and loaded from .env, so it won't be hardcoded here.
    )
    
    prompts = {
        'topics': (
            "You are an academic expert for West Bengal universities. Analyze these papers and identify top recurring topics.\n\n"
            "Output strictly in this format, exactly as shown:\n\n"
            "### Topic Extraction on [subject(subject code)]\n"
            "Topic: [Name]\n"
            "  - Priority: [High/Medium/Low]\n"
            "  - Subtopics: [List of subtopics]\n\n"
            "After listing all topics, conclude with this exact header:\n"
            "### Important Related Topics \n"
            "[List Other Core Important Topics related to this.]"
            "### Exam Strategy\n"
            "[Your 2-sentence strategy note]"
        ),

        'summary': (
            "STRICT INSTRUCTION: DO NOT OUTPUT PARAGRAPHS. USE MARKDOWN HEADERS AND BULLET POINTS ONLY. DOUBLE NEWLINE BETWEEN SECTIONS.\n\n"
            "You are a tutor. Summarize these papers as follows:\n\n"
            "### Executive Summary\n- [Brief Summary]\n\n"
            "### Key Concepts Covered\n- [Item 1]\n- [Item 2]\n\n"
            "### Common Probable Questions\n- [Question 1]\n- [Question 2]\n\n"
            "### Suggested Study Resources\n- [Resource 1]"
        ),

        'pdf_upload': (
                "STRICT INSTRUCTION: DO NOT OUTPUT DENSE PARAGRAPHS. USE MARKDOWN HEADERS AND BULLET POINTS ONLY.\n"
                
                "You are a Senior Academic Analyst. Analyze the provided documents:\n\n"
                "### 1. Context Assessment\n"
                "- [One sentence identifying the relationship between the documents]\n\n"
                "### 2. Conceptual Pillars & Weightage\n"
                "- [Identify the 'High-Value' knowledge areas. Focus on topic clusters, module weightage, and difficulty tiers. Do not write questions here; focus solely on the 'What to study' aspect.]\n\n"
                "### 3. Practical Exam Simulation (Practice Set)\n"
                "- [Translate the concepts from Point 2 into a comprehensive list of specific, exam-style questions. Focus on the 'How it is tested' aspect. Provide enough questions to cover the full breadth of the topics.]\n  - Answer Expectation: [Brief explanation of what the answer requires, e.g., 'Diagram', 'Derivation', 'Case Study']\n\n"
                "### 4. Required Answer Complexity\n"
                "- [Brief bulleted summary of the depth, technical vocabulary, and structure required to score high marks.]\n\n"
                "### 5. Future Trend Projection (Next Year's Probable Q)\n"
                "- [Predict evolutionary trends. Identify related, more complex, or peripheral concepts that are logically next in the learning progression. Do not repeat current questions.]"
            ),

        'mock_test': (
            "STRICT INSTRUCTION: FORMAT AS A CLEAN LIST. NO INTRODUCTIONS. NO PARAGRAPHS.\n\n"
            "Create 25 high-priority MCQs. Follow this exact template for every question and use double-spacing:\n\n"
            "### 25 high-priority MCQs \n"
            "Q[Number]: [Question Text]\n\n"
            "A) [Option]\n"
            "B) [Option]\n"
            "C) [Option]\n"
            "D) [Option]\n\n"
            "Correct Answer: [Option]\n"
            "Explanation: [Brief reason]\n\n"
            "---" # Visual separator for the AI
        )
    }

    try:
        # We use the Gemini Flash 2.0 model via OpenRouter's gateway
        completion = client.chat.completions.create( # This line sends a request to the OpenRouter API to create a chat completion using the Gemini Flash 2.0 model. The messages parameter contains the prompt that we want the AI to analyze, which is constructed based on the task type and the combined text extracted from the papers or uploaded PDFs. The prompt is designed to instruct the AI on how to process the text and what kind of output to generate based on the user's selected task (e.g., extracting topics, summarizing content, creating mock test questions, etc.). For example, if the task type is 'topics', the prompt will ask the AI to identify recurring topics in the provided text and format the output in a specific way.
            model="google/gemini-2.0-flash-001", # chat.completions is it build in method for chat-based models, and we specify the model we want to use (in this case, Gemini Flash 2.0) to ensure that we are leveraging the capabilities of that specific model for our analysis. By using this model, we can take advantage of its advanced language understanding and generation capabilities to produce high-quality results based on the input text and the task requirements.
            messages=[
                {"role": "user", "content": f"{prompts.get(task_type, 'Analyze:')}\n\n{combined_text[:10000]}"} #promts.get(task_type, 'Analyze:') retrieves the appropriate prompt template based on the task_type. If the task_type is not found in the prompts dictionary, it defaults to a simple "Analyze:" prompt. The combined_text[:10000] part ensures that we only send the first 10,000 characters of the combined text to the AI, which helps manage token limits and ensures that we are sending a manageable amount of data for analysis. This way, we can still provide a substantial amount of content for the AI to work with while avoiding issues with excessively long inputs.
            ],
        )
        return completion.choices[0].message.content # This line retrieves the content of the AI's response from the completion object returned by the OpenRouter API. The completion.choices is a list of possible completions generated by the AI, and we typically take the first one (choices[0]) as the most relevant response. The message.content contains the actual text generated by the AI based on the prompt and input we provided. This is the result that will be returned to the user and displayed in the ai_result.html template. For example, if the task was 'summary', this content would contain the summary generated by the AI based on the combined text from the papers or uploaded PDFs.
        
    except Exception as e: # Exception handling is crucial for managing potential errors that may arise during the API call, such as network issues, invalid API keys, or rate limits. By catching exceptions, we can provide meaningful feedback to the user instead of crashing the application. For example, if the API key is missing or invalid, an exception will be raised, and we can catch that to inform the user about the issue rather than allowing the application to fail silently or with a generic error.
        error_msg = str(e)
        # OpenRouter uses similar error codes, so this catch remains useful
        if "429" in error_msg:   # if too many requests send
            return "AI Rate Limit: The server is busy. Please wait 60 seconds."
        return f"AI Error: {error_msg}" # For any other exceptions that occur during the API call, we return a generic error message that includes the specific error details. This helps users understand what went wrong and can assist in troubleshooting issues related to the AI analysis. For example, if there is a network error or an issue with the input data, the exception message will provide insight into the nature of the problem, allowing users to take corrective action or report the issue with more context.

def extract_text_from_pdf(pdf_file): # This function is responsible for extracting text from a given PDF file. It uses the PyPDF2 library to read the PDF and extract text from its pages. The function is designed to handle potential errors gracefully, ensuring that if there are issues with reading the PDF (such as a corrupted file), it will catch the exception and print an error message instead of crashing the application. For example, if a user uploads a PDF that cannot be read, this function will catch that error and provide feedback, allowing the user to try again with a valid file.
    """Kept identical so you don't need to change other files."""
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file) #pypdf2.PdfReader is a class from the PyPDF2 library that is used to read PDF files. By creating an instance of PdfReader with the provided pdf_file, we can access the contents of the PDF and extract text from its pages. This line initializes the reader object that will be used to iterate through the pages of the PDF and extract text content for further processing. For example, if a user uploads a PDF file, this line will create a reader object that allows us to read the file and access its pages to extract the necessary text for AI analysis.
        for page in reader.pages[:8]:   # For now only read the first 8 pages of the pdf
            content = page.extract_text() # The extract_text() method is called on each page object to extract the text content from that page. This method processes the PDF's internal structure to retrieve the textual information, which can then be combined and analyzed. By iterating through the first 8 pages of the PDF, we can gather a substantial amount of text for analysis while managing performance and token limits for the AI. For example, if a user uploads a lengthy PDF, this loop will ensure that we only extract text from the first 8 pages, which is often sufficient for analysis while avoiding issues with excessively long inputs.
            if content:
                text += content
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text