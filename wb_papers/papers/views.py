from django.shortcuts import render, redirect,get_object_or_404
from .models import Paper
from .forms import PaperUploadForm 
from colleges.models import College, Stream
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
import datetime
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from .ai_utils import extract_text_from_pdf, get_gemini_analysis


def dashboard(request):
    colleges = College.objects.all()
    return render(request, 'dashboard.html', {'colleges': colleges})

# Paper Search  Filter Logic
def paper_search(request):
    papers = Paper.objects.all().order_by('-year') # Default sorting: Newest papers first
    college_id = request.GET.get('college')
    stream_id = request.GET.get('stream')# Get filter values from query parameters in the URL. For example, if the user selects a college and stream from dropdowns on the frontend, those selections will be sent as query parameters like ?college=1&stream=2. The view retrieves these values using request.GET.get() to apply the appropriate filters to the papers queryset.
    sem = request.GET.get('semester')
    year = request.GET.get('year')
    exam_type = request.GET.get('exam_type') #

    if college_id: papers = papers.filter(college_id=college_id) # If the college_id parameter is present in the query parameters, the view filters the papers queryset to include only those papers that belong to the specified college. This is done using the filter() method on the queryset, which adds a condition to match the college_id field of the Paper model with the provided college_id value. For example, if college_id=1, only papers associated with the college that has an ID of 1 will be included in the results.
    if stream_id: papers = papers.filter(stream_id=stream_id)
    if sem: papers = papers.filter(semester=sem)
    if year: papers = papers.filter(year=year) # Similarly, if the year parameter is provided, the view filters the papers queryset to include only those papers that were published in the specified year. This allows users to narrow down their search results based on the publication year of the papers. For example, if year=2023, only papers published in the year 2023 will be included in the results.
    
    if exam_type: papers = papers.filter(exam_type=exam_type)

    # ---- Applying Paginator Logic -----
    paginator = Paginator(papers, 10) # 10 papers per page
    page_number = request.GET.get('page') # Get the current page number from query parameters. For example, if the user clicks on a pagination link that points to ?page=2, the view retrieves this value using request.GET.get('page') to determine which set of papers to display.
    page_obj = paginator.get_page(page_number) # The get_page() method of the Paginator class takes the page number as an argument and returns a Page object containing the papers for that specific page. If the page number is not provided or is invalid, it defaults to the first page. For example, if page_number=2, the view will return a Page object containing papers 11-20 from the filtered queryset. This allows users to navigate through multiple pages of search results without overwhelming them with too many papers at once.


    current_year = datetime.datetime.now().year
    year_range = range(current_year, current_year - 10, -1) # This line generates a range of years starting from the current year and going back 10 years. The range is created using the range() function, which takes three arguments: the start year (current_year), the end year (current_year - 10), and the step (-1) to generate the years in descending order. For example, if the current year is 2024, the year_range will include 2024, 2023, 2022, and so on down to 2015. This range can be used in the frontend to populate a dropdown menu for filtering papers by publication year.

    context = { # This context dictionary is passed to the template to provide the necessary data for rendering the papers page. It includes the paginated papers (page_obj), a list of all colleges and streams for filter dropdowns, and the year_range for the year filter. The template can access these variables to display the papers and populate the filter options accordingly.
        'papers': page_obj, #  
        'colleges': College.objects.all(),
        'streams': Stream.objects.all(),
        'year_range': year_range,
    }
    return render(request, 'papers.html', context)

@login_required
def upload_paper(request):
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        messages.error(request, "Account error: Profile not found.")
        return redirect('dashboard')

    if profile.role == 'FACULTY' and profile.is_verified:
        if request.method == 'POST':
            form = PaperUploadForm(request.POST, request.FILES) # This line initializes the PaperUploadForm with the data submitted by the user through the POST request. The request.POST contains the form data (such as title, college, stream, etc.), while request.FILES contains any uploaded files (in this case, the PDF file of the paper). By passing both of these to the form, it allows the form to validate and process all the submitted information correctly. For example, if a faculty member fills out the form to upload a paper and submits it, this line will create an instance of PaperUploadForm populated with their input, which can then be validated and saved to the database if everything is correct.
            if form.is_valid():
                paper = form.save(commit=False) # COMMIT=False -> This line saves the form data to create a new Paper instance but does not commit it to the database yet. This allows us to set additional fields on the paper instance (such as uploaded_by) before saving it permanently. For example, after validating the form data and creating the paper instance, we can assign the currently logged-in user to the uploaded_by field before calling paper.save() to save it to the database.
                paper.uploaded_by = request.user
                paper.save()
                messages.success(request, "Paper successfully published!")
                return redirect('dashboard')
            else:
                messages.error(request, "Error publishing paper.")
        else:
            form = PaperUploadForm()

        return render(request, 'upload.html', {'form': form})

    else:
        messages.warning(request, "Verification Pending: Access Denied.")
        return redirect('dashboard')

