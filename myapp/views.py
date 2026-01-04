from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadFileForm
from .models import UploadFile

def home(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
               
                instance = form.instance
                
              
                if hasattr(instance, 'compressed_size') and instance.compressed_size:
                    messages.success(
                        request,
                        f'✅ File uploaded successfully! '
                        f'Compressed from {instance.original_size/1024/1024:.1f}MB '
                        f'to {instance.compressed_size/1024/1024:.1f}MB '
                        f'({instance.compression_ratio()} smaller)'
                    )
                else:
                    messages.success(request, '✅ File uploaded successfully!')
                return redirect('/')
            except ValueError as e:
              
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'❌ Error uploading file: {str(e)}')
        else:
          
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        form = UploadFileForm()

    files = UploadFile.objects.all().order_by('-uploaded_at')
    
    
    storage_info = UploadFile.get_storage_info()
    
 
    image_count = 0
    audio_count = 0
    video_count = 0
    document_count = 0
    archive_count = 0
    
    for file in files:
        
        if hasattr(file, 'is_image') and file.is_image():
            image_count += 1
        elif hasattr(file, 'is_audio') and file.is_audio():
            audio_count += 1
        elif hasattr(file, 'is_video') and file.is_video():
            video_count += 1
        elif hasattr(file, 'is_document') and file.is_document():
            document_count += 1
        elif hasattr(file, 'is_archive') and file.is_archive():
            archive_count += 1
        else:
           
            document_count += 1

    return render(request, 'myapp/home.html', {
        'form': form,
        'files': files,
        'storage_info': storage_info,
        'image_count': image_count,
        'audio_count': audio_count,
        'video_count': video_count,
        'document_count': document_count,
        'archive_count': archive_count,
        'total_count': len(files),
    })