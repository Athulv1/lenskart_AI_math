import json
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import os
import tempfile
import base64
import uuid
import logging
from django.core.files.base import ContentFile
from django.contrib.admin import SimpleListFilter
from django.contrib import messages
from django.utils.html import format_html
from app.models import Project, ProjectFile, SiteMedia
from django.db.models import Q

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportlabImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image as PILImage
import io


logger = logging.getLogger("app")

# Custom filter for file_type property
class FileTypeFilter(SimpleListFilter):
    title = 'file type'
    parameter_name = 'file_type'

    def lookups(self, request, model_admin):
        # Get unique file types from the database
        file_types = set()
        for project_file in ProjectFile.objects.all():
            file_types.add(project_file.file_type)
        return [(file_type, file_type) for file_type in sorted(file_types)]

    def queryset(self, request, queryset):
        if self.value():
            # Filter files based on the extension
            filtered_files = []
            for project_file in queryset:
                if project_file.file_type == self.value():
                    filtered_files.append(project_file.pk)
            return queryset.filter(pk__in=filtered_files)
        return queryset
    

class SiteMediaTypeFilter(SimpleListFilter):
    title = 'media type'
    parameter_name = 'media_type'

    def lookups(self, request, model_admin):
        return SiteMedia.MEDIA_TYPE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(media_type=self.value())
        return queryset

    
class ProjectStatusFilter(SimpleListFilter):
    title = 'project status'
    parameter_name = 'project_status'

    def lookups(self, request, model_admin):
        return Project.STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project__status=self.value())
        return queryset
    

class ProjectNameFilter(SimpleListFilter):
    title = 'project'  # This is the title that will appear in the admin
    parameter_name = 'project' # This is the URL parameter

    def lookups(self, request, model_admin):
        projects = Project.objects.all().order_by('name')
        return [(p.id, p.name) for p in projects]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project__id=self.value())
        return queryset


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1  # Number of empty forms to display for adding new files
    fields = ['file', 'created_at']
    readonly_fields = ['created_at']