# Password change Logic
@login_required # This decorator ensures that only authenticated users can access the change_password view. If an unauthenticated user tries to access this view, they will be redirected to the login page. This is important for security reasons, as changing a password should only be allowed for users who are currently logged in and have verified their identity.
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST) # This line initializes the PasswordChangeForm with the current user and the data submitted through the POST request. The form will use the current user's information to validate the old password and ensure that the new password meets the required criteria. For example, when a user submits the password change form, this line creates an instance of PasswordChangeForm that is aware of which user is trying to change their password, allowing it to perform the necessary checks and validations based on that user's credentials.
        if form.is_valid():
            user = form.save()
            # This is the key: prevents logging the user out after change
            update_session_auth_hash(request, user) # After successfully changing the password, this line updates the session authentication hash for the user. This is important because when a user's password is changed, their session authentication hash becomes invalid, which would normally log them out of the system. By calling update_session_auth_hash(), we ensure that the user remains logged in even after changing their password, providing a smoother user experience. For example, if a user changes their password successfully, they will not be forced to log in again immediately, allowing them to continue using the application without interruption.
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)  
    return render(request, 'password_change.html', {'form': form})

# Implementing Papers Edit and Delete Logic
@login_required
def edit_paper(request, pk):  
    # pk is Primary Key / id , to get the exact row where we will update
    paper = get_object_or_404(Paper, pk=pk) # pk is passed as an argument to the view, which is used to retrieve the specific Paper instance from the database. The get_object_or_404 function is a shortcut that tries to fetch the Paper with the given primary key (pk). If a Paper with that pk exists, it will be returned; otherwise, it will raise a 404 error, indicating that the requested paper was not found. This ensures that the view only proceeds if a valid paper is being edited. For example, if a user tries to access /edit_paper/5/, this line will attempt to retrieve the Paper with an ID of 5. If it exists, it will be stored in the variable paper for further processing; if not, a 404 error page will be shown.
    
    if paper.uploaded_by != request.user: # This line checks if the currently logged-in user is the same as the user who uploaded the paper. This is a security measure to ensure that only the original uploader of the paper can edit it. If the logged-in user is not the one who uploaded the paper, they are not authorized to make changes to it, and an error message is displayed, followed by a redirect to the papers page. For example, if User A uploaded a paper and User B tries to access the edit page for that paper, this check will fail, and User B will see an "Unauthorized access" message and be redirected away from the edit page.
        messages.error(request, "Unauthorized access.")
        return redirect('papers')

    if request.method == 'POST':
        form = PaperUploadForm(request.POST, request.FILES, instance=paper) #   This line initializes the PaperUploadForm with the data submitted through the POST request, any uploaded files, and the existing paper instance that is being edited. By passing instance=paper, the form will be pre-populated with the current data of the paper, allowing the user to see and modify the existing information. For example, when a user submits changes to a paper, this line creates a form instance that includes both the new data they entered and the original paper data, enabling the form to validate and save the updates correctly. request.files is included to handle any new PDF file that the user may upload while editing the paper. If no new file is uploaded, the form will still validate and allow changes to other fields without requiring a new PDF.
        # If faculty didn't upload a new PDF, don't make it mandatory
        if not request.FILES.get('pdf_file'):
            form.fields['pdf_file'].required = False
        if form.is_valid():
            updated_paper = form.save(commit=False) # This line saves the form data to create an updated Paper instance but does not commit it to the database yet. This allows us to perform additional logic before saving, such as checking if a new PDF file was uploaded. For example, after validating the form data and creating the updated paper instance, we can check if the user uploaded a new PDF file. If they did not, we can choose to update only the other fields without affecting the existing PDF file in the database.
            if not request.FILES.get('pdf_file'):
                # No new file uploaded — update all other fields only
                # Using queryset.update() instead of .save() so Django
                # never touches the pdf_file column in the DB
                # pk = paper.pk ensures we update the correct record without needing to load it into memory as a model instance
                Paper.objects.filter(pk=paper.pk).update( # This line performs a direct update on the Paper instance in the database without using the save() method. By using Paper.objects.filter(pk=paper.pk).update(), we can update specific fields of the paper without affecting the pdf_file field. This is important because if we were to call updated_paper.save(), it would attempt to save all fields, including pdf_file, which could lead to issues if no new file was uploaded (since the form would not have a valid file to save). By using the update() method, we can ensure that only the specified fields are updated while leaving the existing PDF file intact. For example, if a user edits a paper and changes the title and subject name but does not upload a new PDF, this line will update only the title and subject name in the database, while keeping the original PDF file unchanged.
                    title=updated_paper.title,
                    subject_name=updated_paper.subject_name,
                    subject_code=updated_paper.subject_code, # This line updates the subject_code field of the Paper instance in the database with the new value provided in the updated_paper instance. If the user made changes to the subject code while editing the paper, this line ensures that those changes are saved to the database. For example, if the original subject code was "CS-401" and the user changed it to "CS-402" in the edit form, this line will update the subject_code field in the database to reflect that change.
                    college=updated_paper.college,
                    stream=updated_paper.stream,
                    exam_type=updated_paper.exam_type,
                    year=updated_paper.year,
                    semester=updated_paper.semester,
                )
            else:
                # New paper pdf file uploaded — so, save everything including the new PDF
                updated_paper.save()
            messages.success(request, f"Changes saved for {paper.subject_code}!")
            return redirect('dashboard')
    else:
        # GET request — load the form pre-filled with existing paper data
        form = PaperUploadForm(instance=paper) # When the edit_paper view is accessed via a GET request, this line initializes the PaperUploadForm with the existing paper instance. This means that the form will be pre-filled with the current data of the paper, allowing the user to see all the existing information and make changes as needed. For example, if a user clicks on an "Edit" button for a specific paper, they will be taken to a form that already contains the current title, subject name, subject code, college, stream, exam type, year, semester, and any other relevant information about that paper. This makes it easier for users to update only the fields they want to change without having to re-enter all the information from scratch.
        # PDF not required on GET so faculty can view/edit without re-uploading
        form.fields['pdf_file'].required = False  #
    
    return render(request, 'edit_paper.html', {'form': form, 'paper': paper})

