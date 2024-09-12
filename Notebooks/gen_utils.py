import open3d as o3d
import numpy as np
import os
import json
import trimesh



def load_json(file_path):
    with open(file_path, "r") as st_json:
        return json.load(st_json)

def save_json(file_path, json_obj):
    with open(file_path, "w") as json_file:

        json.dump(json_obj, json_file)

def load_mesh(mesh_path, only_tooth_crop = False):
    mesh = o3d.io.read_triangle_mesh(mesh_path)
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()
    mesh.remove_unreferenced_vertices()
    
    if only_tooth_crop:
        cluster_idxes, cluster_nums, _ = mesh.cluster_connected_triangles()
        cluster_idxes = np.asarray(cluster_idxes)
        cluster_nums = np.asarray(cluster_nums)
        tooth_cluster_num = np.argmax(cluster_nums)
        mesh.remove_triangles_by_mask(cluster_idxes!=tooth_cluster_num)
    return mesh

def get_colored_mesh(mesh, label_arr):
    palte = np.array([
        [255,153,153],

        [153,76,0],
        [153,153,0],
        [76,153,0],
        [0,153,153],
        [0,0,153],
        [153,0,153],
        [153,0,76],
        [64,64,64],

        [255,128,0],
        [153,153,0],
        [76,153,0],
        [0,153,153],
        [0,0,153],
        [153,0,153],
        [153,0,76],
        [64,64,64],
    ])/255
    palte[9:] *= 0.4
    label_arr = label_arr.copy()
    label_colors = np.zeros((label_arr.shape[0], 3))
    unique_labels = np.unique(label_arr)
    print(unique_labels)
    for idx, label in enumerate(unique_labels):
        label_colors[label_arr == label] = palte[idx]
    mesh.vertex_colors = o3d.utility.Vector3dVector(label_colors)
    print(type(mesh))
    labels_colored={str(unique_labels[i]):palte[i].tolist() for i in range(len(unique_labels))}
    return mesh,labels_colored


def read_txt_obj_ls(path, ret_mesh=False, use_tri_mesh=False):
    # In some cases, trimesh can change vertex order
    if use_tri_mesh:
        tri_mesh_loaded_mesh = trimesh.load_mesh(path, process=False)
        vertex_ls = np.array(tri_mesh_loaded_mesh.vertices)
        tri_ls = np.array(tri_mesh_loaded_mesh.faces)+1
    else:
        f = open(path, 'r')
        vertex_ls = []
        tri_ls = []
        #vertex_color_ls = []
        while True:
            line = f.readline().split()
            if not line: break
            if line[0]=='v':
                vertex_ls.append(list(map(float,line[1:4])))
                #vertex_color_ls.append(list(map(float,line[4:7])))
            elif line[0]=='f':
                tri_verts_idxes = list(map(str,line[1:4]))
                if "//" in tri_verts_idxes[0]:
                    for i in range(len(tri_verts_idxes)):
                        tri_verts_idxes[i] = tri_verts_idxes[i].split("//")[0]
                tri_verts_idxes = list(map(int, tri_verts_idxes))
                tri_ls.append(tri_verts_idxes)
            else:
                continue
        f.close()

    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertex_ls)
    mesh.triangles = o3d.utility.Vector3iVector(np.array(tri_ls)-1)
    mesh.compute_vertex_normals()

    norms = np.array(mesh.vertex_normals)

    vertex_ls = np.array(vertex_ls)
    output = [np.concatenate([vertex_ls,norms], axis=1)]

    if ret_mesh:
        output.append(mesh)
    return output