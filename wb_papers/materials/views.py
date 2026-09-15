from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Material
from .forms import MaterialUploadForm
from colleges.models import College, Stream
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

def materials_list(request):
    materials = Material.objects.all().order_by('-uploaded_at') # uploaded_at is a field in the Material model that stores the timestamp of when the material was uploaded. The '-' sign before 'uploaded_at' indicates that the materials should be ordered in descending order, meaning the most recently uploaded materials will appear first in the list.

    college_id = request.GET.get('college')
    stream_id = request.GET.get('stream')
    sem = request.GET.get('semester')
    material_type = request.GET.get('material_type')

    if college_id and college_id.strip(): #college_id.strip() is used to check if the college_id is not just empty spaces. This prevents filtering with an empty value, which could lead to unintended results.
        materials = materials.filter(college_id=college_id)
    if stream_id and stream_id.strip():
        materials = materials.filter(stream_id=stream_id)
    if sem and sem.strip():
        materials = materials.filter(semester=sem)
    if material_type and material_type.strip():
        materials = materials.filter(material_type=material_type)

    # Placement specific subject filter
    placement_subject = request.GET.get('placement_subject', '').strip()
    if placement_subject:
        materials = materials.filter(subject_name=placement_subject)

    paginator = Paginator(materials, 10)
    page_number = request.GET.get('page') # Get the current page number from the query parameters. If not provided, it defaults to the first page.
    page_obj = paginator.get_page(page_number) # Retrieves the appropriate page of materials based on the current page number. It handles invalid page numbers gracefully, returning the first or last page as needed.get_page() method of the Paginator class is used to get the page object for the current page number. This page object contains the materials for that page and also provides information about pagination (like has_next, has_previous, etc.).

    context = {
        'materials': page_obj,
        'colleges': College.objects.all(),
        'streams': Stream.objects.all(),
    }
    return render(request, 'materials.html', context)


@login_required
def upload_material(request):
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        messages.error(request, "Account error: Profile not found.")
        return redirect('dashboard')

    if profile.role == 'FACULTY' and profile.is_verified:
        if request.method == 'POST':
            form = MaterialUploadForm(request.POST, request.FILES) #request.files is a dictionary-like object that contains all the files uploaded via the form. It is used to handle file uploads in Django forms. When a user submits a form with a file input, the uploaded file is included in request.FILES, allowing the form to process and save the file along with other form data.,request.POST is a dictionary-like object that contains all the data submitted via the form. It is used to handle form submissions in Django. When a user submits a form, the data entered in the form fields is included in request.POST, allowing the form to process and validate the input data.
            if form.is_valid():
                material = form.save(commit=False)#commit=False is used to create a Material instance from the form data without saving it to the database immediately. This allows you to modify the instance (e.g., set the uploaded_by field) before saving it.
                material.uploaded_by = request.user
                # convert empty semester to None for placement notes
                if not material.semester:
                    material.semester = None
                material.save()
                messages.success(request, "Material successfully uploaded!")
                return redirect('materials')
            else:
                messages.error(request, "Error uploading material. Please check the form.")
        else:
            form = MaterialUploadForm()
        return render(request, 'upload_material.html', {'form': form})
    else:
        messages.warning(request, "Verification Pending: Access Denied.")
        return redirect('dashboard')


@login_required
def edit_material(request, pk):
    material = get_object_or_404(Material, pk=pk) #get_object_or_404 is a Django shortcut function that retrieves an object from the database based on the provided primary key (pk). If the object does not exist, it raises a 404 error, which is useful for handling cases where a user tries to access a material that doesn't exist.

    if material.uploaded_by != request.user:
        messages.error(request, "Access Denied: You cannot edit this material.")
        return redirect('materials')

    if request.method == 'POST':
        form = MaterialUploadForm(request.POST, request.FILES, instance=material) #instance=material is used to bind the form to an existing Material instance. This allows the form to pre-populate with the current data of the material being edited, and when the form is submitted, it will update that specific instance instead of creating a new one.
        if not request.FILES.get('pdf_file'): #pdf_file is the name of the file input field in the form. request.FILES.get('pdf_file') checks if a new file has been uploaded. If no new file is uploaded, it means the user wants to keep the existing file, so we set the pdf_file field to not required to avoid validation errors.
            form.fields['pdf_file'].required = False
        if form.is_valid():
            material = form.save(commit=False)
            if not material.semester:
                material.semester = None
            material.save()
            messages.success(request, f"Material updated successfully!")
            return redirect('materials')
    else:
        form = MaterialUploadForm(instance=material) # instance=material is used to pre-fill the form with the existing data of the material being edited. This allows the user to see the current values and make changes as needed. When the form is submitted, it will update this specific instance instead of creating a new one.
        form.fields['pdf_file'].required = False # form.fields['pdf_file'].required = False is used to make the pdf_file field optional when editing an existing material. This means that if the user does not upload a new PDF file while editing, the form will not raise a validation error, allowing the existing file to remain unchanged.

    return render(request, 'edit_material.html', {'form': form, 'material': material})

@login_required
def delete_material(request, pk):
    material = get_object_or_404(Material, pk=pk)

    if material.uploaded_by != request.user:
        messages.error(request, "Access Denied: You cannot delete this material.")
        return redirect('materials')

    if request.method == 'POST':
        material.delete()
        messages.success(request, "Material has been permanently removed.")
        return redirect('materials')

    return render(request, 'delete_material.html', {'material': material})


def get_placement_subjects(request):
    """Returns distinct subjects that have PLACEMENT type materials"""
    subjects = Material.objects.filter(
        material_type='PLACEMENT'
    ).values_list('subject_name', flat=True).distinct().order_by('subject_name') #values_list('subject_name', flat=True) retrieves a list of subject names from the Material model where the material_type is 'PLACEMENT'. The flat=True argument ensures that the result is a flat list of values rather than a list of tuples. distinct() ensures that only unique subject names are returned, eliminating duplicates. order_by('subject_name') sorts the subjects alphabetically by their names.
    return JsonResponse({'subjects': list(subjects)}) #JsonResponse is a Django class that allows you to return JSON-encoded responses from your views. In this case, it takes a dictionary with a key 'subjects' and a value that is a list of distinct placement subjects, and returns it as a JSON response to the client. This is useful for creating API endpoints that can be consumed by frontend applications or other services.


def get_placement_colleges(request):
    """Returns colleges that have PLACEMENT materials for a given subject"""
    subject = request.GET.get('subject', '')
    colleges = Material.objects.filter(
        material_type='PLACEMENT',
        subject_name=subject
    ).values('college__id', 'college__name').distinct()
    return JsonResponse({'colleges': list(colleges)})