@login_required
def delete_paper(request, pk):
    paper = get_object_or_404(Paper, pk=pk) # This line retrieves the Paper instance with the given primary key (pk) from the database. If a Paper with that pk exists, it will be returned; otherwise, a 404 error will be raised, indicating that the requested paper was not found. This ensures that the view only proceeds if a valid paper is being targeted for deletion. For example, if a user tries to access /delete_paper/5/, this line will attempt to retrieve the Paper with an ID of 5. If it exists, it will be stored in the variable paper for further processing; if not, a 404 error page will be shown.
    
    # Security Check
    if paper.uploaded_by != request.user:
        messages.error(request, "Access Denied: You cannot delete this paper.")
        return redirect('papers')

    if request.method == 'POST':
        paper.delete()
        messages.success(request, "Paper has been permanently removed.")
        return redirect('papers')
    
    return render(request, 'delete_paper.html', {'paper': paper})

# ----------- AI INTEGRATION -------------

def ai_lab_dashboard(request):
    # Step 1: Initial Filter Form
    colleges = Paper.objects.values_list('college__name', flat=True).distinct() # This line retrieves a list of unique college names from the Paper model. The values_list() method is used to specify that we only want the 'college__name' field, and flat=True ensures that we get a simple list of names instead of a list of tuples. The distinct() method ensures that only unique college names are returned, eliminating any duplicates. For example, if there are multiple papers associated with the same college, this line will return only one instance of that college name in the resulting list. This list can then be used to populate a dropdown menu on the frontend for users to select a college as part of their filters for AI analysis.
    streams = Stream.objects.all()
    return render(request, 'ai_lab_form.html', {
        'colleges': colleges,
        'streams': streams
    })

