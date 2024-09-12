from django.shortcuts import render
from django.shortcuts import redirect
from django.core.files.base import ContentFile
from .models import  DentalMesh
from django.core.files.storage import default_storage
from django.conf import settings
import os
from django.http import JsonResponse
import json

import numpy as np
import open3d as o3d
import Notebooks.gen_utils as gu
from django.views.decorators.csrf import csrf_exempt

#------ obj to ply file------------#

def convert_obj_to_ply(file_path):

  file_path_obj = os.path.join(settings.MEDIA_ROOT,file_path[7:])
  print("to ply..",file_path_obj)
  mesh_obj = o3d.io.read_triangle_mesh(file_path_obj)
    
    # Ensure normals are computed (optional, depending on your mesh)
  
  mesh_obj.compute_vertex_normals()
  

  
  file_path_store=file_path_obj[:-3]+"ply"
  o3d.io.write_triangle_mesh( file_path_store, mesh_obj)
  
  
  file_path_ply=file_path[:-3]+"ply"

  
  return file_path_ply

  


#----------------Upload file------------------------#
@csrf_exempt
def upload_mesh(request):
  from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from .models import DentalMesh

def upload_mesh(request):
    if request.method == 'POST':
        
        files_Url=[]
        

        # Check and save the upper file if it exists
        if 'upper-file' in request.FILES:
            upper_file = request.FILES['upper-file']
            upper_file.name="upper.obj"
            upper_mesh = DentalMesh(name="upper", file=upper_file)
            upper_mesh.save()
            file_url_upper = default_storage.url(upper_mesh.file.name)  # Get the URL for the saved file
            files_Url.append(file_url_upper)
        # Check and save the lower file if it exists
        if 'lower-file' in request.FILES:
            lower_file = request.FILES['lower-file']
            lower_file.name="lower.obj"
            lower_mesh = DentalMesh(name="lower", file=lower_file)
            
            lower_mesh.save()
            file_url_lower = default_storage.url(lower_mesh.file.name)
            files_Url.append(file_url_lower)

        # Redirect to the visualization page with the relevant file path
        # Adjust the file path according to which file was uploaded
      
        return redirect('visualization', file_path=files_Url)
        
            
        
            

    # If not POST, just render the upload page
    return render(request, 'upload_mesh.html')





#---------------------Visulaization Mesh----------------------------#




def Visualization(request,file_path):
  
     return render(request,'visual.html',{'file_path':file_path}) 
  

#----------------- segmentation -------------------------------#




@csrf_exempt 
def segment_mesh(request):
        
      # ------------Input----------- #

      #==> Mesh_path: mesh_path
      #==> result.json :pred_json_path

      if request.method == 'POST':
          data = json.loads(request.body)
          file_path = data.get('file_path')
          full_path = os.path.join(settings.MEDIA_ROOT, file_path.split('/')[2])

          #pred_json_path = perform_segmentation(file_path)
          if "lower" in file_path :
            pred_json_lower="Templates/013FHA7K_lower.json"
          else :
            pred_json_lower="Templates/013FHA7K_upper.json"
              
          pred_loaded_json = gu.load_json(pred_json_lower)
          pred_labels = np.array(pred_loaded_json['labels']).reshape(-1)

          _, mesh = gu.read_txt_obj_ls(full_path, ret_mesh=True, use_tri_mesh=True)

          Mesh_segmented,labels_colored=gu.get_colored_mesh(mesh, pred_labels)
          base_name=file_path.split('/')[2]
          print(base_name)
          print(np.asarray(Mesh_segmented.vertex_colors))
          output_file_name = f'{base_name[:-4]}_segmented_mesh.obj'
          full=os.path.join(settings.MEDIA_ROOT,output_file_name)
        
          o3d.io.write_triangle_mesh(full, Mesh_segmented)
        
          #path_mesh = os.path.join(settings.MEDIA_ROOT, output_file_name)
        
      file_url = default_storage.url(output_file_name)
      print(labels_colored)
      
      print(full)
      return JsonResponse({'status': 'success','path':file_url,'labels':labels_colored})







  




      