class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectFileInline]
    list_display = ['name', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    actions = None

    
    # Specify the template to use for the change form
    change_form_template = 'admin/app/project/change_form.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve-project/<uuid:project_id>/', self.admin_site.admin_view(self.approve_project), name='approve_project'),
        ]
        return custom_urls + urls
    
    def approve_project(self, request, project_id):
        """Approve a project"""
        project = get_object_or_404(Project, id=project_id)
        
        # Update the status
        project.status = 'approved'
        project.save()
        
        # Show success message
        messages.success(request, f"Project '{project.name}' has been approved!")
        
        # Redirect back to the project detail page
        return redirect('admin:app_project_change', project_id)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        project = self.get_object(request, object_id)
        if project and project.status == 'pending':
            extra_context['show_approve_button'] = True
            extra_context['project_id'] = object_id
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['get_project_name', 'filename', 'file_type', 'created_at']
    list_filter = [FileTypeFilter, ProjectStatusFilter, 'created_at', ProjectNameFilter]
    search_fields = ['project__name', 'file']
    readonly_fields = ['created_at', 'file_type', 'filename']
    raw_id_fields = ('project',)


    actions = None
    
    # Specify the template to use for the change form
    change_form_template = 'admin/app/projectfile/change_form.html'

    def get_project_name(self, obj):
        return obj.project.name
    
    get_project_name.short_description = 'Project Name'
    # This tells Django how to sort this column.
    get_project_name.admin_order_field = 'project__name'

    
    def project_status(self, obj):
        if obj.project.status == 'approved':
            return format_html('<span style="color: green; font-weight: bold;">Approved</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">Pending</span>')
    project_status.short_description = 'Project Status'
    project_status.admin_order_field = 'project__status'

    # Add custom URLs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('save-edited-image/', self.admin_site.admin_view(self.save_edited_image), name='save_edited_image'),
            path('process-floorplan/<uuid:file_id>/', self.admin_site.admin_view(self.process_floorplan), name='process_floorplan'),
            path('download-processed/<uuid:file_id>/', self.admin_site.admin_view(self.download_processed_file), name='download_processed_file'),
            path('download-processed-zip/<uuid:file_id>/', self.admin_site.admin_view(self.download_processed_zip), name='download_processed_zip'), 
            path('approve-project-from-file/<uuid:file_id>/', self.admin_site.admin_view(self.approve_project_from_file), name='approve_project_from_file'),
            path('save-fixtures-config/', self.admin_site.admin_view(self.save_fixtures_config), name='save_fixtures_config'),
            path('get-fixtures-config/<uuid:file_id>/', self.admin_site.admin_view(self.get_fixtures_config), name='get_fixtures_config'),
            path('download-project-pdf/<uuid:file_id>/', self.admin_site.admin_view(self.download_project_pdf), name='download_project_pdf'),

        ]
        return custom_urls + urls
    
    def download_project_pdf(self, request, file_id):
        """Generate and download project PDF report"""
        try:
            project_file = get_object_or_404(ProjectFile, id=file_id)
            project = project_file.project
            
            # Create response with PDF content type
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{project.name}_report.pdf"'
            
            # Create PDF document
            doc = SimpleDocTemplate(response, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.darkgreen
            )
            
            # Title
            story.append(Paragraph(f"Project Report: {project.name}", title_style))
            story.append(Spacer(1, 20))
            
            # Project Description
            if project.description:
                story.append(Paragraph("Description", heading_style))
                story.append(Paragraph(project.description, styles['Normal']))
                story.append(Spacer(1, 15))
            
            # Section 1: General Information
            story.append(Paragraph("1. General Information", heading_style))
            address_text = project.address or 'N/A'
            address_formatted = Paragraph(address_text, styles['Normal'])
            general_data = [
                ['Field', 'Value'],
                ['Address', address_formatted],
                ['Location Reference', project.location_reference or 'N/A'],
                ['Status', project.get_status_display()],
                ['Created Date', project.created_at.strftime('%Y-%m-%d %H:%M')],
                ['Updated Date', project.updated_at.strftime('%Y-%m-%d %H:%M')],
            ]
            general_table = Table(general_data, colWidths=[2.5*inch, 4*inch], rowHeights=None)
            general_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(general_table)
            story.append(Spacer(1, 20))
            
            # (All other table sections remain the same)
            # Section 2: Site Details
            story.append(Paragraph("2. Site Details", heading_style))
            site_data = [['Field', 'Value'],['Total Carpet Area', f"{project.total_carpet_area} sq.ft." if project.total_carpet_area else 'N/A'],['Floor Level', project.floor_level or 'N/A'],['Electricity Load', f"{project.electricity_load} KW" if project.electricity_load else 'N/A'],['Electricity Meter Location', project.electricity_meter_location or 'N/A'],]
            site_table = Table(site_data, colWidths=[2.5*inch, 4*inch])
            site_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('ALIGN', (0, 0), (-1, -1), 'LEFT'),('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),('FONTSIZE', (0, 0), (-1, 0), 12),('BOTTOMPADDING', (0, 0), (-1, 0), 12),('BACKGROUND', (0, 1), (-1, -1), colors.beige),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            story.append(site_table)
            story.append(Spacer(1, 20))
            # Section 3: HVAC and Utilities
            story.append(Paragraph("3. HVAC and Utilities", heading_style))
            hvac_data = [['Field', 'Value'],['HVAC System Type', project.get_hvac_system_type_display() if project.hvac_system_type else 'N/A'],['AC Outdoor Units Location', project.ac_outdoor_units_location or 'N/A'],['Drainage Facility', 'Yes' if project.drainage_facility else 'No'],['Water Connection', 'Yes' if project.water_connection else 'No'],]
            hvac_table = Table(hvac_data, colWidths=[2.5*inch, 4*inch])
            hvac_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('ALIGN', (0, 0), (-1, -1), 'LEFT'),('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),('FONTSIZE', (0, 0), (-1, 0), 12),('BOTTOMPADDING', (0, 0), (-1, 0), 12),('BACKGROUND', (0, 1), (-1, -1), colors.beige),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            story.append(hvac_table)
            story.append(Spacer(1, 20))
            # Section 4: Site Orientation and Access
            story.append(Paragraph("4. Site Orientation and Access", heading_style))
            orientation_data = [['Field', 'Value'],['Main Entrance Direction', project.main_entrance_direction or 'N/A'],['Nearest Airport', project.nearest_airport or 'N/A'],['Airport Distance', f"{project.airport_distance} KM" if project.airport_distance else 'N/A'],['Nearest Railway Station', project.nearest_railway_station or 'N/A'],['Railway Station Distance', f"{project.railway_station_distance} KM" if project.railway_station_distance else 'N/A'],]
            orientation_table = Table(orientation_data, colWidths=[2.5*inch, 4*inch])
            orientation_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('ALIGN', (0, 0), (-1, -1), 'LEFT'),('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),('FONTSIZE', (0, 0), (-1, 0), 12),('BOTTOMPADDING', (0, 0), (-1, 0), 12),('BACKGROUND', (0, 1), (-1, -1), colors.beige),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            story.append(orientation_table)
            story.append(Spacer(1, 20))
            # Section 5: Additional Facilities
            story.append(Paragraph("5. Additional Facilities", heading_style))
            facilities_data = [['Field', 'Value'],['Washroom', project.washroom or 'N/A'],['Remarks', project.remarks or 'N/A'],]
            facilities_table = Table(facilities_data, colWidths=[2.5*inch, 4*inch])
            facilities_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),('ALIGN', (0, 0), (-1, -1), 'LEFT'),('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),('FONTSIZE', (0, 0), (-1, 0), 12),('BOTTOMPADDING', (0, 0), (-1, 0), 12),('BACKGROUND', (0, 1), (-1, -1), colors.beige),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            story.append(facilities_table)
            story.append(Spacer(1, 30))
            
            # Define the available width for images on the A4 page
            available_width = A4[0] - 2*inch
            
            # Project Files Section
            project_files = project.files.all()
            image_files = [pf for pf in project_files if pf.file_type in ['png', 'jpg', 'jpeg']]
            if image_files:
                story.append(Paragraph("Project Files", heading_style))
                for idx, pf in enumerate(image_files, 1):
                    try:
                        with PILImage.open(pf.file.path) as img:
                            orig_width, orig_height = img.size
                        aspect = orig_height / float(orig_width)
                        display_width = available_width
                        display_height = display_width * aspect
                        rl_img = ReportlabImage(pf.file.path, width=display_width, height=display_height)
                        
                        # --- CHANGE 1: REMOVED FILENAME DISPLAY ---
                        # story.append(Paragraph(f"<b>File: {pf.filename}</b>", styles['Normal']))
                        
                        story.append(rl_img)

                        filename_lower = pf.filename.lower()
                        if 'note' in filename_lower or 'beam' in filename_lower:
                            room_measurements_dir = os.path.join(settings.MEDIA_ROOT, 'room_measurements')
                            safe_project_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                            json_filename = f"{safe_project_name}_{project.id}_room_measurements.json"
                            json_file_path = os.path.join(room_measurements_dir, json_filename)
                            if os.path.exists(json_file_path):
                                try:
                                    with open(json_file_path, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                        notes_data = data.get('room_measurements', {}).get('notes', [])
                                        if notes_data:
                                            story.append(Spacer(1, 10))
                                            story.append(Paragraph("<b>Associated Notes:</b>", styles['Normal']))
                                            notes_table_data = [['#', 'Text']]
                                            def get_note_text(note_item):
                                                if not isinstance(note_item, dict): return 'Invalid note format'
                                                for key in ['text', 'Text', 'label', 'note']:
                                                    if key in note_item: return note_item[key]
                                                for key, value in note_item.items():
                                                    if isinstance(value, str) and key != 'number': return value
                                                return 'N/A'
                                            for note in notes_data:
                                                note_text_content = get_note_text(note)
                                                note_text_para = Paragraph(str(note_text_content), styles['Normal'])
                                                notes_table_data.append([note.get('number', 'N/A'), note_text_para])
                                            notes_table = Table(notes_table_data, colWidths=[0.5*inch, 6.0*inch])
                                            notes_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),('TEXTCOLOR', (0, 0), (-1, 0), colors.black),('ALIGN', (0, 0), (0, -1), 'CENTER'),('ALIGN', (1, 0), (1, -1), 'LEFT'),('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),('BOTTOMPADDING', (0, 0), (-1, 0), 10),('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),('GRID', (0, 0), (-1, -1), 0.5, colors.grey),('VALIGN', (0,0), (-1,-1), 'TOP')]))
                                            story.append(notes_table)
                                except Exception as e:
                                    logger.warning(f"Could not process notes JSON {json_filename} for PDF report: {e}")
                        story.append(Spacer(1, 25)) # Increased spacer for better separation between images
                    except Exception as e:
                        logger.warning(f"Could not process image {pf.filename}: {e}")
                        story.append(Paragraph(f"Image could not be displayed", styles['Normal']))
                        story.append(Spacer(1, 10))
            
            # Site Media Section
            site_media = project.site_media.all()
            site_images = [sm for sm in site_media if sm.is_image]
            if site_images:
                story.append(Paragraph("Site Media", heading_style))
                for idx, sm in enumerate(site_images, 1):
                    try:
                        with PILImage.open(sm.file.path) as img:
                            orig_width, orig_height = img.size
                        aspect = orig_height / float(orig_width)
                        display_width = available_width
                        display_height = display_width * aspect
                        rl_img = ReportlabImage(sm.file.path, width=display_width, height=display_height)
                        
                        # --- CHANGE 2: REMOVED FILENAME DISPLAY ---
                        # story.append(Paragraph(f"<b>File: {sm.filename}</b>", styles['Normal']))
                        
                        story.append(rl_img)
                        story.append(Spacer(1, 25)) # Increased spacer for better separation
                    except Exception as e:
                        logger.warning(f"Could not process site media {sm.filename}: {e}")
                        story.append(Paragraph(f"Site media image could not be displayed", styles['Normal']))
                        story.append(Spacer(1, 10))

            def set_pdf_metadata(canvas, doc):
                canvas.setTitle("Project Report")
                canvas.setAuthor("ThinkNeural AI")
                canvas.setSubject("Project Details Report")
            
            doc.build(story, onFirstPage=set_pdf_metadata)
            return response
            
        except Exception as e:
            logger.exception(f"Error generating PDF for project file {file_id}: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})


        
        

    

    def save_fixtures_config(self, request):
        if request.method == 'POST':
            try:
                import json
                
                file_id = request.POST.get('file_id')
                fixtures_data = request.POST.get('fixtures_data')
                
                if not file_id or not fixtures_data:
                    return JsonResponse({'success': False, 'error': 'Missing required data'})
                
                project_file = get_object_or_404(ProjectFile, id=file_id)
                project = project_file.project
                
                new_data = json.loads(fixtures_data)

                # Get the existing fixtures data from the database.
                # If it's null or empty, start with an empty dictionary.
                existing_fixtures = project.fixtures or {}

                # Update the existing data with the new values.
                # The .update() method merges the dictionaries, overwriting only the keys that match.
                existing_fixtures.update(new_data)
                
                
                project.fixtures = existing_fixtures
                project.save()
                
                return JsonResponse({'success': True, 'message': 'Fixtures configuration saved successfully'})
                
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
            except Exception as e:
                logger.exception(f"Error saving fixtures config: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    

    def get_fixtures_config(self, request, file_id):
        """Get current fixtures configuration for a project"""
        try:
            project_file = get_object_or_404(ProjectFile, id=file_id)
            project = project_file.project
            
            # Default fixtures configuration
            default_fixtures = {
                "proto": "15L",
                "primary_side": "Left",  # Default value for the radio button
                "branded_eye": 0.0,
                "branded_sun": 0.0,
                "jj_eye": 4.0,
                "jj_sun": 1.0,
                "vc_eye": 4.1,
                "vc_sun": 2.2,
                "lk_air": 4.7,
                "vc_kids": 2.0,
                "reading_glasses": 0.0,
                "cl": 0.0,
                "od": 0.0,
                "lpl": 0.0,
                "tentpole": 5.0,
                "hustlr": 5.0,
                "total": 20.0, # This can be made auto-calculating in the frontend if needed
            }

            
            # Use saved fixtures or default
            fixtures_config = project.fixtures
            if not fixtures_config or "proto" not in fixtures_config:
                fixtures_config = default_fixtures
            
            return JsonResponse({
                'success': True,
                'fixtures': fixtures_config,
                'project_name': project.name
            })

            
        except Exception as e:
            logger.exception(f"Error getting fixtures config: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})


        
    def approve_project_from_file(self, request, file_id):
        """Approve a project from the file admin page"""
        project_file = get_object_or_404(ProjectFile, id=file_id)
        project = project_file.project
        
        # Update the status
        project.status = 'approved'
        project.save()
        
        # Show success message
        messages.success(request, f"Project '{project.name}' has been approved!")
        
        # Redirect back to the project file detail page
        return redirect('admin:app_projectfile_change', file_id)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        project_file = self.get_object(request, object_id)
        if not project_file:
            return super().change_view(request, object_id, form_url, extra_context)

        project = project_file.project
        extra_context["original"] = project_file
        extra_context["file_id"] = str(project_file.id)
        extra_context["show_approve_button"] = project.status == "pending"
        
        # Add fixtures_configured check
        extra_context["fixtures_configured"] = bool(project.fixtures)

        # Determine which file ID to use for ZIP lookup
        zip_file_base_id = project_file.id

        # If the current file is an FCStd, fall back to most recent image in project
        if project_file.file.name.lower().endswith('.fcstd'):
            image_file = (
                ProjectFile.objects.filter(project=project)
                .filter(Q(file__iendswith=".png") | Q(file__iendswith=".jpg") | Q(file__iendswith=".jpeg"))
                .order_by('-created_at')
                .first()
            )
            if image_file:
                zip_file_base_id = image_file.id
        
        # If the current file is a processed DXF, find the original image file that was processed
        elif project_file.file.name.lower().endswith('.dxf') and 'processed' in project_file.filename.lower():
            # Look for the original image file in the same project
            image_file = (
                ProjectFile.objects.filter(project=project)
                .filter(Q(file__iendswith=".png") | Q(file__iendswith=".jpg") | Q(file__iendswith=".jpeg"))
                .order_by('-created_at')
                .first()
            )
            if image_file:
                zip_file_base_id = image_file.id

        # Look for ZIP file
        output_dir = os.path.join(os.getcwd(), f"{zip_file_base_id}_floorplan_output")
        zip_path = os.path.join(output_dir, "package.zip")

        if os.path.exists(zip_path):
            extra_context["show_download_zip_button"] = True
            extra_context["download_zip_url"] = reverse("admin:download_processed_zip", args=[zip_file_base_id])
        else:
            extra_context["show_download_zip_button"] = False

        return super().change_view(request, object_id, form_url, extra_context=extra_context)






    def process_floorplan(self, request, file_id):
        """Process an image through the Django Ninja API"""
        # Instead of using TestClient, we'll make a direct call to the underlying function
        from app.api import process_floorplan as api_process_floorplan
        
        project_file = get_object_or_404(ProjectFile, id=file_id)

        # Check if the project is approved
        if project_file.project.status != 'approved':
            messages.error(request, "Project must be approved before processing files")
            return redirect('admin:app_projectfile_change', project_file.id)
        
        # Check if the file is an image
        if project_file.file_type not in ['png', 'jpg', 'jpeg']:
            messages.error(request, "Only image files can be processed")
            return redirect('admin:app_projectfile_change', project_file.id)
        
        try:
            # Call the function directly instead of using TestClient
            result = api_process_floorplan(request, file_id)
            
            if result and isinstance(result, tuple) and len(result) == 2:
                status_code, data = result
                
                if status_code == 200:
                    # Get the processed file
                    processed_file_id = data.get("processed_file_id")

                    import time
                    time.sleep(2)
                    
                    # Show success message
                    messages.success(request, "Floorplan processed successfully!")
                    
                    # Redirect to the processed file
                    return redirect('admin:app_projectfile_change', processed_file_id)
                else:
                    # Show error message
                    error_message = data.get("message", "Unknown error")
                    messages.error(request, f"Error processing floorplan: {error_message}")
                    return redirect('admin:app_projectfile_change', file_id)
            else:
                messages.error(request, "Unexpected response format")
                return redirect('admin:app_projectfile_change', file_id)
        
        except Exception as e:
            logger.exception(f"Error processing floorplan in admin: {str(e)}")
            messages.error(request, f"Error processing floorplan: {str(e)}")
            return redirect('admin:app_projectfile_change', file_id)

    def download_processed_file(self, request, file_id):
        """Download a processed file"""
        project_file = get_object_or_404(ProjectFile, id=file_id)
        
        # Check if the project is approved
        if project_file.project.status != 'approved':
            messages.error(request, "Project must be approved before downloading files")
            return redirect('admin:app_projectfile_change', project_file.id)
        
        # Open the file and return it as a download
        response = FileResponse(
            project_file.file.open(),
            as_attachment=True,
            filename=project_file.filename
        )
        return response
    

    def download_processed_zip(self, request, file_id):
        """Download the generated package.zip file for a processed floorplan"""
        project_file = get_object_or_404(ProjectFile, id=file_id)
        
        # Check if the project is approved (optional, but good for consistency)
        if project_file.project.status != 'approved':
            messages.error(request, "Project must be approved before downloading files.")
            return redirect('admin:app_projectfile_change', project_file.id)

        # Construct the expected path to the package.zip file
        project_name_from_file_id = f"{project_file.id}_floorplan"
        output_dir_name = f"{project_name_from_file_id}_output"
        project_root = settings.BASE_DIR
        
        # Check both possible ZIP file locations
        zip_file_path = os.path.join(project_root, output_dir_name, "package.zip")
        zip_file_path_alt = os.path.join(project_root, f"{project_name_from_file_id}_package.zip")
        
        print(f"[DEBUG] Looking for ZIP files:")
        print(f"[DEBUG] Path 1: {zip_file_path}")
        print(f"[DEBUG] Path 2: {zip_file_path_alt}")
        
        # Try the first path, then the alternative
        if os.path.exists(zip_file_path):
            print(f"[DEBUG] Found ZIP at: {zip_file_path}")
            response = FileResponse(
                open(zip_file_path, 'rb'),
                as_attachment=True,
                filename=f"{project_name_from_file_id}_package.zip",
                content_type='application/zip'
            )
            return response
        elif os.path.exists(zip_file_path_alt):
            print(f"[DEBUG] Found ZIP at: {zip_file_path_alt}")
            response = FileResponse(
                open(zip_file_path_alt, 'rb'),
                as_attachment=True,
                filename=f"{project_name_from_file_id}_package.zip",
                content_type='application/zip'
            )
            return response
        else:
            print(f"[DEBUG] No ZIP file found at either location")
            messages.error(request, "Processed ZIP file not found.")
            return redirect('admin:app_projectfile_change', project_file.id)

    # Add a display function for the list_display
    def download_processed_zip_link(self, obj):
        project_name_from_file_id = f"{obj.id}_floorplan" # Consistent naming
        output_dir_name = f"{project_name_from_file_id}_output"
        project_root = settings.BASE_DIR
        zip_file_path = os.path.join(project_root, output_dir_name, "package.zip")

        if os.path.exists(zip_file_path):
            return format_html(
                '<a href="{}">Download ZIP</a>',
                reverse('admin:download_processed_zip', args=[obj.id])
            )
        return "N/A"
    
    download_processed_zip_link.short_description = 'Processed ZIP'

    @method_decorator(csrf_protect)
    def save_edited_image(self, request):
        if request.method == 'POST':
            try:
                file_id = request.POST.get('file_id')
                image = request.FILES.get('image')
                rotation_raw = request.POST.get('rotation')
                
                # Parse rotation angle
                try:
                    rotation = float(rotation_raw) if rotation_raw is not None else 0.0
                except (ValueError, TypeError):
                    rotation = 0.0

                if not file_id or not image:
                    return JsonResponse({'success': False, 'error': 'Missing file ID or image data'})

                project_file = get_object_or_404(ProjectFile, id=file_id)
                project = project_file.project

                
                room_measurements_data = project.room_measurements or {}

                
                room_measurements_data['rotation'] = rotation

                # 3. Save the modified dictionary back to the project's JSONField.
                project.room_measurements = room_measurements_data
                project.save()

                original_path = project_file.file.path
                project_file.file.save(
                    os.path.basename(original_path),
                    image,
                    save=True
                )
                
                logger.info(f"Updated rotation to {rotation}° in room_measurements for project {project.id}")
                return JsonResponse({'success': True})

            except ProjectFile.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'File not found'})
            except Exception as e:
                logger.exception(f"Error saving edited image: {e}")
                return JsonResponse({'success': False, 'error': str(e)})

        return JsonResponse({'success': False, 'error': 'Invalid request method'})


    

class SiteMediaAdmin(admin.ModelAdmin):
    list_display = ['id','project_name', 'filename', 'media_type', 'file_type', 'created_at']
    list_filter = [SiteMediaTypeFilter, ProjectStatusFilter, 'created_at', 'project']
    search_fields = ['project__name', 'file']
    readonly_fields = ['created_at', 'file_type', 'filename', 'media_type']
    
    def project_name(self, obj):
        return obj.project.name
    project_name.short_description = 'Project Name'
    project_name.admin_order_field = 'project__name'
    
    def project_status(self, obj):
        if obj.project.status == 'approved':
            return format_html('<span style="color: green; font-weight: bold;">Approved</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">Pending</span>')
    project_status.short_description = 'Project Status'
    project_status.admin_order_field = 'project__status'



# Register with custom admin classes
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectFile, ProjectFileAdmin)
admin.site.register(SiteMedia, SiteMediaAdmin)