def ai_select_subject(request):
    """ Intermediate step to find valid subjects based on filters """
    if request.method == 'POST':
        task = request.POST.get('task_type') # task_type is sent from the frontend when the user submits the initial filter form. This line retrieves the selected task type (e.g., 'topics', 'summary', 'mock_test', or 'pdf_upload') from the POST data. The task type will determine the subsequent flow of the analysis process. For example, if the user selects "Topic Extraction" as their analysis goal, task will be set to 'topics', which can then be used in later steps to customize the AI analysis accordingly.

        # If user chose manual PDF upload, skip straight to analysis
        if task == 'pdf_upload':
            return ai_analyze(request)

        # Get filter data
        start = request.POST.get('start_year')
        end = request.POST.get('end_year')
        sem = request.POST.get('semester')
        institution_name = request.POST.get('institution')
        stream_id = request.POST.get('stream')
        exam_type = request.POST.get('exam_type')

        # Find all unique subjects that actually exist for these filters
        papers = Paper.objects.filter(year__range=(start, end), semester=sem) # This line filters the Paper queryset to include only those papers that were published within the specified year range (from start to end) and belong to the specified semester (sem). The year__range lookup is used to filter papers based on their publication year, while the semester filter ensures that only papers from the selected semester are included. For example, if a user selects a start year of 2020, an end year of 2023, and a semester of "Fall", this line will return all papers published between 2020 and 2023 that are associated with the "Fall" semester.
        if institution_name != 'All':
            papers = papers.filter(college__name=institution_name) # If the institution_name filter is not set to 'All', this line further filters the papers queryset to include only those papers that are associated with the specified institution (college). The filter is applied using the college__name lookup, which checks the name of the related College model for each paper. For example, if a user selects "ABC University" as their institution filter, this line will narrow down the papers to only those that are linked to a college with the name "ABC University". If the user selects 'All', this filter is skipped, and papers from all institutions will be included in the results.
        if stream_id != 'All':
            papers = papers.filter(stream_id=stream_id)
        if exam_type and exam_type != 'All':
            papers = papers.filter(exam_type=exam_type)

        # Using QuerySets in Django
        subjects = papers.values( # papers.values() is used to create a QuerySet that returns dictionaries containing only the specified fields for each paper. In this case, we are interested in the 'subject_name', 'subject_code', 'year', and 'exam_type' fields. By using values(), we can efficiently retrieve only the necessary information about the subjects that match the applied filters, without loading the entire Paper model instances into memory. For example, if there are multiple papers with the same subject name and code but different years or exam types, this line will return a list of dictionaries with unique combinations of those fields based on the filtered papers.
            'subject_name', 
            'subject_code', 
            'year',
            'exam_type'
        ).distinct().order_by('-year') # The distinct() method ensures that only unique combinations of the specified fields are returned, eliminating any duplicate entries. The order_by('-year') method sorts the results in descending order based on the year field, so that the most recent subjects appear first in the list. For example, if there are multiple papers for "Data Structures" with different years, this will ensure that only one entry for "Data Structures" is returned, and it will be sorted to show the most recent year at the top of the list.

        return render(request, 'ai_select_subject.html', {
            'subjects': subjects,
            'task': task,
            'filters': request.POST # This line includes the original filter parameters in the context passed to the template. By including 'filters': request.POST, we ensure that all the filter values selected by the user in the initial form are available in the ai_select_subject.html template. This allows us to maintain the user's filter selections as they navigate through the analysis process, and we can also pass these filters along to subsequent views (like ai_analyze) to ensure that the AI analysis is performed based on the same criteria. For example, if a user selected a specific college, stream, year range, semester, and exam type in the initial form, all of those selections will be included in the filters context variable, which can then be used to pre-populate forms or make decisions in later steps of the analysis workflow.
        })
    return redirect('ai_lab')

