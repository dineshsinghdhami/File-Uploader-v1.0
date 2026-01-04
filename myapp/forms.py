from django import forms
from .models import UploadFile
from django.core.exceptions import ValidationError

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ['file']
        labels = {'file': ''}
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': '*'  
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            
            max_upload_size = 5 * 1024 * 1024  
            
            if file.size > max_upload_size:
                size_mb = file.size / (1024 * 1024)
                raise ValidationError(
                    f'File size must be under 5MB. Your file is {size_mb:.1f}MB.'
                )
            
            
            total_used = UploadFile.get_total_storage()
            max_storage = 500 * 1024 * 1024  
            
            if total_used + file.size > max_storage:
               
                ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
                
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                   
                    estimated_compressed_size = 500 * 1024 
                    if total_used + estimated_compressed_size <= max_storage:
                        
                        pass
                    else:
                        available_mb = (max_storage - total_used) / (1024 * 1024)
                        raise ValidationError(
                            f'Storage limit reached! Only {available_mb:.1f}MB available. '
                            f'Please delete some files to free up space.'
                        )
                else:
                    available_mb = (max_storage - total_used) / (1024 * 1024)
                    raise ValidationError(
                        f'Storage limit reached! Only {available_mb:.1f}MB available. '
                        f'Please delete some files or upload a smaller file.'
                    )
            
            dangerous_extensions = ['exe', 'bat', 'cmd', 'sh', 'php', 'js', 'html']
            ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
            
            if ext in dangerous_extensions:
               
                print(f"⚠️ Warning: Uploaded file with potentially dangerous extension: .{ext}")
                
        
        return file