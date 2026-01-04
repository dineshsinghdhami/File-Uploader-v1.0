from django.db import models
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import sys
from django.core.files.storage import default_storage

class UploadFile(models.Model):
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    original_size = models.BigIntegerField(default=0)  
    compressed_size = models.BigIntegerField(default=0)  
    
    @property
    def file_exists(self):
        """Check if the physical file exists on disk."""
        if self.file and self.file.name:
            try:
                return default_storage.exists(self.file.name)
            except:
                return False
        return False
    
    def save(self, *args, **kwargs):
        
        if not self.pk:
            
            self.original_size = self.file.size
            
            
            ext = self.extension().lower()
            
            
            max_upload_size = 5 * 1024 * 1024 
            if self.file.size > max_upload_size:
                raise ValueError(f"File size must be under 5MB. Your file is {self.file.size/1024/1024:.1f}MB.")
            
            
            total_used = self.get_total_storage()
            max_storage = 500 * 1024 * 1024  
            
            if total_used + self.file.size > max_storage:
               
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                    compressed_data = self.compress_image(self.file, ext)
                    if compressed_data and (total_used + len(compressed_data)) <= max_storage:
                       
                        self.file.save(self.file.name, ContentFile(compressed_data), save=False)
                        self.compressed_size = len(compressed_data)
                    else:
                        
                        raise ValueError("Storage limit reached! Please delete some files.")
                else:
                    
                    raise ValueError("Storage limit reached! Please delete some files.")
            
            
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                compressed_data = self.compress_image(self.file, ext)
                if compressed_data:
                    self.file.save(self.file.name, ContentFile(compressed_data), save=False)
                    self.compressed_size = len(compressed_data)
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def compress_image(file, ext, max_size_kb=500, quality=85):
        """Compress image to reduce file size"""
        try:
            img = Image.open(file)
            
          
            original_mode = img.mode
            
        
            if img.mode in ('RGBA', 'LA', 'P'):
                if img.mode == 'P' and 'transparency' in img.info:
                    img = img.convert('RGBA')
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
        
            if ext in ['png', 'gif', 'bmp']:
              
                output_format = 'JPEG'
                ext = 'jpg'
            else:
                output_format = 'JPEG'
            
            
            img.save(buffer, format=output_format, quality=quality, optimize=True)
            
            
            current_size = buffer.tell()
            min_quality = 30
            
            while current_size > max_size_kb * 1024 and quality > min_quality:
                quality = max(min_quality, quality - 20)
                buffer = BytesIO()
                img.save(buffer, format=output_format, quality=quality, optimize=True)
                current_size = buffer.tell()
            
            return buffer.getvalue()
        except Exception as e:
            print(f"Error compressing image {file.name}: {e}", file=sys.stderr)
            return None
    
    @staticmethod
    def get_total_storage():
        """Calculate total storage used by all files"""
        try:
            total = 0
            for upload in UploadFile.objects.all():
               
                total += upload.get_safe_size()
            return total
        except:
        
            return 0
    
    def get_safe_size(self):
        """Safely get file size, handling missing files"""
        try:
          
            if self.compressed_size and self.compressed_size > 0:
                return self.compressed_size
         
            if self.file_exists and self.file:
                return self.file.size
            
            if self.original_size and self.original_size > 0:
                return self.original_size
            
            return 0
        except (OSError, FileNotFoundError, ValueError, AttributeError):
            return 0
    
    @staticmethod
    def get_storage_info():
        """Get storage usage information"""
        total_used = UploadFile.get_total_storage()
        max_storage = 500 * 1024 * 1024  # 500MB
        
        return {
            'used_bytes': total_used,
            'used_mb': total_used / (1024 * 1024) if total_used > 0 else 0,
            'used_percentage': (total_used / max_storage) * 100 if total_used > 0 else 0,
            'max_mb': 500,
            'remaining_mb': (max_storage - total_used) / (1024 * 1024) if total_used > 0 else 500
        }
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    def extension(self):
       
        name = self.file.name
        if '.' in name:
            return name.split('.')[-1].lower()
        return ''
    
    def is_image(self):
        """Check if file is an image for preview purposes"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'tiff', 'ico']
        return self.extension() in image_extensions
    
    def is_audio(self):
        """Check if file is audio"""
        audio_extensions = ['mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'wma', 'mid', 'midi']
        return self.extension() in audio_extensions
    
    def is_video(self):
        """Check if file is video"""
        video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'mpeg', 'mpg', '3gp', 'm4v']
        return self.extension() in video_extensions
    
    def is_document(self):
        """Check if file is a document"""
        document_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'xml', 'json']
        return self.extension() in document_extensions
    
    def is_archive(self):
        """Check if file is an archive"""
        archive_extensions = ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'iso']
        return self.extension() in archive_extensions
    
    def is_code(self):
        """Check if file is code"""
        code_extensions = ['py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'rb', 'go', 'rs', 'ts']
        return self.extension() in code_extensions
    
    def get_file_icon(self):
        """Get appropriate icon based on file type"""
        if self.is_image():
            return 'fa-image'
        elif self.is_audio():
            return 'fa-music'
        elif self.is_video():
            return 'fa-video'
        elif self.is_document():
            return 'fa-file-alt'
        elif self.is_archive():
            return 'fa-file-archive'
        elif self.is_code():
            return 'fa-code'
        else:
            return 'fa-file'
    
    def get_file_type(self):
        """Get human-readable file type"""
        if self.is_image():
            return 'Image'
        elif self.is_audio():
            return 'Audio'
        elif self.is_video():
            return 'Video'
        elif self.is_document():
            return 'Document'
        elif self.is_archive():
            return 'Archive'
        elif self.is_code():
            return 'Code'
        else:
            return 'File'
    
    def get_size_display(self):
        """Get human readable file size - SAFE VERSION"""
        try:
           
            size_bytes = self.get_safe_size()
            
            if size_bytes == 0:
                return "0 Bytes" if self.file_exists else "File missing"
            
            for unit in ['Bytes', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
            
        except Exception as e:
            return "Size unknown"
    
    def compression_ratio(self):
        """Calculate compression ratio if file was compressed"""
        if hasattr(self, 'compressed_size') and hasattr(self, 'original_size'):
            if self.compressed_size and self.original_size and self.original_size > 0:
                ratio = ((self.original_size - self.compressed_size) / self.original_size) * 100
                return f"{ratio:.1f}%"
        return "N/A"
    
    def get_file_info(self):
        """Get detailed file information"""
        return {
            'filename': self.filename(),
            'extension': self.extension(),
            'type': self.get_file_type(),
            'size': self.get_size_display(),
            'file_exists': self.file_exists,
            'is_image': self.is_image(),
            'is_audio': self.is_audio(),
            'is_video': self.is_video(),
            'is_document': self.is_document(),
            'is_archive': self.is_archive(),
            'is_code': self.is_code(),
            'icon': self.get_file_icon(),
            'compressed': self.compressed_size > 0,
            'compression_ratio': self.compression_ratio(),
            'uploaded_at': self.uploaded_at
        }
    
    def __str__(self):
        return self.filename()