def ai_analyze(request):
    if request.method == 'POST':
        task = request.POST.get('task_type') # This line retrieves the task type from the POST data, which indicates the specific AI analysis that the user wants to perform (e.g., 'topics', 'summary', 'mock_test', or 'pdf_upload'). The task variable will be used to determine how the combined text extracted from the papers should be processed and what kind of analysis should be performed by the AI. For example, if task is set to 'topics', the AI might focus on extracting key topics from the text, while if it's set to 'summary', the AI would generate a concise summary of the content. This allows for a flexible analysis process that can adapt to different user goals based on their selection.
        combined_text = "" # This variable will be used to accumulate the text extracted from the selected papers or uploaded PDFs. By initializing it as an empty string, we can concatenate the extracted text from multiple sources into a single string that can then be passed to the AI for analysis. For example, if a user selects multiple papers for topic extraction, the text from all those papers will be combined into this variable before being sent to the AI, allowing for a comprehensive analysis of all the selected content at once.

        # Logic for stored papers
        if task in ['topics', 'summary','mock_test']: # If the task is one of 'topics', 'summary', or 'mock_test', this block of code will execute to extract text from the papers that match the user's filters. The logic will retrieve the selected subject name and other filter criteria from the POST data, then query the Paper model to find all papers that match those criteria. The text from each of those papers will be extracted and combined into a single string (combined_text) that can then be analyzed by the AI. For example, if a user selects "Topic Extraction" as their task and chooses a specific subject, year range, semester, and exam type, this block will find all papers that match those filters, extract their text, and prepare it for AI analysis.
            subject_name = request.POST.get('selected_subject')
            exam_type = request.POST.get('exam_type')
            papers = Paper.objects.filter(
                subject_name=subject_name,
                year__range=(request.POST.get('start_year'), request.POST.get('end_year')),
                semester=request.POST.get('semester')
            )
            if exam_type and exam_type != 'All':
                papers = papers.filter(exam_type=exam_type)
            for paper in papers[:5]:
                combined_text += extract_text_from_pdf(paper.pdf_file) #extract_text_from_pdf is a utility function(we made this function in ai_utils.py) that takes a PDF file as input and returns the extracted text content as a string. In this line, we are iterating over the filtered papers (limited to the first 5 for performance reasons) and calling extract_text_from_pdf on each paper's pdf_file field. The extracted text from each paper is then concatenated to the combined_text variable, which will accumulate the text from all selected papers. For example, if there are 3 papers that match the user's filters, this loop will extract text from each of those 3 PDFs and combine it into a single string that can be analyzed by the AI.
        
        # Logic for manual uploads
        elif task == 'pdf_upload':
            for slot in ['pdf1', 'pdf2', 'pdf3']:
                f = request.FILES.get(slot) # This line retrieves the uploaded file from the request for each of the specified slots (pdf1, pdf2, pdf3). The request.FILES is a dictionary-like object that contains all the files uploaded in the request, and get(slot) is used to access the file associated with each slot name. If a file was uploaded for that slot, it will be returned; otherwise, it will return None. This allows us to check if the user has uploaded a file for each slot and process it accordingly. For example, if a user uploads a PDF file in the "pdf1" slot, this line will retrieve that file and store it in the variable f for further processing (such as extracting text from it).
                if f:
                    combined_text += extract_text_from_pdf(f)

        # Execution
        if not combined_text.strip(): # This line checks if the combined_text variable is empty or contains only whitespace after stripping leading and trailing whitespace characters. If combined_text.strip() evaluates to an empty string, it means that no valid text was extracted from the selected papers or uploaded PDFs. In such a case, we return an error message to the user indicating that no text could be extracted, which prompts them to check their file selections or filters. For example, if a user selects papers that have issues with their PDFs (e.g., corrupted files) or uploads invalid files, this check will catch that scenario and provide feedback instead of attempting to run the AI analysis on empty input.
            return render(request, 'ai_result.html', {'result': "Error: No text could be extracted. Please check your files or selection."})

        # Single API call - task parameter will determine the prompt and analysis style in ai_utils.py
        result = get_gemini_analysis(combined_text, task) # This line calls the get_gemini_analysis function (defined in ai_utils.py) with the combined text extracted from the papers or uploaded PDFs and the specified task type. The get_gemini_analysis function is responsible for sending the text to the Gemini API and receiving the analysis results based on the task. The task parameter will help determine how the prompt is structured and what kind of analysis is performed by the AI (e.g., extracting topics, generating a summary, creating mock test questions, etc.). For example, if task is 'topics', the function might send a prompt to Gemini asking it to identify key topics from the provided text, and then return those topics as the result.

        return render(request, 'ai_result.html', {'result': result, 'task': task}) # task is included in the context to allow the ai_result.html template to customize the display of the results based on the type of analysis performed. For example, if the task was 'summary', the template might display the result as a concise summary, while if the task was 'topics', it might format the result as a list of key topics. By passing both the result and the task to the template, we can ensure that the presentation of the AI analysis is tailored to the user's selected goal.
    
    return redirect('ai_lab')
